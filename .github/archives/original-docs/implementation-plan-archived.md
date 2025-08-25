# RTK Implementation Plan

**Goal**: Minimal viable RTK client supporting ZED-F9P and UM980 with NTRIP corrections.  
**Architecture**: Flutter frontend + Python backend via WebSocket/HTTP APIs.  
**Compliance**: MINIMALISM_STANDARDS.md enforced - 150 lines max per file.

---

## Phase 1: Core Driver System (1 week)

### Milestone 1.1: Driver Interface
- Create `IGNSSDriver` abstract base class
- Implement `GNSSState` normalized data model
- Basic connection and data streaming contracts

**Key Files**: `src/drivers/IGNSSDriver.py`, `src/core/gnss_state.py`

### Milestone 1.2: ZED-F9P Driver
- UBX parser for NAV-PVT messages
- ZED-F9P driver implementation
- Unit tests with recorded UBX frames

**Key Files**: `src/drivers/zedf9p/ubx_parser.py`, `src/drivers/zedf9p/zedf9p_driver.py`

### Milestone 1.3: UM980 Driver  
- Unicore binary parser for BESTPOS messages
- UM980 driver implementation
- Unit tests with recorded Unicore frames

**Key Files**: `src/drivers/um980/unicore_parser.py`, `src/drivers/um980/um980_driver.py`

## Phase 2: Data Processing (1 week)

### Milestone 2.1: GNSS Abstraction
- Driver manager for multi-receiver coordination
- Protocol normalization layer
- Event-driven state updates

**Key Files**: `src/core/gnss_abstraction.py`, `src/core/driver_manager.py`

### Milestone 2.2: NTRIP Client
- NTRIP client with authentication and reconnection
- RTCM correction injection to active drivers
- Latency monitoring and metrics

**Key Files**: `src/core/ntrip_client.py`, `src/core/correction_manager.py`

## Phase 3: Data Persistence (3 days)

### Milestone 3.1: Data Logger
- Raw and corrected position logging
- File rotation and metadata management
- CSV and GeoJSON export capabilities

**Key Files**: `src/core/data_logger.py`, `src/tools/data_exporter.py`

## Phase 4: User Interface (1 week)

### Milestone 4.1: Backend API
- WebSocket server for real-time data
- HTTP REST API for configuration
- Android resource management

**Key Files**: `src/api/websocket_server.py`, `src/api/http_server.py`

### Milestone 4.2: Flutter Frontend
- Responsive map view with position display
- RTK status indicators and satellite skyplot
- Configuration panels for receivers and NTRIP

**Key Files**: `lib/widgets/map_view.dart`, `lib/widgets/status_panel.dart`

---

*See architecture.md for technical details and android-requirements.md for platform constraints*
