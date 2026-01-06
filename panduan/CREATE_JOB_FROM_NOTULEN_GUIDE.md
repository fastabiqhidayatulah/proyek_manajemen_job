# Panduan: Membuat Job dari Notulen Item

## Overview

Fitur "Create Job from Notulen" memungkinkan user untuk mengkonversi action items dari meeting notulen menjadi job yang dapat ditrack di Core job management system.

**Tujuan:**
- Memastikan hasil meeting ditindaklanjuti dengan tracking yang proper
- Link otomatis antara notulen dan job untuk audit trail
- Flexible job scheduling independen dari notulen deadline
- Hierarchy-based permission untuk kontrol akses

## Workflow: Dari Notulen ke Job

### Step 1: Meeting → Finalize → Create Notulen Items

1. User membuat meeting (Draft status)
2. Di meeting detail, user menambah notulen items (pokok bahasan + PIC + target deadline)
3. User finalize meeting (status berubah ke Final)

### Step 2: Create Job dari Notulen Item

1. Di meeting detail (Final/Closed status), setiap notulen item punya tombol "CREATE JOB" (icon arrow-right-circle)
2. Tombol hanya muncul jika:
   - Notulen status bukan "done"
   - Job belum pernah dibuat dari item ini (job_created FK kosong)
   - User dalam hierarchy notulen PIC

3. Click tombol → Buka form Create Job from Notulen

### Step 3: Fill Job Details

Form pre-fill data dari notulen:
- **Pokok Bahasan** (read-only) - dari notulen
- **PIC** (read-only) - user yang di-assign notulen item
- **Target Deadline Notulen** (read-only) - sebagai reference

User bisa edit:
- **Nama Pekerjaan** - default dari pokok_bahasan, bisa diubah
- **Tipe Job** - Daily atau Project
- **Ditugaskan Kepada** - dropdown hanya user dalam hierarchy PIC
- **Job Deadline** - **INDEPENDENT** dari notulen deadline
- **Jadwal Pelaksanaan** - multi-date picker (Required untuk Daily, Optional untuk Project)
- **Priority** - P1, P2, P3, P4
- **Fokus** - Perawatan, Perbaikan, Proyek, Lainnya
- **Project** - Optional
- **Mesin/Sub-Mesin** - Optional
- **Deskripsi** - Optional

### Step 4: Submit & Link

1. Click "Buat Job" → Job created
2. Job automatis ter-link ke notulen item (OneToOneField)
3. Notulen status berubah menjadi "progress"
4. Redirect ke meeting detail
5. Button "CREATE JOB" hilang (sudah ada job)

## Permission Model: Hierarchy-Based Access Control

### Who Can Create Jobs from Notulen?

**Rule:** Hanya user dalam hierarchy of notulen PIC bisa create job dari notulen item.

**Hierarchy = PIC + All Supervisors + All Subordinates**

#### Example:

```
                  ADMIN (Supervisor)
                      ↓
              FOREMAN A (PIC notulen)
                    ↓     ↓
             TECH-1    TECH-2
```

Jika FOREMAN A adalah PIC notulen item:

✅ **CAN create job:**
- ADMIN (supervisor dari FOREMAN A)
- FOREMAN A (PIC sendiri)
- TECH-1 (subordinate dari FOREMAN A)
- TECH-2 (subordinate dari FOREMAN A)

