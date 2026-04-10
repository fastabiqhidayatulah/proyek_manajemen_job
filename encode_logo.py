#!/usr/bin/env python
import os
import base64

logo_path = r"\\192.168.10.239\proyek_management_job\media\logos\company-logo.png"

# Read and encode as base64
with open(logo_path, 'rb') as f:
    image_data = f.read()
    base64_data = base64.b64encode(image_data).decode('utf-8')

print(f"Base64 encoded (first 100 chars): {base64_data[:100]}")
print(f"Total base64 length: {len(base64_data)}")

# Create the data URI
data_uri = f"data:image/png;base64,{base64_data}"

# Write to a temp file for template
with open('base64_logo.txt', 'w') as f:
    f.write(data_uri)

print("\nData URI created and saved to base64_logo.txt")
print(f"Data URI (first 150 chars): {data_uri[:150]}...")
