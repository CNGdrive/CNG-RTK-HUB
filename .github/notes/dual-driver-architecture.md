# Dual-Driver Architecture Specification

**Purpose**: Plugin-based driver system supporting ZED-F9P (UBX) and UM980 (Unicore binary) with unified data normalization for Android deployment.

**Date**: August 24, 2025  
**Status**: Design Phase  
**Complexity**: Medium-High

---

## Architecture Overview

```
[ZED-F9P Receiver] ──UBX──→ [ZED-F9P Driver] ──┐
                                                 ├──→ [Driver Manager] ──→ [GNSS Abstraction] ──→ [Flutter UI]
[UM980 Receiver] ──Unicore──→ [UM980 Driver] ──┘
                                                 ↓
                                           [Normalized RTK State]
```

## Core Components

### 1. Driver Interface (`IGNSSDriver`)
**Purpose**: Standardized contract for all GNSS receiver drivers

**Key Methods**:
```python
class IGNSSDriver(ABC):
    @abstractmethod
    async def connect(self, connection_config: ConnectionConfig) -> bool
    
    @abstractmethod
    async def start_data_stream(self) -> None
    
    @abstractmethod
    async def stop_data_stream(self) -> None
    
    @abstractmethod
    def get_current_state(self) -> GNSSState
    
    @abstractmethod
    def inject_corrections(self, rtcm_data: bytes) -> bool
    
    @abstractmethod
    def get_driver_info(self) -> DriverInfo
```

### 2. Protocol Parsers

#### ZED-F9P UBX Parser
**Target Messages**:
- `UBX-NAV-PVT` (Position, Velocity, Time)
- `UBX-NAV-STATUS` (Navigation Status)
- `UBX-NAV-SAT` (Satellite Information)
- `UBX-NAV-HPPOSLLH` (High Precision Position)

#### UM980 Unicore Parser  
**Target Messages**:
- `BESTPOS` (Best Position)
- `BESTVEL` (Best Velocity)
- `PSRVEL` (Pseudorange Velocity)
- `SATELLITESTATUS` (Satellite Status)

### 3. Data Normalization Layer
**Purpose**: Convert protocol-specific data to unified `GNSSState` object

```python
@dataclass
class GNSSState:
    timestamp_utc: str          # ISO8601
    fix_type: FixType          # NO_FIX|DGPS|FLOAT|FIX
    latitude: float            # WGS84 degrees
    longitude: float           # WGS84 degrees
    altitude_m: float          # Ellipsoidal height
    accuracy_m: float          # 1-sigma horizontal
    sats: Dict[str, int]       # {"GPS":6,"GLO":4,"GAL":8,"BDS":3}
    snr: Dict[str, float]      # {"G01":42.5, "R08":38.2, ...}
    pdop: float
    hdop: float
    vdop: float
    baseline_m: float          # RTK baseline distance
    correction_source: str     # NTRIP source URL
    correction_latency_ms: int # Correction age
    antenna_offset_m: Point3D  # Antenna phase center offset
    receiver_meta: Dict        # Model, firmware, etc.
```

### 4. Driver Manager
**Purpose**: Coordinate multiple receivers, handle resource allocation

**Key Features**:
- Simultaneous multi-receiver support (max 2 on Android)
- Resource monitoring and allocation
- Driver lifecycle management
- Event coordination between drivers

## Android-Specific Considerations

### Resource Management
- **Memory Monitoring**: Track heap usage per driver
- **CPU Allocation**: Limit processing threads per receiver  
- **Battery Optimization**: Coordinate with Android power management
- **Connection Limits**: Maximum 2 receivers based on hardware capabilities

### USB Host Support
- **Detection**: Check Android USB host mode capability on startup
- **Fallback**: Bluetooth connection when USB host unavailable
- **Error Handling**: Graceful degradation with user notifications

## File Structure

```
src/
├── drivers/
│   ├── IGNSSDriver.py              # Abstract base interface
│   ├── base_driver.py              # Common driver functionality
│   ├── driver_manager.py           # Multi-driver coordinator
│   ├── zedf9p/
│   │   ├── ubx_parser.py          # UBX protocol parser
│   │   ├── ubx_messages.py        # UBX message definitions
│   │   └── zedf9p_driver.py       # ZED-F9P implementation
│   └── um980/
│       ├── unicore_parser.py      # Unicore binary parser
│       ├── unicore_messages.py    # Unicore message definitions
│       └── um980_driver.py        # UM980 implementation
├── core/
│   ├── gnss_state.py              # Normalized state object
│   ├── gnss_abstraction.py        # Driver→UI abstraction
│   └── protocol_normalizer.py     # Protocol→unified mapping
└── android/
    ├── usb_host_manager.py        # USB host detection
    ├── resource_monitor.py        # System resource tracking
    └── battery_optimizer.py      # Power management
```

## Data Flow

1. **Connection Phase**:
   - Driver Manager detects available receivers
   - Creates appropriate driver instances (ZED-F9P, UM980)
   - Establishes connections via USB/Serial/Bluetooth

2. **Data Streaming Phase**:
   - Each driver parses incoming binary data (UBX/Unicore)
   - Protocol normalizer converts to unified `GNSSState`
   - GNSS Abstraction layer publishes state updates

3. **Correction Injection**:
   - NTRIP client receives RTCM corrections
   - Driver Manager distributes corrections to active drivers
   - Drivers inject corrections into receiver correction streams

## Error Handling & Fallbacks

### Protocol Parsing Errors
- **UBX Checksum Failure**: Log error, continue with next frame
- **Unicore CRC Failure**: Log error, continue with next frame  
- **Unknown Message Types**: Log and ignore
- **Safe Mode**: Fall back to NMEA GGA parsing when binary fails

### Connection Failures
- **USB Disconnect**: Attempt reconnection with exponential backoff
- **Bluetooth Timeout**: Switch to alternative connection method
- **Resource Exhaustion**: Gracefully shutdown secondary receiver

## Testing Strategy

### Unit Testing
- **UBX Parser**: Test with recorded binary frames from ZED-F9P
- **Unicore Parser**: Test with recorded binary frames from UM980
- **Normalization**: Verify protocol→unified state mapping accuracy
- **Driver Manager**: Test multi-receiver coordination scenarios

### Integration Testing  
- **Dual-Receiver**: Simultaneous ZED-F9P + UM980 operation
- **Android Resource**: Memory/CPU usage under load
- **Connection Stress**: USB disconnect/reconnect scenarios
- **Correction Injection**: RTCM distribution to multiple receivers

## Performance Targets

### Relaxed for MVP
- **Latency**: <1000ms (relaxed from <300ms for accuracy priority)
- **Memory**: <100MB total for dual-receiver operation
- **CPU**: <30% sustained load on mid-range Android tablet
- **Battery**: 8+ hour operation with power optimization

## Future Extensibility

### Additional Receiver Support
- **Trimble**: Add new driver implementing `IGNSSDriver`
- **Hemisphere**: Add new driver implementing `IGNSSDriver`  
- **Septentrio**: Add new driver implementing `IGNSSDriver`

### Protocol Extensions
- **CMR/CMR+**: Extend correction injection interface
- **RINEX Real-time**: Add real-time RINEX streaming
- **Custom Protocols**: Plugin architecture supports proprietary formats

---

**Next Phase**: Implementation via `feat/20250824-dual-driver-architecture` branch with 6 checkpoint commits.
