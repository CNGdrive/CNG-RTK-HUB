# Flutter-Python API Contract

## WebSocket Message Protocol

### Message Format
```json
{"type":"position_update|command|response|error","id":"uuid","timestamp":"ISO8601","payload":{}}
```

### Position Updates (Python → Flutter)
```json
{"type":"position_update","payload":{"timestamp_utc":"ISO8601","fix_type":"NO_FIX|DGPS|FLOAT|FIX","lat":40.7128,"lon":-74.0060,"altitude_m":10.5,"accuracy_m":0.018,"correction_latency_ms":180}}
```

### Commands (Flutter → Python)
```json
{"type":"command","payload":{"action":"connect|disconnect|set_profile|capture_point","params":{}}}
```

### Error Handling
```json
{"type":"error","payload":{"code":"CONNECTION_FAILED|INVALID_CONFIG|TIMEOUT","message":"Human readable error","details":{}}}
```

## HTTP REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profiles` | List all profiles |
| POST | `/api/profiles` | Create new profile |
| PUT | `/api/profiles/{id}` | Update profile |
| DELETE | `/api/profiles/{id}` | Delete profile |
| GET | `/api/devices` | List connected devices |
| POST | `/api/devices/scan` | Scan for new devices |
| GET | `/api/devices/{id}/status` | Get device status |
| GET | `/api/export/csv?session_id={id}` | Export CSV |
| GET | `/api/export/rinex?session_id={id}` | Export RINEX |
| GET | `/api/export/pdf?session_id={id}` | Generate PDF report |
