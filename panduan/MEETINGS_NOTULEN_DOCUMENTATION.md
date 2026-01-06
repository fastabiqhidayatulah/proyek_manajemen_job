# DOKUMENTASI FITUR MEETINGS & NOTULEN
## Aplikasi Proyek Management Job

**Tanggal:** 20 Desember 2025  
**Status:** Planning/Design Phase  
**Version:** 1.0

---

## 1. OVERVIEW

Modul Meetings & Notulen adalah fitur baru untuk mengelola hasil diskusi/meeting/FGD dan mengkonversinya menjadi action items (Job) dalam sistem.

### Objectives:
- ✅ Digitalisasi notulen rapat (paperless)
- ✅ Track action items dengan PIC & deadline
- ✅ Otomatis convert notulen → Job dalam sistem
- ✅ Link notulen dengan job yang tercipta
- ✅ Monitor progress notulen items
- ✅ Notifikasi ke PIC & atasan

---

## 2. DATA MODELS (ERD)

### 2.1 MEETING (Header Notulen)
```python
Meeting
├── id (PK)
├── no_dokumen_base (CharField, editable=False) [FIXED: F.93/WM/01/03]
├── no_urut (IntegerField, auto_increment) [AUTO-GENERATE: 0001, 0002, dst]
├── no_dokumen (CharField, unique, editable=False) [AUTO-GENERATE: F.93/WM/01/03/0001]
├── revisi (IntegerField, default=0)
├── terbitan (IntegerField, default=1)
├── tanggal_dokumen (DateField)
├── tanggal_meeting (DateField)
├── hari (CharField) [Senin, Selasa, dst - auto from tanggal]
├── jam_mulai (TimeField)
├── jam_selesai (TimeField)
├── tempat (CharField)
├── agenda (TextField)
├── status (CharField) [draft, final, closed]
├── qr_code_token (CharField, unique) [unique token untuk QR code]
├── qr_code_active (BooleanField, default=False) [QR active/inactive]
├── qr_code_created_at (DateTimeField, null=True)
├── peserta (M2M → CustomUser via MeetingPeserta)
├── created_by (FK → CustomUser)
├── updated_by (FK → CustomUser)
├── created_at (DateTimeField, auto_now_add=True)
├── updated_at (DateTimeField, auto_now=True)
└── notes (TextField, optional)

Meta:
  - ordering: ['-created_at']
  - verbose_name: "Meeting/Notulen Rapat"
  - indexes: [tanggal_meeting, status, qr_code_token]
```

### 2.2 MEETING PESERTA (Through model - Internal & External)
```python
MeetingPeserta
├── id (PK)
├── meeting (FK → Meeting)
├── peserta (FK → CustomUser, null=True) [untuk internal users]
├── peserta_eksternal (CharField, null=True) [untuk external: "Nama|NIK|Bagian"]
├── nama (CharField) [auto-fill dari peserta atau peserta_eksternal]
├── nik (CharField, optional) [external peserta NIK]
├── bagian (CharField, optional) [external peserta department]
├── status_kehadiran (CharField) [hadir, izin, alpa]
├── tipe_peserta (CharField) [internal, external]
├── waktu_check_in (DateTimeField, null=True) [saat scan QR]
├── catatan (TextField, optional)
└── unique_together: (meeting, peserta) atau (meeting, peserta_eksternal)
```

### 2.3 NOTULEN ITEM (Detail action items)
```python
NotulenItem
├── id (PK)
├── meeting (FK → Meeting)
├── no (IntegerField) [urutan dalam 1 meeting]
├── pokok_bahasan (TextField) [hasil diskusi/keputusan]
├── tanggapan (TextField) [detail/penjelasan]
├── pic (FK → CustomUser) [PIC yang handle]
├── target_deadline (DateField) [target dari diskusi - soft]
├── status (CharField) [open, progress, done, overdue]
├── job_created (FK → Job, null=True) [link ke job jika sudah convert]
├── created_at (DateTimeField, auto_now_add=True)
├── updated_at (DateTimeField, auto_now=True)
└── notes (TextField, optional)

Meta:
  - unique_together: (meeting, no)
  - ordering: ['meeting', 'no']
  - indexes: [pic, status, target_deadline]
```

---

