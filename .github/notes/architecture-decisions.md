# Architecture Decision Records (ADR)

## ADR-001: Primary Platform - Android First
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Field deployment requirements specify ruggedized Android tablets/phones as primary target.

**Decision**: 
- Primary: Flutter framework for Android
- Secondary: Windows integration via file export/import
- Future: Raspberry Pi embedded deployment

**Consequences**:
- Cross-platform codebase, Type-C USB host required, battery optimization critical

---

## ADR-002: Technology Stack - Python Backend + Flutter Frontend
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Need cross-platform support with robust binary protocol parsing.

**Decision**:
- Backend: Python for UBX/RTCM parsing, NTRIP client, data processing
- Frontend: Flutter for Android-first UI with Windows compatibility
- Communication: WebSocket/HTTP API between backend and frontend
- Alternative: Consider native Android with NDK for performance-critical parsing

**Consequences**:
- Modular platform-specific optimizations, rich GNSS ecosystem, consistent cross-platform UI

---

## ADR-003: Settings Architecture - Profile-Based Configuration
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Field requirements demand extensive configuration management for antennas, NTRIP sources, hardware, and session parameters.

**Decision**:
- Hierarchical profiles: Site → Equipment → Session
- Local-first storage with cloud backup
- JSON schema validation for profile integrity
- Import/export capabilities for team sharing

**Consequences**:
- Complex settings system, critical profile validation, essential backup/restore workflows

---

## ADR-004: Data Flow - Local-First with Cloud Sync
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Field environments have intermittent connectivity but require remote monitoring.

**Decision**:
- All data logged locally first (SQLite + file storage)
- Opportunistic cloud sync when connectivity available
- Real-time streaming when connection stable
- Offline-first UI design

**Consequences**:
- Robust offline capabilities, sync conflict resolution, best-effort remote monitoring

---

## ADR-005: Multi-Device Support - Simultaneous Connections
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Benchmarking and validation workflows require multiple receivers.

**Decision**:
- Plugin architecture for receiver drivers
- Concurrent connection management
- Unified data model for comparison
- Device-specific configuration profiles

**Consequences**:
- Complex connection state management, resource scaling, multi-device UI complexity

---

## ADR-006: Modular Architecture Pattern
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Need maintainable, testable, and reusable codebase with clear separation of concerns.

**Decision**:
- Layered architecture (Presentation → Application → Domain → Infrastructure)
- Dependency injection container for loose coupling
- Event-driven communication between components
- Shared utility libraries for common functionality
- Plugin system with factory patterns

**Consequences**:
- Higher initial complexity but better maintainability, easier testing, consistent patterns (see `modular-architecture.md`)

---

## ADR-007: Responsive UI Framework
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Android deployment requires universal screen size support from phones to tablets.

**Decision**:
- Breakpoint-based responsive design (mobile: <600, tablet: <1024, desktop: 1025+)
- Adaptive navigation (bottom bar for mobile, navigation rail for tablet+)
- Scalable map views with device-appropriate sizing
- Orientation-aware layouts with separate portrait/landscape components

**Consequences**:
- Consistent UX across devices, complex but future-proof layout management, better accessibility (see `responsive-ui-framework.md`)

---

## ADR-008: Settings Inheritance Model
**Status**: Accepted  
**Date**: 2025-08-23

**Context**: Field deployment requires complex configuration management with team sharing capabilities.

**Decision**:
- Hierarchical profile inheritance: Site → Equipment → Session
- JSON schema validation with versioning support
- Local-first storage with cloud backup and sharing
- Profile manager with conflict resolution and validation

**Consequences**:
- Flexible field configuration, complex but reliable validation, team collaboration (see `settings-framework.md`)
