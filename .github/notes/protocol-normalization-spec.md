# Protocol Normalization Specification

**Purpose**: Define exact mapping from UBX (ZED-F9P) and Unicore binary (UM980) protocols to unified `GNSSState` object.

**Date**: August 24, 2025  
**Complexity**: Medium  
**Priority**: Critical for data accuracy

---

## Target Unified State Object

```python
@dataclass
class GNSSState:
    timestamp_utc: str          # ISO8601: "2025-08-24T14:30:15.123Z"
    fix_type: FixType          # NO_FIX|DGPS|FLOAT|FIX
    latitude: float            # WGS84 degrees, signed
    longitude: float           # WGS84 degrees, signed  
    altitude_m: float          # Ellipsoidal height in meters
    accuracy_m: float          # 1-sigma horizontal accuracy
    sats: Dict[str, int]       # {"GPS":6,"GLO":4,"GAL":8,"BDS":3}
    snr: Dict[str, float]      # {"G01":42.5, "R08":38.2, "E12":45.1}
    pdop: float               # Position dilution of precision
    hdop: float               # Horizontal dilution of precision
    vdop: float               # Vertical dilution of precision
    baseline_m: float         # RTK baseline distance (0.0 if not RTK)
    correction_source: str    # "NTRIP://server:port/mount" or "None"
    correction_latency_ms: int # Age of corrections in milliseconds
    antenna_offset_m: Point3D # Phase center offset {x, y, z}
    receiver_meta: Dict       # {"model":"ZED-F9P","fw":"1.13","sn":"123"}
```

---

## ZED-F9P UBX Protocol Mapping

### Primary Message: UBX-NAV-PVT (0x01 0x07)
**Source Data → Unified State**:

```python
def ubx_nav_pvt_to_state(ubx_msg: UBX_NAV_PVT) -> GNSSState:
    return GNSSState(
        timestamp_utc=format_iso8601(ubx_msg.year, ubx_msg.month, ubx_msg.day, 
                                   ubx_msg.hour, ubx_msg.min, ubx_msg.sec, ubx_msg.nano),
        fix_type=ubx_fix_type_map[ubx_msg.fixType],
        latitude=ubx_msg.lat * 1e-7,        # Scale factor: 1e-7 degrees
        longitude=ubx_msg.lon * 1e-7,       # Scale factor: 1e-7 degrees
        altitude_m=ubx_msg.hMSL * 1e-3,     # Height above MSL, mm to m
        accuracy_m=ubx_msg.hAcc * 1e-3,     # Horizontal accuracy, mm to m
        sats={"GPS": ubx_msg.numSV},        # Total satellites (refined by NAV-SAT)
        pdop=ubx_msg.pDOP * 0.01,           # Scale factor: 0.01
        hdop=0.0,  # Not in NAV-PVT, get from NAV-DOP
        vdop=0.0,  # Not in NAV-PVT, get from NAV-DOP
        baseline_m=0.0,  # Get from NAV-HPPOSLLH if RTK
        correction_source="None",  # Determined by correction injection
        correction_latency_ms=0,   # Get from correction subsystem
        antenna_offset_m=Point3D(0, 0, 0),  # From configuration
        receiver_meta={"model": "ZED-F9P", "fw": get_fw_version()}
    )
```

### UBX Fix Type Mapping
```python
ubx_fix_type_map = {
    0: FixType.NO_FIX,    # No fix
    1: FixType.NO_FIX,    # Dead reckoning only  
    2: FixType.DGPS,      # 2D fix
    3: FixType.DGPS,      # 3D fix
    4: FixType.DGPS,      # GNSS + dead reckoning
    5: FixType.FIX        # Time only fix (edge case)
}

# RTK-specific flags from carrSoln field:
# carrSoln = 0: No RTK
# carrSoln = 1: RTK Float → FixType.FLOAT  
# carrSoln = 2: RTK Fixed → FixType.FIX
```

### Supplementary Messages

#### UBX-NAV-SAT (0x01 0x35) - Satellite Details
**Purpose**: Populate `sats` and `snr` dictionaries with per-constellation breakdown