## 2.5 AUTO-GENERATION LOGIC (NO_DOKUMEN)

### Penomoran Dokumen Structure:
```
Format: [NO_DOKUMEN_BASE]/[NO_URUT]

Contoh:
- F.93/WM/01/03/0001  ← Meeting pertama
- F.93/WM/01/03/0002  ← Meeting kedua
- F.93/WM/01/03/0003  ← Meeting ketiga
dst...

Breakdown:
- F.93           = Kode dokumen (fixed)
- WM             = Kode unit/departemen (fixed)
- 01             = Tahun (01 = 2025, 02 = 2026, dst - fixed)
- 03             = Jenis dokumen/kategori (fixed)
- 0001, 0002...  = Nomor urut otomatis ← INCREMENT INI
```

### Implementation Logic:

**saat CREATE meeting:**
```
1. User input meeting data (tanggal, jam, tempat, agenda)
2. Sistem ambil konfigurasi NO_DOKUMEN_BASE (dari settings atau DB config)
3. Hitung no_urut terbaru dengan base yang sama
   - Query: Meeting.objects.filter(no_dokumen_base="F.93/WM/01/03").last()
   - Jika ada: no_urut_baru = last.no_urut + 1
   - Jika tidak ada: no_urut_baru = 1
4. Generate no_dokumen: f"{no_dokumen_base}/{no_urut_baru:04d}"
   - Format :04d = 0001, 0002, dst (zero-padded 4 digits)
5. Save meeting dengan:
   - no_dokumen_base = "F.93/WM/01/03" (tetap)
   - no_urut = 0001, 0002, dst (increment)
   - no_dokumen = "F.93/WM/01/03/0001" (concat)
   - revisi = 0
   - terbitan = 1
```

### Configuration:
```python
# settings.py
MEETING_CONFIG = {
    'NO_DOKUMEN_BASE': 'F.93/WM/01/03',  ← Bisa diubah di settings
    'REVISI_START': 0,
    'TERBITAN_START': 1,
}
```

### User Interface:
- Meeting form: **NO INPUT untuk no_dokumen** (auto-generated, read-only di display)
- Meeting detail: **SHOW** "Dokumen No: F.93/WM/01/03/0001" (display only)
- Meeting list: **SHOW** no_dokumen di tabel

### Unique Constraint:
- `no_dokumen` = UNIQUE (prevent duplicate)
- Combination check: `(no_dokumen_base, no_urut)` = UNIQUE

---
```python
Job (Existing)
├── ... existing fields ...
├── notulen_item (FK → NotulenItem, null=True, blank=True) [NEW]
│   └─ Track job mana yang dari notulen
├── notulen_target_date (DateField, null=True) [NEW]
│   └─ Reference target date dari notulen
└── ... existing fields ...
```

---

## 3. FEATURES & FUNCTIONALITY

### 3.1 MANAGE MEETING

**CREATE MEETING**
- Form input: tanggal, jam, tempat, agenda
- Select peserta: dari CustomUser (multiple selection)
- Auto-generate: no_dokumen = no_dokumen_base + "/" + no_urut (e.g., F.93/WM/01/03/0001)
  - no_dokumen_base: Fixed format (e.g., "F.93/WM/01/03") - MANUAL INPUT SAAT SETUP
  - no_urut: Auto-increment per base (sequential: 0001, 0002, 0003, dst)
- Initial status: DRAFT
- Bisa add/edit/delete peserta setelah create (jika masih DRAFT)

**EDIT MEETING (hanya jika DRAFT)**
- Edit: tanggal, jam, tempat, agenda
- Edit peserta (internal) via modal
- Tidak bisa edit: no_dokumen, revisi, terbitan
- Delete meeting (hanya DRAFT)

**QR CODE PRESENSI (NEW FEATURE)**
- Generate QR code: Saat peserta sudah ditambah
- QR code link: `/meetings/{meeting_id}/presensi/{qr_token}/`
- Display: Show QR code di meeting detail (untuk ditampilkan di projector)
- Activate/Deactivate: Bisa on/off QR code kapanpun saat meeting berlangsung
- Durasi: QR code valid selama meeting berlangsung (jam_mulai - jam_selesai + buffer)
- Scan limitation: 1 peserta bisa scan max 1x (prevent double entry)

