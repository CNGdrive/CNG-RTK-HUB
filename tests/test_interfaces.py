"""
Tests for core interfaces and data models.
Following testing patterns from IMPLEMENTATION_GUIDE.md
"""

import pytest
from src.core.interfaces import GNSSState, FixType, IGNSSDriver, ConnectionError, ProtocolError


def test_gnss_state_creation():
    """Test GNSSState dataclass creation and validation."""
    state = GNSSState(
        timestamp_utc="2025-08-25T14:30:15.123Z",
        fix_type=FixType.FIX,
        latitude=37.7749,
        longitude=-122.4194,
        altitude_m=10.5,
        accuracy_m=0.5,
        sats={"GPS": 8, "GLO": 4},
        pdop=1.2,
        baseline_m=100.0,
        correction_source="NTRIP_SERVER",
        receiver_meta={"model": "ZED-F9P", "fw": "1.13"}
    )
    
    # Validate basic fields
    assert state.fix_type == FixType.FIX
    assert -90 <= state.latitude <= 90
    assert -180 <= state.longitude <= 180
    assert state.accuracy_m > 0
    assert state.sats["GPS"] == 8


def test_fix_type_enum():
    """Test FixType enumeration values."""
    assert FixType.NO_FIX.value == "NO_FIX"
    assert FixType.DGPS.value == "DGPS"
    assert FixType.FLOAT.value == "FLOAT"
    assert FixType.FIX.value == "FIX"


def test_custom_exceptions():
    """Test custom exception classes."""
    conn_error = ConnectionError("Test connection error")
    assert str(conn_error) == "Test connection error"
    
    proto_error = ProtocolError("Test protocol error")
    assert str(proto_error) == "Test protocol error"


class MockGNSSDriver(IGNSSDriver):
    """Mock driver for testing interface compliance."""
    
    def __init__(self):
        self.connected = False
        self.streaming = False
        self.current_state = None
    
    async def connect(self, port: str, baudrate: int = 115200) -> bool:
        if port == "invalid_port":
            raise ConnectionError("Invalid port specified")
        self.connected = True
        return True
    
    async def start_data_stream(self) -> None:
        if not self.connected:
            raise ProtocolError("Not connected")
        self.streaming = True
    
    def get_current_state(self):
        return self.current_state
    
    def inject_corrections(self, rtcm_data: bytes) -> bool:
        return self.connected
    
    async def disconnect(self) -> None:
        self.connected = False
        self.streaming = False


@pytest.mark.asyncio
async def test_driver_interface():
    """Test IGNSSDriver interface implementation."""
    driver = MockGNSSDriver()
    
    # Test connection
    result = await driver.connect("/dev/ttyUSB0")
    assert result is True
    assert driver.connected is True
    
    # Test data stream
    await driver.start_data_stream()
    assert driver.streaming is True
    
    # Test corrections injection
    result = driver.inject_corrections(b"test_rtcm_data")
    assert result is True
    
    # Test disconnect
    await driver.disconnect()
    assert driver.connected is False


@pytest.mark.asyncio
async def test_connection_error_handling():
    """Test connection error handling."""
    driver = MockGNSSDriver()
    
    with pytest.raises(ConnectionError):
        await driver.connect("invalid_port")
