"""
Main RTK service coordinator.
Integrates WebSocket server, HTTP API, and driver manager for real-time operation.
"""

import asyncio
import logging
import signal
from typing import Optional
from src.api.websocket_server import WebSocketServer
from src.api.http_server import HTTPServer
from src.core.driver_manager import DriverManager, ReceiverType
from src.core.interfaces import GNSSState


class RTKService:
    """
    Main service coordinator for RTK client.
    Manages WebSocket streaming, HTTP API, and dual receivers.
    """
    
    def __init__(self, 
                 websocket_host: str = "localhost", 
                 websocket_port: int = 8765,
                 http_host: str = "localhost", 
                 http_port: int = 8080):
        
        # Core components
        self.driver_manager = DriverManager()
        self.websocket_server = WebSocketServer(websocket_host, websocket_port)
        self.http_server = HTTPServer(self.driver_manager, http_host, http_port)
        
        # State
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Setup callbacks
        self.driver_manager.add_state_callback(self._on_gnss_state_update)
        
        # Setup NTRIP integration
        self._setup_ntrip_integration()
        
    async def start(self) -> None:
        """Start all services."""
        self.logger.info("Starting RTK service...")
        
        try:
            # Start servers
            await self.websocket_server.start()
            await self.http_server.start()
            
            self.running = True
            self.logger.info("RTK service started successfully")
            
            # Log service endpoints
            self.logger.info(f"WebSocket server: ws://{self.websocket_server.host}:{self.websocket_server.port}")
            self.logger.info(f"HTTP API server: http://{self.http_server.host}:{self.http_server.port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start RTK service: {e}")
            await self.stop()
            raise
            
    async def stop(self) -> None:
        """Stop all services."""
        self.logger.info("Stopping RTK service...")
        
        self.running = False
        
        # Stop all streams first
        await self.driver_manager.stop_all_streams()
        
        # Stop servers
        await self.websocket_server.stop()
        await self.http_server.stop()
        
        self.logger.info("RTK service stopped")
        
    async def _on_gnss_state_update(self, driver_id: str, state: GNSSState) -> None:
        """Handle GNSS state updates from drivers."""
        try:
            # Broadcast to WebSocket clients
            await self.websocket_server.broadcast_gnss_state(state, driver_id)
            
            # Log significant state changes
            if state.fix_type.value in ["FIX", "FLOAT"]:
                self.logger.debug(f"{driver_id}: {state.fix_type.value} - "
                                f"Lat: {state.latitude:.7f}, Lon: {state.longitude:.7f}, "
                                f"Acc: {state.accuracy_m:.2f}m")
                                
        except Exception as e:
            self.logger.error(f"Error handling state update from {driver_id}: {e}")
            
    def add_receiver(self, driver_id: str, receiver_type: ReceiverType, 
                    port: str, baudrate: int = 115200) -> bool:
        """Add a GNSS receiver to the system."""
        return self.driver_manager.add_driver(driver_id, receiver_type, port, baudrate)
        
    async def connect_receiver(self, driver_id: str) -> bool:
        """Connect a specific receiver."""
        return await self.driver_manager.connect_driver(driver_id)
        
    async def start_data_streams(self) -> bool:
        """Start data streaming from all connected receivers."""
        return await self.driver_manager.start_all_streams()
        
    def get_status(self) -> dict:
        """Get overall system status."""
        return {
            "service_running": self.running,
            "websocket_clients": self.websocket_server.client_count,
            "drivers": self.driver_manager.get_all_status(),
            "ntrip": self.driver_manager.get_ntrip_status()
        }
        
    async def run_forever(self) -> None:
        """Run the service until interrupted."""
        # Setup signal handlers for graceful shutdown
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._signal_handler)
            
        try:
            await self.start()
            
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Service error: {e}")
        finally:
            await self.stop()
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        
    def _setup_ntrip_integration(self) -> None:
        """Setup NTRIP integration between driver manager and WebSocket server."""
        try:
            # Initialize NTRIP manager in driver manager
            self.driver_manager.setup_ntrip()
            
            # Set WebSocket server for NTRIP status broadcasting
            self.driver_manager.set_websocket_server(self.websocket_server)
            
            self.logger.info("NTRIP integration setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup NTRIP integration: {e}")
            
    def add_ntrip_mount(self, host: str, port: int, mount: str, 
                       username: str, password: str, priority: int = 0,
                       description: str = "") -> bool:
        """Add NTRIP mountpoint for corrections."""
        return self.driver_manager.add_ntrip_mount(
            host, port, mount, username, password, priority, description
        )
        
    async def start_ntrip_corrections(self) -> bool:
        """Start NTRIP correction streaming."""
        return await self.driver_manager.start_ntrip_corrections()
        
    async def stop_ntrip_corrections(self) -> bool:
        """Stop NTRIP correction streaming."""
        await self.driver_manager.stop_ntrip_corrections()
        return True
        
    def get_ntrip_status(self) -> dict:
        """Get NTRIP status and statistics."""
        return self.driver_manager.get_ntrip_status()
        
    def get_ntrip_mounts(self) -> list:
        """Get list of configured NTRIP mounts."""
        return self.driver_manager.get_ntrip_mounts()


async def main():
    """Main entry point for RTK service."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run service
    service = RTKService()
    
    # Example: Add receivers (commented out for now)
    # service.add_receiver("zedf9p", ReceiverType.ZED_F9P, "/dev/ttyUSB0")
    # service.add_receiver("um980", ReceiverType.UM980, "/dev/ttyUSB1")
    
    await service.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
