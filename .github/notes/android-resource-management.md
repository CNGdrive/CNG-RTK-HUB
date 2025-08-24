# Android Resource Management Strategy

**Purpose**: Optimize dual-receiver operation for Android mobile devices with limited resources.

**Date**: August 24, 2025  
**Priority**: Critical for field deployment  
**Target**: 8+ hour operation on ruggedized Android tablets

---

## Resource Constraints & Targets

### Android Hardware Assumptions
- **CPU**: Quad-core ARM Cortex-A53 @ 1.8GHz (typical ruggedized tablet)
- **RAM**: 4GB total, ~2GB available for apps  
- **Storage**: 64GB eMMC with ~40GB user available
- **Battery**: 7000-10000mAh with Type-C charging
- **Connectivity**: WiFi 802.11ac, LTE Cat 4, Bluetooth 5.0, USB 3.0 host

### Performance Targets
- **CPU Usage**: <30% sustained load for dual-receiver operation
- **Memory Usage**: <100MB total heap size  
- **Battery Life**: 8+ hours continuous operation
- **Data Processing**: <1000ms latency (relaxed from <300ms)
- **Storage**: <1GB per 8-hour session (including raw logs)

---

## Memory Management Strategy

### Heap Allocation Limits
```python
class ResourceManager:
    MAX_TOTAL_MEMORY_MB = 80      # Conservative Android limit
    MAX_PER_DRIVER_MB = 35        # Per-receiver memory budget
    BUFFER_SIZE_BYTES = 8192      # Serial/USB buffer size
    MAX_LOG_BUFFER_KB = 512       # In-memory log buffer
    
    def monitor_memory_usage(self) -> MemoryStats:
        heap_size = get_heap_size_mb()
        per_driver = {
            "zedf9p": get_driver_memory_mb("zedf9p"),
            "um980": get_driver_memory_mb("um980")
        }
        
        if heap_size > self.MAX_TOTAL_MEMORY_MB:
            self.trigger_memory_cleanup()
            
        return MemoryStats(heap_size, per_driver)
```

### Buffer Management
- **Serial Buffers**: 8KB circular buffers per receiver connection
- **Parse Buffers**: 4KB temporary buffers for protocol parsing
- **Log Buffers**: 512KB rotating buffers before disk write
- **State Buffers**: Single current state per receiver (no history in memory)

### Garbage Collection Optimization
```python
def optimize_gc_for_realtime():
    # Configure Python GC for real-time processing
    import gc
    gc.set_threshold(700, 10, 10)  # More frequent collection
    gc.disable()  # Manual GC control during data streaming
    
    # Periodic cleanup every 30 seconds
    schedule_periodic_gc(interval_seconds=30)
```

---

## CPU Resource Allocation

### Threading Strategy
```python
class ThreadManager:
    # Core thread allocation for dual-receiver system
    MAIN_THREAD = 1           # UI/coordination
    DRIVER_THREADS = 2        # One per active receiver
    NTRIP_THREAD = 1          # Correction client
    LOGGER_THREAD = 1         # Disk I/O
    TOTAL_THREADS = 5         # Maximum concurrent threads
    
    def create_driver_thread(self, driver_name: str) -> Thread:
        thread = Thread(
            target=self.driver_loop,
            name=f"driver_{driver_name}",
            daemon=True
        )
        thread.priority = ThreadPriority.HIGH
        return thread
```

### CPU Priority Management
- **High Priority**: Real-time data parsing (UBX/Unicore)
- **Normal Priority**: NTRIP corrections, state management
- **Low Priority**: Logging, file I/O, diagnostics
- **Background**: Periodic cleanup, statistics

### Processing Load Distribution
```python
def balance_processing_load():
    # Distribute CPU-intensive tasks across available cores
    if cpu_count() >= 4:
        assign_core(0, "main_ui")
        assign_core(1, "zedf9p_driver") 
        assign_core(2, "um980_driver")
        assign_core(3, "ntrip_logger")
    else:
        # Fallback for dual-core devices
        use_thread_affinity_hints()
```

---

## Battery Optimization Strategy

### Android Power Management Integration
```python
class BatteryOptimizer:
    def __init__(self):
        self.wake_lock = acquire_partial_wake_lock()
        self.foreground_service = create_foreground_service()
        
    def optimize_for_field_operation(self):
        # Request battery optimization whitelist
        request_battery_optimization_exemption()
        
        # Configure CPU governor for sustained performance
        set_cpu_governor_mode("performance")
        
        # Disable unnecessary Android services
        disable_background_app_refresh()
        
    def monitor_power_consumption(self) -> PowerStats:
        return PowerStats(
            battery_level=get_battery_percentage(),
            power_draw_mw=estimate_power_consumption(),
            time_remaining_hours=calculate_remaining_hours()
        )
```

### Power-Aware Processing
```python
def adaptive_processing_based_on_battery():
    battery_level = get_battery_percentage()
    
    if battery_level < 20:
        # Emergency power saving
        reduce_logging_frequency()
        disable_secondary_diagnostics()
        reduce_ntrip_retry_frequency()
        
    elif battery_level < 50:
        # Conservative power saving  
        reduce_satellite_tracking_updates()
        increase_gc_intervals()
        
    # Normal operation above 50%
```

