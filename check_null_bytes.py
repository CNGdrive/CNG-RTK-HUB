#!/usr/bin/env python3
"""
Diagnostic script to check for null bytes in source files
"""

import os

def check_file_for_null_bytes(filepath):
    """Check if a file contains null bytes"""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            return b'\x00' in data
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def main():
    print("🔍 CHECKING FOR NULL BYTES IN SOURCE FILES")
    print("=" * 50)
    
    source_files = [
        'src/rtk_service.py',
        'src/core/driver_manager.py', 
        'src/core/interfaces.py',
        'src/ntrip/ntrip_client.py',
        'src/ntrip/mount_manager.py',
        'src/api/websocket_server.py',
        'src/api/http_server.py'
    ]
    
    issues_found = 0
    
    for filepath in source_files:
        if os.path.exists(filepath):
            has_null_bytes = check_file_for_null_bytes(filepath)
            if has_null_bytes is True:
                print(f"❌ NULL BYTES FOUND: {filepath}")
                issues_found += 1
            elif has_null_bytes is False:
                print(f"✅ Clean: {filepath}")
            else:
                print(f"⚠️  Error checking: {filepath}")
                issues_found += 1
        else:
            print(f"❌ NOT FOUND: {filepath}")
            issues_found += 1
    
    print("=" * 50)
    if issues_found > 0:
        print(f"🚨 ISSUES FOUND: {issues_found} files have problems")
        print("These files need to be restored from git or rewritten")
    else:
        print("✅ ALL FILES CLEAN - No null bytes found")
    
    return issues_found == 0

if __name__ == "__main__":
    main()
