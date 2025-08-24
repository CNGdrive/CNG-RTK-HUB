# Architecture Decision Records (ADR)

| ID | Decision | Rationale | Key Implementation | Status |
|---|---|---|---|---|
| 001 | **Android Primary Platform** | Ruggedized field deployment requirements | Flutter framework, Type-C USB host, battery optimization | Accepted |
| 002 | **Python Backend + Flutter Frontend** | Cross-platform + robust protocol parsing | Python: UBX/RTCM parsing, NTRIP client. Flutter: Android-first UI. WebSocket/HTTP API | Accepted |
| 003 | **Profile-Based Configuration** | Complex field configuration management | Hierarchical profiles (Site→Equipment→Session), JSON validation, cloud backup | Accepted |
| 004 | **Local-First Data Flow** | Intermittent field connectivity | SQLite local storage, opportunistic cloud sync, offline-first UI | Accepted |
| 005 | **Multi-Device Support** | Benchmarking requires multiple receivers | Plugin architecture, concurrent connections, unified data model | Accepted |
| 006 | **Modular Architecture** | Maintainable, testable codebase | Layered architecture, dependency injection, event-driven (see `implementation-checklist.md` Architecture Overview) | Accepted |
| 007 | **Responsive UI Framework** | Universal Android screen support | Breakpoint design (mobile<600, tablet<1024), adaptive navigation (see `responsive-ui-framework.md`) | Accepted |
| 008 | **Settings Inheritance Model** | Team sharing and field complexity | Profile inheritance, JSON validation, conflict resolution (see `settings-framework.md`) | Accepted |
