# Dual-Driver Architecture Implementation Memo

**Branch**: feat/20250824-dual-driver-architecture  
**Date**: August 24, 2025  
**Purpose**: Implement plugin-based driver system supporting ZED-F9P (UBX) and UM980 (Unicore binary) with unified data normalization for Android deployment.

---

## Implementation Plan Overview

### Risk Assessment
- **HIGH**: UBX/Unicore binary protocol parsing complexity
- **MEDIUM**: Android resource usage with dual receivers
- **LOW**: Driver interface abstraction

### Complexity Estimate
**Medium-High** - 13-19 days with relaxed performance requirements

---

## Checkpoint Implementation Plan

### Checkpoint 1: Driver Interface & Base Classes
**Commit Message**: `feat: add driver interface and base classes (note#1)`

**Scope**:
- Create `IGNSSDriver` abstract interface
- Implement `BaseDriver` common functionality
- Define `GNSSState` normalized data model
- Set up basic error handling framework

**Files Created**:
- `src/drivers/IGNSSDriver.py`
- `src/drivers/base_driver.py`
- `src/core/gnss_state.py`
- `src/core/exceptions.py`

**Success Criteria**:
- Interface contract clearly defined
- Base driver instantiates without errors
- GNSSState object validates correctly

**Smoke Test**: `python -c "from src.drivers.IGNSSDriver import IGNSSDriver; print('Interface loaded successfully')"`

**Status**: ⏳ Pending

---

### Checkpoint 2: ZED-F9P UBX Parser Implementation
**Commit Message**: `feat: implement ZED-F9P UBX parser (note#2)`

**Scope**:
- Implement UBX protocol parser (NAV-PVT, NAV-SAT, NAV-HPPOSLLH)
- Create UBX message definitions and constants
- Implement checksum validation
- Add UBX → GNSSState normalization

**Files Created**:
- `src/drivers/zedf9p/ubx_parser.py`
- `src/drivers/zedf9p/ubx_messages.py`
- `src/drivers/zedf9p/zedf9p_driver.py`
- `tests/drivers/test_ubx_parser.py`

**Success Criteria**:
- UBX parser handles sample binary frames
- Checksum validation catches corrupted frames
- NAV-PVT correctly maps to GNSSState

**Smoke Test**: `python -m pytest tests/drivers/test_ubx_parser.py -v`

**Status**: ⏳ Pending

---

### Checkpoint 3: UM980 Unicore Parser Implementation  
**Commit Message**: `feat: implement UM980 Unicore parser (note#3)`

**Scope**:
- Implement Unicore binary protocol parser (BESTPOS, SATELLITESTATUS)
- Create Unicore message definitions
- Implement CRC validation
- Add Unicore → GNSSState normalization

**Files Created**:
- `src/drivers/um980/unicore_parser.py`
- `src/drivers/um980/unicore_messages.py`
- `src/drivers/um980/um980_driver.py`
- `tests/drivers/test_unicore_parser.py`

**Success Criteria**:
- Unicore parser handles sample binary frames
- CRC validation catches corrupted frames
- BESTPOS correctly maps to GNSSState

**Smoke Test**: `python -m pytest tests/drivers/test_unicore_parser.py -v`

**Status**: ⏳ Pending

---

### Checkpoint 4: GNSS Abstraction Layer
**Commit Message**: `feat: add GNSS abstraction layer (note#4)`

**Scope**:
- Implement protocol normalization logic
- Create event-based state publisher
- Add antenna offset handling
- Implement coordinate system transformations

**Files Created**:
- `src/core/gnss_abstraction.py`
- `src/core/protocol_normalizer.py`
- `src/core/coordinate_transformer.py`
- `tests/core/test_gnss_abstraction.py`

**Success Criteria**:
- Both UBX and Unicore protocols map to unified state
- Event system publishes state updates
- Antenna offsets apply correctly

**Smoke Test**: `python -m pytest tests/core/test_gnss_abstraction.py -v`

**Status**: ⏳ Pending

---

### Checkpoint 5: Dual-Driver Manager Integration
**Commit Message**: `feat: integrate dual-driver manager (note#5)`

**Scope**:
- Implement multi-receiver coordinator
- Add connection management and lifecycle
- Create driver discovery and instantiation
- Implement resource allocation logic

**Files Created**:
- `src/drivers/driver_manager.py`
- `src/core/connection_manager.py`
- `tests/drivers/test_driver_manager.py`

**Success Criteria**:
- Manager can instantiate both driver types
- Simultaneous dual-receiver operation
- Graceful handling of connection failures

**Smoke Test**: `python -m pytest tests/drivers/test_driver_manager.py -v`

