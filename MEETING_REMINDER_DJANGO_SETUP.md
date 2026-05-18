# ✅ DJANGO MEETING REMINDER CONFIGURATION - SETUP CHECKLIST

## Phase 1: Model & Database ✅ COMPLETED

### Models Updated:
- [x] **Departemen** - Tambah field `google_sheet_id`
- [x] **GoogleAPISettings** - New singleton model untuk global API settings
- [x] Migration created: `0027_googleapisettings_departemen_google_sheet_id_and_more.py`

**Next Step:** Apply migration
```bash
python manage.py migrate core
```

---

## Phase 2: Services ✅ COMPLETED

### Google Sheets Service Created:
- [x] `core/services/google_sheets.py` - GoogleSheetsService class
- [x] Functions:
  - `append_meeting_row()` - Append meeting ke Meetings sheet
  - `test_connection()` - Test koneksi ke spreadsheet
  - `get_spreadsheet_id_from_url()` - Extract ID dari URL

**Usage:**
```python
from core.services import get_sheets_service

service = get_sheets_service()
service.append_meeting_row(
    spreadsheet_id='ABC123...',
    meeting_data={
        'no_dokumen': 'RAPAT-001',
        'agenda': 'Meeting aja',
        'tanggal': '2026-04-11',
        'waktu_mulai': '10:00',
        'waktu_selesai': '11:00',
        'lokasi': 'Ruang A',
        'peserta': 'Fasta, Hanif'
    }
)
```

---

## Phase 3: Signals ✅ COMPLETED

### Auto-Sync Signal Created:
- [x] `meetings/signals.py` - Added `sync_meeting_to_google_sheets()`
- [x] Trigger: `post_save(Meeting)` - Auto-append ke Sheets saat meeting dibuat

**Behavior:**
- Hanya sync jika status meeting = 'final'
- Hanya sync jika departemen punya `google_sheet_id`
- Auto-append ke Meetings sheet di spreadsheet

---

## Phase 4: Forms & Views ✅ COMPLETED

### Configuration Forms:
- [x] `DepartemenGoogleSettingsForm` - Form untuk google_sheet_id per departemen
- [x] `GoogleAPISettingsForm` - Form untuk global API settings (Fonnte token, reminder time)

### Configuration Views:
- [x] `MeetingReminderSettingsView` - Departemen config page
  - Show/edit `google_sheet_id` per departemen
  - Test connectivity
  - Hanya accessible oleh departemen head atau admin

- [x] `GoogleAPISettingsView` - Global API settings page
  - Configure Fonnte API token
  - Configure reminder send time
  - Configure Google credentials path
  - Only admin accessible

### URLs:
- [x] `/meetings/config/reminder-settings/` - Departemen settings
- [x] `/meetings/config/google-api-settings/` - Global settings (admin)

---

## Phase 5: Templates ✅ COMPLETED

- [x] `reminder_settings.html` - Departemen configuration UI
- [x] `google_api_settings.html` - Admin global settings UI

---

## 🚀 NEXT STEPS TO COMPLETE SETUP

### 1. Apply Database Migration
```bash
python manage.py migrate core
```

### 2. Collect Static Files (if needed)
```bash
python manage.py collectstatic --noinput
```

### 3. Verify Installation
```bash
python manage.py shell
```

Inside shell:
```python
from core.models import GoogleAPISettings, Departemen
from core.services import GoogleSheetsService

# Check GoogleAPISettings
settings = GoogleAPISettings.get_instance()
print(f"Settings ID: {settings.pk}")

# Check Departemen
depts = Departemen.objects.all()
for d in depts:
    print(f"{d.nama_departemen}: google_sheet_id = {d.google_sheet_id}")

# Test service
service = GoogleSheetsService()
print(f"Service connected: {service.service is not None}")
```

---

## 📋 CONFIGURATION WORKFLOW (After Migration)

### For Departemen Head:
1. Login ke Django admin
2. Go to `/meetings/config/reminder-settings/`
3. Paste Google Spreadsheet ID
4. Save → Test connection
5. ✅ Setup complete! Meetings otomatis ke-sync ke spreadsheet

