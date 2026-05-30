#!/usr/bin/env python
"""Create test leave events for future dates (May 2026 onwards)"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import LeaveEvent, Departemen, Karyawan

# Get Teknik departemen
try:
    dept_teknik = Departemen.objects.get(nama_departemen='Teknik')
except:
    print("❌ Departemen Teknik not found")
    exit(1)

# Get some karyawan for testing
karyawan_list = list(Karyawan.objects.filter(status='Aktif', departemen=dept_teknik)[:10])

if not karyawan_list:
    print("❌ No active karyawan found in Teknik departemen")
    exit(1)

# Create events for May 27 onwards (today onwards)
today = datetime.now().date()
base_date = today

events_created = 0

for i, karyawan in enumerate(karyawan_list):
    # Create 2-3 day cuti for each person starting from different dates in May/June
    start_date = base_date + timedelta(days=i*3)
    end_date = start_date + timedelta(days=2)
    
    # Generate comma-separated dates
    date_range = []
    current = start_date
    while current <= end_date:
        date_range.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    tanggal_str = ','.join(date_range)
    
    # Create event
    event, created = LeaveEvent.objects.get_or_create(
        karyawan=karyawan,
        tanggal=tanggal_str,
        tipe_leave='Cuti',
        defaults={
            'departemen': dept_teknik,
            'deskripsi': f'Test cuti for {karyawan.nama_lengkap}',
            'created_by': None,
        }
    )
    
    if created:
        print(f"✅ Created event for {karyawan.nama_lengkap}: {tanggal_str}")
        events_created += 1
    else:
        print(f"⏭️  Event already exists for {karyawan.nama_lengkap}")

print(f"\n✨ Total new events created: {events_created}")

# Verify
all_events = LeaveEvent.objects.filter(departemen=dept_teknik)
print(f"\nTotal events in Teknik dept: {all_events.count()}")

# Check date range
min_date = None
max_date = None
for e in all_events:
    tgl_list = e.get_tanggal_list()
    if tgl_list:
        dates = sorted(tgl_list)
        if not min_date or dates[0] < min_date:
            min_date = dates[0]
        if not max_date or dates[-1] > max_date:
            max_date = dates[-1]

print(f"Event date range: {min_date} to {max_date}")
