#!/usr/bin/env python3
"""Check and fix null bytes in source files"""

import os
from pathlib import Path

def check_and_fix_null_bytes():
    root_dir = Path("c:/AppDevelopment/Superior Position/CNG-RTK-HUB")
    src_files = list(root_dir.glob("src/**/*.py"))
    
    print("Checking for null bytes...")
    
    for file_path in src_files:
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            null_count = data.count(b'\x00')
            if null_count > 0:
                print(f"FOUND {null_count} null bytes in {file_path}")
                # Remove null bytes
                cleaned_data = data.replace(b'\x00', b'')
                with open(file_path, 'wb') as f:
                    f.write(cleaned_data)
                print(f"CLEANED {file_path}")
            else:
                print(f"CLEAN: {file_path}")
                
        except Exception as e:
            print(f"ERROR checking {file_path}: {e}")

if __name__ == "__main__":
    check_and_fix_null_bytes()
