# Architecture Decisions for Implementation

**Purpose**: Design rationale and constraints for AI implementation  
**Context**: ZED-F9P + UM980 dual-receiver RTK client

---

## Core Design Rationale

### Plugin Architecture (IGNSSDriver Interface)
**Decision**: Abstract base class with standardized methods  
**Why**: Support multiple receiver types without code duplication  
**Implementation**: Each receiver (ZED-F9P, UM980) implements same interface  
**Benefit**: Add new receivers without modifying core system

### Dual-Receiver Support (Driver Manager)  
**Decision**: Simultaneous operation of 2 receivers maximum  
**Why**: Hardware benchmarking and redundancy for critical applications  
**Constraint**: Android memory limits prevent more than 2 active drivers  
**Implementation**: Resource allocation per driver (<35MB each)

### Data Normalization (GNSSState Model)
**Decision**: Single unified data structure for all receivers  
**Why**: Simplify UI and logging - same data format regardless of receiver  
**Implementation**: Protocol-specific parsers → normalized GNSSState  
**Benefit**: Receiver-agnostic application code

### Threading Model (5-Thread Maximum)
**Decision**: Dedicated threads for UI, drivers, NTRIP, logging  
**Why**: Real-time data processing without blocking UI  
**Constraint**: Android performance limits on mobile hardware  
**Threads**: UI + 2×drivers + NTRIP + logger = 5 total

---

## Technology Choices

### Python Backend
**Decision**: Python for protocol parsing and data processing  
**Why**: Complex binary protocol parsing (UBX + Unicore binary)  
**Alternative Rejected**: Pure Dart - insufficient binary parsing libraries  
**Trade-off**: Cross-platform communication complexity vs parsing capability

### Flutter Frontend  
**Decision**: Flutter for Android-first UI  
**Why**: Single codebase, excellent Android integration, responsive design  
**Alternative Rejected**: Native Android - longer development time  
**Benefit**: Future iOS/desktop support with minimal changes

### WebSocket API (Real-time Data)
**Decision**: WebSocket for live position streaming  
**Why**: Low-latency real-time updates for field applications  
**Implementation**: Python backend → WebSocket → Flutter frontend  
**Fallback**: HTTP REST API for configuration and bulk operations

### SQLite Storage (Offline-First)
**Decision**: Local SQLite database for all data  
**Why**: Field environments have unreliable connectivity  
**Implementation**: Local-first with opportunistic cloud sync  
**Benefit**: No data loss in remote locations

---

## Implementation Constraints

### MINIMALISM_STANDARDS.md Compliance
- Maximum 150 lines per code file
- Single responsibility per class/function
- Zero code duplication across modules
- Progressive disclosure - simple first, complex later

### Android Resource Limits
- **Memory**: <100MB total heap size for entire application
- **CPU**: <30% sustained load during dual-receiver operation  
- **Battery**: 8+ hours continuous operation requirement
- **Storage**: <1GB per 8-hour session including logs

### Field Deployment Requirements
- Ruggedized Android tablets as primary platform
- USB host mode for direct receiver connections
- Bluetooth fallback for wireless receiver connections
- Foreground service to prevent Android power management interference

### Battery Optimization Needs
- Request exemption from Android Doze mode
- Implement foreground service for continuous operation
- Monitor and optimize CPU usage patterns
- Power-aware processing based on battery level

---

## Key Implementation Patterns

### Error Handling (Graceful Degradation)
**Pattern**: Try operation → catch specific exceptions → fallback or retry  
**Examples**: 
- USB connection failure → try Bluetooth
- Corrupted data → skip frame, continue processing
- Memory pressure → reduce buffer sizes, increase flush frequency
- Receiver disconnect → maintain last known state, attempt reconnection

### Memory Management (Buffer Limits)
**Pattern**: Fixed-size circular buffers with overflow protection  
**Implementation**:
- 8KB circular buffers per receiver connection
- 512KB log buffer before disk flush
- Monitor heap usage per driver (<35MB limit)
- Garbage collection optimization for real-time processing

### Connection Management (Lifecycle Patterns)  
**Pattern**: Connect → Configure → Start → Monitor → Stop → Disconnect  
**Error Recovery**: Exponential backoff for reconnection attempts  
**Resource Cleanup**: Always disconnect in finally blocks  
**State Management**: Track connection state for UI indicators

### Testing Approach (Mock Data Strategy)
**Pattern**: Record real receiver data → replay for testing  
**Implementation**:
- Capture UBX and Unicore binary frames from hardware
- Mock receiver objects for unit testing
- Integration tests with recorded data streams
- Error simulation with corrupted/incomplete messages

---

## Performance Optimization Guidelines

### Real-time Processing (<1000ms Latency)
- Minimize object allocation in data processing loops
- Use pre-allocated buffers for protocol parsing
- Batch database operations to reduce I/O overhead
- Process corrections immediately upon receipt

### Memory Efficiency
- Reuse objects in parsing loops
- Implement object pools for frequent allocations
- Monitor memory usage with periodic checks
- Use weak references where appropriate

### Threading Efficiency  
- Minimize thread synchronization overhead
- Use lock-free data structures where possible
- Batch inter-thread communications
- Avoid blocking operations in UI thread

---

*All architectural context for implementation - no external dependencies required*
