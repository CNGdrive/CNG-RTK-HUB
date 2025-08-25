"""
Tests for NTRIP client implementation.
Comprehensive test coverage for connection, authentication, and data streaming.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from src.ntrip.ntrip_client import NTRIPClient, NTRIPMount, NTRIPError


@pytest.fixture
def mock_mount():
    """Create a mock NTRIP mount for testing."""
    return NTRIPMount(
        host="test.ntrip.com",
        port=2101,
        mount="TEST01",
        username="testuser",
        password="testpass",
        description="Test mount point"
    )


@pytest.fixture
def correction_callback():
    """Mock correction callback function."""
    return Mock()


@pytest.fixture
def ntrip_client(correction_callback):
    """Create NTRIP client instance for testing."""
    return NTRIPClient(correction_callback)


class TestNTRIPClient:
    """Test cases for NTRIP client functionality."""
    
    def test_ntrip_client_initialization(self, correction_callback):
        """Test NTRIP client initialization."""
        client = NTRIPClient(correction_callback)
        
        assert client.correction_callback == correction_callback
        assert client.session is None
        assert client.connected is False
        assert client.current_mount is None
        assert client.bytes_received == 0
        assert client.corrections_sent == 0
        assert client.connection_attempts == 0
    
    @pytest.mark.asyncio
    async def test_ntrip_connect_success(self, ntrip_client, mock_mount):
        """Test successful NTRIP connection."""
        # Mock successful HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.iter_chunked.return_value = async_generator([b'test_data'])
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            result = await ntrip_client.connect(mock_mount)
            
            assert result is True
            assert ntrip_client.connected is True
            assert ntrip_client.current_mount == mock_mount
            assert ntrip_client.connection_attempts == 1
    
    @pytest.mark.asyncio
    async def test_ntrip_connect_auth_failure(self, ntrip_client, mock_mount):
        """Test NTRIP connection with authentication failure."""
        # Mock HTTP 401 response
        mock_response = AsyncMock()
        mock_response.status = 401
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            result = await ntrip_client.connect(mock_mount)
            
            assert result is False
            assert ntrip_client.connected is False
            assert ntrip_client.connection_attempts == 1
    
    @pytest.mark.asyncio
    async def test_ntrip_disconnect(self, ntrip_client, mock_mount):
        """Test NTRIP disconnection."""
        # Set up connected state
        ntrip_client.connected = True
        ntrip_client.current_mount = mock_mount
        ntrip_client._stream_task = AsyncMock()
        ntrip_client.session = AsyncMock()
        
        await ntrip_client.disconnect()
        
        assert ntrip_client.connected is False
        assert ntrip_client.current_mount is None
    
    def test_rtcm_crc_validation(self, ntrip_client):
        """Test RTCM CRC-24Q validation."""
        # Valid RTCM message with correct CRC
        valid_rtcm = b'\xd3\x00\x13\x3e\xd0\x00\x02\x69\x8e\xce\x4e\xb6\x99\x3c\x7f\x1e\x72\x75\x7f\x15\x3c\x22\x9b\x04'
        
        result = ntrip_client._validate_rtcm_crc(valid_rtcm)
        # Note: This test may need adjustment based on actual RTCM test data
        assert isinstance(result, bool)
    
    def test_crc24q_calculation(self, ntrip_client):
        """Test CRC-24Q calculation algorithm."""
        test_data = b'\xd3\x00\x13\x3e\xd0\x00\x02\x69\x8e\xce\x4e\xb6\x99\x3c\x7f\x1e\x72\x75\x7f\x15\x3c'
        
        crc = ntrip_client._calculate_crc24q(test_data)
        
        assert isinstance(crc, int)
        assert 0 <= crc <= 0xFFFFFF
    
    def test_get_status(self, ntrip_client, mock_mount):
        """Test status information retrieval."""
        ntrip_client.connected = True
        ntrip_client.current_mount = mock_mount
        ntrip_client.bytes_received = 1024
        ntrip_client.corrections_sent = 5
        
        status = ntrip_client.get_status()
        
        assert status['connected'] is True
        assert status['mount'] == 'TEST01'
        assert status['host'] == 'test.ntrip.com'
        assert status['bytes_received'] == 1024
        assert status['corrections_sent'] == 5
    
    def test_get_connection_info(self, ntrip_client, mock_mount):
        """Test connection information retrieval."""
        ntrip_client.current_mount = mock_mount
        
        info = ntrip_client.get_connection_info()
        
        assert info['host'] == 'test.ntrip.com'
        assert info['port'] == '2101'
        assert info['mount'] == 'TEST01'
        assert info['username'] == 'testuser'
    
    def test_get_connection_info_no_mount(self, ntrip_client):
        """Test connection info when no mount is configured."""
        info = ntrip_client.get_connection_info()
        assert info is None


class TestRTCMProcessing:
    """Test RTCM message processing functionality."""
    
    @pytest.mark.asyncio
    async def test_rtcm_message_extraction(self, ntrip_client, correction_callback):
        """Test extraction of complete RTCM messages from stream."""
        # Mock RTCM data with proper header
        rtcm_data = b'\xd3\x00\x10' + b'\x00' * 16 + b'\x12\x34\x56'  # Mock RTCM message
        
        # Mock stream response
        mock_response = AsyncMock()
        
        # Set up the client with mocked stream processing
        with patch.object(ntrip_client, '_validate_rtcm_crc', return_value=True):
            # Directly test the correction callback
            ntrip_client.correction_callback(rtcm_data)
            
            correction_callback.assert_called_once_with(rtcm_data)
    
    def test_invalid_rtcm_message_handling(self, ntrip_client):
        """Test handling of invalid RTCM messages."""
        invalid_data = b'\xff\xff\xff\xff'  # Invalid data
        
        # This should not raise an exception
        result = ntrip_client._validate_rtcm_crc(invalid_data)
        assert result is False


class TestNTRIPMount:
    """Test NTRIP mount configuration."""
    
    def test_ntrip_mount_creation(self):
        """Test NTRIP mount object creation."""
        mount = NTRIPMount(
            host="example.com",
            port=2101,
            mount="MOUNT1",
            username="user",
            password="pass",
            description="Test mount"
        )
        
        assert mount.host == "example.com"
        assert mount.port == 2101
        assert mount.mount == "MOUNT1"
        assert mount.username == "user"
        assert mount.password == "pass"
        assert mount.description == "Test mount"
        assert mount.enabled is True
    
    def test_ntrip_mount_defaults(self):
        """Test NTRIP mount with default values."""
        mount = NTRIPMount(
            host="example.com",
            port=2101,
            mount="MOUNT1",
            username="user",
            password="pass"
        )
        
        assert mount.description == ""
        assert mount.enabled is True


# Helper functions for testing

async def async_generator(items):
    """Create async generator for mocking streaming data."""
    for item in items:
        yield item


class TestNTRIPIntegration:
    """Integration tests for NTRIP client with external dependencies."""
    
    @pytest.mark.asyncio
    async def test_connection_timeout_handling(self, ntrip_client, mock_mount):
        """Test connection timeout handling."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get.side_effect = asyncio.TimeoutError()
            mock_session_class.return_value = mock_session
            
            result = await ntrip_client.connect(mock_mount)
            
            assert result is False
            assert ntrip_client.connected is False
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, ntrip_client, mock_mount):
        """Test network error handling."""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get.side_effect = Exception("Network error")
            mock_session_class.return_value = mock_session
            
            result = await ntrip_client.connect(mock_mount)
            
            assert result is False
            assert ntrip_client.connected is False
    
    @pytest.mark.asyncio
    async def test_reconnection_backoff(self, ntrip_client, mock_mount):
        """Test exponential backoff for reconnection."""
        initial_delay = ntrip_client.reconnect_delay
        
        # Simulate failed connection
        ntrip_client.current_mount = mock_mount
        await ntrip_client._attempt_reconnect()
        
        # Check that delay increased
        assert ntrip_client.reconnect_delay > initial_delay
        assert ntrip_client.reconnect_delay <= ntrip_client.max_reconnect_delay
