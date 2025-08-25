"""
Tests for Driver Manager functionality.
Testing dual receiver coordination and resource management.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.core.driver_manager import DriverManager, ReceiverType, DriverStatus
from src.core.interfaces import GNSSState, FixType, IGNSSDriver


class MockDriver(IGNSSDriver):
    """Mock driver for testing."""
    
    def __init__(self):
        self.connected = False
        self.streaming = False
        self.current_state = None
        self.corrections_received = []
        
    async def connect(self, port: str, baudrate: int = 115200) -> bool:
        if port == "fail_port":
            raise Exception("Connection failed")
        self.connected = True
        return True
        
    async def start_data_stream(self) -> None:
        if not self.connected:
            raise Exception("Not connected")
        self.streaming = True
        
    def get_current_state(self):
        return self.current_state
        
    def inject_corrections(self, rtcm_data: bytes) -> bool:
        if self.connected:
            self.corrections_received.append(rtcm_data)
            return True
        return False
        
    async def disconnect(self) -> None:
        self.connected = False
        self.streaming = False


def test_driver_manager_initialization():
    """Test driver manager initialization."""
    manager = DriverManager()
    
    assert len(manager.drivers) == 0
    assert len(manager.driver_status) == 0
    assert len(manager.state_callbacks) == 0
    assert manager.MAX_DRIVERS == 2
    assert manager.MAX_MEMORY_PER_DRIVER_MB == 35


def test_add_driver_success():
    """Test successful driver addition."""
    manager = DriverManager()
    
    # Mock the driver creation
    original_zedf9p = None
    try:
        # Temporarily replace ZedF9PDriver with mock
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        dm.ZedF9PDriver = MockDriver
        
        success = manager.add_driver("test_zedf9p", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
        
        assert success is True
        assert "test_zedf9p" in manager.drivers
        assert manager.driver_status["test_zedf9p"] == DriverStatus.DISCONNECTED
        assert manager.driver_configs["test_zedf9p"]["type"] == ReceiverType.ZED_F9P
        assert manager.driver_configs["test_zedf9p"]["port"] == "/dev/ttyUSB0"
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p


def test_add_driver_max_limit():
    """Test driver addition limit enforcement."""
    manager = DriverManager()
    
    # Mock driver creation
    original_zedf9p = None
    original_um980 = None
    try:
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        original_um980 = dm.UM980Driver
        dm.ZedF9PDriver = MockDriver
        dm.UM980Driver = MockDriver
        
        # Add maximum drivers
        success1 = manager.add_driver("driver1", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
        success2 = manager.add_driver("driver2", ReceiverType.UM980, "/dev/ttyUSB1")
        
        assert success1 is True
        assert success2 is True
        
        # Try to add third driver (should fail)
        success3 = manager.add_driver("driver3", ReceiverType.ZED_F9P, "/dev/ttyUSB2")
        assert success3 is False
        assert len(manager.drivers) == 2
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p
            dm.UM980Driver = original_um980


def test_remove_driver():
    """Test driver removal."""
    manager = DriverManager()
    
    # Mock driver creation
    original_zedf9p = None
    try:
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        dm.ZedF9PDriver = MockDriver
        
        # Add driver
        manager.add_driver("test_driver", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
        assert len(manager.drivers) == 1
        
        # Remove driver
        success = manager.remove_driver("test_driver")
        assert success is True
        assert len(manager.drivers) == 0
        assert "test_driver" not in manager.driver_status
        assert "test_driver" not in manager.driver_configs
        
        # Try to remove non-existent driver
        success = manager.remove_driver("nonexistent")
        assert success is False
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p


@pytest.mark.asyncio
async def test_connect_driver():
    """Test driver connection."""
    manager = DriverManager()
    
    # Mock driver creation
    original_zedf9p = None
    try:
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        dm.ZedF9PDriver = MockDriver
        
        # Add driver
        manager.add_driver("test_driver", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
        
        # Connect driver
        success = await manager.connect_driver("test_driver")
        assert success is True
        assert manager.driver_status["test_driver"] == DriverStatus.CONNECTED
        
        # Test connection failure
        manager.add_driver("fail_driver", ReceiverType.ZED_F9P, "fail_port")
        success = await manager.connect_driver("fail_driver")
        assert success is False
        assert manager.driver_status["fail_driver"] == DriverStatus.ERROR
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p


def test_state_callbacks():
    """Test state callback management."""
    manager = DriverManager()
    
    # Create mock callback
    callback_calls = []
    def test_callback(driver_id: str, state):
        callback_calls.append((driver_id, state))
    
    # Add callback
    manager.add_state_callback(test_callback)
    assert len(manager.state_callbacks) == 1
    
    # Remove callback
    manager.remove_state_callback(test_callback)
    assert len(manager.state_callbacks) == 0


def test_get_driver_status():
    """Test driver status retrieval."""
    manager = DriverManager()
    
    # Mock driver creation
    original_zedf9p = None
    try:
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        dm.ZedF9PDriver = MockDriver
        
        # Test non-existent driver
        status = manager.get_driver_status("nonexistent")
        assert status is None
        
        # Add driver and test status
        manager.add_driver("test_driver", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
        status = manager.get_driver_status("test_driver")
        assert status == DriverStatus.DISCONNECTED
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p


def test_inject_corrections():
    """Test RTCM corrections injection."""
    manager = DriverManager()
    
    # Mock driver creation
    original_zedf9p = None
    try:
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        dm.ZedF9PDriver = MockDriver
        
        # Add driver
        manager.add_driver("test_driver", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
        
        # Test injection on disconnected driver
        rtcm_data = b"test_rtcm_data"
        success = manager.inject_corrections("test_driver", rtcm_data)
        assert success is False
        
        # Connect driver and test injection
        driver = manager.drivers["test_driver"]
        driver.connected = True  # Simulate connection
        
        success = manager.inject_corrections("test_driver", rtcm_data)
        assert success is True
        assert rtcm_data in driver.corrections_received
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p


def test_get_all_status():
    """Test getting status of all drivers."""
    manager = DriverManager()
    
    # Mock driver creation
    original_zedf9p = None
    original_um980 = None
    try:
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        original_um980 = dm.UM980Driver
        dm.ZedF9PDriver = MockDriver
        dm.UM980Driver = MockDriver
        
        # Add drivers
        manager.add_driver("zedf9p", ReceiverType.ZED_F9P, "/dev/ttyUSB0", 115200)
        manager.add_driver("um980", ReceiverType.UM980, "/dev/ttyUSB1", 9600)
        
        all_status = manager.get_all_status()
        
        assert len(all_status) == 2
        assert "zedf9p" in all_status
        assert "um980" in all_status
        
        assert all_status["zedf9p"]["status"] == "DISCONNECTED"
        assert all_status["zedf9p"]["config"]["port"] == "/dev/ttyUSB0"
        assert all_status["zedf9p"]["config"]["baudrate"] == 115200
        
        assert all_status["um980"]["status"] == "DISCONNECTED"
        assert all_status["um980"]["config"]["port"] == "/dev/ttyUSB1"
        assert all_status["um980"]["config"]["baudrate"] == 9600
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p
            dm.UM980Driver = original_um980


# NTRIP Integration Tests

def test_setup_ntrip():
    """Test NTRIP manager setup."""
    manager = DriverManager()
    
    # Test initial state
    assert manager.ntrip_manager is None
    assert manager.ntrip_enabled is False
    
    # Setup NTRIP
    success = manager.setup_ntrip()
    assert success is True
    assert manager.ntrip_manager is not None
    
    # Test setup when already initialized
    success = manager.setup_ntrip()
    assert success is True


def test_add_ntrip_mount():
    """Test adding NTRIP mount point."""
    manager = DriverManager()
    
    # Add mount (should auto-initialize NTRIP)
    success = manager.add_ntrip_mount(
        host="test.ntrip.com",
        port=2101,
        mount="TEST01",
        username="testuser",
        password="testpass",
        priority=1,
        description="Test mount"
    )
    
    assert success is True
    assert manager.ntrip_manager is not None
    
    # Verify mount was added
    mounts = manager.get_ntrip_mounts()
    assert len(mounts) == 1
    assert mounts[0]['host'] == "test.ntrip.com"
    assert mounts[0]['mount'] == "TEST01"


@pytest.mark.asyncio
async def test_start_ntrip_corrections_no_manager():
    """Test starting NTRIP corrections without manager initialized."""
    manager = DriverManager()
    
    success = await manager.start_ntrip_corrections()
    assert success is False


@pytest.mark.asyncio
async def test_start_ntrip_corrections_with_manager():
    """Test starting NTRIP corrections with manager."""
    manager = DriverManager()
    manager.setup_ntrip()
    
    # Mock the mount manager start method
    with patch.object(manager.ntrip_manager, 'start', return_value=True) as mock_start:
        success = await manager.start_ntrip_corrections()
        
        assert success is True
        assert manager.ntrip_enabled is True
        mock_start.assert_called_once()


@pytest.mark.asyncio
async def test_stop_ntrip_corrections():
    """Test stopping NTRIP corrections."""
    manager = DriverManager()
    manager.setup_ntrip()
    manager.ntrip_enabled = True
    
    # Mock the mount manager stop method
    with patch.object(manager.ntrip_manager, 'stop') as mock_stop:
        await manager.stop_ntrip_corrections()
        
        assert manager.ntrip_enabled is False
        mock_stop.assert_called_once()


def test_ntrip_correction_received():
    """Test NTRIP correction handling and distribution."""
    manager = DriverManager()
    
    # Mock driver creation and add drivers
    original_zedf9p = None
    original_um980 = None
    try:
        import src.core.driver_manager as dm
        original_zedf9p = dm.ZedF9PDriver
        original_um980 = dm.UM980Driver
        dm.ZedF9PDriver = MockDriver
        dm.UM980Driver = MockDriver
        
        # Add drivers
        manager.add_driver("zedf9p", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
        manager.add_driver("um980", ReceiverType.UM980, "/dev/ttyUSB1")
        
        # Set drivers as connected
        manager.driver_status["zedf9p"] = DriverStatus.CONNECTED
        manager.driver_status["um980"] = DriverStatus.CONNECTED
        
        # Test correction injection
        rtcm_data = b'\xd3\x00\x13test_rtcm_data'
        manager._ntrip_correction_received(rtcm_data)
        
        # Verify statistics updated
        assert manager.correction_stats['total_corrections'] == 1
        assert manager.correction_stats['total_bytes'] == len(rtcm_data)
        assert manager.correction_stats['last_correction_time'] is not None
        
        # Verify corrections were injected to drivers
        zedf9p_driver = manager.drivers["zedf9p"]
        um980_driver = manager.drivers["um980"]
        assert rtcm_data in zedf9p_driver.corrections_received
        assert rtcm_data in um980_driver.corrections_received
        
    finally:
        if original_zedf9p:
            import src.core.driver_manager as dm
            dm.ZedF9PDriver = original_zedf9p
            dm.UM980Driver = original_um980


def test_get_ntrip_status_no_manager():
    """Test getting NTRIP status when manager not initialized."""
    manager = DriverManager()
    
    status = manager.get_ntrip_status()
    
    assert status['enabled'] is False
    assert status['initialized'] is False
    assert status['active_mount'] is None
    assert status['manager_status'] is None
    assert 'correction_stats' in status


def test_get_ntrip_status_with_manager():
    """Test getting NTRIP status with manager initialized."""
    manager = DriverManager()
    manager.setup_ntrip()
    manager.ntrip_enabled = True
    
    # Mock manager methods
    with patch.object(manager.ntrip_manager, 'get_active_mount', return_value={'mount': 'TEST01'}), \
         patch.object(manager.ntrip_manager, 'get_manager_status', return_value={'running': True}):
        
        status = manager.get_ntrip_status()
        
        assert status['enabled'] is True
        assert status['initialized'] is True
        assert status['active_mount']['mount'] == 'TEST01'
        assert status['manager_status']['running'] is True


def test_get_ntrip_mounts_no_manager():
    """Test getting NTRIP mounts when manager not initialized."""
    manager = DriverManager()
    
    mounts = manager.get_ntrip_mounts()
    assert mounts == []


def test_get_ntrip_mounts_with_manager():
    """Test getting NTRIP mounts with manager initialized."""
    manager = DriverManager()
    manager.setup_ntrip()
    
    # Mock mount manager method
    mock_mounts = [{'host': 'test.ntrip.com', 'mount': 'TEST01'}]
    with patch.object(manager.ntrip_manager, 'get_mounts', return_value=mock_mounts):
        mounts = manager.get_ntrip_mounts()
        assert mounts == mock_mounts


def test_websocket_server_integration():
    """Test WebSocket server integration for NTRIP status broadcasting."""
    manager = DriverManager()
    
    # Mock WebSocket server
    mock_websocket = Mock()
    manager.set_websocket_server(mock_websocket)
    
    assert manager.websocket_server == mock_websocket