**VIEW MEETING**
- List all meetings (filter by status, tanggal, agenda)
- Detail meeting dengan peserta list
- Show notulen items under meeting
- Action buttons: EDIT (if draft), FINALIZE, CLOSE, DELETE

**FINALIZE MEETING**
- Change status: DRAFT → FINAL (read-only setelah ini)
- Trigger: Auto-create Job untuk setiap notulen item (optional/user pilih)
- Send notification: ke semua peserta + PIC notulen items
- Lock: notulen tidak bisa di-edit lagi

**CLOSE MEETING**
- Change status: FINAL → CLOSED
- Hanya bisa close jika semua notulen items = DONE
- Lock permanently

---

### 3.2 MANAGE NOTULEN ITEMS

**ADD NOTULEN ITEM (saat DRAFT meeting)**
- Form input:
  - Pokok Bahasan (required)
  - Tanggapan (optional)
  - PIC: select dari CustomUser (required)
  - Target Deadline: date picker (required)
- Status default: OPEN
- No: auto-increment per meeting

**EDIT NOTULEN ITEM (saat DRAFT meeting)**
- Edit all fields
- Auto-update: updated_at

**DELETE NOTULEN ITEM (saat DRAFT meeting)**
- Soft delete atau hard delete (decide)

**VIEW NOTULEN ITEMS**
- List dalam context meeting
- Show: no, pokok_bahasan, pic, target_deadline, status
- Action buttons: EDIT, DELETE, VIEW DETAIL

**CREATE JOB FROM NOTULEN ITEM**
- After FINALIZE meeting
- Click: "CREATE JOB" button pada setiap item
- Form muncul:
  - Nama: auto-fill from pokok_bahasan
  - PIC: auto-fill from notulen pic
  - Tipe Job: DAILY atau PROJECT (user pilih)
  - Jadwal Rencana: multi-date picker (optional, dengan target_deadline sebagai default)
  - Job Deadline: auto-fill dari target_deadline (user bisa adjust)
  - Deskripsi/notes: optional
- Save → Job tercipta dengan notulen_item link
- Update notulen_item.job_created = new_job

---

### 3.3 NOTULEN STATUS TRACKING

**Status Flow:**
```
OPEN (awal)
  ↓ (saat PIC mulai kerjakan job)
PROGRESS
  ↓ (saat job selesai)
DONE
  ↓ (auto-check deadline)
OVERDUE (jika deadline < today)
```

**Auto-update status:**
- Saat job.status = Done → notulen_item.status = Done
- Saat job.deadline < today & job.status ≠ Done → notulen_item.status = Overdue
- Saat job.status = Progress → notulen_item.status = Progress

---

## 4. VIEWS & URLS

### 4.1 URL Structure
```
/meetings/
  ├── (GET, POST)                      → list & create meeting
  ├── {meeting_id}/
  │   ├── detail/ (GET)                → view meeting detail
  │   ├── edit/ (GET, POST)            → edit meeting (if draft)
  │   ├── finalize/ (POST)             → finalize meeting
  │   ├── close/ (POST)                → close meeting
  │   ├── delete/ (POST)               → delete meeting
  │   ├── qr-code/ (POST, GET)         → generate/display QR code [NEW]
  │   ├── presensi/{qr_token}/ (GET, POST) → public form presensi [NEW]
  │   ├── notulen/
  │   │   ├── add/ (GET, POST)         → add notulen item
  │   │   ├── {item_id}/
  │   │   │   ├── edit/ (GET, POST)    → edit notulen item
  │   │   │   ├── delete/ (POST)       → delete notulen item
  │   │   │   └── create-job/ (GET, POST) → create job from notulen
  │   │   └── list/ (GET)              → list notulen items
  │   └── peserta/
  │       └── list/ (GET)              → list peserta + status
  └── api/
      ├── peserta/{id}/status/ (PATCH) → update peserta status (for AJAX)
      └── qr-code/{meeting_id}/toggle/ (POST) → activate/deactivate QR [NEW]
```

### 4.2 Views to Create

