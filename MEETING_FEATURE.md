# 📋 Meeting Feature - Complete Documentation

**Last Updated:** April 11, 2026  
**App Location:** `/meetings` app  
**Status:** ✅ Fully Implemented

---

## 📌 Overview

Meeting feature adalah sistem manajemen rapat dan notulen berbasis web yang terintegrasi dengan job management system. 

**Core Functionality:**
- 📅 Create, edit, manage meetings (rapat)
- 📝 Notulen item management (hasil diskusi & keputusan meeting)
- 👥 Internal & External participant management
- 🎯 QR Code for automatic check-in
- 🔗 Convert notulen items into trackable jobs
- 📊 Track meeting status (Draft → Final → Closed)

---

## 🏗️ Database Architecture

### 1. **Meeting Model** (Header/Master)
```
Meeting
├── no_dokumen           : Auto-generated (F.93/WM/01/03/0001)
├── tanggal_meeting      : Date of meeting
├── jam_mulai/jam_selesai: Start & end times
├── tempat              : Meeting location
├── agenda              : Meeting topic
├── status              : draft | final | closed
├── qr_code_token       : Unique token for QR code
├── qr_code_active      : Toggle on/off
├── peserta (M2M)       : Through MeetingPeserta
├── created_by          : FK to User
└── created_at
```

**Status Flow:**
```
draft → finalize → final → close → closed
 ↓(delete)        ↑(edit)
 X                (edit notulen)
```

---

### 2. **MeetingPeserta Model** (Through Table)
Handles both **internal** (system users) and **external** (QR scan) participants.

```
MeetingPeserta
├── meeting              : FK to Meeting
├── peserta             : FK to User (nullable)
├── nama                : Full name
├── nik                 : ID number (for external)
├── bagian              : Department (for external)
├── tipe_peserta        : internal | external
├── status_kehadiran    : belum | hadir | izin | alpa
├── waktu_check_in      : Timestamp saat scan QR
└── catatan             : Notes
```

**Status Kehadiran:**
- `belum`: Default state (not checked in)
- `hadir`: Present
- `izin`: Excused absence
- `alpa`: Unexcused absence

---

### 3. **NotulenItem Model** (Action Items/Results)
Detailed meeting discussion items with action items.

```
NotulenItem
├── meeting             : FK to Meeting
├── no                  : Auto-numbered (1, 2, 3...)
├── pokok_bahasan       : Discussion topic
├── tanggapan           : Details/resolution
├── pic                 : FK to User (system user PIC)
├── pic_eksternal       : Char field (if PIC is external)
├── target_deadline     : Soft deadline for action
├── status              : open | progress | done | overdue
├── job_created         : FK to Job (if converted)
└── created_at
```

**Status Meanings:**
- `open`: Action not started
- `progress`: Work in progress
- `done`: Completed
- `overdue`: Deadline passed & not done

---

### 4. **MeetingReminder Model** (WA Notification Tracking)
Tracks WhatsApp reminders to prevent duplicates.

```
MeetingReminder
├── meeting             : FK to Meeting
├── peserta             : FK to MeetingPeserta
├── timing              : 1day_08am | 10min_before
├── status              : pending | sent | failed
└── created_at
```

---

## 🎯 Key Features

### 1️⃣ Meeting Management
**Create Meeting:**
- Auto-generate document number: `F.93/WM/01/03/0001`
- Set date, time, location, agenda
- Auto-calculate day of week
- Add internal participants

**Edit Meeting:**
- Only in draft status
- Update agenda, time, participants
- Add/remove peserta

**Finalize Meeting:**
- Change status from `draft` → `final`
- Lock from further changes (edit disabled)
- Enable job creation from notulen

**Close Meeting:**
- Only when all notulen items are `done`
- Change status: `final` → `closed`

---

### 2️⃣ Participant Management

**Internal Participants:**
- Select from active system users
- Auto-populate name from user profile
- Track attendance status manually

**External Participants:**
- Via QR code scan
- Enter nama, NIK, bagian manually
- Auto-record check-in timestamp

