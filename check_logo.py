#!/usr/bin/env python
import os
from pathlib import Path

logo_path = r"\\192.168.10.239\proyek_management_job\media\logos\company-logo.png"

# Check if file exists
exists = os.path.exists(logo_path)
print(f"File exists: {exists}")

if exists:
    # Check file size
    size = os.path.getsize(logo_path)
    print(f"File size: {size} bytes")
    
    # Check magic bytes for PNG
    with open(logo_path, 'rb') as f:
        magic_bytes = f.read(8)
        hex_bytes = ' '.join(f'{b:02X}' for b in magic_bytes)
        print(f"Magic bytes: {hex_bytes}")
        
        # PNG magic: 89 50 4E 47 0D 0A 1A 0A
        if hex_bytes.startswith('89 50 4E 47'):
            print("✓ Valid PNG file signature")
        else:
            print("✗ NOT a valid PNG file!")
    
    # Try with Path.as_uri()
    p = Path(logo_path)
    file_uri = p.as_uri()
    print(f"\nPath.as_uri() result: {file_uri}")
