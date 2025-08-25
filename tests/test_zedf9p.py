"""
Tests for ZED-F9P driver and UBX protocol parsing.
Following testing patterns from IMPLEMENTATION_GUIDE.md
"""

import pytest
from src.drivers.zedf9p import parse_ubx_nav_pvt, validate_ubx_checksum, ZedF9PDriver
from src.core.interfaces import FixType, ProtocolError, ConnectionError


def test_ubx_checksum_validation():
    """Test UBX checksum validation function."""
    # Valid UBX message with correct checksum
    valid_ubx = b'\xb5\x62\x01\x07\x00\x08test\x12\x34'  # Simplified for test
    
    # Invalid UBX - too short
    assert validate_ubx_checksum(b'\xb5\x62') is False
    
    # Invalid UBX - wrong checksum
    invalid_ubx = b'\xb5\x62\x01\x07\x00\x08test\xFF\xFF'
    assert validate_ubx_checksum(invalid_ubx) is False


def test_ubx_nav_pvt_parsing():
    """Test UBX-NAV-PVT message parsing."""
    # Create a mock UBX-NAV-PVT message (simplified structure)
    # Real message would be 100 bytes, this is a test pattern
    ubx_data = bytearray(100)
    ubx_data[0:4] = b'\xb5\x62\x01\x07'  # UBX sync + class + ID
    
    # Set payload fields (little-endian)
    # Year, month, day, hour, minute, second
    ubx_data[10:12] = (2025).to_bytes(2, 'little')
    ubx_data[12] = 8  # August
    ubx_data[13] = 25  # 25th
    ubx_data[14] = 14  # 14 hours
    ubx_data[15] = 30  # 30 minutes
    ubx_data[16] = 15  # 15 seconds
    
    # Nano seconds
    ubx_data[22:26] = (123000000).to_bytes(4, 'little')
    
    # Fix type and carrier solution
    ubx_data[26] = 3  # 3D fix
    ubx_data[27] = 2  # RTK fixed
    
    # Position (lat/lon in 1e-7 degrees, height in mm)
    lat_int = int(37.7749 * 1e7)
    lon_int = int(-122.4194 * 1e7)
    height_int = int(10.5 * 1000)
    
    ubx_data[32:36] = lat_int.to_bytes(4, 'little', signed=True)
    ubx_data[36:40] = lon_int.to_bytes(4, 'little', signed=True)
    ubx_data[40:44] = height_int.to_bytes(4, 'little', signed=True)
    
    # Horizontal accuracy (mm)
    ubx_data[48:52] = int(500).to_bytes(4, 'little')  # 0.5m
    
    # Number of satellites
    ubx_data[29] = 12
    
    # PDOP (0.01 scale)
    ubx_data[82:84] = int(120).to_bytes(2, 'little')  # 1.20
    
    # Parse the message
    result = parse_ubx_nav_pvt(bytes(ubx_data))
    
    # Validate results
    assert result.fix_type == FixType.FIX  # RTK fixed
    assert abs(result.latitude - 37.7749) < 1e-6
    assert abs(result.longitude - (-122.4194)) < 1e-6
    assert abs(result.altitude_m - 10.5) < 0.01
    assert result.accuracy_m == 0.5
    assert result.sats["GPS"] == 12
    assert result.pdop == 1.2
    assert result.receiver_meta["model"] == "ZED-F9P"
    assert "2025-08-25T14:30:15.123Z" == result.timestamp_utc


def test_ubx_nav_pvt_error_handling():
    """Test UBX-NAV-PVT error handling."""
    # Message too short
    with pytest.raises(ProtocolError):
        parse_ubx_nav_pvt(b'\xb5\x62\x01\x07\x00\x08short')


def test_fix_type_mapping():
    """Test fix type mapping from UBX carrier solution."""
    # Create minimal valid message for different fix types
    base_msg = bytearray(100)
    base_msg[0:4] = b'\xb5\x62\x01\x07'
    
    # Set required timestamp fields
    base_msg[10:12] = (2025).to_bytes(2, 'little')
    base_msg[12:16] = bytes([8, 25, 14, 30])  # month, day, hour, minute
    
    # Test RTK fixed (carr_soln = 2)
    base_msg[27] = 2
    result = parse_ubx_nav_pvt(bytes(base_msg))
    assert result.fix_type == FixType.FIX
    
    # Test RTK float (carr_soln = 1)
    base_msg[27] = 1
    result = parse_ubx_nav_pvt(bytes(base_msg))
    assert result.fix_type == FixType.FLOAT
    
    # Test 3D fix (fix_type = 3, carr_soln = 0)
    base_msg[26] = 3
    base_msg[27] = 0
    result = parse_ubx_nav_pvt(bytes(base_msg))
    assert result.fix_type == FixType.DGPS


@pytest.mark.asyncio
async def test_zedf9p_driver_error_handling():
    """Test ZED-F9P driver error handling."""
    driver = ZedF9PDriver()
    
    # Test connection error
    with pytest.raises(ConnectionError):
        await driver.connect("invalid_port")
    
    # Test protocol error when not connected
    with pytest.raises(ProtocolError):
        await driver.start_data_stream()
