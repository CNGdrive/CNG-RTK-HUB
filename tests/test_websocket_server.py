"""
Tests for WebSocket server functionality.
Testing real-time data streaming and client management.
"""

import pytest
import asyncio
import json
import websockets
from src.api.websocket_server import WebSocketServer
from src.core.interfaces import GNSSState, FixType


@pytest.mark.asyncio
async def test_websocket_server_startup_shutdown():
    """Test WebSocket server startup and shutdown."""
    server = WebSocketServer("localhost", 8766)  # Use different port for testing
    
    # Start server
    await server.start()
    assert server.running is True
    assert server.server is not None
    
    # Stop server
    await server.stop()
    assert server.running is False


@pytest.mark.asyncio
async def test_client_connection_and_welcome():
    """Test client connection and welcome message."""
    server = WebSocketServer("localhost", 8767)
    
    try:
        await server.start()
        
        # Connect client
        uri = f"ws://{server.host}:{server.port}"
        async with websockets.connect(uri) as websocket:
            # Should receive welcome message
            welcome_msg = await websocket.recv()
            data = json.loads(welcome_msg)
            
            assert data["type"] == "connection_established"
            assert data["payload"]["server"] == "CNG-RTK-HUB"
            assert data["payload"]["version"] == "0.1.0"
            assert len(server.clients) == 1
            
    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_ping_pong():
    """Test ping-pong message handling."""
    server = WebSocketServer("localhost", 8768)
    
    try:
        await server.start()
        
        uri = f"ws://{server.host}:{server.port}"
        async with websockets.connect(uri) as websocket:
            # Consume welcome message
            await websocket.recv()
            
            # Send ping
            ping_msg = {"type": "ping"}
            await websocket.send(json.dumps(ping_msg))
            
            # Should receive pong
            pong_msg = await websocket.recv()
            data = json.loads(pong_msg)
            
            assert data["type"] == "pong"
            assert "timestamp" in data["payload"]
            
    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_gnss_state_broadcast():
    """Test GNSS state broadcasting to clients."""
    server = WebSocketServer("localhost", 8769)
    
    try:
        await server.start()
        
        # Create test GNSS state
        test_state = GNSSState(
            timestamp_utc="2025-08-25T14:30:15.123Z",
            fix_type=FixType.FIX,
            latitude=37.7749,
            longitude=-122.4194,
            altitude_m=10.5,
            accuracy_m=0.5,
            sats={"GPS": 8},
            pdop=1.2,
            baseline_m=100.0,
            correction_source="NTRIP",
            receiver_meta={"model": "ZED-F9P"}
        )
        
        uri = f"ws://{server.host}:{server.port}"
        async with websockets.connect(uri) as websocket:
            # Consume welcome message
            await websocket.recv()
            
            # Broadcast GNSS state
            await server.broadcast_gnss_state(test_state, "test_receiver")
            
            # Should receive position update
            update_msg = await websocket.recv()
            data = json.loads(update_msg)
            
            assert data["type"] == "position_update"
            assert data["payload"]["receiver_id"] == "test_receiver"
            assert data["payload"]["state"]["fix_type"] == "FIX"
            assert data["payload"]["state"]["latitude"] == 37.7749
            assert data["payload"]["state"]["longitude"] == -122.4194
            
    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_multiple_clients():
    """Test broadcasting to multiple clients."""
    server = WebSocketServer("localhost", 8770)
    
    try:
        await server.start()
        
        # Connect multiple clients
        uri = f"ws://{server.host}:{server.port}"
        
        async with websockets.connect(uri) as client1, \
                   websockets.connect(uri) as client2:
            
            # Consume welcome messages
            await client1.recv()
            await client2.recv()
            
            assert len(server.clients) == 2
            
            # Create test state
            test_state = GNSSState(
                timestamp_utc="2025-08-25T14:30:15.123Z",
                fix_type=FixType.FLOAT,
                latitude=37.7749,
                longitude=-122.4194,
                altitude_m=10.5,
                accuracy_m=0.5,
                sats={"GPS": 8},
                pdop=1.2,
                baseline_m=100.0,
                correction_source="NTRIP",
                receiver_meta={"model": "UM980"}
            )
            
            # Broadcast to all clients
            await server.broadcast_gnss_state(test_state, "multi_test")
            
            # Both clients should receive the message
            msg1 = await client1.recv()
            msg2 = await client2.recv()
            
            data1 = json.loads(msg1)
            data2 = json.loads(msg2)
            
            assert data1["type"] == "position_update"
            assert data2["type"] == "position_update"
            assert data1["payload"]["receiver_id"] == "multi_test"
            assert data2["payload"]["receiver_id"] == "multi_test"
            
    finally:
        await server.stop()


@pytest.mark.asyncio
async def test_invalid_message_handling():
    """Test handling of invalid client messages."""
    server = WebSocketServer("localhost", 8771)
    
    try:
        await server.start()
        
        uri = f"ws://{server.host}:{server.port}"
        async with websockets.connect(uri) as websocket:
            # Consume welcome message
            await websocket.recv()
            
            # Send invalid JSON
            await websocket.send("invalid json")
            
            # Should receive error message
            error_msg = await websocket.recv()
            data = json.loads(error_msg)
            
            assert data["type"] == "error"
            assert "Invalid JSON format" in data["payload"]["message"]
            
    finally:
        await server.stop()


def test_gnss_state_to_dict_conversion():
    """Test GNSSState to dictionary conversion."""
    server = WebSocketServer()
    
    state = GNSSState(
        timestamp_utc="2025-08-25T14:30:15.123Z",
        fix_type=FixType.FIX,
        latitude=37.7749,
        longitude=-122.4194,
        altitude_m=10.5,
        accuracy_m=0.5,
        sats={"GPS": 8},
        pdop=1.2,
        baseline_m=100.0,
        correction_source="NTRIP",
        receiver_meta={"model": "ZED-F9P"}
    )
    
    state_dict = server._gnss_state_to_dict(state)
    
    # Check that FixType enum is converted to string
    assert state_dict["fix_type"] == "FIX"
    assert state_dict["latitude"] == 37.7749
    assert state_dict["longitude"] == -122.4194
    assert isinstance(state_dict["sats"], dict)