❌ **CANNOT create job:**
- FOREMAN B (different hierarchy)
- TECH-3 (not in FOREMAN A's hierarchy)

**Exception:**
- Admin/Superuser: Always can create job (bypass permission check)

### Who Can Be Assigned the Job?

**Dropdown "Ditugaskan Kepada" only shows users dalam hierarchy PIC.**

Same hierarchy rules as above - prevents cross-hierarchy job assignments.

## Key Features

### 1. **Notulen Data as Reference**

- Pre-filled read-only fields show context
- User dapat edit job details tanpa mengubah notulen
- Notulen tetap original untuk audit trail

### 2. **Independent Job Deadline**

**PENTING:** Job deadline **COMPLETELY INDEPENDENT** dari notulen target_deadline.

Why?
- Notulen deadline adalah soft deadline dari meeting
- Job deadline bisa lebih realistis berdasarkan execution planning
- Multi-date support untuk flexible scheduling

Example:
```
Notulen Item:
- Pokok Bahasan: Maintenance Panel A
- Target Deadline: 2025-01-20 (dari meeting discussion)

Job Created:
- Job Deadline: 2025-01-25 (execution reality)
- Jadwal Pelaksanaan: 2025-01-21, 2025-01-22, 2025-01-24 (actual work dates)
```

### 3. **Multi-Date Scheduling**

Untuk **Daily Job**: User bisa pilih multiple dates via Flatpickr date picker.

Dates disimpan sebagai `JobDate` entries:
- Setiap date = 1 JobDate record
- Status tracking per tanggal
- Report dapat disaggregate by date

Untuk **Project Job**: Multi-date optional.

### 4. **Automatic Linking**

```python
# Auto-filled di form save:
job.notulen_item = notulen_item  # OneToOneField
job.notulen_target_date = notulen_item.target_deadline  # For reference

# Notulen status updated:
notulen_item.status = 'progress'
notulen_item.job_created = job  # ForeignKey link
```

## Data Model Changes

### Job Model Fields (ALREADY EXIST)

```python
# Already di core/models.py:
notulen_item = models.OneToOneField(
    'meetings.NotulenItem',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='job',
    help_text="Notulen item yang membuat job ini"
)

notulen_target_date = models.DateField(
    null=True,
    blank=True,
    help_text="Reference target date dari notulen"
)
```

### NotulenItem Model Fields (ALREADY EXIST)

```python
# Already di meetings/models.py:
job_created = models.ForeignKey(
    'core.Job',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='notulen_items',
    help_text="Job yang dibuat dari notulen item ini"
)
```

**NO DATABASE MIGRATIONS NEEDED** - Fields sudah exist!

## Forms & Views

### Form: `JobFromNotulenForm` (core/forms.py)

Custom form dengan:
- Read-only display fields untuk notulen data
- Multi-date picker field (Flatpickr)
- Validation: Daily job harus punya jadwal

```python
class JobFromNotulenForm(forms.Form):
    # Read-only reference fields
    pokok_bahasan_notulen = ...
    pic_notulen = ...
    target_deadline_notulen = ...
    
    # Editable fields
    nama_pekerjaan = ...
    tipe_job = ...
    assigned_to = ...  # Filtered by hierarchy
    job_deadline = ...
    jadwal_pelaksanaan = ...  # Multi-date
    ...
```

### View: `CreateJobFromNotulenView` (meetings/views.py)

```python
class CreateJobFromNotulenView(LoginRequiredMixin, View):
    """
    GET: Display form dengan pre-fill dari notulen
    POST: Create job dengan permission check
    """
    
    def _can_create_job(user, notulen_pic):
        # Check: user dalam hierarchy notulen PIC?
        
    def _get_allowed_users(notulen_pic):
        # Return: CustomUser dalam hierarchy
```

### URLs (meetings/urls.py)

```python
path('notulen/<uuid:item_pk>/create-job/', 
     views.CreateJobFromNotulenView.as_view(), 
     name='create-job-from-notulen')
```

### Template (templates/meetings/create_job_from_notulen.html)

Form dengan 4 sections:
1. Notulen Item Reference (read-only)
2. Informasi Pekerjaan (editable)
3. Penjadwalan (multi-date, job deadline)
4. Penugasan & Project (assigned_to, project, mesin)

Uses Flatpickr untuk multi-date selection.

## Template: Meeting Detail Update

Added "CREATE JOB" button di notulen items table:

```html
{% if item.status != 'done' and not item.job_created %}
<a href="{% url 'meetings:create-job-from-notulen' item.pk %}" 
   class="btn btn-xs btn-sm btn-link text-success">
    <i class="bi bi-arrow-right-circle"></i>
</a>
{% endif %}
```

Tombol hanya visible jika:
- Notulen belum done
- Belum ada job yang di-create

## Error Handling

### Permission Denied

User tidak dalam hierarchy:
```
HttpResponseForbidden(
    "Anda tidak memiliki akses untuk membuat job dari notulen item ini. "
    "Hanya PIC dan user dalam hierarchy mereka yang dapat membuat job."
)
```

### Form Validation Errors

Ditampilkan di form dengan error messages:
- Daily job tanpa jadwal: "Daily Job harus punya jadwal pelaksanaan"
- Assigned to kosong: "Field required"
- Invalid date format: "Format tanggal tidak valid"

## Testing Checklist

```
□ Permission check works:
  □ Non-hierarchy user blocked
  □ PIC dapat create
  □ Supervisor dapat create
  □ Subordinate dapat create
  □ Admin bypass works

□ Form functionality:
  □ Pre-fill dari notulen works
  □ Multi-date picker responds
  □ Assigned-to dropdown filtered
  □ Form validation works

□ Job creation:
  □ Job created dengan correct fields
  □ JobDate entries created
  □ Notulen status updated to 'progress'
  □ Button disappears from table

□ Data integrity:
  □ notulen_item OneToOne link correct
  □ notulen_target_date filled
  □ job_created FK link working
  □ Hierarchy filtering correct
```

## Troubleshooting

### Button tidak muncul?

1. **Notulen status = done?** → Button hanya untuk open/progress
2. **Job sudah di-create?** → Check notulen.job_created field
3. **User tidak dalam hierarchy?** → Permission denied (tidak ada button)

### Error "User tidak memiliki akses"?

- User harus dalam hierarchy of notulen PIC
- Hierarchy = PIC + supervisors + subordinates
- Check CustomUser.atasan relationships

### Multi-date picker tidak berfungsi?

- Pastikan Flatpickr library loaded (cdn.jsdelivr.net)
- Check browser console untuk JS errors
- Verify field id = 'jadwal_pelaksanaan_picker'

### Job tidak ter-link ke notulen?

- Check: notulen.job_created field
- Check: job.notulen_item field (OneToOne)
- Verify: Notulen status = 'progress'

## Future Enhancements

Fitur yang bisa ditambah:

1. **Email Notification**
   - Notify assigned user ketika job created
   - Include notulen context

2. **Status Sync**
   - Job status change → Update notulen status
   - Notulen done → Mark job done

3. **Bulk Job Creation**
   - Create multiple jobs sekaligus dari meeting
   - Template untuk recurring jobs

4. **Notulen Export**
   - Export meeting + jobs summary
   - Audit trail report

5. **Approval Workflow**
   - Job creation requires supervisor approval
   - Optional untuk critical items

## See Also

- [MEETINGS_WORKFLOW.md](MEETINGS_WORKFLOW.md) - Complete meeting workflow
- [MEETINGS_NOTULEN_DOCUMENTATION.md](MEETINGS_NOTULEN_DOCUMENTATION.md) - Feature overview
- `core/models.py` - Job, CustomUser models
- `meetings/models.py` - Meeting, NotulenItem models
- `meetings/views.py` - CreateJobFromNotulenView
