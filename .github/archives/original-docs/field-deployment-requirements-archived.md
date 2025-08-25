# Field Deployment Requirements

**Primary Target**: Android ruggedized tablets/phones with Type-C charging
**Future**: Windows integration, Raspberry Pi mounting options

## Hardware Integration Matrix

| Connection Type | Use Case | Priority |
|---|---|---|
| USB/Type-C | Direct receiver connection | P0 |
| Serial | Legacy receiver support | P1 |
| Bluetooth | Wireless receiver pairing | P0 |
| UDP/Network | NTRIP corrections, cloud sync | P0 |

**Simultaneous Support**: All connection types active for different data streams

## Settings Framework Requirements

### Antenna Configuration
- Survey rod height compensation (vertical offset)
- Multi-antenna heading/attitude systems (rover + base)
- Fixed installation with known monument offsets
- **Storage**: User profiles with validation

### NTRIP Source Management
- Commercial services (subscription-based, cellular/WiFi required)
- Local base station (company-owned, radio link)
- Government networks (free, limited coverage)
- Mixed sources with automatic failover
- **Storage**: Saved profiles per job site/region

### Session Management
- Auto-detect hardware on startup
- Point capture modes: manual click OR continuous logging
- 8+ hour continuous operation support
- Power management integration
- Data storage capacity monitoring

## Real-time Requirements

### User Interface
- Real-time map view with current position
- Accuracy circles (visual confidence indicators)
- Connectivity status indicators
- Battery/power status monitoring

### Data Flow
- <300ms latency target (correction receipt → solution)
- Intermittent connectivity handling with user notifications
- **Critical**: No algorithmic reversion - show actual signal impact
- Graceful degradation notifications (no DGPS fallback masking)

## Data Export & Cloud Integration

### Local Storage
- Raw RINEX files for post-processing
- Cleaned CSV coordinates (CAD-ready)
- PDF reports with accuracy statistics
- All data saved locally first

### Remote Access
- Real-time data push to cloud/office
- Remote device monitoring from laptop
- Remote device control capabilities
- Windows file system integration (copy/export)

## Multi-Device Scenarios

### Benchmarking Use Cases
- Quality assurance (brand comparison)
- Equipment calibration/validation
- Technical training exercises
- Research/testing scenarios
- Routine field validation

### Dual-Device Operation
- Simultaneous receiver comparison
- Real-time accuracy assessment
- Cross-validation workflows

## Field Workflow Summary

1. **Setup**: Power receiver → Launch app → Auto-detect hardware
2. **Configuration**: Load saved NTRIP profile for location
3. **Operation**: Real-time map with accuracy indicators
4. **Data Capture**: Manual points OR continuous logging (user preference)
5. **Monitoring**: Live connectivity, battery, signal quality alerts
6. **Export**: Local storage + cloud sync + Windows compatibility

---

**Implementation Priority**: All "settings" items require robust profile management system with validation and backup/restore capabilities.
