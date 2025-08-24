# Android Platform Requirements

**Purpose**: Essential constraints for dual-receiver RTK operation on Android tablets.  
**Target**: 8+ hour field operation on ruggedized Android devices.  
**Compliance**: MINIMALISM_STANDARDS.md enforced

---

## Hardware Assumptions
- **CPU**: Quad-core ARM Cortex-A53 @ 1.8GHz (ruggedized tablet)
- **RAM**: 4GB total, ~2GB available for applications
- **Storage**: 64GB eMMC with ~40GB user available
- **Battery**: 7000-10000mAh with USB-C charging
- **Connectivity**: WiFi 802.11ac, LTE, Bluetooth 5.0, USB 3.0 host

## Performance Targets
- **CPU Usage**: <30% sustained load for dual-receiver operation
- **Memory Usage**: <100MB total heap size
- **Battery Life**: 8+ hours continuous operation  
- **Data Latency**: <1000ms end-to-end processing
- **Storage Usage**: <1GB per 8-hour session (logs included)

## Resource Management

### Memory Allocation
```python
# Resource limits per component
MAX_TOTAL_MEMORY_MB = 80        # Conservative Android heap limit
MAX_PER_DRIVER_MB = 35          # Per-receiver memory budget  
BUFFER_SIZE_BYTES = 8192        # Serial/USB circular buffer
MAX_LOG_BUFFER_KB = 512         # In-memory log buffer before disk flush
```

### Threading Strategy
- **Main Thread**: UI and coordination only
- **Driver Threads**: One per active receiver (max 2)
- **NTRIP Thread**: Correction client with background processing
- **Logger Thread**: Disk I/O operations
- **Total Threads**: Maximum 5 concurrent threads

### Connection Management
- **USB Serial**: Primary connection method for receivers
- **Bluetooth**: Fallback for wireless receiver connections
- **WiFi/LTE**: NTRIP correction data and cloud sync
- **Power Management**: USB host mode power budgeting

## Android-Specific Considerations

### Permissions Required
- `INTERNET` - NTRIP corrections and cloud services
- `ACCESS_FINE_LOCATION` - GPS comparison and validation
- `WRITE_EXTERNAL_STORAGE` - Log file storage
- `USB_PERMISSION` - Direct receiver communication

### Background Processing
- **Foreground Service**: Maintain receiver connections during screen off
- **Wake Locks**: Prevent CPU sleep during data collection
- **Battery Optimization**: Request exemption from Doze mode

### File System
- **Log Storage**: `/Android/data/com.cng.rtkhub/files/logs/`
- **Config Storage**: Shared preferences for receiver settings
- **Export Path**: Public Documents folder for user access

---

*See architecture.md for technical implementation and implementation-plan.md for development phases*
