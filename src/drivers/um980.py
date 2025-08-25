"""
UM980 GNSS receiver driver with Unicore binary protocol support.
Implementation from IMPLEMENTATION_GUIDE.md
"""

import asyncio
import datetime
from typing import Optional
from ..core.interfaces import IGNSSDriver, GNSSState, FixType, ConnectionError, ProtocolError


class UM980Driver(IGNSSDriver):
    def __init__(self):
        self._serial_reader = None
        self._serial_writer = None
        self._current_state: Optional[GNSSState] = None
        self._running = False
        
    async def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Connect to UM980 receiver via serial port."""
        try:
            # Note: Using same pattern as ZedF9P, will need serial_asyncio
            import serial_asyncio
            self._serial_reader, self._serial_writer = await serial_asyncio.open_serial_connection(
                url=port, baudrate=baudrate
            )
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to UM980 on {port}: {e}")
    
    async def start_data_stream(self) -> None:
        """Start receiving and parsing Unicore binary data."""
        if not self._serial_reader:
            raise ProtocolError("Not connected - call connect() first")
        
        self._running = True
        asyncio.create_task(self._data_processing_loop())
    
    async def _data_processing_loop(self):
        """Main data processing loop for Unicore binary messages."""
        buffer = bytearray()
        
        while self._running and self._serial_reader:
            try:
                # Read data from serial port
                data = await self._serial_reader.read(1024)
                if not data:
                    continue
                    
                buffer.extend(data)
                
                # Process complete Unicore messages
                while len(buffer) >= 28:  # Minimum Unicore header size
                    # Look for Unicore sync chars (0xAA 0x44 0x12 0x1C)
                    sync_pos = -1
                    for i in range(len(buffer) - 3):
                        if (buffer[i] == 0xAA and buffer[i+1] == 0x44 and 
                            buffer[i+2] == 0x12 and buffer[i+3] == 0x1C):
                            sync_pos = i
                            break
                    
                    if sync_pos == -1:
                        buffer.clear()
                        break
                    
                    # Remove data before sync
                    if sync_pos > 0:
                        buffer = buffer[sync_pos:]
                    
                    # Check if we have enough data for header
                    if len(buffer) < 28:
                        break
                    
                    # Extract message length from header
                    msg_length = int.from_bytes(buffer[8:10], 'little')
                    total_length = 28 + msg_length + 4  # header + payload + CRC
                    
                    if len(buffer) < total_length:
                        break  # Wait for more data
                    
                    # Extract complete message
                    unicore_message = buffer[:total_length]
                    buffer = buffer[total_length:]
                    
                    # Process Unicore message
                    await self._process_unicore_message(unicore_message)
                    
            except Exception as e:
                print(f"Error in UM980 data processing: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_unicore_message(self, message: bytes):
        """Process a complete Unicore binary message."""
        try:
            # Extract message ID from header (bytes 4-6)
            msg_id = int.from_bytes(message[4:6], 'little')
            
            # BESTPOS message (ID 42)
            if msg_id == 42:
                self._current_state = parse_unicore_bestpos(message)
                    
        except Exception as e:
            print(f"Error processing Unicore message: {e}")
    
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


def parse_unicore_bestpos(data: bytes) -> GNSSState:
    """Parse Unicore BESTPOS message."""
    # Unicore binary header + BESTPOS payload
    if len(data) < 72:  # BESTPOS minimum size
        raise ProtocolError("BESTPOS message too short")
    
    # Extract GPS week and seconds
    gps_week = int.from_bytes(data[14:16], 'little')
    gps_seconds = int.from_bytes(data[16:20], 'little') / 1000.0
    
    # Position and accuracy
    lat = int.from_bytes(data[20:28], 'little', signed=True) / 1e7
    lon = int.from_bytes(data[28:36], 'little', signed=True) / 1e7
    height = int.from_bytes(data[36:44], 'little', signed=True) / 1000.0
    
    lat_stdev = int.from_bytes(data[44:48], 'little') / 1000.0
    lon_stdev = int.from_bytes(data[48:52], 'little') / 1000.0
    
    sol_status = data[4:20].decode('ascii').strip('\x00')  # Solution status
    num_svs = data[64]
    
    # Map solution status to FixType
    status_map = {
        "SOL_COMPUTED": FixType.FIX,
        "INSUFFICIENT_OBS": FixType.NO_FIX,
        "NO_CONVERGENCE": FixType.NO_FIX,
        "SINGULARITY": FixType.NO_FIX,
        "COV_TRACE": FixType.DGPS,
        "TEST_DIST": FixType.DGPS,
        "COLD_START": FixType.NO_FIX,
        "V_H_LIMIT": FixType.DGPS,
        "VARIANCE": FixType.DGPS,
        "RESIDUALS": FixType.DGPS,
        "DELTA_POS": FixType.DGPS,
        "NEGATIVE_VAR": FixType.DGPS,
        "INTEGRITY_WARNING": FixType.FLOAT,
        "INS_INACTIVE": FixType.DGPS,
        "INS_ALIGNING": FixType.DGPS,
        "INS_BAD": FixType.DGPS,
        "IMU_UNPLUGGED": FixType.DGPS,
        "PENDING": FixType.NO_FIX,
        "INVALID_FIX": FixType.NO_FIX
    }
    
    return GNSSState(
        timestamp_utc=gps_week_to_iso8601(gps_week, gps_seconds),
        fix_type=status_map.get(sol_status, FixType.NO_FIX),
        latitude=lat,
        longitude=lon,
        altitude_m=height,
        accuracy_m=max(lat_stdev, lon_stdev),
        sats={"GPS": num_svs},
        pdop=0.0,  # Get from separate DOP message
        baseline_m=0.0,
        correction_source="None",
        receiver_meta={"model": "UM980"}
    )


def gps_week_to_iso8601(week: int, seconds: float) -> str:
    """Convert GPS week/seconds to ISO8601 timestamp."""
    # GPS epoch: 1980-01-06 00:00:00 UTC
    gps_epoch = datetime.datetime(1980, 1, 6, tzinfo=datetime.timezone.utc)
    timestamp = gps_epoch + datetime.timedelta(weeks=week, seconds=seconds)
    return timestamp.isoformat().replace('+00:00', 'Z')
