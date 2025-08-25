"""
Core GNSS interfaces and data models for RTK client.
Direct implementation from IMPLEMENTATION_GUIDE.md
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional


class FixType(Enum):
    NO_FIX = "NO_FIX"
    DGPS = "DGPS" 
    FLOAT = "FLOAT"
    FIX = "FIX"


class ConnectionError(Exception):
    pass


class ProtocolError(Exception):
    pass


@dataclass
class GNSSState:
    timestamp_utc: str          # ISO8601: "2025-08-25T14:30:15.123Z"
    fix_type: FixType
    latitude: float             # WGS84 degrees
    longitude: float            # WGS84 degrees
    altitude_m: float           # Ellipsoidal height
    accuracy_m: float           # 1-sigma horizontal
    sats: Dict[str, int]        # {"GPS":6,"GLO":4,"GAL":8,"BDS":3}
    pdop: float                 # Position dilution
    baseline_m: float           # RTK baseline distance
    correction_source: str      # NTRIP source or "None"
    receiver_meta: Dict         # {"model":"ZED-F9P","fw":"1.13"}


class IGNSSDriver(ABC):
    @abstractmethod
    async def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Connect to receiver. Raise ConnectionError on failure."""
        pass
    
    @abstractmethod
    async def start_data_stream(self) -> None:
        """Start receiving data. Raise ProtocolError on failure."""
        pass
    
    @abstractmethod
    def get_current_state(self) -> Optional[GNSSState]:
        """Return latest normalized state or None if no data."""
        pass
    
    @abstractmethod
    def inject_corrections(self, rtcm_data: bytes) -> bool:
        """Inject RTCM corrections. Return success status."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Clean shutdown and disconnect."""
        pass
