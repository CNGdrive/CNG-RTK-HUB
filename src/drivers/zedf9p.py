"""
ZED-F9P GNSS receiver driver with UBX protocol support.
Implementation from IMPLEMENTATION_GUIDE.md
"""

import asyncio
import serial_asyncio
from typing import Optional
from ..core.interfaces import IGNSSDriver, GNSSState, FixType, ConnectionError, ProtocolError


class ZedF9PDriver(IGNSSDriver):
    def __init__(self):
        self._serial_reader = None
        self._serial_writer = None
        self._current_state: Optional[GNSSState] = None
        self._running = False
        
    async def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Connect to ZED-F9P receiver via serial port."""
        try:
            self._serial_reader, self._serial_writer = await serial_asyncio.open_serial_connection(
                url=port, baudrate=baudrate
            )
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to ZED-F9P on {port}: {e}")
    
    async def start_data_stream(self) -> None:
        """Start receiving and parsing UBX data."""
        if not self._serial_reader:
            raise ProtocolError("Not connected - call connect() first")
        
        self._running = True
        asyncio.create_task(self._data_processing_loop())
    
    async def _data_processing_loop(self):
        """Main data processing loop for UBX messages."""
        buffer = bytearray()
        
        while self._running and self._serial_reader:
            try:
                # Read data from serial port
                data = await self._serial_reader.read(1024)
                if not data:
                    continue
                    
                buffer.extend(data)
                
                # Process complete UBX messages
                while len(buffer) >= 8:  # Minimum UBX message size
                    # Look for UBX sync chars (0xB5 0x62)
                    sync_pos = buffer.find(b'\xb5\x62')
                    if sync_pos == -1:
                        buffer.clear()
                        break
                    
                    # Remove data before sync
                    if sync_pos > 0:
                        buffer = buffer[sync_pos:]
                    
                    # Check if we have enough data for header
                    if len(buffer) < 6:
                        break
                    
                    # Extract message length
                    msg_length = int.from_bytes(buffer[4:6], 'little')
                    total_length = 6 + msg_length + 2  # header + payload + checksum
                    
                    if len(buffer) < total_length:
                        break  # Wait for more data
                    
                    # Extract complete message
                    ubx_message = buffer[:total_length]
                    buffer = buffer[total_length:]
                    
                    # Process UBX message
                    await self._process_ubx_message(ubx_message)
                    
            except Exception as e:
                print(f"Error in data processing: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_ubx_message(self, message: bytes):
        """Process a complete UBX message."""
        try:
            # Check message type (bytes 2-3 are class, bytes 4-5 are ID)
            msg_class = message[2]
            msg_id = message[3]
            
            # UBX-NAV-PVT (0x01 0x07)
            if msg_class == 0x01 and msg_id == 0x07:
                if validate_ubx_checksum(message):
                    self._current_state = parse_ubx_nav_pvt(message)
                else:
                    print("UBX checksum validation failed")
                    
        except Exception as e:
            print(f"Error processing UBX message: {e}")
    
    def get_current_state(self) -> Optional[GNSSState]:
        """Return latest normalized state or None if no data."""
        return self._current_state
    
    def inject_corrections(self, rtcm_data: bytes) -> bool:
        """Inject RTCM corrections to receiver."""
        if not self._serial_writer:
            return False
        
        try:
            self._serial_writer.write(rtcm_data)
            return True
        except Exception:
            return False
    
    async def disconnect(self) -> None:
        """Clean shutdown and disconnect."""
        self._running = False
        
        if self._serial_writer:
            self._serial_writer.close()
            await self._serial_writer.wait_closed()
            
        self._serial_reader = None
        self._serial_writer = None
        self._current_state = None


def parse_ubx_nav_pvt(data: bytes) -> GNSSState:
    """Parse UBX-NAV-PVT message (0x01 0x07) - Position, Velocity, Time"""
    # UBX header: 0xB5 0x62 0x01 0x07 [length] [payload] [checksum]
    if len(data) < 100:  # NAV-PVT is 92 bytes + headers
        raise ProtocolError("UBX-NAV-PVT message too short")
    
    # Extract fields (little-endian)
    year = int.from_bytes(data[10:12], 'little')
    month = data[12]
    day = data[13]
    hour = data[14]
    minute = data[15]
    second = data[16]
    nano = int.from_bytes(data[22:26], 'little')
    
    fix_type = data[26]  # 0=none, 1=DR, 2=2D, 3=3D, 4=GNSS+DR, 5=time
    carr_soln = data[27]  # 0=none, 1=float, 2=fixed
    
    lat = int.from_bytes(data[32:36], 'little', signed=True) * 1e-7
    lon = int.from_bytes(data[36:40], 'little', signed=True) * 1e-7
    height = int.from_bytes(data[40:44], 'little', signed=True) * 1e-3
    h_acc = int.from_bytes(data[48:52], 'little') * 1e-3
    num_sv = data[29]
    p_dop = int.from_bytes(data[82:84], 'little') * 0.01
    
    # Map to FixType
    if carr_soln == 2:
        fix_type_enum = FixType.FIX
    elif carr_soln == 1:
        fix_type_enum = FixType.FLOAT
    elif fix_type in [2, 3, 4]:
        fix_type_enum = FixType.DGPS
    else:
        fix_type_enum = FixType.NO_FIX
    
    return GNSSState(
        timestamp_utc=f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{nano//1000000:03d}Z",
        fix_type=fix_type_enum,
        latitude=lat,
        longitude=lon,
        altitude_m=height,
        accuracy_m=h_acc,
        sats={"GPS": num_sv},
        pdop=p_dop,
        baseline_m=0.0,
        correction_source="None",
        receiver_meta={"model": "ZED-F9P"}
    )


def validate_ubx_checksum(data: bytes) -> bool:
    """Validate UBX message checksum."""
    if len(data) < 8:
        return False
    ck_a = ck_b = 0
    for byte in data[2:-2]:  # Skip sync chars and checksum
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return data[-2] == ck_a and data[-1] == ck_b
