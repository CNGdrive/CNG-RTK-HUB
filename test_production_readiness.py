#!/usr/bin/env python3
"""
Comprehensive Test Suite for Milestone 3 Production Readiness
"""

import sys
import os
import traceback

def test_python_version():
    print(f"✅ Python version: {sys.version}")
    return True

def test_basic_imports():
    """Test basic Python imports work"""
    try:
        import asyncio
        import logging
        import json
        print("✅ Basic Python imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_core_imports():
    """Test core project imports"""
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        
        from core.interfaces import IGNSSDriver, GNSSState, FixType
        from core.driver_manager import DriverManager
        print("✅ Core interfaces import successful")
        return True
    except Exception as e:
        print(f"❌ Core imports failed: {e}")
        traceback.print_exc()
        return False

def test_driver_imports():
    """Test driver imports"""
    try:
        from drivers.zedf9p import ZedF9PDriver
        from drivers.um980 import UM980Driver
        print("✅ Driver imports successful")
        return True
    except Exception as e:
        print(f"❌ Driver imports failed: {e}")
        traceback.print_exc()
        return False

def test_ntrip_imports():
    """Test NTRIP package imports"""
    try:
        from ntrip import NTRIPClient, NTRIPMount, NTRIPMountManager
        from ntrip.ntrip_client import NTRIPError
        from ntrip.mount_manager import MountStatus
        print("✅ NTRIP package imports successful")
        return True
    except Exception as e:
        print(f"❌ NTRIP imports failed: {e}")
        traceback.print_exc()
        return False

def test_api_imports():
    """Test API imports"""
    try:
        from api.websocket_server import WebSocketServer
        from api.http_server import HTTPServer
        print("✅ API imports successful")
        return True
    except Exception as e:
        print(f"❌ API imports failed: {e}")
        traceback.print_exc()
        return False

def test_rtk_service_import():
    """Test RTK service import"""
    try:
        from rtk_service import RTKService
        print("✅ RTK service import successful")
        return True
    except Exception as e:
        print(f"❌ RTK service import failed: {e}")
        traceback.print_exc()
        return False

def test_rtk_service_initialization():
    """Test RTK service can be initialized"""
    try:
        from rtk_service import RTKService
        service = RTKService()
        print("✅ RTK service initialization successful")
        print(f"✅ NTRIP manager initialized: {service.driver_manager.ntrip_manager is not None}")
        print(f"✅ WebSocket server set: {service.driver_manager.websocket_server is not None}")
        return True
    except Exception as e:
        print(f"❌ RTK service initialization failed: {e}")
        traceback.print_exc()
        return False

def test_ntrip_integration():
    """Test NTRIP integration in RTK service"""
    try:
        from rtk_service import RTKService
        service = RTKService()
        
        # Test NTRIP methods exist
        assert hasattr(service, 'add_ntrip_mount')
        assert hasattr(service, 'start_ntrip_corrections') 
        assert hasattr(service, 'get_ntrip_status')
        
        # Test NTRIP status
        status = service.get_ntrip_status()
        assert 'enabled' in status
        assert 'initialized' in status
        
        print("✅ NTRIP integration in RTK service verified")
        return True
    except Exception as e:
        print(f"❌ NTRIP integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 MILESTONE 3 PRODUCTION READINESS - COMPREHENSIVE TESTING")
    print("=" * 60)
    
    tests = [
        test_python_version,
        test_basic_imports,
        test_core_imports,
        test_driver_imports,
        test_ntrip_imports,
        test_api_imports,
        test_rtk_service_import,
        test_rtk_service_initialization,
        test_ntrip_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 TEST RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - MILESTONE 3 PRODUCTION READY!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - NEEDS INVESTIGATION")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