#### Meetings App Views
```python
class MeetingListView(ListView)
  - model: Meeting
  - template: meetings/meeting_list.html
  - paginate_by: 20
  - filters: status, tanggal, agenda, pic

class MeetingCreateView(CreateView)
  - form_class: MeetingForm
  - template: meetings/meeting_form.html
  - success_url: /meetings/{id}/detail/

class MeetingDetailView(DetailView)
  - model: Meeting
  - template: meetings/meeting_detail.html
  - context: peserta_list, notulen_items, qr_code_token

class QRCodeGenerateView(View) [NEW]
  - POST only
  - Generate QR code token untuk meeting
  - Return: JSON dengan qr_code_url
  - Usage: AJAX call dari meeting detail

class QRCodeDisplayView(TemplateView) [NEW]
  - GET only
  - Display full screen QR code
  - Template: meetings/qr_code_display.html
  - Auto-refresh setiap 30 detik (untuk check status)

class PresensiExternalView(FormView) [NEW]
  - GET: Display form presensi eksternal
  - POST: Process & save presensi
  - Validation: QR token valid, meeting waktu valid, tidak double entry
  - Form fields: nama, nik, bagian
  - Save: Create MeetingPeserta (type=external)
  - Redirect: Success message atau error message
  - No login required (public form)

class MeetingEditView(UpdateView)
  - model: Meeting
  - form_class: MeetingForm
  - template: meetings/meeting_form.html
  - check: status == 'draft' only

class MeetingFinalizeView(View)
  - POST only
  - Change status: draft → final
  - Trigger: optional auto-create jobs
  - Send notifications

class MeetingDeleteView(DeleteView)
  - model: Meeting
  - check: status == 'draft' only
  - success_url: /meetings/

class NotulenItemAddView(CreateView)
  - form_class: NotulenItemForm
  - check: meeting.status == 'draft' only

class NotulenItemEditView(UpdateView)
  - form_class: NotulenItemForm
  - check: meeting.status == 'draft' only

class NotulenItemDeleteView(DeleteView)
  - check: meeting.status == 'draft' only

class CreateJobFromNotulenView(CreateView)
  - form_class: JobFormFromNotulen
  - initial: dari notulen item (nama, pic, target_deadline)
  - create: Job dengan notulen_item FK
```

---

## 5. FORMS

### 5.1 Forms to Create

```python
class MeetingForm(ModelForm)
  - fields: tanggal_meeting, jam_mulai, jam_selesai, tempat, agenda
  - widget peserta: ModelMultipleChoiceField (CheckboxSelectMultiple)
  - clean(): validate jam (jam_selesai > jam_mulai)

class NotulenItemForm(ModelForm)
  - fields: pokok_bahasan, tanggapan, pic, target_deadline
  - widget pic: select (CustomUser filter)

class JobFormFromNotulen(JobForm)
  - Extend existing JobForm
  - Pre-fill: nama_pekerjaan, pic, dari notulen
  - Add field: jadwal_rencana_dates (CheckboxSelectMultiple untuk multi-date)
  - Add field: job_deadline (DateField, with initial=notulen.target_deadline)
  - clean(): validate deadline
  - save(): create JobDate entries untuk setiap tanggal pilihan

class MeetingPesertaStatusForm(ModelForm)
  - fields: status_kehadiran, catatan
  - For AJAX update

class PresensiExternalForm(ModelForm) [NEW]
  - fields: nama, nik, bagian
  - No authentication required
  - Validation: format NIK (16 digits), bagian dari list choices
  - clean(): check duplicate (NIK + meeting unique)
  - save(): create MeetingPeserta (tipe_peserta='external')
```

---

## 6. TEMPLATES

### 6.1 Templates to Create