```python
def ubx_nav_sat_to_constellation_data(ubx_sat: UBX_NAV_SAT) -> Tuple[Dict[str, int], Dict[str, float]]:
    sats = {"GPS": 0, "GLO": 0, "GAL": 0, "BDS": 0, "QZSS": 0}
    snr = {}
    
    for sat in ubx_sat.satellites:
        constellation = gnss_id_to_constellation[sat.gnssId]
        sat_id = format_sat_id(constellation, sat.svId)
        
        if sat.flags & 0x08:  # Satellite used in navigation
            sats[constellation] += 1
            
        if sat.cno > 0:  # Valid C/N0 measurement
            snr[sat_id] = sat.cno  # dB-Hz
            
    return sats, snr

gnss_id_to_constellation = {
    0: "GPS",    # GPS (G01-G32)
    1: "SBAS",   # SBAS (S120-S158) 
    2: "GAL",    # Galileo (E01-E36)
    3: "BDS",    # BeiDou (B01-B37)
    4: "IMES",   # IMES (I01-I10)
    5: "QZSS",   # QZSS (Q01-Q10)
    6: "GLO"     # GLONASS (R01-R24)
}
```

#### UBX-NAV-HPPOSLLH (0x01 0x14) - High Precision RTK
**Purpose**: Provide RTK-specific accuracy and baseline information

```python
def ubx_nav_hpposllh_to_rtk_data(ubx_hp: UBX_NAV_HPPOSLLH) -> Tuple[float, float]:
    # Enhanced accuracy from high-precision message
    accuracy_m = min(ubx_hp.hAcc, ubx_hp.vAcc) * 1e-4  # 0.1mm resolution
    
    # Baseline distance (if available from RTK processing)
    baseline_m = 0.0  # UBX doesn't directly provide this - calculate from reference
    
    return accuracy_m, baseline_m
```

---

## UM980 Unicore Protocol Mapping

### Primary Message: BESTPOS
**Source Data → Unified State**:

```python
def unicore_bestpos_to_state(bestpos: BESTPOS) -> GNSSState:
    return GNSSState(
        timestamp_utc=format_gps_week_to_iso8601(bestpos.week, bestpos.seconds),
        fix_type=unicore_sol_status_map[bestpos.sol_status],
        latitude=bestpos.lat,               # Already in degrees
        longitude=bestpos.lon,              # Already in degrees  
        altitude_m=bestpos.hgt,             # Already in meters
        accuracy_m=max(bestpos.lat_stdev, bestpos.lon_stdev),  # Conservative estimate
        sats={"GPS": bestpos.num_svs},      # Total SVs (refined by SATELLITESTATUS)
        pdop=bestpos.pdop,                  # Already scaled correctly
        hdop=bestpos.hdop,                  # Already scaled correctly
        vdop=bestpos.vdop,                  # Already scaled correctly
        baseline_m=bestpos.diff_age,        # Differential age approximation
        correction_source="None",           # Determined by correction injection
        correction_latency_ms=int(bestpos.diff_age * 1000),  # Age to latency
        antenna_offset_m=Point3D(0, 0, 0),  # From configuration
        receiver_meta={"model": "UM980", "fw": get_fw_version()}
    )
```

### Unicore Solution Status Mapping
```python
unicore_sol_status_map = {
    "NONE": FixType.NO_FIX,           # No solution
    "FIXEDPOS": FixType.FIX,          # Fixed position
    "FIXEDHEIGHT": FixType.FIX,       # Fixed height
    "DOPPLER_VELOCITY": FixType.DGPS, # Doppler velocity
    "SINGLE": FixType.DGPS,           # Single point position
    "PSRDIFF": FixType.DGPS,          # Pseudorange differential
    "WAAS": FixType.DGPS,             # WAAS corrections
    "PROPAGATE": FixType.NO_FIX,      # Propagated by dead reckoning
    "OMNISTAR": FixType.DGPS,         # OmniSTAR corrections
    "L1_FLOAT": FixType.FLOAT,        # L1 float ambiguity
    "IONOFREE_FLOAT": FixType.FLOAT,  # Ionosphere-free float
    "NARROW_FLOAT": FixType.FLOAT,    # Narrow-lane float
    "L1_INT": FixType.FIX,            # L1 fixed ambiguity
    "WIDE_INT": FixType.FIX,          # Wide-lane fixed
    "NARROW_INT": FixType.FIX,        # Narrow-lane fixed
    "RTK_DIRECT_INS": FixType.FIX,    # RTK with INS
    "INS": FixType.DGPS,              # INS only
    "INS_PSRSP": FixType.DGPS,        # INS with pseudorange
    "INS_PSRDIFF": FixType.DGPS,      # INS with differential
    "INS_RTKFLOAT": FixType.FLOAT,    # INS with RTK float
    "INS_RTKFIXED": FixType.FIX       # INS with RTK fixed
}
```

