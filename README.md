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

### 🔄 Next Milestones
- WebSocket API for real-time data streaming
- Flutter frontend with map display
- NTRIP client for correction data
- Android platform integration

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
pytest tests/
```

## Project Structure

```
src/
├── core/
│   └── interfaces.py      # IGNSSDriver, GNSSState, exceptions
├── drivers/
│   ├── zedf9p.py         # ZED-F9P UBX protocol driver
│   └── um980.py          # UM980 Unicore binary driver
tests/
├── test_interfaces.py    # Core interface tests
└── test_zedf9p.py        # ZED-F9P driver tests
```

## Memory Constraints

- **Total application**: <100MB heap
- **Per driver**: <35MB memory limit
- **Threading**: Maximum 5 threads (UI + 2×drivers + NTRIP + logger)

## Android Deployment

Target platform: Ruggedized Android tablets with USB host mode for direct receiver connections.

---

*Implemented from IMPLEMENTATION_GUIDE.md and ARCHITECTURE_DECISIONS.md*
