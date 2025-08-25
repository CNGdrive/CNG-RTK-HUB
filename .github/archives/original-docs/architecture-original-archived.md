# RTK Dual-Driver Architecture

**Purpose**: Plugin-based driver system supporting ZED-F9P (UBX) and UM980 (Unicore binary) with unified data normalization.  
**Date**: August 24, 2025  
**Compliance**: MINIMALISM_STANDARDS.md enforced

---

## System Overview

```
[ZED-F9P] ──UBX──→ [ZED-F9P Driver] ──┐
                                        ├──→ [Driver Manager] ──→ [GNSS Abstraction] ──→ [Flutter UI]
[UM980] ──Unicore──→ [UM980 Driver] ───┘
                                        ↓
                                   [Normalized RTK State]
```

## Core Interface

### IGNSSDriver Contract
```python
class IGNSSDriver(ABC):
    @abstractmethod
    async def connect(self, connection_config: ConnectionConfig) -> bool
    
    @abstractmethod
    async def start_data_stream(self) -> None
    
    @abstractmethod
    def get_current_state(self) -> GNSSState
    
    @abstractmethod
    def inject_corrections(self, rtcm_data: bytes) -> bool
```

### Unified Data Model
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
    pdop: float               # Position dilution
    baseline_m: float         # RTK baseline distance
    correction_source: str    # NTRIP source or "None"
    receiver_meta: Dict       # Model, firmware, etc.
```

## Protocol Essentials

### ZED-F9P UBX Mapping
- **Primary**: UBX-NAV-PVT (position, velocity, time)
- **Fix Types**: 0-1=NO_FIX, 2-4=DGPS, RTK flags from carrSoln field
- **Scale Factors**: lat/lon × 1e-7, accuracy × 1e-3

### UM980 Unicore Mapping  
- **Primary**: BESTPOS (best position)
- **Fix Types**: Map solution status to FixType enum
- **Data**: Direct field mapping to GNSSState

## Android Resource Limits
- **Memory**: <100MB total heap, <35MB per driver
- **CPU**: <30% sustained load for dual-receiver operation
- **Threading**: 5 threads max (UI, 2×drivers, NTRIP, logger)

## Driver Manager
- **Multi-receiver**: Support 2 simultaneous receivers
- **Resource monitoring**: Memory and CPU usage tracking
- **Event coordination**: Synchronized state updates
- **Lifecycle management**: Connect, start, stop, disconnect

## Implementation Notes
- **Buffer Management**: 8KB circular buffers per receiver
- **Error Handling**: Graceful degradation on receiver failures
- **NTRIP Integration**: Inject corrections to active drivers
- **State Synchronization**: Thread-safe state updates

---

*See archives/ for detailed protocol mappings and optimization strategies*
