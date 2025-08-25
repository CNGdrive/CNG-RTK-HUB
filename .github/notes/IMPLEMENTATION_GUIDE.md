# Complete Implementation Guide

**Purpose**: Single-source implementation context for AI agents  
**Target**: ZED-F9P + UM980 dual-receiver RTK client  
**Platform**: Android tablets with 8+ hour field operation

---

## Core Interfaces (Copy-Paste Ready)

### IGNSSDriver Interface
```python
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional

class FixType(Enum):
    NO_FIX = "NO_FIX"
    DGPS = "DGPS" 
    FLOAT = "FLOAT"
    FIX = "FIX"

class ConnectionError(Exception):
    pass

class ProtocolError(Exception):
    pass

@dataclass
class GNSSState:
    timestamp_utc: str          # ISO8601: "2025-08-25T14:30:15.123Z"
    fix_type: FixType
    latitude: float             # WGS84 degrees
    longitude: float            # WGS84 degrees
    altitude_m: float           # Ellipsoidal height
    accuracy_m: float           # 1-sigma horizontal
    sats: Dict[str, int]        # {"GPS":6,"GLO":4,"GAL":8,"BDS":3}
    pdop: float                 # Position dilution
    baseline_m: float           # RTK baseline distance
    correction_source: str      # NTRIP source or "None"
    receiver_meta: Dict         # {"model":"ZED-F9P","fw":"1.13"}

class IGNSSDriver(ABC):
    @abstractmethod
    async def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Connect to receiver. Raise ConnectionError on failure."""
        pass
    
    @abstractmethod
    async def start_data_stream(self) -> None:
        """Start receiving data. Raise ProtocolError on failure."""
        pass
    
    @abstractmethod
    def get_current_state(self) -> Optional[GNSSState]:
        """Return latest normalized state or None if no data."""
        pass
    
    @abstractmethod
    def inject_corrections(self, rtcm_data: bytes) -> bool:
        """Inject RTCM corrections. Return success status."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Clean shutdown and disconnect."""
        pass
```

## ZED-F9P Implementation Essentials

### UBX Protocol Core
```python
# UBX-NAV-PVT message (0x01 0x07) - Position, Velocity, Time
def parse_ubx_nav_pvt(data: bytes) -> GNSSState:
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

# Error handling: Checksum validation
def validate_ubx_checksum(data: bytes) -> bool:
    if len(data) < 8:
        return False
    ck_a = ck_b = 0
    for byte in data[2:-2]:  # Skip sync chars and checksum
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return data[-2] == ck_a and data[-1] == ck_b
```

### Memory Constraint: <35MB per driver

## UM980 Implementation Essentials

### Unicore Protocol Core
```python
# BESTPOS message parsing
def parse_unicore_bestpos(data: bytes) -> GNSSState:
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
    # GPS epoch: 1980-01-06 00:00:00 UTC
    import datetime
    gps_epoch = datetime.datetime(1980, 1, 6, tzinfo=datetime.timezone.utc)
    timestamp = gps_epoch + datetime.timedelta(weeks=week, seconds=seconds)
    return timestamp.isoformat().replace('+00:00', 'Z')
```

### Memory Constraint: <35MB per driver

## Android Implementation Constraints

### Resource Limits
```python
# Memory management
MAX_TOTAL_MEMORY_MB = 80        # Total app heap limit
MAX_PER_DRIVER_MB = 35          # Per receiver limit
BUFFER_SIZE_BYTES = 8192        # Circular buffer size
MAX_LOG_BUFFER_KB = 512         # Before disk flush

# Threading limits
MAX_THREADS = 5  # UI + 2×drivers + NTRIP + logger
```

### Required Permissions (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.USB_PERMISSION" />
<uses-feature android:name="android.hardware.usb.host" android:required="true" />
```

### Connection Types (Priority Order)
1. **USB Serial**: Primary (most reliable)
2. **Bluetooth**: Fallback (wireless convenience)
3. **WiFi/LTE**: NTRIP corrections only

## Testing Patterns

### Essential Tests
```python
import pytest
from unittest.mock import Mock

class TestDrivers:
    def test_ubx_parsing(self):
        ubx_data = b'\xb5\x62\x01\x07' + b'\x00' * 96  # UBX-NAV-PVT
        result = parse_ubx_nav_pvt(ubx_data)
        assert result.fix_type == FixType.FIX
        assert -90 <= result.latitude <= 90
    
    def test_error_handling(self):
        driver = ZedF9PDriver()
        with pytest.raises(ConnectionError):
            await driver.connect("invalid_port")
    
    def test_memory_compliance(self):
        assert get_process_memory_mb() < MAX_PER_DRIVER_MB

# Mock data: MOCK_UBX_NAV_PVT, MOCK_UNICORE_BESTPOS
```

---

*Single file contains complete implementation context - no external references needed*
