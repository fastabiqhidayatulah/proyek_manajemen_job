#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services import get_sheets_service

print("Attempting to initialize GoogleSheetsService...")
try:
    service = get_sheets_service()
    print(f"✅ Service type: {type(service).__name__}")
    print(f"✅ Service initialized: {service is not None}")

    if service:
        # Test connection with spreadsheet ID
        spreadsheet_id = '1Z-YovrNia5Gw5QrQvz1Lgy5xLfW54OGnZVpHA0w5b8E'
        print(f"\nTesting connection to spreadsheet: {spreadsheet_id}")
        result = service.test_connection(spreadsheet_id)
        print(f"✅ Test result: {result}")
    else:
        print("❌ Service is still None")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
