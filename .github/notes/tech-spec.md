# File: tech-spec.md

**Title**: Universal RTK App — One-page Technical Specification

**Purpose**: Single cross-vendor RTK client and toolkit. Normalizes receiver outputs. Manages corrections (NTRIP). Logs and exports survey-grade data. Provides diagnostics, benchmarking and APIs for external consumers.

**Development Philosophy**: Follow MINIMALISM_STANDARDS.md - prefer simple, working solutions over complex specifications.

**Scope**: Mobile and desktop deployments supporting USB/serial/BT/UDP receivers. **Primary targets**: u‑blox ZED‑F9P, Unicore UM980 with dual-receiver capability. Future drivers: Trimble, Hemisphere, Septentrio.

---

## Architecture (concise)

[ZED-F9P Receiver] <--> [UBX Driver Plugin] ──┐
                                                ├──> [Core Services]
[UM980 Receiver] <--> [Unicore Driver Plugin] ──┘

Core Services: GNSS Abstraction, NTRIP Correction Service, Data Logger, Benchmark Engine, Health Monitor, Protocol Normalizer.

App UI consumes Core Services via internal API. Extensibility: Plugin manager, Cloud sync, Replay, Dual-receiver benchmarking.

**Implementation**: Follows layered architecture with dependency injection (see `implementation-plan.md`). Responsive UI design for all Android screen sizes (see `responsive-ui-framework.md`).

**API**: WebSocket messages: `{"type":"position_update|command|response|error","payload":{}}`. REST endpoints: GET `/api/profiles`, POST `/api/devices/scan`, GET `/api/export/csv?session_id={id}`.

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

## Non-functional constraints

- Real-time latency target: <1000 ms from correction receipt to published corrected solution (relaxed from <300ms for accuracy priority).
- Memory/CPU: run on lightweight Linux device or user laptop. **Android-optimized**: <100MB memory, <30% CPU for dual-receiver operation.
- Modular code for Copilot to generate drivers and services.
- **Responsive Design**: Universal screen size support (phones to tablets) with adaptive layouts.
- **API Integration**: WebSocket real-time communication and HTTP REST endpoints (see above).
- **Configuration Management**: Hierarchical profile system with validation and inheritance (see `settings-framework.md`).

---