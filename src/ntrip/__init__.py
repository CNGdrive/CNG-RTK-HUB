"""
NTRIP Client Package for RTK Correction Data

Provides NTRIP v1.0/v2.0 protocol implementation with multi-mount support,
authentication, automatic failover, and real-time RTCM correction streaming.
"""

from .ntrip_client import NTRIPClient, NTRIPMount, NTRIPError
from .mount_manager import NTRIPMountManager, MountStatus

__all__ = [
    'NTRIPClient',
    'NTRIPMount', 
    'NTRIPError',
    'NTRIPMountManager',
    'MountStatus'
]

__version__ = '1.0.0'
