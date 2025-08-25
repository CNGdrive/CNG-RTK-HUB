"""
NTRIP Mount Manager for Multi-Mount Support and Failover

Manages multiple NTRIP mountpoints with automatic failover, priority ordering,
and connection health monitoring for reliable RTK correction streaming.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from .ntrip_client import NTRIPClient, NTRIPMount, NTRIPError

logger = logging.getLogger(__name__)


@dataclass
class MountStatus:
    """Status information for an NTRIP mount."""
    mount: NTRIPMount
    connected: bool = False
    last_attempt: Optional[float] = None
    consecutive_failures: int = 0
    total_bytes: int = 0
    total_corrections: int = 0
    last_data_time: Optional[float] = None
    priority: int = 0  # Lower number = higher priority


class NTRIPMountManager:
    """
    Manages multiple NTRIP mountpoints with failover capability.
    
    Features:
    - Priority-based mount selection
    - Automatic failover on connection loss
    - Health monitoring and statistics
    - Configurable retry policies
    """
    
    def __init__(self, correction_callback: Callable[[bytes], None]):
        """
        Initialize mount manager.
        
        Args:
            correction_callback: Function to call with received RTCM data
        """
        self.correction_callback = correction_callback
        self.mounts: List[MountStatus] = []
        self.active_client: Optional[NTRIPClient] = None
        self.active_mount: Optional[MountStatus] = None
        self.running = False
        
        # Configuration
        self.max_consecutive_failures = 3
        self.retry_delay = 30.0  # Seconds before retrying failed mount
        self.health_check_interval = 60.0  # Health check frequency
        self.data_timeout = 120.0  # No data timeout
        
        # Monitoring
        self._monitor_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    def add_mount(self, mount: NTRIPMount, priority: int = 0):
        """
        Add NTRIP mount to manager.
        
        Args:
            mount: NTRIP mount configuration
            priority: Priority level (lower = higher priority)
        """
        mount_status = MountStatus(mount=mount, priority=priority)
        self.mounts.append(mount_status)
        
        # Sort by priority
        self.mounts.sort(key=lambda m: m.priority)
        
        logger.info(f"Added NTRIP mount: {mount.host}:{mount.port}/{mount.mount} (priority {priority})")
    
    def remove_mount(self, mount_identifier: str):
        """
        Remove mount by host:port/mount identifier.
        
        Args:
            mount_identifier: Format "host:port/mount"
        """
        for i, mount_status in enumerate(self.mounts):
            mount = mount_status.mount
            identifier = f"{mount.host}:{mount.port}/{mount.mount}"
            if identifier == mount_identifier:
                # Disconnect if currently active
                if self.active_mount == mount_status:
                    asyncio.create_task(self._disconnect_active())
                
                self.mounts.pop(i)
                logger.info(f"Removed NTRIP mount: {mount_identifier}")
                return
        
        logger.warning(f"Mount not found for removal: {mount_identifier}")
    
    def get_mounts(self) -> List[Dict[str, Any]]:
        """Get list of all configured mounts with status."""
        return [
            {
                'host': status.mount.host,
                'port': status.mount.port,
                'mount': status.mount.mount,
                'username': status.mount.username,
                'description': status.mount.description,
                'priority': status.priority,
                'connected': status.connected,
                'enabled': status.mount.enabled,
                'consecutive_failures': status.consecutive_failures,
                'total_bytes': status.total_bytes,
                'total_corrections': status.total_corrections,
                'last_data_time': status.last_data_time
            }
            for status in self.mounts
        ]
    
    async def start(self) -> bool:
        """
        Start mount manager and connect to highest priority mount.
        
        Returns:
            True if successfully connected to any mount
        """
        if self.running:
            logger.warning("Mount manager already running")
            return True
        
        if not self.mounts:
            logger.error("No mounts configured")
            return False
        
        self.running = True
        self._stop_event.clear()
        
        # Start monitoring task
        self._monitor_task = asyncio.create_task(self._monitor_connections())
        
        # Attempt connection to best available mount
        return await self._connect_best_mount()
    
    async def stop(self):
        """Stop mount manager and disconnect from all mounts."""
        logger.info("Stopping NTRIP mount manager")
        self.running = False
        self._stop_event.set()
        
        # Stop monitoring
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        # Disconnect active client
        await self._disconnect_active()
    
    async def _connect_best_mount(self) -> bool:
        """Connect to the best available mount based on priority and status."""
        # Find best mount (enabled, lowest consecutive failures, highest priority)
        available_mounts = [
            status for status in self.mounts
            if status.mount.enabled and status.consecutive_failures < self.max_consecutive_failures
        ]
        
        if not available_mounts:
            logger.error("No available mounts for connection")
            return False
        
        # Sort by consecutive failures, then priority
        available_mounts.sort(key=lambda m: (m.consecutive_failures, m.priority))
        
        for mount_status in available_mounts:
            if await self._attempt_connection(mount_status):
                return True
        
        logger.error("Failed to connect to any available mount")
        return False
    
    async def _attempt_connection(self, mount_status: MountStatus) -> bool:
        """Attempt connection to specific mount."""
        mount = mount_status.mount
        logger.info(f"Attempting connection to {mount.host}:{mount.port}/{mount.mount}")
        
        # Disconnect current client if any
        await self._disconnect_active()
        
        # Create new client
        self.active_client = NTRIPClient(self._correction_received)
        mount_status.last_attempt = asyncio.get_event_loop().time()
        
        # Attempt connection
        success = await self.active_client.connect(mount)
        
        if success:
            self.active_mount = mount_status
            mount_status.connected = True
            mount_status.consecutive_failures = 0
            logger.info(f"Successfully connected to {mount.mount}")
            return True
        else:
            mount_status.consecutive_failures += 1
            await self._disconnect_active()
            logger.warning(f"Failed to connect to {mount.mount} (failures: {mount_status.consecutive_failures})")
            return False
    
    async def _disconnect_active(self):
        """Disconnect the currently active client."""
        if self.active_client:
            await self.active_client.disconnect()
            self.active_client = None
        
        if self.active_mount:
            self.active_mount.connected = False
            self.active_mount = None
    
    def _correction_received(self, rtcm_data: bytes):
        """Handle received RTCM correction data."""
        if self.active_mount:
            self.active_mount.total_bytes += len(rtcm_data)
            self.active_mount.total_corrections += 1
            self.active_mount.last_data_time = asyncio.get_event_loop().time()
        
        # Forward to application callback
        try:
            self.correction_callback(rtcm_data)
        except Exception as e:
            logger.error(f"Error in correction callback: {e}")
    
    async def _monitor_connections(self):
        """Monitor connection health and handle failover."""
        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.health_check_interval)
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Continue monitoring
            
            if not self.running:
                break
            
            await self._check_connection_health()
            await self._retry_failed_mounts()
    
    async def _check_connection_health(self):
        """Check health of active connection."""
        if not self.active_mount or not self.active_client:
            logger.info("No active connection, attempting to connect")
            await self._connect_best_mount()
            return
        
        # Check if connection is still alive
        if not self.active_client.connected:
            logger.warning("Active connection lost, attempting failover")
            await self._handle_failover()
            return
        
        # Check for data timeout
        current_time = asyncio.get_event_loop().time()
        if (self.active_mount.last_data_time and 
            current_time - self.active_mount.last_data_time > self.data_timeout):
            logger.warning("Data timeout on active connection, attempting failover")
            await self._handle_failover()
    
    async def _handle_failover(self):
        """Handle connection failover to backup mount."""
        if self.active_mount:
            self.active_mount.consecutive_failures += 1
            logger.info(f"Failover from {self.active_mount.mount.mount} (failures: {self.active_mount.consecutive_failures})")
        
        await self._disconnect_active()
        await self._connect_best_mount()
    
    async def _retry_failed_mounts(self):
        """Reset failure counts for mounts after retry delay."""
        current_time = asyncio.get_event_loop().time()
        
        for mount_status in self.mounts:
            if (mount_status.consecutive_failures >= self.max_consecutive_failures and
                mount_status.last_attempt and
                current_time - mount_status.last_attempt > self.retry_delay):
                
                logger.info(f"Resetting failure count for {mount_status.mount.mount}")
                mount_status.consecutive_failures = 0
    
    def get_active_mount(self) -> Optional[Dict[str, Any]]:
        """Get information about currently active mount."""
        if not self.active_mount:
            return None
        
        mount = self.active_mount.mount
        return {
            'host': mount.host,
            'port': mount.port,
            'mount': mount.mount,
            'username': mount.username,
            'description': mount.description,
            'connected': self.active_mount.connected,
            'total_bytes': self.active_mount.total_bytes,
            'total_corrections': self.active_mount.total_corrections,
            'last_data_time': self.active_mount.last_data_time
        }
    
    def get_manager_status(self) -> Dict[str, Any]:
        """Get overall manager status."""
        return {
            'running': self.running,
            'total_mounts': len(self.mounts),
            'active_mount': self.get_active_mount(),
            'enabled_mounts': len([m for m in self.mounts if m.mount.enabled]),
            'failed_mounts': len([m for m in self.mounts if m.consecutive_failures >= self.max_consecutive_failures])
        }
