"""
Diagnose null bytes issue in Python files.
"""

import os
import glob

def check_file_for_null_bytes(filepath):
    """Check if file contains null bytes."""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            has_null = b'\x00' in content
            return {
                'file': filepath,
                'size': len(content),
                'has_null_bytes': has_null,
                'first_100': content[:100]
            }
    except Exception as e:
        return {
            'file': filepath,
            'error': str(e)
        }

def main():
    """Check all Python files for null bytes."""
    print("🔍 CHECKING FOR NULL BYTES IN PYTHON FILES")
    print("=" * 50)
    
    # Check source files
    source_files = glob.glob('src/**/*.py', recursive=True)
    test_files = glob.glob('tests/**/*.py', recursive=True)
    all_files = source_files + test_files
    
    corrupted_files = []
    
    for filepath in all_files:
        result = check_file_for_null_bytes(filepath)
        
        if 'error' in result:
            print(f"❌ {result['file']}: ERROR - {result['error']}")
            corrupted_files.append(filepath)
        elif result['has_null_bytes']:
            print(f"⚠️  {result['file']}: {result['size']} bytes - CONTAINS NULL BYTES")
            corrupted_files.append(filepath)
        else:
            print(f"✅ {result['file']}: {result['size']} bytes - OK")
    
    print("\n" + "=" * 50)
    if corrupted_files:
        print(f"❌ Found {len(corrupted_files)} corrupted files:")
        for file in corrupted_files:
            print(f"  - {file}")
    else:
        print("✅ All files are clean - no null bytes found")

if __name__ == '__main__':
    main()
