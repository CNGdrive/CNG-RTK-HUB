# File: implementation-checklist.md

**Goal**: Prioritized implementation checklist. Deliverable: minimal viable product (MVP) that runs a ZED‑F9P over serial/USB with NTRIP corrections, a data logger and a simple dashboard.

## Architecture
**Layers**: Presentation (Flutter) → Application (Business Logic) → Domain (Models) → Infrastructure (I/O)
**Patterns**: Plugin system via `IGNSSDriver` interface, Dependency injection `DIContainer`, Event-driven `EventBus`
**Structure**: `src/core/` (models, services, utils), `src/drivers/` (zedf9p, um980), `src/infrastructure/` (storage, network), `src/api/` (websocket, http), `src/android/` (resource management)

## Milestone 0 — Repo scaffold (1 day)
- Create repo, CI skeleton, linter, pre-commit.
- Add architecture README and contributor guide.
- **Architecture validation**: Verify modular design patterns and responsive UI framework setup.

**Files/classes**
- `README.md`
- `pyproject.toml` (Python backend) + `pubspec.yaml` (Flutter frontend)
- `src/` base folders: `core/ drivers/ ui/ tests/ tools/`
- **Architecture references**: `responsive-ui-framework.md`, `settings-framework.md`, API (in `tech-spec.md`)


## Milestone 1 — Dual-Driver Interface + ZED‑F9P driver (3–5 days)
- Define driver contract interface supporting multiple receiver types.
- Implement UBX parser and ZED‑F9P driver mapping to normalized state.
- Unit tests with recorded UBX frames.
- **Updated**: Support for dual-receiver architecture (ZED-F9P + UM980).

**Files/classes**
- `src/drivers/IGNSSDriver.py` (interface)
- `src/drivers/base_driver.py` (common functionality)
- `src/drivers/zedf9p/ubx_parser.py`
- `src/drivers/zedf9p/zedf9p_driver.py`
- `tests/drivers/test_ubx_parser.py`

**Copilot prompt**: Generate Python class `Zedf9pDriver` implementing `IGNSSDriver` with UBX frame parsing and RTK state normalization.


## Milestone 1.5 — UM980 Unicore Driver (2–3 days)
- Implement Unicore binary parser and UM980 driver mapping to normalized state.
- Add support for BESTPOS, SATELLITESTATUS messages.
- Unit tests with recorded Unicore binary frames.

**Files/classes**
- `src/drivers/um980/unicore_parser.py`
- `src/drivers/um980/unicore_messages.py`
- `src/drivers/um980/um980_driver.py`
- `tests/drivers/test_unicore_parser.py`

**Copilot prompt**: Generate Python class `Um980Driver` implementing `IGNSSDriver` with Unicore binary parsing and RTK state normalization.


## Milestone 2 — GNSS Abstraction & Data Model (2 days)
- Implement normalized state object and pub/sub or callback API for subscribers.
- Antenna offset application and EPSG handling.
- **Updated**: Protocol normalization layer for UBX and Unicore binary formats.

**Files/classes**
- `src/core/gnss_state.py`
- `src/core/gnss_abstraction.py`
- `src/core/protocol_normalizer.py`
- `tests/core/test_gnss_state.py`


## Milestone 3 — NTRIP client & correction pipeline (3–5 days)
- Implement NTRIP client with multi-mount support, TLS, reconnect and latency metrics.
- Wire NTRIP output to driver correction input or internal correction handler.

**Files/classes**
- `src/core/ntrip_client.py`
- `tests/core/test_ntrip.py` (use local mock server)

**Copilot prompt**: Create NTRIP client with auth, RTCM stream, latency metrics, reconnect backoff.


## Milestone 4 — Data logger & export (2–3 days)
- Raw + corrected logging. Rotation and metadata.
- Export CSV and GeoJSON. RINEX as an optional task.

**Files/classes**
- `src/core/data_logger.py`
- `src/tools/rinex_exporter.py`
- `tests/core/test_data_logger.py`


## Milestone 5 — Minimal UI dashboard (4–7 days)
- Flutter UI with responsive design for Android tablets/phones.
- Map (leaflet/Mapbox), RTK indicator, skyplot, basic point capture.
- **Responsive Design**: Implement adaptive layouts for all screen sizes (see `responsive-ui-framework.md`).
- **API Integration**: WebSocket/HTTP communication with Python backend (see `tech-spec.md`).

**Files/classes**
- `lib/main.dart`
- `lib/widgets/map_view.dart`
- `lib/widgets/skyplot.dart`
- `lib/widgets/responsive_grid.dart` (adaptive layout system)
- `lib/widgets/adaptive_navigation.dart` (responsive navigation)
- `src/backend/api_server.py` (serves normalized state over WebSocket/HTTP)


## Milestone 6 — Benchmark engine & dual-receiver comparison (3 days)
- Dual-device comparison module and replay of logs.
- **Updated**: Enhanced for ZED-F9P vs UM980 benchmarking scenarios.

**Files/classes**
- `src/core/benchmark.py`
- `src/core/replay.py`
- `src/drivers/driver_manager.py` (dual-receiver coordination)


## Milestone 7 — Health monitor & reports (2 days)
- SNR time series, PDOP alerts, receiver telemetry capture.

**Files/classes**
- `src/core/health_monitor.py`
- `src/tools/report_generator.py`


## Milestone 8 — Plugin manager, cloud sync, packaging (4 days)
- Plugin discovery, driver install pattern, cloud log push with token-based auth.
- Desktop packaging (Electron) or containerization.

**Files/classes**
- `src/plugins/manager.py`
- `src/core/cloud_sync.py`


## Testing & validation (parallel)
- HIL scripts and long-run soak tests.
- Integration test plan doc.

**Files**
- `tests/hil/run_hil.sh`
- `tests/fixtures/recordings/*.ubx` and `*.rtcm`


## Priority order (MVP first)
1. Repo scaffold
2. Dual-Driver interface + UBX ZED‑F9P
3. UM980 Unicore driver
4. GNSS abstraction + protocol normalization
5. NTRIP client
6. Data logger
7. Minimal dashboard (read-only)
8. Dual-receiver benchmark
9. Health monitor
10. Cloud sync + plugin manager


## Developer guidance
- Single-responsibility functions, explicit prompts, ship tests with code.

## Risk mitigation  
- Binary logging for root-cause analysis. Safe mode: NMEA GGA fallback.

---