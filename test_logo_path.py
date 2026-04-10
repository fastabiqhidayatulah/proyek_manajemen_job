#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.conf import settings

print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")

logo_path = os.path.join(settings.MEDIA_ROOT, "logos", "company-logo.png")
print(f"Logo full path: {logo_path}")
print(f"Logo file exists: {os.path.exists(logo_path)}")

if os.path.exists(logo_path):
    print(f"Logo file size: {os.path.getsize(logo_path)} bytes")
    
# Also show what's in the media directory
media_root = settings.MEDIA_ROOT
print(f"\nDirectories in MEDIA_ROOT:")
if os.path.exists(media_root):
    for item in os.listdir(media_root):
        full_path = os.path.join(media_root, item)
        item_type = "DIR" if os.path.isdir(full_path) else "FILE"
        print(f"  [{item_type}] {item}")
else:
    print(f"  MEDIA_ROOT does not exist!")
