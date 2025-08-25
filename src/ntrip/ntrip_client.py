"""
NTRIP Client for RTK Correction Data Streaming

Implements NTRIP v1.0/v2.0 protocol for real-time RTCM correction data.
Supports authentication, multiple mountpoints, and automatic reconnection.
"""

import asyncio
import aiohttp
import base64
import logging
from typing import Optional, Callable, Dict, Any
from urllib.parse import urlparse
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NTRIPMount:
    """NTRIP mountpoint configuration."""
    host: str
    port: int
    mount: str
    username: str
    password: str
    description: str = ""
    enabled: bool = True


class NTRIPError(Exception):
    """NTRIP-specific errors."""
    pass


class NTRIPClient:
    """
    NTRIP client for streaming RTCM correction data.
    
    Features:
    - HTTP/TCP NTRIP v1.0/v2.0 support
    - Basic authentication
    - Automatic reconnection with exponential backoff
    - Real-time RTCM data streaming
    """
    
    def __init__(self, correction_callback: Callable[[bytes], None]):
        """
        Initialize NTRIP client.
        
        Args:
            correction_callback: Function to call with received RTCM data
        """
        self.correction_callback = correction_callback
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        self.current_mount: Optional[NTRIPMount] = None
        self.reconnect_delay = 1.0  # Start with 1 second
        self.max_reconnect_delay = 60.0  # Maximum 60 seconds
        self._stream_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        
        # Statistics
        self.bytes_received = 0
        self.corrections_sent = 0
        self.connection_attempts = 0
        self.last_data_time: Optional[float] = None
    
    async def connect(self, mount: NTRIPMount) -> bool:
        """
        Connect to NTRIP caster and start streaming.
        
        Args:
            mount: NTRIP mountpoint configuration
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.current_mount = mount
            self.connection_attempts += 1
            
            # Create HTTP session with timeout
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Build NTRIP request URL
            url = f"http://{mount.host}:{mount.port}/{mount.mount}"
            
            # Create authentication header
            auth_string = f"{mount.username}:{mount.password}"
            auth_bytes = auth_string.encode('ascii')
            auth_header = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'User-Agent': 'CNG-RTK-HUB/1.0',
                'Authorization': f'Basic {auth_header}',
                'Ntrip-Version': 'Ntrip/2.0',
                'Connection': 'close'
            }
            
            # Connect to NTRIP caster
            logger.info(f"Connecting to NTRIP: {mount.host}:{mount.port}/{mount.mount}")
            response = await self.session.get(url, headers=headers)
            
            if response.status == 200:
                logger.info(f"NTRIP connected successfully to {mount.mount}")
                self.connected = True
                self.reconnect_delay = 1.0  # Reset backoff
                
                # Start streaming task
                self._stream_task = asyncio.create_task(self._stream_corrections(response))
                return True
            else:
                logger.error(f"NTRIP connection failed: HTTP {response.status}")
                await self._cleanup()
                return False
                
        except Exception as e:
            logger.error(f"NTRIP connection error: {e}")
            await self._cleanup()
            return False
    
    async def disconnect(self):
        """Disconnect from NTRIP caster."""
        logger.info("Disconnecting NTRIP client")
        self._stop_event.set()
        
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
        
        await self._cleanup()
        self.connected = False
        self.current_mount = None
    
    async def _stream_corrections(self, response: aiohttp.ClientResponse):
        """Stream RTCM corrections from NTRIP response."""
        try:
            buffer = bytearray()
            
            async for chunk in response.content.iter_chunked(1024):
                if self._stop_event.is_set():
                    break
                
                buffer.extend(chunk)
                self.bytes_received += len(chunk)
                self.last_data_time = asyncio.get_event_loop().time()
                
                # Process complete RTCM messages
                while len(buffer) >= 3:
                    # Look for RTCM v3 preamble (0xD3)
                    if buffer[0] != 0xD3:
                        buffer.pop(0)  # Remove invalid byte
                        continue
                    
                    # Extract message length from RTCM header
                    if len(buffer) < 3:
                        break
                    
                    message_length = ((buffer[1] & 0x03) << 8) | buffer[2]
                    total_length = message_length + 6  # Header(3) + Data + CRC(3)
                    
                    if len(buffer) < total_length:
                        break  # Wait for complete message
                    
                    # Extract complete RTCM message
                    rtcm_message = bytes(buffer[:total_length])
                    buffer = buffer[total_length:]
                    
                    # Validate RTCM message CRC
                    if self._validate_rtcm_crc(rtcm_message):
                        # Send to correction callback
                        try:
                            self.correction_callback(rtcm_message)
                            self.corrections_sent += 1
                        except Exception as e:
                            logger.error(f"Error in correction callback: {e}")
                    else:
                        logger.warning("Invalid RTCM CRC, discarding message")
                        
        except asyncio.CancelledError:
            logger.info("NTRIP streaming cancelled")
        except Exception as e:
            logger.error(f"NTRIP streaming error: {e}")
            if self.connected:
                # Attempt reconnection
                await self._attempt_reconnect()
    
    def _validate_rtcm_crc(self, message: bytes) -> bool:
        """Validate RTCM v3 CRC-24Q checksum."""
        if len(message) < 6:
            return False
        
        # Extract CRC from last 3 bytes
        received_crc = (message[-3] << 16) | (message[-2] << 8) | message[-1]
        
        # Calculate CRC-24Q for data (excluding CRC bytes)
        data = message[:-3]
        calculated_crc = self._calculate_crc24q(data)
        
        return received_crc == calculated_crc
    
    def _calculate_crc24q(self, data: bytes) -> int:
        """Calculate RTCM CRC-24Q checksum."""
        CRC24Q_POLY = 0x1864CFB
        crc = 0
        
        for byte in data:
            crc ^= byte << 16
            for _ in range(8):
                if crc & 0x800000:
                    crc = (crc << 1) ^ CRC24Q_POLY
                else:
                    crc <<= 1
                crc &= 0xFFFFFF
        
        return crc
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect with exponential backoff."""
        if not self.current_mount:
            return
        
        logger.info(f"Attempting NTRIP reconnection in {self.reconnect_delay} seconds")
        await asyncio.sleep(self.reconnect_delay)
        
        # Exponential backoff
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
        
        success = await self.connect(self.current_mount)
        if not success and not self._stop_event.is_set():
            await self._attempt_reconnect()
    
    async def _cleanup(self):
        """Clean up session resources."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current NTRIP client status."""
        return {
            'connected': self.connected,
            'mount': self.current_mount.mount if self.current_mount else None,
            'host': self.current_mount.host if self.current_mount else None,
            'bytes_received': self.bytes_received,
            'corrections_sent': self.corrections_sent,
            'connection_attempts': self.connection_attempts,
            'last_data_time': self.last_data_time,
            'reconnect_delay': self.reconnect_delay
        }
    
    def get_connection_info(self) -> Optional[Dict[str, str]]:
        """Get current connection information."""
        if not self.current_mount:
            return None
        
        return {
            'host': self.current_mount.host,
            'port': str(self.current_mount.port),
            'mount': self.current_mount.mount,
            'username': self.current_mount.username,
            'description': self.current_mount.description
        }