**Attendance Summary:**
```python
meeting.get_presensi_summary()
# Returns:
{
    'hadir': 5,
    'izin': 2,
    'alpa': 1,
    'total': 8
}
```

---

### 3️⃣ QR Code for Check-in
**Generate QR:**
- Click "Generate QR Code" on meeting detail
- Creates unique token for that meeting
- Generates PNG image + base64 encoding

**Scan QR (External):**
- Non-system users scan QR
- Fill form: nama, NIK, bagian
- Auto-creates MeetingPeserta entry
- Records check-in timestamp

**QR Features:**
- Toggle active/inactive status
- Support for ngrok/public URLs (via `DJANGO_PUBLIC_URL` setting)
- Shows presensi count in real-time

---

### 4️⃣ Notulen Item Management

**Add Notulen Item:**
- Only in draft status
- Pokok bahasan (required): what was discussed
- Tanggapan (optional): details
- PIC (required): assign to internal user OR external name
- Target deadline (required): soft deadline

**Edit Notulen Item:**
- AJAX-based inline editing
- Disable when meeting not draft
- Auto-renumber items if needed

**Delete Notulen Item:**
- AJAX delete
- Only when meeting is draft

**Auto-numbering:**
```python
# Items automatically numbered per meeting
Item 1: ...
Item 2: ...
Item 3: ...
```

---

### 5️⃣ Create Job From Notulen
**Critical Feature:** Convert action items into trackable jobs.

**Workflow:**
```
Notulen Item (open)
    ↓ (Create Job)
Job created (Open status)
    ↓
Notulen Item status → progress
    ↓
Link created: NotulenItem.job_created = Job
```

**Permission Model:**
- Only PIC and users in their hierarchy can create job
- PIC: the person responsible for action item
- Supervisors: can create on behalf of subordinates
- Subordinates: can create jobs assigned to them

**Job Details (From Notulen):**
- `nama_pekerjaan`: From notulen pokok_bahasan (editable)
- `tipe_job`: Daily or Project (selectable)
- `pic`: Selected user from dropdown (required)
- `job_deadline`: Date selected (required)
- `jadwal_pelaksanaan`: For Daily jobs (dates comma-separated)
- `prioritas`: P1-P4 (user selects)
- `fokus`: Custom focus area
- `project`: Optional project link
- `aset`: Optional equipment/asset link (Teknik only)

**Auto-created:**
- Job status = "Open"
- JobDate entries for each selected date
- Link to meeting via NotulenItem.job_created

---

## 🔄 Workflow Example

### Scenario: Create Meeting → Add Notulen → Convert to Job

**Step 1: Create Meeting**
```
GET /meetings/create/
→ Form: date, time, location, agenda, peserta
→ Save → Status: DRAFT
```

**Step 2: Add Notulen Items**
```
GET /meetings/<id>/detail/
→ Click "Add Notulen Item"
→ Form: pokok_bahasan, tanggapan, pic, deadline
→ Save → Item 1, Item 2, Item 3...
```

**Step 3: Finalize Meeting**
```
POST /meetings/<id>/finalize/
→ Status: DRAFT → FINAL
→ No more edits allowed
```

**Step 4: Convert Item to Job**
```
GET /meetings/notulen/<item_id>/create_job/
→ Form: nama_pekerjaan, pic, deadline, prioritas, etc.
→ Save → Job created
→ Notulen status: open → progress
```

**Step 5: Close Meeting**
```
POST /meetings/<id>/close/
→ Checks: All notulen items = done?
→ YES: Status FINAL → CLOSED
→ NO: Show warning, keep status FINAL
```

---

## 📱 UI/UX Components

### Meeting List View
- Filter by status (draft/final/closed)
- Date range filter
- Search by agenda
- Pagination (20 per page)

### Meeting Detail View
- Header with meeting info
- Peserta section: add/remove, attendance status
- Notulen items: add/edit/delete inline
- QR Code section: generate, display, toggle
- Status badges: draft/final/closed
- Action buttons: edit, finalize, close, delete

