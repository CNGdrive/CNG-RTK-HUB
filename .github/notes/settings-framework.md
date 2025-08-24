# Settings Framework Architecture

## Profile Hierarchy

```
Site Profile (Company HQ, Job Site A, etc.)
├── Equipment Profile (Rover Unit 1, Base Station A, etc.)
│   └── Session Profile (Morning Survey, Boundary Check, etc.)
```

## Data Models

```python
@dataclass
class SiteProfile:
    id: str
    name: str
    location: GeoPoint
    default_ntrip_sources: List[NTRIPConfig]
    coordinate_system: str
    created_at: datetime
    updated_at: datetime

@dataclass  
class EquipmentProfile:
    id: str
    site_id: str
    name: str
    receiver_type: str
    antenna_config: AntennaConfig
    connection_config: ConnectionConfig
    calibration_data: Dict[str, Any]

@dataclass
class SessionProfile:
    id: str
    equipment_id: str
    name: str
    capture_mode: str  # "manual" | "continuous"
    logging_interval: int  # seconds
    accuracy_threshold: float  # meters
    session_type: str  # "survey" | "monitoring" | "calibration"
```

## Profile Inheritance & Validation

```python
class ProfileManager:
    def resolve_effective_config(self, session_id: str) -> EffectiveConfig:
        session = self.get_session_profile(session_id)
        equipment = self.get_equipment_profile(session.equipment_id)
        site = self.get_site_profile(equipment.site_id)
        
        # Merge configs with session taking priority
        return self._merge_configs(site, equipment, session)
    
    def validate_profile_chain(self, session_id: str) -> ValidationResult:
        # Validate entire profile inheritance chain
        pass
```

## Schema Versioning

```python
class ProfileSchema:
    VERSION = "1.0.0"
    
    @staticmethod
    def migrate_from_v1_0_0(data: Dict) -> Dict:
        # Migration logic for schema changes
        pass
    
    def validate(self, profile_data: Dict) -> ValidationResult:
        # JSON schema validation
        pass
```

## Import/Export Format

```json
{
  "export_version": "1.0.0",
  "timestamp": "2025-08-23T10:30:00Z",
  "profiles": {
    "sites": [...],
    "equipment": [...],
    "sessions": [...]
  },
  "metadata": {
    "exported_by": "user@company.com",
    "device_id": "tablet-001"
  }
}
```

## Coordinate System Transformations

### EPSG Handling
```python
class CoordinateTransformer:
    def validate_epsg_code(self, epsg: int) -> bool:
        pass
    
    def transform_coordinates(self, from_epsg: int, to_epsg: int, 
                            lat: float, lon: float) -> Tuple[float, float]:
        pass
    
    def get_datum_parameters(self, epsg: int) -> DatumConfig:
        pass
```

### Projection Parameters
- WGS84 (EPSG:4326) - Global standard
- Local grid systems - Site-specific projections
- UTM zones - Regional coordinate systems
- State plane coordinates - US surveying standard

### Transformation Validation
- Coordinate bounds checking
- Datum shift parameters
- Projection accuracy assessment