```
templates/meetings/
├── meeting_list.html
│   ├── Table: no_dokumen, agenda, tanggal, status, peserta_count
│   ├── Filter: status, date range, agenda search
│   ├── Buttons: CREATE, VIEW, EDIT, DELETE
│   ├── Color coding: draft (yellow), final (blue), closed (gray)
│   └── Pagination
│
├── meeting_form.html
│   ├── Form fields: tanggal, jam, tempat, agenda
│   ├── Peserta selection: multi-select with search
│   ├── Submit/Cancel buttons
│   └── Validation messages
│
├── meeting_detail.html
│   ├── Header: no_dokumen, status, tanggal, jam, tempat, agenda
│   ├── QR CODE SECTION [NEW]:
│   │   ├── [🔲 GENERATE QR CODE] button (if status != closed)
│   │   ├── QR code display (after generated)
│   │   ├── [👁️ VIEW FULLSCREEN] button (show in projector)
│   │   ├── [⚪ ACTIVATE/DEACTIVATE] toggle
│   │   └── Last 10 check-ins (real-time updates)
│   ├── Peserta section: list dengan status kehadiran (modal inline edit)
│   │   └── Filter: internal, external, all
│   │   └── Column: Nama, NIK, Bagian, Status, Waktu Check-in
│   ├── Notulen items section:
│   │   ├── Table: no, pokok_bahasan, tanggapan, pic, deadline, status
│   │   ├── Action buttons per item: EDIT, DELETE, CREATE JOB
│   │   └── [+ ADD ITEM] button (if draft)
│   ├── Meeting actions: [EDIT] [FINALIZE] [CLOSE] [DELETE] (conditional)
│   └── Back button
│
├── qr_code_display.html [NEW]
│   ├── Full-screen QR code (untuk di-projector)
│   ├── Meeting info: tanggal, jam, agenda (small di bawah QR)
│   ├── Real-time check-in counter (top right)
│   ├── Auto-refresh setiap 30 detik
│   ├── [← KEMBALI] button (small)
│   └── Responsive (mobile-friendly untuk scan)
│
├── presensi_form.html [NEW]
│   ├── Display: Meeting info (tanggal, jam, tempat, agenda)
│   ├── Form fields: nama, nik, bagian
│   ├── Form validation messages (client + server)
│   ├── [SUBMIT PRESENSI] button
│   ├── Success message dengan timestamp check-in
│   ├── Error message jika QR invalid atau sudah absen
│   ├── Responsive mobile-first design
│   ├── No login required (public form)
│   └── Loading spinner saat submit
│
├── notulen_form.html (reuse for add/edit)
│   ├── Form fields: pokok_bahasan, tanggapan, pic, target_deadline
│   ├── Submit/Cancel buttons
│   └── If edit: show existing data
│
└── create_job_from_notulen.html
    ├── Display notulen item data (read-only)
    ├── Form fields: tipe_job (radio), job_deadline (date)
    ├── Jadwal rencana: multi-date checkboxes
    ├── Warning: notulen target date display
    ├── [CREATE JOB] [CANCEL] buttons
    └── Show preview: "Will create Job: {nama} for {pic} by {deadline}"
```

---

## 7. INTEGRATION WITH EXISTING SYSTEM

### 7.1 Integration Points

**With CustomUser (Existing):**
- ✅ Use existing CustomUser untuk peserta, pic
- ✅ Maintain hierarchy: atasan/bawahan
- ✅ Use existing jabatan

**With Job (Existing):**
- ✅ Create Job dengan existing form/model
- ✅ Add fields: notulen_item FK, notulen_target_date
- ✅ Reuse JobDate untuk multiple dates
- ✅ Sync status: notulen_item.status ← job.status

**With Dashboard (Existing):**
- ✅ Add widget: "My notulen items" (by PIC)
- ✅ Add widget: "Upcoming meetings"
- ✅ Add widget: "Overdue notulen actions"

**With Permissions (Existing):**
- ✅ Create PIC dapat edit/update job
- ✅ Atasan dapat view bawahan's notulen items
- ✅ Creator dapat edit/finalize meeting

---

## 8. NOTIFICATIONS & ALERTS

### 8.1 Notification Triggers

```
Trigger 1: SAAT CREATE JOB FROM NOTULEN
├─ To: PIC (notulen.pic)
├─ Message: "Anda di-assign task dari notulen: {pokok_bahasan}"
├─ Link: /jobs/{job_id}/detail/
└─ Channel: Email + In-app notification

Trigger 2: X DAYS BEFORE DEADLINE (misal 3 hari)
├─ To: PIC
├─ Message: "Task {nama} deadline dalam 3 hari: {date}"
├─ Link: /jobs/{job_id}/detail/
└─ Channel: Email + In-app

Trigger 3: DEADLINE OVERDUE
├─ To: PIC + Atasan PIC
├─ Message: "Task {nama} sudah overdue! Deadline: {date}"
├─ Link: /jobs/{job_id}/detail/
└─ Channel: Email + In-app (urgent)

Trigger 4: FINALIZE MEETING
├─ To: Semua peserta + semua PIC notulen items
├─ Message: "Meeting {agenda} sudah final. Buka untuk lihat action items."
├─ Link: /meetings/{id}/detail/
└─ Channel: Email + In-app

Trigger 5: JOB STATUS CHANGE
├─ To: Atasan PIC + Meeting creator
├─ Message: "Task {nama} changed to {status}"
└─ Channel: In-app

Trigger 6: FINALIZE MEETING → AUTO CREATE JOBS
├─ To: Meeting creator
├─ Message: "{X} jobs created from notulen items"
└─ Channel: In-app confirmation
```