### Notulen Item Table
- Auto-numbered rows
- Inline editing (AJAX)
- Status badges: open/progress/done/overdue
- PIC display (internal user or external name)
- Target deadline
- Quick actions: edit, delete, create job

---

## 🔐 Permission System

**Meeting Creator** (created_by):
- Create: ✅
- Edit: ✅ (only draft)
- Finalize: ✅
- Close: ✅
- Delete: ✅ (only draft)
- Add/Remove peserta: ✅
- Add notulen items: ✅

**Non-Creator Users:**
- View meetings: ✅ (list view)
- View detail: ✅
- Create job from notulen: ✅ (if PIC or in hierarchy)
- Edit/Delete: ❌

**Hierarchy-based Job Creation:**
- PIC of notulen item: can create job
- PIC's supervisors: can create job
- PIC's subordinates: can create job
- Admin/Superuser: bypass all checks

---

## 📊 Models Summary

| Model | Count | Purpose |
|-------|-------|---------|
| Meeting | 1:M | Master record |
| MeetingPeserta | M:M | Internal + External participants |
| NotulenItem | 1:M | Action items from discussion |
| MeetingReminder | 1:M | WA notification tracking |

---

## 🔗 Integration Points

### With Core Job System
- `NotulenItem.job_created` → links to `Job`
- Create job from notulen converts to trackable job
- Job keeps reference to source notulen

### With User System
- Uses `CustomUser` model
- Supports hierarchy (atasan/subordinates)
- Job creation permission via hierarchy

### With QR/Authentication
- Generates QR codes for external check-in
- Supports ngrok URLs for public access
- Public form for external presensi (no login needed)

---

## 📋 Templates

### Key Templates:
- `meetings/meeting_list.html` - List all meetings
- `meetings/meeting_form.html` - Create/edit meeting
- `meetings/meeting_detail.html` - Meeting detail + notulen mgmt
- `meetings/notulen_form.html` - Notulen item edit
- `meetings/qr_code_display.html` - Full-screen QR code
- `meetings/presensi_form.html` - Public QR scan form
- `meetings/create_job_from_notulen.html` - Job creation from notulen

---

## ⚙️ Settings

### DJANGO_PUBLIC_URL (for ngrok)
```python
# settings.py
DJANGO_PUBLIC_URL = 'https://ngrok-xxxx.ngrok.io'
```

### Document Number Format
```python
# In Meeting.no_dokumen_base
DEFAULT: 'F.93/WM/01/03'
# Auto-generates: F.93/WM/01/03/0001, 0002, 0003, etc.
```

---

## 🚀 Usage Tips

**1. Meeting Creation:**
- Always set tanggal_meeting (system calculates day)
- Add all peserta during creation or edit later
- Set agenda clearly for notulen reference

**2. Notulen During Meeting:**
- Add items as discussion progresses
- Use pokok_bahasan for action items
- Always assign PIC (system user or external)
- Set realistic target_deadline

**3. Converting to Job:**
- Review notulen items carefully
- Only convert necessary items as jobs
- Ensure correct PIC is selected in job form
- For Daily jobs, select all work dates

**4. Closing Meeting:**
- All notulen items must be marked "done"
- Update job status in Job module first
- Then mark notulen item as done
- Then close meeting

---

## 📌 Status Codes

**Meeting Status:**
- `draft` - Being prepared, can edit
- `final` - Ready, locked, jobs can be created
- `closed` - Completed, archived

**Notulen Item Status:**
- `open` - Not started
- `progress` - Active work (when job created)
- `done` - Completed
- `overdue` - Deadline passed & not done

**Participant Status:**
- `belum` - Not checked in
- `hadir` - Present
- `izin` - Excused
- `alpa` - Absent without excuse

---

## 🎓 Key Takeaways

**What Meeting Feature Does:**
✅ Organized meeting documentation  
✅ Automatic participant tracking  
✅ Convert discussions into actionable jobs  
✅ QR-based attendance system  
✅ Integration with job management  

**Best For:**
- Departemen HRD/Ops meetings
- Project kickoff meetings
- Daily standup meetings
- Meeting minutes documentation