### Supplementary Message: SATELLITESTATUS
**Purpose**: Populate detailed satellite constellation and SNR data

```python
def unicore_satstat_to_constellation_data(satstat: SATELLITESTATUS) -> Tuple[Dict[str, int], Dict[str, float]]:
    sats = {"GPS": 0, "GLO": 0, "GAL": 0, "BDS": 0, "QZSS": 0}
    snr = {}
    
    for sat in satstat.satellites:
        constellation = unicore_constellation_map[sat.constellation]
        sat_id = format_sat_id(constellation, sat.prn)
        
        if sat.tracking_state == "TRACKING":
            sats[constellation] += 1
            
        if sat.cn0 > 0:  # Valid C/N0 measurement
            snr[sat_id] = sat.cn0  # dB-Hz
            
    return sats, snr

unicore_constellation_map = {
    "GPS": "GPS",
    "GLONASS": "GLO", 
    "GALILEO": "GAL",
    "BEIDOU": "BDS",
    "QZSS": "QZSS",
    "SBAS": "SBAS"
}
```

---

## Protocol Conflict Resolution

### Fix Type Priority Resolution
When multiple receivers provide conflicting fix types:

```python
fix_type_priority = {
    FixType.FIX: 4,      # Highest priority
    FixType.FLOAT: 3,    # Second priority  
    FixType.DGPS: 2,     # Third priority
    FixType.NO_FIX: 1    # Lowest priority
}

def resolve_fix_type_conflict(zedf9p_fix: FixType, um980_fix: FixType) -> FixType:
    if fix_type_priority[zedf9p_fix] >= fix_type_priority[um980_fix]:
        return zedf9p_fix
    return um980_fix
```

### Accuracy Estimation Differences
- **UBX**: Reports 1-sigma horizontal accuracy in mm (hAcc field)
- **Unicore**: Reports standard deviation in meters (lat_stdev, lon_stdev)
- **Resolution**: Use conservative (larger) accuracy estimate

### Satellite ID Standardization
Both protocols use different satellite numbering schemes:

```python
def format_sat_id(constellation: str, prn: int) -> str:
    constellation_prefix = {
        "GPS": "G",
        "GLO": "R", 
        "GAL": "E",
        "BDS": "B",
        "QZSS": "Q",
        "SBAS": "S"
    }
    return f"{constellation_prefix[constellation]}{prn:02d}"
```

---

## Validation & Testing

### Cross-Protocol Validation
- **Position Comparison**: Lat/lon differences <1m for same location
- **Fix Type Consistency**: Both protocols should agree on RTK status  
- **Satellite Overlap**: Common satellites should report similar SNR
- **Timing Synchronization**: Timestamps should align within 100ms

### Error Detection
- **Checksum Validation**: UBX and Unicore CRC verification
- **Range Checking**: Latitude [-90,90], longitude [-180,180]
- **Sanity Checking**: Accuracy values must be positive and reasonable
- **Temporal Validation**: Timestamps must be monotonically increasing

### Test Data Requirements
- **UBX Binary Samples**: Record from ZED-F9P in various fix states
- **Unicore Binary Samples**: Record from UM980 in various fix states
- **Side-by-side Comparison**: Synchronized data from both receivers
- **Edge Cases**: Startup, signal loss, RTK acquisition scenarios

---

**Implementation Note**: All parsing functions must handle incomplete or malformed messages gracefully, logging errors and continuing with next message in stream.