---

## 9. FOLDER STRUCTURE

```
meetings/                          [NEW APP]
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py           [create Meeting, MeetingPeserta, NotulenItem]
│
├── management/
│   └── commands/
│       └── update_notulen_status.py  [cron job to auto-update notulen status]
│
├── __init__.py
├── admin.py                       [register models in Django admin]
├── apps.py
├── forms.py                       [MeetingForm, NotulenItemForm, JobFormFromNotulen]
├── models.py                      [Meeting, MeetingPeserta, NotulenItem]
├── urls.py                        [URL patterns]
├── views.py                       [All views]
├── signals.py                     [Auto-sync notulen status from job]
│
└── templates/
    └── meetings/
        ├── meeting_list.html
        ├── meeting_form.html
        ├── meeting_detail.html
        ├── notulen_form.html
        ├── create_job_from_notulen.html
        └── components/
            ├── notulen_items_table.html
            └── peserta_list.html

config/
└── settings.py                    [Add 'meetings' to INSTALLED_APPS]

core/
└── models.py                      [Add notulen_item, notulen_target_date to Job]
```

---

## 10. DATABASE CHANGES

### 10.1 Migrations to Create

```
1. meetings/migrations/0001_initial.py
   - CreateModel: Meeting
   - CreateModel: MeetingPeserta
   - CreateModel: NotulenItem
   - AddConstraint: unique_together (meeting, no)
   - AddConstraint: unique_together (meeting, peserta)

2. core/migrations/00XX_add_notulen_fields.py
   - AddField: Job.notulen_item (FK, null=True)
   - AddField: Job.notulen_target_date (DateField, null=True)
   - AddIndex: Job (notulen_item)
```

---

## 11. TESTING PLAN

### 11.1 Unit Tests

```python
test_meetings/
├── test_models.py
│   ├── test_meeting_creation
│   ├── test_meeting_auto_generate_no_dokumen
│   ├── test_notulen_item_creation
│   ├── test_meeting_status_flow
│   └── test_peserta_tracking
│
├── test_views.py
│   ├── test_meeting_list_view
│   ├── test_meeting_create_view
│   ├── test_meeting_finalize
│   ├── test_create_job_from_notulen
│   └── test_permissions
│
├── test_forms.py
│   ├── test_meeting_form_validation
│   ├── test_notulen_item_form
│   └── test_job_form_from_notulen
│
└── test_signals.py
    ├── test_auto_update_notulen_status
    └── test_job_status_sync
```

### 11.2 Integration Tests

```python
test_meetings/
└── test_integration.py
    ├── test_full_flow_create_meeting_to_job
    ├── test_notulen_to_job_conversion
    ├── test_multi_date_job_creation
    └── test_notification_triggers
```

### 11.3 Manual Testing Checklist

```
[ ] Create meeting dengan peserta
[ ] Add notulen items dengan multiple PIC
[ ] Edit notulen item target deadline
[ ] Finalize meeting (status berubah)
[ ] Create job dari notulen item
[ ] Verify multi-date input
[ ] Verify job deadline vs notulen target
[ ] Update job status (check notulen status sync)
[ ] Test overdue calculation
[ ] Verify notifications sent
[ ] Test permissions (who can edit/view)
[ ] Test filter & search di meeting list
```

---

## 12. IMPLEMENTATION CHECKLIST

### Phase 1: Models & Database
- [ ] Create Meeting model (+ qr_code fields)
- [ ] Create MeetingPeserta model (+ external peserta support)
- [ ] Create NotulenItem model
- [ ] Add notulen fields to Job model
- [ ] Create migrations
- [ ] Run migrations
- [ ] Register models in admin

