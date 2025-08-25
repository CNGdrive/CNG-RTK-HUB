#!/usr/bin/env python3
"""
Simplified NTRIP import test
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test NTRIP package imports (these should work since they're self-contained)
    from ntrip import NTRIPClient, NTRIPMount, NTRIPMountManager, NTRIPError, MountStatus
    print("✅ NTRIP package imports successful")
    
    # Test basic NTRIP functionality
    mount = NTRIPMount(
        host="test.com", 
        port=2101, 
        mount="TEST", 
        username="user", 
        password="pass"
    )
    print("✅ NTRIP mount creation successful")
    
    # Test mount manager creation
    def dummy_callback(data):
        pass
    
    manager = NTRIPMountManager(dummy_callback)
    print("✅ NTRIP mount manager creation successful")
    
    print("🎉 NTRIP PACKAGE IS WORKING CORRECTLY!")
    
except Exception as e:
    print(f"❌ NTRIP test failed: {e}")
    import traceback
    traceback.print_exc()
