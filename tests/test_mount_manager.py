"""
Tests for NTRIP mount manager functionality.
Covers multi-mount support, failover, and priority management.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.ntrip.mount_manager import NTRIPMountManager, MountStatus
from src.ntrip.ntrip_client import NTRIPMount


@pytest.fixture
def correction_callback():
    """Mock correction callback function."""
    return Mock()


@pytest.fixture
def mount_manager(correction_callback):
    """Create mount manager for testing."""
    return NTRIPMountManager(correction_callback)


@pytest.fixture
def test_mounts():
    """Create test mount configurations."""
    return [
        NTRIPMount("test1.ntrip.com", 2101, "MOUNT1", "user1", "pass1", "Primary mount"),
        NTRIPMount("test2.ntrip.com", 2101, "MOUNT2", "user2", "pass2", "Backup mount"),
        NTRIPMount("test3.ntrip.com", 2101, "MOUNT3", "user3", "pass3", "Secondary backup")
    ]


class TestNTRIPMountManager:
    """Test cases for NTRIP mount manager."""
    
    def test_mount_manager_initialization(self, correction_callback):
        """Test mount manager initialization."""
        manager = NTRIPMountManager(correction_callback)
        
        assert manager.correction_callback == correction_callback
        assert manager.mounts == []
        assert manager.active_client is None
        assert manager.active_mount is None
        assert manager.running is False
    
    def test_add_mount(self, mount_manager, test_mounts):
        """Test adding mounts to manager."""
        mount = test_mounts[0]
        mount_manager.add_mount(mount, priority=1)
        
        assert len(mount_manager.mounts) == 1
        assert mount_manager.mounts[0].mount == mount
        assert mount_manager.mounts[0].priority == 1
    
    def test_add_multiple_mounts_priority_sorting(self, mount_manager, test_mounts):
        """Test that mounts are sorted by priority."""
        # Add mounts in reverse priority order
        mount_manager.add_mount(test_mounts[0], priority=3)  # Lowest priority
        mount_manager.add_mount(test_mounts[1], priority=1)  # Highest priority
        mount_manager.add_mount(test_mounts[2], priority=2)  # Medium priority
        
        # Check they are sorted by priority (lower number = higher priority)
        assert mount_manager.mounts[0].priority == 1  # test_mounts[1]
        assert mount_manager.mounts[1].priority == 2  # test_mounts[2]
        assert mount_manager.mounts[2].priority == 3  # test_mounts[0]
    
    def test_remove_mount(self, mount_manager, test_mounts):
        """Test removing mount from manager."""
        mount = test_mounts[0]
        mount_manager.add_mount(mount, priority=1)
        
        mount_id = f"{mount.host}:{mount.port}/{mount.mount}"
        mount_manager.remove_mount(mount_id)
        
        assert len(mount_manager.mounts) == 0
    
    def test_get_mounts(self, mount_manager, test_mounts):
        """Test getting mount list with status."""
        mount_manager.add_mount(test_mounts[0], priority=1)
        mount_manager.add_mount(test_mounts[1], priority=2)
        
        mounts = mount_manager.get_mounts()
        
        assert len(mounts) == 2
        assert mounts[0]['host'] == test_mounts[0].host
        assert mounts[0]['priority'] == 1
        assert mounts[0]['connected'] is False
        assert 'total_bytes' in mounts[0]
        assert 'consecutive_failures' in mounts[0]
    
    @pytest.mark.asyncio
    async def test_start_no_mounts(self, mount_manager):
        """Test starting manager with no mounts configured."""
        result = await mount_manager.start()
        
        assert result is False
        assert mount_manager.running is False
    
    @pytest.mark.asyncio
    async def test_start_with_mounts(self, mount_manager, test_mounts):
        """Test starting manager with configured mounts."""
        mount_manager.add_mount(test_mounts[0], priority=1)
        
        with patch.object(mount_manager, '_connect_best_mount', return_value=True) as mock_connect:
            result = await mount_manager.start()
            
            assert result is True
            assert mount_manager.running is True
            mock_connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop(self, mount_manager, test_mounts):
        """Test stopping manager."""
        mount_manager.add_mount(test_mounts[0], priority=1)
        mount_manager.running = True
        
        with patch.object(mount_manager, '_disconnect_active') as mock_disconnect:
            await mount_manager.stop()
            
            assert mount_manager.running is False
            mock_disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_best_mount_success(self, mount_manager, test_mounts):
        """Test connecting to best available mount."""
        mount_manager.add_mount(test_mounts[0], priority=1)
        mount_manager.add_mount(test_mounts[1], priority=2)
        
        with patch.object(mount_manager, '_attempt_connection', return_value=True) as mock_attempt:
            result = await mount_manager._connect_best_mount()
            
            assert result is True
            # Should try highest priority mount first
            mock_attempt.assert_called_once_with(mount_manager.mounts[0])
    
    @pytest.mark.asyncio
    async def test_connect_best_mount_with_failures(self, mount_manager, test_mounts):
        """Test connecting with some mounts having failures."""
        mount_manager.add_mount(test_mounts[0], priority=1)
        mount_manager.add_mount(test_mounts[1], priority=2)
        
        # Set first mount as failed
        mount_manager.mounts[0].consecutive_failures = mount_manager.max_consecutive_failures
        
        with patch.object(mount_manager, '_attempt_connection', return_value=True) as mock_attempt:
            result = await mount_manager._connect_best_mount()
            
            assert result is True
            # Should try second mount (first is failed)
            mock_attempt.assert_called_once_with(mount_manager.mounts[1])
    
    @pytest.mark.asyncio
    async def test_attempt_connection_success(self, mount_manager, test_mounts):
        """Test successful connection attempt."""
        mount_status = MountStatus(mount=test_mounts[0])
        
        with patch('src.ntrip.mount_manager.NTRIPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect.return_value = True
            mock_client_class.return_value = mock_client
            
            result = await mount_manager._attempt_connection(mount_status)
            
            assert result is True
            assert mount_status.connected is True
            assert mount_status.consecutive_failures == 0
            assert mount_manager.active_mount == mount_status
            assert mount_manager.active_client == mock_client
    
    @pytest.mark.asyncio
    async def test_attempt_connection_failure(self, mount_manager, test_mounts):
        """Test failed connection attempt."""
        mount_status = MountStatus(mount=test_mounts[0])
        
        with patch('src.ntrip.mount_manager.NTRIPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.connect.return_value = False
            mock_client_class.return_value = mock_client
            
            result = await mount_manager._attempt_connection(mount_status)
            
            assert result is False
            assert mount_status.connected is False
            assert mount_status.consecutive_failures == 1
            assert mount_manager.active_mount is None
            assert mount_manager.active_client is None
    
    def test_correction_received(self, mount_manager, test_mounts, correction_callback):
        """Test handling of received correction data."""
        mount_status = MountStatus(mount=test_mounts[0])
        mount_manager.active_mount = mount_status
        
        rtcm_data = b'\xd3\x00\x13test_rtcm_data'
        
        mount_manager._correction_received(rtcm_data)
        
        assert mount_status.total_bytes == len(rtcm_data)
        assert mount_status.total_corrections == 1
        assert mount_status.last_data_time is not None
        correction_callback.assert_called_once_with(rtcm_data)
    
    def test_correction_received_callback_error(self, mount_manager, test_mounts, correction_callback):
        """Test handling of callback error during correction processing."""
        mount_status = MountStatus(mount=test_mounts[0])
        mount_manager.active_mount = mount_status
        correction_callback.side_effect = Exception("Callback error")
        
        rtcm_data = b'\xd3\x00\x13test_rtcm_data'
        
        # Should not raise exception
        mount_manager._correction_received(rtcm_data)
        
        # Statistics should still be updated
        assert mount_status.total_bytes == len(rtcm_data)
        assert mount_status.total_corrections == 1
    
    @pytest.mark.asyncio
    async def test_health_check_no_active_connection(self, mount_manager, test_mounts):
        """Test health check when no active connection exists."""
        mount_manager.add_mount(test_mounts[0], priority=1)
        
        with patch.object(mount_manager, '_connect_best_mount') as mock_connect:
            await mount_manager._check_connection_health()
            
            mock_connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_connection_lost(self, mount_manager, test_mounts):
        """Test health check when active connection is lost."""
        mount_status = MountStatus(mount=test_mounts[0])
        mount_manager.active_mount = mount_status
        
        mock_client = Mock()
        mock_client.connected = False
        mount_manager.active_client = mock_client
        
        with patch.object(mount_manager, '_handle_failover') as mock_failover:
            await mount_manager._check_connection_health()
            
            mock_failover.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_data_timeout(self, mount_manager, test_mounts):
        """Test health check with data timeout."""
        import time
        
        mount_status = MountStatus(mount=test_mounts[0])
        mount_status.last_data_time = time.time() - 200  # Old data
        mount_manager.active_mount = mount_status
        mount_manager.data_timeout = 120  # 2 minutes
        
        mock_client = Mock()
        mock_client.connected = True
        mount_manager.active_client = mock_client
        
        with patch.object(mount_manager, '_handle_failover') as mock_failover:
            await mount_manager._check_connection_health()
            
            mock_failover.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_failover(self, mount_manager, test_mounts):
        """Test failover handling."""
        mount_status = MountStatus(mount=test_mounts[0])
        mount_manager.active_mount = mount_status
        
        with patch.object(mount_manager, '_disconnect_active') as mock_disconnect, \
             patch.object(mount_manager, '_connect_best_mount') as mock_connect:
            
            await mount_manager._handle_failover()
            
            assert mount_status.consecutive_failures == 1
            mock_disconnect.assert_called_once()
            mock_connect.assert_called_once()
    
    def test_get_active_mount(self, mount_manager, test_mounts):
        """Test getting active mount information."""
        mount_status = MountStatus(mount=test_mounts[0])
        mount_status.connected = True
        mount_status.total_bytes = 1024
        mount_manager.active_mount = mount_status
        
        active_info = mount_manager.get_active_mount()
        
        assert active_info is not None
        assert active_info['host'] == test_mounts[0].host
        assert active_info['mount'] == test_mounts[0].mount
        assert active_info['connected'] is True
        assert active_info['total_bytes'] == 1024
    
    def test_get_active_mount_none(self, mount_manager):
        """Test getting active mount when none is active."""
        active_info = mount_manager.get_active_mount()
        assert active_info is None
    
    def test_get_manager_status(self, mount_manager, test_mounts):
        """Test getting overall manager status."""
        mount_manager.add_mount(test_mounts[0], priority=1)
        mount_manager.add_mount(test_mounts[1], priority=2)
        mount_manager.running = True
        
        # Set one mount as failed
        mount_manager.mounts[1].consecutive_failures = mount_manager.max_consecutive_failures
        
        status = mount_manager.get_manager_status()
        
        assert status['running'] is True
        assert status['total_mounts'] == 2
        assert status['enabled_mounts'] == 2  # Both enabled by default
        assert status['failed_mounts'] == 1   # One has failures
    
    @pytest.mark.asyncio
    async def test_retry_failed_mounts(self, mount_manager, test_mounts):
        """Test resetting failure counts after retry delay."""
        import time
        
        mount_status = MountStatus(mount=test_mounts[0])
        mount_status.consecutive_failures = mount_manager.max_consecutive_failures
        mount_status.last_attempt = time.time() - 40  # 40 seconds ago
        mount_manager.mounts.append(mount_status)
        mount_manager.retry_delay = 30  # 30 seconds
        
        await mount_manager._retry_failed_mounts()
        
        assert mount_status.consecutive_failures == 0


class TestMountStatus:
    """Test mount status data structure."""
    
    def test_mount_status_initialization(self, test_mounts):
        """Test MountStatus initialization."""
        mount = test_mounts[0]
        status = MountStatus(mount=mount, priority=5)
        
        assert status.mount == mount
        assert status.connected is False
        assert status.last_attempt is None
        assert status.consecutive_failures == 0
        assert status.total_bytes == 0
        assert status.total_corrections == 0
        assert status.last_data_time is None
        assert status.priority == 5