### Phase 2: Forms & Views
- [ ] Create MeetingForm
- [ ] Create NotulenItemForm
- [ ] Create JobFormFromNotulen (extend existing)
- [ ] Create PresensiExternalForm [NEW]
- [ ] Create MeetingListView
- [ ] Create MeetingCreateView
- [ ] Create MeetingDetailView
- [ ] Create MeetingEditView
- [ ] Create MeetingFinalizeView
- [ ] Create QRCodeGenerateView [NEW]
- [ ] Create QRCodeDisplayView [NEW]
- [ ] Create PresensiExternalView [NEW]
- [ ] Create NotulenItemAddView
- [ ] Create NotulenItemEditView
- [ ] Create CreateJobFromNotulenView

### Phase 3: Templates
- [ ] Create meeting_list.html
- [ ] Create meeting_form.html
- [ ] Create meeting_detail.html (with QR section)
- [ ] Create qr_code_display.html [NEW]
- [ ] Create presensi_form.html [NEW]
- [ ] Create notulen_form.html
- [ ] Create create_job_from_notulen.html
- [ ] Create notulen_items_table.html component
- [ ] Create peserta_list.html component

### Phase 4: Integration & QR Code Logic
- [ ] Create QR code generation logic (token + library)
- [ ] Create QR code validation logic
- [ ] Create real-time check-in tracking
- [ ] Implement duplicate entry prevention
- [ ] Add QR status to meeting detail AJAX
- [ ] Update Job model (add notulen fields)
- [ ] Create signals for auto-sync status
- [ ] Create management command for status updates
- [ ] Update Dashboard with notulen widgets
- [ ] Update existing Job views (if needed)

### Phase 5: Notifications
- [ ] Implement notification system (email/in-app)
- [ ] Add notification triggers (including QR related)
- [ ] Test notification delivery

### Phase 6: Testing
- [ ] Unit tests (models + forms)
- [ ] QR code generation tests
- [ ] Presensi external flow tests
- [ ] Integration tests
- [ ] Manual testing (QR scan simulation)
- [ ] User acceptance testing (UAT)

### Phase 7: Documentation & Deployment
- [ ] User documentation (QR presensi guide)
- [ ] API documentation
- [ ] QR setup & troubleshooting guide
- [ ] Staff training (bagaimana scan QR)
- [ ] Deployment guide

---

## 13. TIMELINE ESTIMATE

```
Phase 1 (Models): 2-3 hours
Phase 2 (Forms & Views): 8-10 hours [+2 hours untuk QR views]
Phase 3 (Templates): 6-8 hours [+2 hours untuk QR templates]
Phase 4 (Integration & QR): 6-7 hours [+3 hours untuk QR logic]
Phase 5 (Notifications): 3-4 hours
Phase 6 (Testing): 5-6 hours [+2 hours untuk QR testing]
Phase 7 (Documentation): 2-3 hours

Total: ~33-41 hours (4-5 hari development + testing)
```

---

## 14. RISKS & MITIGATIONS

| Risk | Mitigation |
|------|-----------|
| Job deadline vs notulen target confusion | Clear UI/docs, warning messages, tutorial |
| Auto-sync status complexity | Use Django signals, thorough testing |
| Notifications spam | Configurable alerts, digest option |
| Permission/security issues | Implement role-based access control |
| Data integrity | Unit tests, transaction management |

---

## 15. ASSUMPTIONS & CONSTRAINTS

**Assumptions:**
- ✓ All peserta sudah terdaftar di CustomUser
- ✓ Job model sudah stable (no major changes)
- ✓ Existing cache/performance fine
- ✓ Email/notification system available

**Constraints:**
- ✓ No breaking changes to existing Job system
- ✓ Separate folder (meetings app) dari core
- ✓ Reuse existing CustomUser & Job models
- ✓ Support multi-date like existing job

---

## 16. APPROVAL & SIGN-OFF

**Prepared by:** GitHub Copilot  
**Date:** 20 Desember 2025  
**Status:** Awaiting User Review & Approval  

**Sign-off:**
- [ ] User approval
- [ ] Requirements confirmed
- [ ] Ready for implementation

---

**NEXT STEP:** User review dokumentasi ini, approve/request changes, kemudian proceed ke implementation phase.
