"""
HTTP REST API server for GNSS receiver configuration and status.
Provides RESTful endpoints for driver management and system control.
"""

import json
import logging
from typing import Dict, Any
from aiohttp import web, web_response
from ..core.driver_manager import DriverManager, ReceiverType


class HTTPServer:
    def __init__(self, driver_manager: DriverManager, host: str = "localhost", port: int = 8080):
        self.driver_manager = driver_manager
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.logger = logging.getLogger(__name__)
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup HTTP API routes."""
        self.app.router.add_get('/api/status', self.get_system_status)
        self.app.router.add_get('/api/drivers', self.get_drivers_status)
        self.app.router.add_post('/api/drivers', self.add_driver)
        self.app.router.add_delete('/api/drivers/{driver_id}', self.remove_driver)
        self.app.router.add_post('/api/drivers/{driver_id}/connect', self.connect_driver)
        self.app.router.add_post('/api/drivers/{driver_id}/disconnect', self.disconnect_driver)
        self.app.router.add_post('/api/drivers/{driver_id}/corrections', self.inject_corrections)
        self.app.router.add_post('/api/streams/start', self.start_streams)
        self.app.router.add_post('/api/streams/stop', self.stop_streams)
        
        # Health check endpoint
        self.app.router.add_get('/health', self.health_check)
        
    async def start(self) -> None:
        """Start the HTTP server."""
        self.logger.info(f"Starting HTTP server on {self.host}:{self.port}")
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
    async def stop(self) -> None:
        """Stop the HTTP server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
            
    async def health_check(self, request: web.Request) -> web_response.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "service": "CNG-RTK-HUB",
            "version": "0.1.0"
        })
        
    async def get_system_status(self, request: web.Request) -> web_response.Response:
        """Get overall system status."""
        try:
            driver_status = self.driver_manager.get_all_status()
            
            response = {
                "status": "running",
                "drivers_count": len(driver_status),
                "max_drivers": self.driver_manager.MAX_DRIVERS,
                "memory_limit_per_driver_mb": self.driver_manager.MAX_MEMORY_PER_DRIVER_MB,
                "drivers": driver_status
            }
            
            return web.json_response(response)
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def get_drivers_status(self, request: web.Request) -> web_response.Response:
        """Get status of all drivers."""
        try:
            return web.json_response(self.driver_manager.get_all_status())
        except Exception as e:
            self.logger.error(f"Error getting drivers status: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def add_driver(self, request: web.Request) -> web_response.Response:
        """Add a new driver."""
        try:
            data = await request.json()
            
            # Validate required fields
            required_fields = ['driver_id', 'receiver_type', 'port']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {"error": f"Missing required field: {field}"},
                        status=400
                    )
                    
            driver_id = data['driver_id']
            receiver_type_str = data['receiver_type'].upper()
            port = data['port']
            baudrate = data.get('baudrate', 115200)
            
            # Validate receiver type
            try:
                receiver_type = ReceiverType[receiver_type_str]
            except KeyError:
                return web.json_response(
                    {"error": f"Invalid receiver type: {receiver_type_str}"},
                    status=400
                )
                
            success = self.driver_manager.add_driver(
                driver_id, receiver_type, port, baudrate
            )
            
            if success:
                return web.json_response({
                    "message": f"Driver {driver_id} added successfully",
                    "driver_id": driver_id
                }, status=201)
            else:
                return web.json_response(
                    {"error": "Failed to add driver"},
                    status=400
                )
                
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            self.logger.error(f"Error adding driver: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def remove_driver(self, request: web.Request) -> web_response.Response:
        """Remove a driver."""
        try:
            driver_id = request.match_info['driver_id']
            
            success = self.driver_manager.remove_driver(driver_id)
            
            if success:
                return web.json_response({
                    "message": f"Driver {driver_id} removed successfully"
                })
            else:
                return web.json_response(
                    {"error": f"Driver {driver_id} not found"},
                    status=404
                )
                
        except Exception as e:
            self.logger.error(f"Error removing driver: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def connect_driver(self, request: web.Request) -> web_response.Response:
        """Connect a driver."""
        try:
            driver_id = request.match_info['driver_id']
            
            success = await self.driver_manager.connect_driver(driver_id)
            
            if success:
                return web.json_response({
                    "message": f"Driver {driver_id} connected successfully"
                })
            else:
                return web.json_response(
                    {"error": f"Failed to connect driver {driver_id}"},
                    status=400
                )
                
        except Exception as e:
            self.logger.error(f"Error connecting driver: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def disconnect_driver(self, request: web.Request) -> web_response.Response:
        """Disconnect a driver."""
        try:
            driver_id = request.match_info['driver_id']
            
            success = await self.driver_manager._disconnect_driver(driver_id)
            
            if success:
                return web.json_response({
                    "message": f"Driver {driver_id} disconnected successfully"
                })
            else:
                return web.json_response(
                    {"error": f"Failed to disconnect driver {driver_id}"},
                    status=400
                )
                
        except Exception as e:
            self.logger.error(f"Error disconnecting driver: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def inject_corrections(self, request: web.Request) -> web_response.Response:
        """Inject RTCM corrections to a driver."""
        try:
            driver_id = request.match_info['driver_id']
            
            # Read raw bytes from request body
            rtcm_data = await request.read()
            
            if not rtcm_data:
                return web.json_response(
                    {"error": "No RTCM data provided"},
                    status=400
                )
                
            success = self.driver_manager.inject_corrections(driver_id, rtcm_data)
            
            if success:
                return web.json_response({
                    "message": f"RTCM corrections injected to {driver_id}",
                    "bytes_injected": len(rtcm_data)
                })
            else:
                return web.json_response(
                    {"error": f"Failed to inject corrections to {driver_id}"},
                    status=400
                )
                
        except Exception as e:
            self.logger.error(f"Error injecting corrections: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def start_streams(self, request: web.Request) -> web_response.Response:
        """Start data streams for all connected drivers."""
        try:
            success = await self.driver_manager.start_all_streams()
            
            if success:
                return web.json_response({
                    "message": "Data streams started"
                })
            else:
                return web.json_response(
                    {"error": "Failed to start streams"},
                    status=400
                )
                
        except Exception as e:
            self.logger.error(f"Error starting streams: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
            
    async def stop_streams(self, request: web.Request) -> web_response.Response:
        """Stop all data streams."""
        try:
            await self.driver_manager.stop_all_streams()
            
            return web.json_response({
                "message": "Data streams stopped"
            })
            
        except Exception as e:
            self.logger.error(f"Error stopping streams: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
