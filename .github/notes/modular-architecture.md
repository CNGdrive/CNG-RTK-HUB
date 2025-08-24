# Modular Architecture Specification

## Core Architecture Patterns

### 1. Layered Architecture
```
┌─────────────────────────────────────┐
│ Presentation Layer (Flutter UI)     │
├─────────────────────────────────────┤
│ Application Layer (Business Logic)  │
├─────────────────────────────────────┤
│ Domain Layer (Core Models)          │
├─────────────────────────────────────┤
│ Infrastructure Layer (I/O, Storage) │
└─────────────────────────────────────┘
```

### 2. Plugin System Architecture
```python
# Base driver interface
class IGNSSDriver(ABC):
    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> bool:
        pass
    
    @abstractmethod
    async def read_position(self) -> GNSSState:
        pass
    
    @abstractmethod
    async def send_corrections(self, rtcm_data: bytes) -> bool:
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        pass
```

### 3. Shared Utility Libraries

#### Connection Management
```python
# src/core/utils/connection_manager.py
class ConnectionManager:
    def register_driver(self, driver_type: str, driver_class: Type[IGNSSDriver])
    def create_connection(self, config: ConnectionConfig) -> IGNSSDriver
    def monitor_health(self, connection_id: str) -> HealthStatus
```

#### Data Validation
```python
# src/core/utils/validators.py
class ProfileValidator:
    def validate_antenna_config(self, config: AntennaConfig) -> ValidationResult
    def validate_ntrip_config(self, config: NTRIPConfig) -> ValidationResult
    def validate_session_config(self, config: SessionConfig) -> ValidationResult
```

### 4. Dependency Injection Container
```python
# src/core/container.py
class DIContainer:
    def __init__(self):
        self._services = {}
        self._singletons = {}
    
    def register_singleton(self, interface: Type, implementation: Type)
    def register_transient(self, interface: Type, implementation: Type)
    def resolve(self, interface: Type) -> Any
```

### 5. Event System for Loose Coupling
```python
# src/core/events/event_bus.py
class EventBus:
    def subscribe(self, event_type: Type, handler: Callable)
    def publish(self, event: Event)
    def unsubscribe(self, event_type: Type, handler: Callable)
```

## File Organization Strategy

```
src/
├── core/
│   ├── models/           # Domain models
│   ├── interfaces/       # Abstract base classes
│   ├── services/         # Business logic
│   ├── utils/           # Shared utilities
│   ├── events/          # Event system
│   ├── repositories/    # Data access
│   └── container.py     # Dependency injection
├── drivers/
│   ├── base/            # Base driver classes
│   ├── zedf9p/          # u-blox ZED-F9P driver
│   ├── um980/           # Unicore UM980 driver
│   └── factory.py       # Driver factory
├── infrastructure/
│   ├── storage/         # File system, database
│   ├── network/         # NTRIP, HTTP clients
│   ├── android/         # Android integrations
│   └── logging/         # Structured logging
└── api/
    ├── websocket/       # WebSocket server
    ├── http/            # HTTP REST API
    └── serializers/     # Data serialization
```