**Status**: ⏳ Pending

---

### Checkpoint 6: Android Resource Monitoring
**Commit Message**: `feat: add basic Android resource monitoring (note#6)`

**Scope**:
- Implement memory usage tracking
- Add CPU usage monitoring
- Create battery optimization hooks
- Add connection quality monitoring

**Files Created**:
- `src/android/resource_monitor.py`
- `src/android/usb_host_manager.py`
- `src/android/battery_optimizer.py`
- `tests/android/test_resource_monitor.py`

**Success Criteria**:
- Resource usage stays within defined limits
- USB host mode detection works
- Battery optimization recommendations trigger

**Smoke Test**: `python -m pytest tests/android/test_resource_monitor.py -v`

**Status**: ⏳ Pending

---

## Rollback Strategy

### Emergency Rollback (Complete)
1. **Switch to main branch**: `git checkout main`
2. **Delete feature branch**: `git branch -D feat/20250824-dual-driver-architecture`
3. **Restore original files**: Use backup files from `.github/backups/`

### Partial Rollback (Checkpoint-specific)
1. **Reset to previous checkpoint**: `git reset --hard HEAD~1`
2. **Force push to remote**: `git push origin feat/20250824-dual-driver-architecture --force`
3. **Update memo status**: Mark failed checkpoint in this memo

### File Backups
All modified files will be backed up to:
```
.github/backups/feat-20250824-dual-driver/
├── implementation-checklist-20250824143000.bak
├── tech-spec-20250824143000.bak
└── architecture-decisions-20250824143000.bak
```

---

## Testing Strategy

### Unit Testing Requirements
- **Protocol Parsers**: Test with recorded binary frames (UBX + Unicore)
- **Data Normalization**: Validate protocol→unified state mapping accuracy
- **Driver Interface**: Mock testing for connection scenarios
- **Resource Management**: Simulate memory/CPU pressure conditions

### Integration Testing
- **Dual-Receiver Operation**: Simultaneous ZED-F9P + UM980 data processing
- **Connection Management**: USB disconnect/reconnect scenarios
- **Resource Limits**: Memory pressure and graceful degradation
- **Error Recovery**: Protocol parsing failures and fallback behavior

### Test Data Requirements
```
tests/fixtures/
├── ubx_samples/
│   ├── nav_pvt_rtk_fixed.ubx
│   ├── nav_pvt_rtk_float.ubx
│   └── nav_sat_multi_constellation.ubx
└── unicore_samples/
    ├── bestpos_rtk_fixed.bin
    ├── bestpos_rtk_float.bin
    └── satellitestatus_multi_constellation.bin
```

---

## Success Metrics

### Performance Targets (Relaxed for MVP)
- **Latency**: <1000ms end-to-end processing
- **Memory Usage**: <100MB for dual-receiver operation
- **CPU Usage**: <30% sustained load on target Android hardware
- **Battery Life**: 8+ hours continuous operation

### Functional Requirements
- **Protocol Support**: 100% parsing accuracy for target UBX and Unicore messages
- **Data Normalization**: Consistent unified state from both protocols
- **Connection Management**: Graceful handling of disconnect/reconnect scenarios
- **Resource Management**: Automatic adaptation to Android resource constraints

---

## Post-Implementation Checklist

### Documentation Updates
- [ ] Update `implementation-checklist.md` with dual-driver milestones
- [ ] Update `tech-spec.md` with expanded protocol support
- [ ] Add new ADR-009 for dual-driver architecture decision
- [ ] Update `technical-risks.md` with dual-protocol complexity risks

### Code Quality
- [ ] All unit tests passing with >80% coverage
- [ ] Code style compliance (linting passed)
- [ ] No critical security vulnerabilities
- [ ] Performance benchmarks meet relaxed targets

### Deployment Readiness
- [ ] Android resource limits validated on target hardware
- [ ] USB host mode compatibility verified
- [ ] Battery optimization settings documented
- [ ] Field deployment guide updated

---

## Next Phase Handover

### To Refactor - Implement Agent
This memo provides the complete implementation plan with:
- ✅ Clear checkpoint breakdown (6 commits)
- ✅ Specific file paths and responsibilities
- ✅ Testing strategy with smoke tests
- ✅ Rollback procedures for each checkpoint
- ✅ Success criteria and validation steps

### Ready for Implementation
- ✅ Architecture documents completed
- ✅ Protocol normalization specifications defined
- ✅ Android resource management strategy documented
- ✅ Branch plan and commit structure prepared

**Status**: Ready for **Refactor - Implement** agent execution

---

*Last Updated: August 24, 2025 14:30:00 UTC*
