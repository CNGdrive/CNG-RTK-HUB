"""
WebSocket server for real-time GNSS data streaming.
Implementation follows ARCHITECTURE_DECISIONS.md specifications.
"""

import asyncio
import json
import logging
import weakref
from typing import Set, Optional, Dict, Any
from dataclasses import asdict
import websockets
from websockets.server import WebSocketServerProtocol
from ..core.interfaces import GNSSState


class WebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.server = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
    async def start(self) -> None:
        """Start the WebSocket server."""
        self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        self.running = True
        
    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Close all client connections
        if self.clients:
            await asyncio.gather(
                *[client.close() for client in self.clients],
                return_exceptions=True
            )
        self.clients.clear()
        
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket client connection."""
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        self.logger.info(f"Client connected: {client_addr}")
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "connection_established",
                "payload": {
                    "server": "CNG-RTK-HUB",
                    "version": "0.1.0",
                    "timestamp": self._get_timestamp()
                }
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Handle client messages
            async for message in websocket:
                try:
                    await self._handle_client_message(websocket, message)
                except json.JSONDecodeError:
                    await self._send_error(websocket, "Invalid JSON format")
                except Exception as e:
                    self.logger.error(f"Error handling client message: {e}")
                    await self._send_error(websocket, "Internal server error")
                    
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"Client disconnected: {client_addr}")
        except Exception as e:
            self.logger.error(f"Client handler error: {e}")
        finally:
            self.clients.discard(websocket)
            
    async def _handle_client_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming client message."""
        data = json.loads(message)
        msg_type = data.get("type")
        
        if msg_type == "ping":
            await websocket.send(json.dumps({
                "type": "pong",
                "payload": {"timestamp": self._get_timestamp()}
            }))
        elif msg_type == "get_status":
            await self._send_status(websocket)
        else:
            await self._send_error(websocket, f"Unknown message type: {msg_type}")
            
    async def _send_error(self, websocket: WebSocketServerProtocol, error_msg: str):
        """Send error message to client."""
        error_response = {
            "type": "error",
            "payload": {
                "message": error_msg,
                "timestamp": self._get_timestamp()
            }
        }
        await websocket.send(json.dumps(error_response))
        
    async def _send_status(self, websocket: WebSocketServerProtocol):
        """Send server status to client."""
        status_response = {
            "type": "status",
            "payload": {
                "clients_connected": len(self.clients),
                "server_running": self.running,
                "timestamp": self._get_timestamp()
            }
        }
        await websocket.send(json.dumps(status_response))
        
    async def broadcast_gnss_state(self, state: GNSSState, receiver_id: str = "default"):
        """Broadcast GNSS state to all connected clients."""
        if not self.clients:
            return
            
        message = {
            "type": "position_update",
            "payload": {
                "receiver_id": receiver_id,
                "state": self._gnss_state_to_dict(state),
                "timestamp": self._get_timestamp()
            }
        }
        
        # Broadcast to all clients
        disconnected_clients = set()
        for client in self.clients.copy():
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)
                
        # Remove disconnected clients
        self.clients -= disconnected_clients
        
    def _gnss_state_to_dict(self, state: GNSSState) -> Dict[str, Any]:
        """Convert GNSSState to dictionary for JSON serialization."""
        state_dict = asdict(state)
        # Convert FixType enum to string value
        state_dict['fix_type'] = state.fix_type.value
        return state_dict
        
    def _get_timestamp(self) -> str:
        """Get current UTC timestamp in ISO8601 format."""
        import datetime
        return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
        
    @property
    def client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)
