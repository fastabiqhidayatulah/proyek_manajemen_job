#!/usr/bin/env python
"""Test that the import is fixed (without DB initialization)"""
import sys
import os

# Add project directory to path (use environment variable or current directory)
project_dir = os.environ.get('PROJECT_PATH', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_dir)

try:
    from core.services.google_sheets import GoogleSheetsService
    print("✅ GoogleSheetsService imported successfully (import error FIXED!)")
    print(f"   Class: {GoogleSheetsService}")
    print(f"   Methods: {[m for m in dir(GoogleSheetsService) if not m.startswith('_')]}")
except ImportError as e:
    print(f"❌ Import error still exists: {e}")
except Exception as e:
    print(f"⚠️  Different error (not import): {type(e).__name__}: {e}")
