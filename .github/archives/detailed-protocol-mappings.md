# Detailed Protocol Mappings Archive

**Purpose**: Comprehensive protocol specifications for UBX and Unicore binary formats.  
**Archived**: August 24, 2025  
**Usage**: Reference for advanced protocol implementation details.

---

## UBX Protocol Detailed Mappings

### UBX-NAV-SAT (0x01 0x35) - Satellite Details
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
    0: "GPS", 1: "SBAS", 2: "GAL", 3: "BDS", 4: "IMES", 5: "QZSS", 6: "GLO"
}
```

### UBX-NAV-HPPOSLLH (0x01 0x14) - High Precision RTK
```python
def ubx_nav_hpposllh_to_rtk_data(ubx_hp: UBX_NAV_HPPOSLLH) -> Tuple[float, float]:
    accuracy_m = min(ubx_hp.hAcc, ubx_hp.vAcc) * 1e-4  # 0.1mm resolution
    baseline_m = 0.0  # Calculate from reference if available
    return accuracy_m, baseline_m
```

## Unicore Protocol Detailed Mappings

### BESTPOS Message Mapping
```python
def unicore_bestpos_to_state(bestpos: BESTPOS) -> GNSSState:
    return GNSSState(
        timestamp_utc=format_gps_week_to_iso8601(bestpos.week, bestpos.seconds),
        fix_type=unicore_sol_status_map[bestpos.sol_status],
        latitude=bestpos.lat,
        longitude=bestpos.lon,
        altitude_m=bestpos.hgt,
        accuracy_m=max(bestpos.lat_stdev, bestpos.lon_stdev),
        sats={"GPS": bestpos.num_svs},
        pdop=bestpos.pdop,
        hdop=bestpos.hdop,
        vdop=bestpos.vdop,
        baseline_m=bestpos.diff_age,
        correction_source="None",
        correction_latency_ms=int(bestpos.diff_age * 1000),
        antenna_offset_m=Point3D(0, 0, 0),
        receiver_meta={"model": "UM980", "fw": get_fw_version()}
    )
```

### Unicore Solution Status Mapping
```python
unicore_sol_status_map = {
    "NONE": FixType.NO_FIX,
    "FIXEDPOS": FixType.FIX,
    "SINGLE": FixType.DGPS,
    "PSRDIFF": FixType.DGPS,
    "L1_FLOAT": FixType.FLOAT,
    "NARROW_FLOAT": FixType.FLOAT,
    "L1_INT": FixType.FIX,
    "NARROW_INT": FixType.FIX,
    # ... [complete mapping table]
}
```

### SATELLITESTATUS Message
```python
def unicore_satstat_to_constellation_data(satstat: SATELLITESTATUS):
    sats = {"GPS": 0, "GLO": 0, "GAL": 0, "BDS": 0, "QZSS": 0}
    snr = {}
    
    for sat in satstat.satellites:
        constellation = unicore_constellation_map[sat.constellation]
        sat_id = format_sat_id(constellation, sat.prn)
        
        if sat.tracking_state == "TRACKING":
            sats[constellation] += 1
            
        if sat.cn0 > 0:
            snr[sat_id] = sat.cn0
            
    return sats, snr
```

## Protocol Conflict Resolution

### Fix Type Priority Resolution
```python
fix_type_priority = {
    FixType.FIX: 4,
    FixType.FLOAT: 3,
    FixType.DGPS: 2,
    FixType.NO_FIX: 1
}

def resolve_fix_type_conflict(zedf9p_fix: FixType, um980_fix: FixType) -> FixType:
    if fix_type_priority[zedf9p_fix] >= fix_type_priority[um980_fix]:
        return zedf9p_fix
    return um980_fix
```

### Satellite ID Standardization
```python
def format_sat_id(constellation: str, prn: int) -> str:
    constellation_prefix = {
        "GPS": "G", "GLO": "R", "GAL": "E", "BDS": "B", "QZSS": "Q", "SBAS": "S"
    }
    return f"{constellation_prefix[constellation]}{prn:02d}"
```

## Validation & Testing

### Cross-Protocol Validation
- Position comparison: <1m difference for same location
- Fix type consistency between protocols
- Satellite overlap with similar SNR values
- Timing synchronization within 100ms

### Error Detection
- Checksum validation for both protocols
- Range checking (lat/lon bounds)
- Sanity checking (positive accuracy values)
- Temporal validation (monotonic timestamps)

### Test Data Requirements
- UBX binary samples from ZED-F9P in various states
- Unicore binary samples from UM980 in various states
- Side-by-side synchronized comparison data
- Edge cases: startup, signal loss, RTK acquisition

---

*Implementation Note: All parsing functions must handle incomplete/malformed messages gracefully*