### For Admin:
1. Login ke Django admin
2. Go to `/meetings/config/google-api-settings/`
3. Input Fonnte API Token
4. Input Reminder send time (default: 08:00)
5. Input Google credentials path (default: JSON GCP/credentials.json)
6. Save
7. ✅ Global settings done!

---

## 🔄 AUTO-SYNC FLOW

1. **Meeting dibuat di Django** → status = 'draft'
2. **Meeting status diubah ke 'final'** → Django signal triggered
3. **Signal: sync_meeting_to_google_sheets()** runs
   - Check: departemen punya google_sheet_id? ✅
   - Prepare meeting data
   - Initialize GoogleSheetsService
   - Append row ke Meetings sheet
   - Log result
4. **Google Apps Script trigger** (daily 08:00)
   - Read Meetings sheet
   - Format message (combined if multiple)
   - Send via Fonnte WhatsApp API
   - Mark "Sudah_Kirim" = "Yes"
   - Log results

---

## ⚙️ CONFIGURATION FILES NEEDED

```
project_root/
├── JSON GCP/
│   └── credentials.json          ← Service account key JSON
├── manage.py
├── core/
│   ├── models.py                 ✅ Updated
│   ├── services/
│   │   ├── __init__.py          ✅ Created
│   │   └── google_sheets.py      ✅ Created
│   └── migrations/
│       └── 0027_...              ✅ Created
├── meetings/
│   ├── signals.py                ✅ Updated
│   ├── forms.py                  ✅ Updated
│   ├── views.py                  ✅ Updated
│   ├── urls.py                   ✅ Updated
│   └── templates/meetings/
│       ├── reminder_settings.html    ✅ Created
│       └── google_api_settings.html  ✅ Created
```

---

## 🔒 PERMISSIONS

- **MeetingReminderSettingsView**: Accessible by departemen head + staff/admin
- **GoogleAPISettingsView**: Accessible by staff/admin only
- **Signal**: Runs automatically on `post_save(Meeting)` when status='final'

---

## 📝 TESTING CHECKLIST

- [ ] Migration applied: `python manage.py migrate core`
- [ ] Login as admin → Access `/meetings/config/google-api-settings/`
- [ ] Set Fonnte token + reminder time
- [ ] Login as departemen head → Access `/meetings/config/reminder-settings/`
- [ ] Set spreadsheet ID (will test connection)
- [ ] Create new meeting → Set status to 'final' → Save
- [ ] Check Google Sheets → New row appended? ✅
- [ ] GAS trigger at 08:00 → Reminder message sent? ✅

---

## 🎯 COMPLETION STATUS

| Phase | Status | Notes |
|-------|--------|-------|
| **Models** | ✅ Done | Departemen + GoogleAPISettings |
| **Database** | ✅ Done | Migration created |
| **Services** | ✅ Done | GoogleSheetsService ready |
| **Signals** | ✅ Done | Auto-sync on post_save |
| **Forms** | ✅ Done | 2 config forms |
| **Views** | ✅ Done | 2 config views with permission |
| **Templates** | ✅ Done | 2 HTML templates |
| **URLs** | ✅ Done | 2 new routes |
| **Migration Apply** | ⏳ Pending | `python manage.py migrate` |
| **Testing** | ⏳ Pending | Manual test end-to-end |

---

## 💡 NOTES

- Jika ada error saat migrate, check:
  - Import errors di models.py / signals.py
  - Google credentials path valid?
  - Firewall blocking Google API?

- Jika auto-sync tidak jalan:
  - Signal sudah registered? (Check signals/__init__.py import)
  - Meeting status = 'final'?
  - Departemen punya google_sheet_id?
  - Credentials file ada?

- Jika spreadsheet tidak connect:
  - Service account email di-share ke spreadsheet?
  - Spreadsheet punya sheet "Meetings"?
  - Spreadsheet ID benar?

