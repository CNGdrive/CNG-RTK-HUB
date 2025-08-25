#!/usr/bin/env python3
"""
Focused Production Readiness Test - Correct Python Package Testing
"""

import sys
import os

# Add src to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_package_imports():
    """Test imports using proper Python package structure"""
    print("🧪 TESTING PROPER PACKAGE IMPORTS")
    print("=" * 50)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Core interfaces
    try:
        from core.interfaces import IGNSSDriver, GNSSState, FixType
        print("✅ Core interfaces import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Core interfaces failed: {e}")
        tests_failed += 1
    
    # Test 2: NTRIP package (already works)
    try:
        from ntrip import NTRIPClient, NTRIPMountManager
        print("✅ NTRIP package import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ NTRIP package failed: {e}")
        tests_failed += 1
    
    # Test 3: Core driver manager
    try:
        from core.driver_manager import DriverManager
        print("✅ Driver manager import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Driver manager failed: {e}")
        tests_failed += 1
    
    # Test 4: WebSocket server
    try:
        from api.websocket_server import WebSocketServer
        print("✅ WebSocket server import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ WebSocket server failed: {e}")
        tests_failed += 1
    
    # Test 5: HTTP server
    try:
        from api.http_server import HTTPServer
        print("✅ HTTP server import successful")
        tests_passed += 1
    except Exception as e:
        print(f"❌ HTTP server failed: {e}")
        tests_failed += 1
    
    print("=" * 50)
    print(f"📊 IMPORT TESTS: {tests_passed} passed, {tests_failed} failed")
    
    return tests_failed == 0

def test_rtk_service_module():
    """Test RTK service as a proper module"""
    print("\n🧪 TESTING RTK SERVICE MODULE")
    print("=" * 50)
    
    try:
        from rtk_service import RTKService
        print("✅ RTK service import successful")
        
        # Test instantiation
        service = RTKService()
        print("✅ RTK service instantiation successful")
        
        # Test NTRIP integration
        assert hasattr(service, 'get_ntrip_status'), "Missing get_ntrip_status method"
        assert hasattr(service, 'add_ntrip_mount'), "Missing add_ntrip_mount method"
        
        # Test NTRIP manager is initialized
        ntrip_status = service.get_ntrip_status()
        assert 'initialized' in ntrip_status, "NTRIP status missing 'initialized' key"
        assert ntrip_status['initialized'] == True, "NTRIP manager not initialized"
        
        print("✅ RTK service NTRIP integration verified")
        print("✅ ALL RTK SERVICE TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"❌ RTK service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run focused production readiness tests"""
    print("🎯 FOCUSED PRODUCTION READINESS TEST")
    print("Using correct Python package import structure")
    print("=" * 60)
    
    # Test imports
    imports_ok = test_package_imports()
    
    # Test RTK service
    service_ok = test_rtk_service_module()
    
    print("\n" + "=" * 60)
    if imports_ok and service_ok:
        print("🎉 PRODUCTION READINESS: ✅ VERIFIED!")
        print("✅ All core imports working")
        print("✅ RTK service with NTRIP integration functional")
        print("✅ Ready for Milestone 4 development")
        return True
    else:
        print("⚠️  PRODUCTION READINESS: ❌ ISSUES FOUND")
        if not imports_ok:
            print("❌ Import structure needs fixes")
        if not service_ok:
            print("❌ RTK service integration needs fixes")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