### Thermal Management
```python
def monitor_thermal_throttling():
    cpu_temp = get_cpu_temperature()
    
    if cpu_temp > 70:  # Celsius
        # Reduce processing intensity
        increase_thread_sleep_intervals()
        reduce_real_time_diagnostics()
        
    if cpu_temp > 80:
        # Emergency thermal protection
        temporarily_disable_secondary_receiver()
        send_thermal_warning_to_ui()
```

---

## Storage Management

### Local Storage Strategy
```python
class StorageManager:
    LOG_ROTATION_SIZE_MB = 100    # Rotate logs at 100MB
    MAX_SESSION_LOGS = 10         # Keep 10 recent sessions
    CLEANUP_THRESHOLD_GB = 5      # Cleanup when <5GB free
    
    def manage_storage_lifecycle(self):
        free_space_gb = get_available_storage_gb()
        
        if free_space_gb < self.CLEANUP_THRESHOLD_GB:
            self.cleanup_old_sessions()
            self.compress_archived_logs()
            
    def optimize_write_patterns(self):
        # Batch writes to reduce eMMC wear
        use_write_batching(batch_size_kb=64)
        sync_to_disk_interval_seconds=30
```

### Data Compression
- **Real-time Logs**: No compression (performance priority)
- **Archive Logs**: gzip compression (reduce storage)  
- **Export Files**: Compression optional based on file size
- **RINEX Files**: Standard compression formats

---

## Connection Resource Management

### USB Host Mode Management
```python
class USBHostManager:
    def detect_usb_host_capability(self) -> bool:
        # Check Android USB host mode support
        return check_feature("android.hardware.usb.host")
        
    def manage_usb_power_consumption(self):
        # Monitor USB power draw
        usb_power_mw = get_usb_power_consumption()
        
        if usb_power_mw > 500:  # >0.5W sustained
            warn_user_about_power_usage()
            
    def handle_usb_disconnection(self):
        # Graceful handling of USB device disconnection
        attempt_reconnection_with_backoff()
        fallback_to_bluetooth_if_available()
```

### Bluetooth Resource Management
```python
class BluetoothManager:
    def optimize_bluetooth_for_continuous_operation(self):
        # Configure for low-latency, continuous data
        set_bluetooth_connection_interval_ms(7.5)  # Minimum interval
        set_bluetooth_supervision_timeout_ms(6000)  # 6 second timeout
        enable_bluetooth_le_scanning_optimization()
        
    def monitor_bluetooth_health(self):
        connection_quality = get_bluetooth_rssi()
        if connection_quality < -80:  # dBm
            suggest_receiver_positioning_adjustment()
```

---

## Concurrent Connection Limits

### Resource-Based Connection Limiting
```python
class ConnectionLimiter:
    def determine_max_receivers(self) -> int:
        available_memory_mb = get_available_memory_mb()
        cpu_cores = cpu_count()
        battery_level = get_battery_percentage()
        
        if available_memory_mb < 150 or cpu_cores < 4:
            return 1  # Single receiver only
            
        if battery_level < 30:
            return 1  # Power conservation
            
        return 2  # Dual receiver (maximum supported)
        
    def graceful_receiver_shutdown(self, receiver_id: str):
        # Clean shutdown of secondary receiver under resource pressure
        stop_data_stream(receiver_id)
        flush_pending_logs(receiver_id)
        release_driver_resources(receiver_id)
        notify_ui_receiver_disabled(receiver_id)
```

---

## Monitoring & Diagnostics

### Real-time Resource Monitoring
```python
@dataclass
class SystemResourceStats:
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_mb: float
    battery_level_percent: int
    storage_free_gb: float
    active_receivers: List[str]
    connection_quality: Dict[str, int]  # RSSI/signal strength
    
def collect_resource_stats() -> SystemResourceStats:
    # Lightweight resource collection every 10 seconds
    pass
    
def log_resource_stats_to_file():
    # Periodic logging for post-analysis
    pass
```

### Performance Alerts
```python
class PerformanceMonitor:
    def check_performance_thresholds(self):
        stats = collect_resource_stats()
        
        if stats.cpu_usage_percent > 80:
            send_alert("High CPU usage detected")
            
        if stats.memory_usage_mb > self.MAX_TOTAL_MEMORY_MB:
            send_alert("Memory limit exceeded")
            trigger_emergency_cleanup()
            
        if stats.battery_level_percent < 15:
            send_alert("Low battery - consider reducing operations")
```

---

## Field Deployment Considerations

### Ruggedized Device Optimization
- **Temperature Range**: -20°C to +60°C operation
- **Vibration Resistance**: Secure all connections, validate data integrity
- **Water Resistance**: IP67 rating compliance for connections
- **Drop Protection**: Graceful handling of sudden power loss/reconnection

### Network Adaptation
```python
def adapt_to_network_conditions():
    connection_type = get_network_connection_type()
    
    if connection_type == "cellular_2g":
        reduce_ntrip_retry_frequency()
        compress_cloud_sync_data()
        
    elif connection_type == "wifi_slow":
        batch_cloud_uploads()
        reduce_real_time_streaming()
        
    # Optimize based on available bandwidth
```

---

**Implementation Priority**: Resource monitoring must be implemented early to validate assumptions and adjust targets based on real-world device performance.
