import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import LeaveEvent, Karyawan, Departemen, CustomUser
from datetime import datetime, timedelta

# Get departemen Teknik
dept = Departemen.objects.get(nama_departemen='Teknik')
print(f"✅ Departemen: {dept.nama_departemen}")
print(f"   Google Calendar ID: {dept.google_calendar_id}")

# Get admin user
admin = CustomUser.objects.get(username='admin')
print(f"✅ Created by: {admin.username}")

# Get sample karyawan - try all active first
kary = Karyawan.objects.filter(status='Aktif').first()
if not kary:
    kary = Karyawan.objects.first()

if kary:
    print(f"✅ Sample Karyawan: {kary.nama_lengkap} (Dept: {kary.departemen})")
else:
    print(f"✅ Sample Karyawan: NONE - will use dummy nama_orang")

# Create multiple leave events untuk Mei/Juni
test_dates = [
    '2026-05-28',  # Besok
    '2026-05-29',  # Lusa
    '2026-06-01',  # Senin
    '2026-06-10',  # Mid-June
]

created_count = 0
for date_str in test_dates:
    event = LeaveEvent.objects.create(
        karyawan=kary,
        nama_orang=kary.nama_lengkap if kary else 'Test User',
        tipe_leave='Cuti',
        tanggal=date_str,
        deskripsi=f'Test event - {date_str}',
        created_by=admin,
        departemen=dept
    )
    created_count += 1
    print(f"   ✅ Created: {event.karyawan} - {event.tanggal}")

print(f"\n✅ Total events created: {created_count}")

# Verify we can query them
all_events = LeaveEvent.objects.filter(departemen=dept).filter(tanggal__gte='2026-05-28')
print(f"\n✅ Query verification:")
print(f"   Total leave events for May 28+ : {all_events.count()}")

# Check upcoming vs past
from datetime import datetime as dt
today = dt.now().date()
upcoming = [e for e in all_events if e.tanggal and e.tanggal >= str(today)]
past = [e for e in all_events if e.tanggal and e.tanggal < str(today)]

print(f"   Upcoming: {len(upcoming)}")
print(f"   Past: {len(past)}")

if upcoming:
    print(f"\n   Sample upcoming events:")
    for e in upcoming[:3]:
        print(f"      - {e.karyawan}: {e.tanggal}")
