# File: tech-spec.md

**Title**: Universal RTK App — One-page Technical Specification

**Purpose**: Single cross-vendor RTK client and toolkit. Normalizes receiver outputs. Manages corrections (NTRIP). Logs and exports survey-grade data. Provides diagnostics, benchmarking and APIs for external consumers.

**Scope**: Mobile and desktop deployments supporting USB/serial/BT/UDP receivers. Initial targets: u‑blox ZED‑F9P, Unicore UM980. Future drivers: Trimble, Hemisphere, Septentrio.

---

## Architecture (concise)

[Receiver HW] <--> [Driver Plugin (one per vendor)] --> [Core Services]

Core Services: GNSS Abstraction, NTRIP Correction Service, Data Logger, Benchmark Engine, Health Monitor.

App UI consumes Core Services via internal API. Extensibility: Plugin manager, Cloud sync, Replay.

**Implementation**: Follows layered architecture with dependency injection (see `modular-architecture.md`). Flutter-Python communication via WebSocket/HTTP API (see `flutter-python-api.md`). Responsive UI design for all Android screen sizes (see `responsive-ui-framework.md`).

---

## Normalized data model (single RTK state object)

```json
{
  "timestamp_utc": "ISO8601",
  "fix_type": "NO_FIX|DGPS|FLOAT|FIX",
  "sats": {"GPS":6,"GLO":4,"GAL":8,"BDS":3},
  "snr": {"G01":42,...},
  "pdop": 1.2,
  "hdop": 0.6,
  "vdop": 1.0,
  "accuracy_m": 0.018,        // estimated 1-sigma
  "baseline_m": 0.0,
  "correction_source": "NTRIP://...",
  "correction_latency_ms": 180,
  "antenna_offset_m": {"x":0.0,"y":0.0,"z":1.5},
  "receiver_meta": {"model":"ZED-F9P","fw":"x.y.z"}
}
```

Fields are minimal and canonical for UI, logging and APIs.

---

## Protocols supported

- Receiver input: UBX, Unicore binary, NMEA, manufacturer ASCII, binary telemetry.
- Corrections: RTCM v2/v3/v3.x. Optionally CMR/CMR+ via vendor modules later.
- Services: NTRIP v2 (HTTP over TCP/TLS) with multi-mountpoint and auth.

---

## Core behaviours & invariants

- Drivers translate device-specific flags to `fix_type` semantically.
- Antenna offsets applied before export and API publication.
- Latency measured from NTRIP server reception to delivered corrected solution.
- Buffered corrections allowed but user-visible latency metric must update in real-time.
- Exports must carry epoch timestamps and metadata (receiver, antenna, correction source, EPSG).

---

## Exports

- RINEX (obs, nav) compliant headers
- CSV (point log), GeoJSON, GPX, KML for mapping
- PDF/CSV reports for Benchmark results

---

## Diagnostics & QA

- Skyplot per-constellation with SNR coloring
- SNR per-sat time series
- Fix-summary intervals (1h/24h): fix %, time-to-fix, RMS
- Dual-device benchmark: scatter, RMS, fix-match rate

---

## Security & operations

- NTRIP over TLS. Store creds securely. Option for OS keychain.
- Cloud sync TLS + token auth. Minimal PII in logs.
- Local-first: store logs locally and batch-push when network available.

---

## Testing

- Unit tests for parser → normalized state mapping.
- Integration tests using recorded UBX/RTCM streams and synthetic NTRIP server.
- Hardware-in-loop (HIL) with live receivers for acceptance.
- Long-duration soak tests for reconnect/recovery behaviour.

---

## Non-functional constraints

- Real-time latency target: <300 ms from correction receipt to published corrected solution for cellular/WAN when possible.
- Memory/CPU: run on lightweight Linux device or user laptop.
- Modular code for Copilot to generate drivers and services.
- **Responsive Design**: Universal screen size support (phones to tablets) with adaptive layouts.
- **API Integration**: WebSocket real-time communication and HTTP REST endpoints (see `flutter-python-api.md`).
- **Configuration Management**: Hierarchical profile system with validation and inheritance (see `settings-framework.md`).

---