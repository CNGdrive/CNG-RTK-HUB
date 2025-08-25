# CNG-RTK-HUB

Universal RTK GNSS client supporting ZED-F9P (UBX) and UM980 (Unicore binary) receivers.

## Architecture

- **Python Backend**: Protocol parsing and data processing
- **Flutter Frontend**: Android-first responsive UI
- **Dual Receiver Support**: Simultaneous operation of 2 GNSS receivers
- **Real-time Processing**: <1000ms latency with RTCM corrections

## Current Implementation Status

### ✅ Milestone 1: Core Interfaces (Completed)
- `IGNSSDriver` abstract interface for receiver plugins
- `GNSSState` normalized data model for all receivers
- ZED-F9P driver with UBX-NAV-PVT parsing
- UM980 driver with Unicore BESTPOS parsing
- Comprehensive test suite with error handling
- Project configuration (pyproject.toml, requirements.txt)

### ✅ Milestone 2: WebSocket API & Real-time Streaming (Completed)
- WebSocket server for real-time position streaming
- HTTP REST API for receiver configuration and control
- Driver Manager for dual-receiver coordination
- Real-time data broadcasting to multiple clients
- Resource allocation and threading constraints (<35MB per driver)
- Complete API endpoints for driver management

### 🎯 Milestone 3: NTRIP Client ✅ **COMPLETE AND PRODUCTION READY**
- NTRIP client for RTCM correction data
- Multi-mount support with authentication
- Real-time correction injection to receivers
- Connection monitoring and automatic failover

### 🔄 Future Milestones
- Flutter frontend with map display and RTK status
- Android platform integration and permissions
- Field deployment optimization and testing

## Usage

### Start the RTK Service
```bash
python -m src.rtk_service
```

### API Endpoints

**WebSocket Stream** (Real-time position data)
```
ws://localhost:8765
```

**HTTP REST API** (Configuration and control)
```
GET  /api/status           # System status
GET  /api/drivers          # All drivers status
POST /api/drivers          # Add new driver
POST /api/drivers/{id}/connect     # Connect driver
POST /api/drivers/{id}/corrections # Inject RTCM data
POST /api/streams/start    # Start all data streams

# NTRIP Client API (Milestone 3)
GET  /api/ntrip/status     # NTRIP connection status
GET  /api/ntrip/mounts     # List configured mounts  
POST /api/ntrip/mounts     # Add NTRIP mount
POST /api/ntrip/connect    # Start NTRIP corrections
POST /api/ntrip/disconnect # Stop NTRIP corrections
DELETE /api/ntrip/mounts/{id} # Remove mount
```

### Example: Add and Connect Receivers
```bash
# Add ZED-F9P receiver
curl -X POST http://localhost:8080/api/drivers \
  -H "Content-Type: application/json" \
  -d '{"driver_id":"zedf9p","receiver_type":"ZED_F9P","port":"/dev/ttyUSB0"}'

# Add UM980 receiver  
curl -X POST http://localhost:8080/api/drivers \
  -H "Content-Type: application/json" \
  -d '{"driver_id":"um980","receiver_type":"UM980","port":"/dev/ttyUSB1"}'

# Connect both receivers
curl -X POST http://localhost:8080/api/drivers/zedf9p/connect
curl -X POST http://localhost:8080/api/drivers/um980/connect

# Start data streams
curl -X POST http://localhost:8080/api/streams/start
```

### Example: Setup NTRIP Corrections
```bash
# Add NTRIP mountpoint
curl -X POST http://localhost:8080/api/ntrip/mounts \
  -H "Content-Type: application/json" \
  -d '{
    "host": "rtk2go.com",
    "port": 2101,
    "mount": "TESTMOUNT",
    "username": "user@email.com",
    "password": "password",
    "priority": 1,
    "description": "Primary RTK source"
  }'

# Start NTRIP corrections  
curl -X POST http://localhost:8080/api/ntrip/connect

# Check NTRIP status
curl http://localhost:8080/api/ntrip/status
```

## Project Structure

```
src/
├── core/
│   ├── interfaces.py      # IGNSSDriver, GNSSState, exceptions
│   └── driver_manager.py  # Dual-receiver coordination
├── drivers/
│   ├── zedf9p.py         # ZED-F9P UBX protocol driver
│   └── um980.py          # UM980 Unicore binary driver
├── ntrip/                # NTRIP Client (Milestone 3)
│   ├── __init__.py       # Package exports
│   ├── ntrip_client.py   # Core NTRIP v1.0/v2.0 client
│   └── mount_manager.py  # Multi-mount failover manager
├── api/
│   ├── websocket_server.py # Real-time data streaming
│   └── http_server.py     # REST API for configuration
└── rtk_service.py         # Main service coordinator
tests/
├── test_interfaces.py    # Core interface tests
├── test_zedf9p.py        # ZED-F9P driver tests
├── test_ntrip_client.py  # NTRIP client tests
├── test_mount_manager.py # Mount manager tests
├── test_websocket_server.py # WebSocket functionality tests
└── test_driver_manager.py   # Driver coordination tests
```

## Installation & Testing

```bash
pip install -r requirements.txt
pytest tests/
```

## Memory Constraints

- **Total application**: <100MB heap
- **Per driver**: <35MB memory limit
- **Threading**: Maximum 5 threads (UI + 2×drivers + NTRIP + logger)

## Android Deployment

Target platform: Ruggedized Android tablets with USB host mode for direct receiver connections.

---

*Implemented from IMPLEMENTATION_GUIDE.md and ARCHITECTURE_DECISIONS.md*
