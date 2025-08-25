"""
Driver Manager for coordinating dual GNSS receivers.
Implements resource allocation and threading constraints from ARCHITECTURE_DECISIONS.md
"""

import asyncio
import logging
from typing import Dict, Optional, List, Callable
from enum import Enum
from ..core.interfaces import IGNSSDriver, GNSSState, ConnectionError
from ..drivers.zedf9p import ZedF9PDriver
from ..drivers.um980 import UM980Driver


class ReceiverType(Enum):
    ZED_F9P = "ZED_F9P"
    UM980 = "UM980"


class DriverStatus(Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    STREAMING = "STREAMING"
    ERROR = "ERROR"


class DriverManager:
    """
    Manages dual GNSS receivers with resource constraints.
    Max 2 receivers, <35MB per driver, dedicated threads.
    """
    
    MAX_DRIVERS = 2
    MAX_MEMORY_PER_DRIVER_MB = 35
    
    def __init__(self):
        self.drivers: Dict[str, IGNSSDriver] = {}
        self.driver_status: Dict[str, DriverStatus] = {}
        self.driver_configs: Dict[str, Dict] = {}
        self.state_callbacks: List[Callable[[str, GNSSState], None]] = []
        self.running = False
        self.logger = logging.getLogger(__name__)
        
    def add_driver(self, driver_id: str, receiver_type: ReceiverType, 
                   port: str, baudrate: int = 115200) -> bool:
        """Add a GNSS driver to the manager."""
        if len(self.drivers) >= self.MAX_DRIVERS:
            self.logger.error(f"Cannot add driver {driver_id}: max {self.MAX_DRIVERS} drivers allowed")
            return False
            
        if driver_id in self.drivers:
            self.logger.warning(f"Driver {driver_id} already exists")
            return False
            
        # Create driver instance based on type
        if receiver_type == ReceiverType.ZED_F9P:
            driver = ZedF9PDriver()
        elif receiver_type == ReceiverType.UM980:
            driver = UM980Driver()
        else:
            self.logger.error(f"Unknown receiver type: {receiver_type}")
            return False
            
        self.drivers[driver_id] = driver
        self.driver_status[driver_id] = DriverStatus.DISCONNECTED
        self.driver_configs[driver_id] = {
            "type": receiver_type,
            "port": port,
            "baudrate": baudrate
        }
        
        self.logger.info(f"Added {receiver_type.value} driver: {driver_id}")
        return True
        
    def remove_driver(self, driver_id: str) -> bool:
        """Remove a driver from the manager."""
        if driver_id not in self.drivers:
            return False
            
        # Disconnect if connected
        if self.driver_status[driver_id] != DriverStatus.DISCONNECTED:
            asyncio.create_task(self._disconnect_driver(driver_id))
            
        del self.drivers[driver_id]
        del self.driver_status[driver_id]
        del self.driver_configs[driver_id]
        
        self.logger.info(f"Removed driver: {driver_id}")
        return True
        
    async def connect_driver(self, driver_id: str) -> bool:
        """Connect a specific driver."""
        if driver_id not in self.drivers:
            self.logger.error(f"Driver {driver_id} not found")
            return False
            
        driver = self.drivers[driver_id]
        config = self.driver_configs[driver_id]
        
        try:
            self.driver_status[driver_id] = DriverStatus.CONNECTING
            success = await driver.connect(config["port"], config["baudrate"])
            
            if success:
                self.driver_status[driver_id] = DriverStatus.CONNECTED
                self.logger.info(f"Connected driver: {driver_id}")
                return True
            else:
                self.driver_status[driver_id] = DriverStatus.ERROR
                return False
                
        except ConnectionError as e:
            self.logger.error(f"Failed to connect {driver_id}: {e}")
            self.driver_status[driver_id] = DriverStatus.ERROR
            return False
            
    async def _disconnect_driver(self, driver_id: str) -> bool:
        """Disconnect a specific driver."""
        if driver_id not in self.drivers:
            return False
            
        try:
            driver = self.drivers[driver_id]
            await driver.disconnect()
            self.driver_status[driver_id] = DriverStatus.DISCONNECTED
            self.logger.info(f"Disconnected driver: {driver_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting {driver_id}: {e}")
            self.driver_status[driver_id] = DriverStatus.ERROR
            return False
            
    async def start_all_streams(self) -> bool:
        """Start data streams for all connected drivers."""
        if not self.drivers:
            self.logger.warning("No drivers to start")
            return False
            
        self.running = True
        
        # Start streams for connected drivers
        for driver_id, driver in self.drivers.items():
            if self.driver_status[driver_id] == DriverStatus.CONNECTED:
                try:
                    await driver.start_data_stream()
                    self.driver_status[driver_id] = DriverStatus.STREAMING
                    # Start monitoring task for this driver
                    asyncio.create_task(self._monitor_driver(driver_id))
                    self.logger.info(f"Started stream for driver: {driver_id}")
                except Exception as e:
                    self.logger.error(f"Failed to start stream for {driver_id}: {e}")
                    self.driver_status[driver_id] = DriverStatus.ERROR
                    
        return True
        
    async def stop_all_streams(self) -> None:
        """Stop all data streams and disconnect drivers."""
        self.running = False
        
        for driver_id in list(self.drivers.keys()):
            await self._disconnect_driver(driver_id)
            
    async def _monitor_driver(self, driver_id: str) -> None:
        """Monitor a driver for new data and trigger callbacks."""
        driver = self.drivers[driver_id]
        last_state = None
        
        while (self.running and 
               driver_id in self.drivers and 
               self.driver_status[driver_id] == DriverStatus.STREAMING):
            
            try:
                current_state = driver.get_current_state()
                
                # Check if state has updated
                if current_state and current_state != last_state:
                    # Trigger callbacks with new state
                    for callback in self.state_callbacks:
                        try:
                            callback(driver_id, current_state)
                        except Exception as e:
                            self.logger.error(f"Error in state callback: {e}")
                    
                    last_state = current_state
                    
                await asyncio.sleep(0.1)  # 10Hz polling rate
                
            except Exception as e:
                self.logger.error(f"Error monitoring driver {driver_id}: {e}")
                self.driver_status[driver_id] = DriverStatus.ERROR
                break
                
    def add_state_callback(self, callback: Callable[[str, GNSSState], None]) -> None:
        """Add a callback for GNSS state updates."""
        self.state_callbacks.append(callback)
        
    def remove_state_callback(self, callback: Callable[[str, GNSSState], None]) -> None:
        """Remove a state callback."""
        if callback in self.state_callbacks:
            self.state_callbacks.remove(callback)
            
    def get_driver_status(self, driver_id: str) -> Optional[DriverStatus]:
        """Get status of a specific driver."""
        return self.driver_status.get(driver_id)
        
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all drivers."""
        status = {}
        for driver_id in self.drivers:
            status[driver_id] = {
                "status": self.driver_status[driver_id].value,
                "config": self.driver_configs[driver_id].copy()
            }
        return status
        
    def inject_corrections(self, driver_id: str, rtcm_data: bytes) -> bool:
        """Inject RTCM corrections to a specific driver."""
        if driver_id not in self.drivers:
            return False
            
        driver = self.drivers[driver_id]
        return driver.inject_corrections(rtcm_data)
