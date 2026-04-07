# SISTEM NOTIFIKASI OVERDUE JOBS

## 📋 Overview
Sistem notifikasi overdue jobs adalah fitur yang melacak dan menampilkan pekerjaan yang melampaui jadwal yang sudah ditentukan. Sistem ini terintegrasi dengan tiga jenis pekerjaan:
1. **Daily Jobs** - Pekerjaan harian
2. **Project Jobs** - Pekerjaan project
3. **Preventive Jobs** - Pekerjaan pencegahan/maintenance

---

## 🔍 KOMPONEN UTAMA SISTEM

### 1. **DATA MODELS (Model Data)**

#### A. JobDate Model (untuk Daily & Project Jobs)
**Lokasi**: `core/models.py` - Baris 700-750

```python
class JobDate(models.Model):
    job = models.ForeignKey(Job, ...)
    tanggal = models.DateField()
    status = models.CharField(
        choices=['Open', 'Done', 'Pending', 'N/A'],
        default='Open'
    )
    catatan = models.TextField(blank=True, null=True)
```

**Method Overdue:**
- `is_overdue()` - Cek apakah tanggal sudah lewat dan status masih Open/Pending
- `days_overdue()` - Hitung berapa hari sudah overdue
- `days_until_overdue()` - Hitung sisa hari sampai overdue

**Kriteria Overdue:**
```
tanggal < today AND status IN ['Open', 'Pending']
```

#### B. PreventiveJobExecution Model
**Lokasi**: `preventive_jobs/models.py` - Baris 400-500

```python
class PreventiveJobExecution(models.Model):
    template = models.ForeignKey(PreventiveJobTemplate, ...)
    scheduled_date = models.DateField()
    status = models.CharField(
        choices=['Scheduled', 'Done', 'Skipped', 'N/A'],
        default='Scheduled'
    )
    assigned_to = models.ForeignKey(CustomUser, ...)
    actual_date = models.DateField(blank=True, null=True)
    aset = models.ForeignKey(AsetMesin, ...)
```

**Method Overdue:**
- `is_overdue()` - Cek jika status=Scheduled dan scheduled_date < today
- `days_overdue()` - Hitung jumlah hari overdue
- `days_until_due()` - Hitung sisa hari

**Kriteria Overdue:**
```
status == 'Scheduled' AND scheduled_date < today
```

#### C. PreventiveJobNotification Model
**Lokasi**: `preventive_jobs/models.py` - Baris 740-810

Untuk tracking/logging notifikasi yang sudah dikirim:

```python
class PreventiveJobNotification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('24h_before', 'Notifikasi 24 jam sebelum'),
        ('2h_before', 'Notifikasi 2 jam sebelum'),
        ('on_schedule', 'Notifikasi saat jadwal'),
        ('overdue', 'Notifikasi job overdue'),
        ('completed', 'Notifikasi job selesai'),
    ]
    
    execution = models.ForeignKey(PreventiveJobExecution, ...)
    user = models.ForeignKey(CustomUser, ...)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
```

---

## 🎯 ALUR PENGAMBILAN DATA OVERDUE

### 1. Context Processor (Navbar Bell Icon)
**Lokasi**: `core/context_processors.py` - Baris 1-130

Fungsi: `overdue_jobs_context()` - Dipanggil setiap page load untuk menampilkan bell icon

**Proses:**
```
1. Check cache (5 menit TTL, key: 'overdue_jobs_{user.id}')
2. Jika cache miss:
   a. Get user's subordinates (untuk permission check)
   b. Query 3 jenis overdue jobs:
      - Daily jobs dengan overdue dates
      - Project jobs dengan overdue dates
      - Preventive job executions dengan status=Scheduled & scheduled_date < today
   c. Untuk setiap job, ambil:
      - Type (daily_job / project_job / preventive)
      - ID, nama, days_overdue, URL
      - assigned_to, aset (untuk preventive)
   d. Sort by days_overdue (descending)
   e. Limit ke 10 items untuk dropdown (simpan semua di total_overdue_count)
   f. Cache hasil selama 5 menit
3. Return structure:
   {
       'overdue_count': <total limited to 10>,
       'overdue_list': [<10 items>],
       'total_overdue_count': <actual total>
   }
```

**SQL Optimization:**
- `select_related()` untuk JoinedForeignKey (pic, assigned_to, template__pic)
- `prefetch_related()` untuk ManyToMany & Reverse relations (tanggal_pelaksanaan)

**Permission Check:**
```python
Q(pic_id__in=all_user_ids) |  # User adalah PIC atau supervisor dari PIC
Q(assigned_to_id__in=all_user_ids)  # User adalah assigned_to atau supervisor
```

---

### 2. Overdue Jobs Listing Page
**Lokasi**: `core/views.py` - Baris 2670-2800

Fungsi: `overdue_jobs_list_view()` - Full listing page dengan filters

**URL**: `/core/overdue-jobs/`

**Data yang dikumpulkan untuk SETIAP overdue item:**

For **Daily Jobs**:
```python
{
    'type': 'Daily Job',
    'type_short': 'daily',
    'id': <job_id>,
    'name': <job_name>,
    'days_overdue': <int>,
    'url': f'/daily-job/{job.id}/',
    'assigned_to': <full_name>,
    'status': <JobDate.status>,  # Open/Done/Pending/N/A
    'tanggal': <date>,
    'pic': <pic_name>,
    'prioritas': <P1/P2/P3/P4>,
    'fokus': <Perawatan/Perbaikan/Inspeksi/...>
}
```

For **Project Jobs**:
```python
{
    'type': 'Project Job',
    'type_short': 'project',
    'id': <job_id>,
    'name': <job_name>,
    'days_overdue': <int>,
    'url': f'/project-job/{job.id}/',
    'assigned_to': <full_name>,
    'status': <JobDate.status>,
    'tanggal': <date>,
    'pic': <pic_name>,
    'prioritas': <P1/P2/P3/P4>,
    'fokus': <...>,
    'project': <project_name>
}
```

For **Preventive Jobs**:
```python
{
    'type': 'Preventive Job',
    'type_short': 'preventive',
    'id': <execution_id>,
    'name': <template_name>,
    'days_overdue': <int>,
    'url': f'/preventive/execution/{execution.id}/detail/',
    'assigned_to': <full_name>,
    'status': 'Scheduled',  # Always Scheduled for overdue
    'tanggal': <scheduled_date>,
    'pic': <pic_name>,
    'prioritas': <P1/P2/P3/P4>,
    'fokus': <Perawatan/Perbaikan/Inspeksi/...>,
    'aset': <asset_name>
}
```

**Fitur Filtering & Sorting:**
```
Filters:
  - type: daily, project, preventive
  - prioritas: P1, P2, P3, P4
  - assigned_to: username
  
Sorting:
  - days_overdue_desc (default)
  - days_overdue_asc
```

**Pagination**: 25 items per page

---

### 3. Individual Job Detail Pages
**Daily Job Detail**: `daily_job_detail_view()` - Baris 2500-2560
**Project Job Detail**: `project_job_detail_view()` - Baris 2570-2650

**Data yang ditampilkan:**
```python
{
    'job': <Job object>,
    'overdue_dates': [
        {
            'date': <JobDate>,
            'days_overdue': <int>
        },
        ...
    ],
    'regular_dates': [<non-overdue dates>],
    'stats': {
        'total': <int>,
        'done': <int>,
        'pending': <int>,
        'overdue': <int>,
        'open': <int>,
        'na': <int>,
        'progress_percent': <int>
    }
}
```

---

## 📊 DATA YANG MASUK DALAM NOTIFICATION

### A. **Navbar Dropdown (Limited Show - 10 items)**

Setiap item menampilkan:
```
┌─────────────────────────────────────────┐
│  Job Name                    [X days]🔴  │
│  Type: Daily Job / Project Job / ...    │
│  Assigned to: Username                  │
└─────────────────────────────────────────┘
```

- **Nama Pekerjaan**: Deskripsi singkat job
- **Tipe**: 'daily', 'project', atau 'preventive'
- **Days Overdue**: Jumlah hari sudah melampaui jadwal
- **Assigned To**: Siapa yang ditugaskan
- **Link**: URL ke detail page

### B. **Listing Page (Full Details - All items)**

Additional data per item:
```
┌─────────────────────────────────────────┐
│ Type        │ Daily Job / Project / ...   │
│ Job Name    │ Nama pekerjaan              │
│ Tanggal     │ Tanggal yang seharusnya     │
│ Days Overdue│ X hari                      │
│ Status      │ Open / Pending              │
│ Assigned To │ Nama lengkap                │
│ PIC         │ Penanggung jawab            │
│ Prioritas   │ P1 / P2 / P3 / P4           │
│ Fokus       │ Perawatan / Perbaikan / ... │
│ Aset (PrevJob) │ Nama aset/mesin          │
│ Project (ProjectJob) │ Project name              │
└─────────────────────────────────────────┘
```

### C. **Job Detail Page (Most Detailed)**

```
OVERDUE DATES:
┌─────────────────────────────────────────┐
│ Tanggal: DD-MM-YYYY                     │
│ Status: Open / Pending / Done           │
│ Catatan: (Notes if any)                 │
│ Days Overdue: X                         │
│ Action: Update Status, View Details     │
└─────────────────────────────────────────┘

SUMMARY STATS:
┌─────────────────────────────────────────┐
│ Total: X dates                          │
│ Done: X                                 │
│ Pending: X                              │
│ Overdue: X                              │
│ Open: X                                 │
│ N/A: X                                  │
│ Progress: X%                            │
└─────────────────────────────────────────┘
```

---

## 💾 SUMBER DATA

### Database Queries:

**1. Daily Jobs dengan Overdue:**
```sql
SELECT * FROM core_job
WHERE (pic_id IN (...) OR assigned_to_id IN (...))
AND tipe_job = 'Daily'
AND id IN (
    SELECT job_id FROM core_jobdate
    WHERE tanggal < TODAY
    AND status IN ('Open', 'Pending')
)
```

**2. Project Jobs dengan Overdue:**
```sql
SELECT * FROM core_job
WHERE (pic_id IN (...) OR assigned_to_id IN (...))
AND tipe_job = 'Project'
AND id IN (
    SELECT job_id FROM core_jobdate
    WHERE tanggal < TODAY
    AND status IN ('Open', 'Pending')
)
```

**3. Preventive Job Executions Overdue:**
```sql
SELECT * FROM preventive_jobs_preventivejobexecution
WHERE (template__pic_id IN (...) OR assigned_to_id IN (...))
AND status = 'Scheduled'
AND scheduled_date < TODAY
```

---

## 🔐 PERMISSION LOGIC

**User dapat melihat overdue job jika:**

```python
# Untuk Daily/Project Jobs (JobDate):
user == job.pic OR
user == job.assigned_to OR
user IN job.pic.subordinates OR
user IN job.assigned_to.subordinates

# Untuk Preventive Jobs (Execution):
user == template.pic OR
user == execution.assigned_to OR
user IN template.pic.subordinates OR
user IN execution.assigned_to.subordinates
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### Caching Strategy:
- **Duration**: 5 menit (300 detik)
- **Key Pattern**: `overdue_jobs_{user.id}`
- **Cache Invalidation**: Automatic setelah 5 menit

### Database Query Optimization:
- **`select_related()`** untuk Foreign Keys
- **`prefetch_related()`** untuk Reverse relations
- **Query Limiting**: 
  - Navbar: Top 10 items (most overdue)
  - Listing: Paginated 25 items per page

---

## 📱 NOTIFICATION CHANNELS

Saat ini ada log model untuk tracking notifikasi yang dikirim, tetapi notifikasi aktif terintegrasi dengan:

### 1. **WhatsApp Notifications** (via Fontte API)
**Lokasi**: `preventive_jobs/whatsapp_utils.py`

Notifikasi dikirim untuk:
- Checklist sudah diisi: PIC mendapat notifikasi via WhatsApp
- Format message berisi:
  - Job name
  - Asset name
  - Siapa yang isi checklist
  - Waktu pengisian
  - Status (OK/NG)

### 2. **In-App Notifications** (Navbar Bell)
- Real-time display di navbar
- Cached untuk performa
- Click ke view detail atau full listing

### 3. **Notification Logging** (PreventiveJobNotification Model)
Untuk future implementation:
- '24h_before' - Notifikasi 24 jam sebelum jadwal
- '2h_before' - Notifikasi 2 jam sebelum jadwal
- 'on_schedule' - Notifikasi saat jadwal
- 'overdue' - Notifikasi job overdue
- 'completed' - Notifikasi job selesai

---

## 🎨 UI COMPONENTS

### Navbar Bell Icon:
**Lokasi**: `templates/base.html` - Baris 290-350

```html
<li class="nav-item dropdown">
    <a class="nav-link" id="overdueJobsBell">
        <i class="bi bi-bell-fill"></i>
        {% if overdue_count > 0 %}
            <span class="badge bg-danger">{{ overdue_count }}</span>
        {% endif %}
    </a>
    <ul class="dropdown-menu" style="max-height: 400px; overflow-y: auto;">
        <li><h6 class="dropdown-header">Overdue Jobs</h6></li>
        <li><a href="{% url 'core:overdue_jobs' %}">View All</a></li>
        {% for item in overdue_list %}
            <li>
                <a href="{{ item.url }}">
                    <strong>{{ item.name }}</strong><br/>
                    <small>{{ item.assigned_to }}</small>
                    <span class="badge bg-danger">{{ item.days_overdue }}d</span>
                </a>
            </li>
        {% endfor %}
    </ul>
</li>
```

### Styling:
- **Overdue Row Highlighting**: Light red background (#ffe5e5)
- **Badge**: Red color (#dc3545) untuk indicator
- **Border**: Left red border (4px) pada overdue rows

---

## 🔄 REQUEST FLOW

```
1. User membuka halaman (any page)
   ↓
2. Django render template base.html
   ↓
3. Context processor 'overdue_jobs_context' dijalankan
   ↓
4. Check cache first (5 min TTL)
   ↓
   ├─ CACHE HIT → Return cached data
   │
   └─ CACHE MISS → Query database
      ├─ Get Daily Jobs dengan overdue dates
      ├─ Get Project Jobs dengan overdue dates
      ├─ Get Preventive Executions overdue
      ├─ Sort by days_overdue (desc)
      ├─ Limit 10 untuk dropdown (keep total)
      └─ Cache selama 5 menit → Return
   ↓
5. Template render navbar dengan data
   ↓
6. Bell icon muncul dengan badge count
```

---

## 🐛 DEBUG & TESTING

### Untuk test sistem:

```python
# Buka shell Django
python manage.py shell

from core.models import JobDate
from django.utils import timezone

# Buat overdue date
jd = JobDate.objects.create(
    job_id=1,
    tanggal=timezone.now().date() - timedelta(days=5),
    status='Open'
)

# Test methods
jd.is_overdue()  # True
jd.days_overdue()  # 5

# Test context processor
from core.context_processors import overdue_jobs_context
from django.test import RequestFactory

factory = RequestFactory()
request = factory.get('/')
request.user = <your_user>

result = overdue_jobs_context(request)
print(result['overdue_count'])
print(result['overdue_list'])
```

---

## 📝 RINGKASAN

**Sistem notifikasi overdue jobs terdiri dari:**

| Komponen | Fungsi | Data |
|----------|--------|------|
| **JobDate Model** | Track status individual dates | tanggal, status, catatan |
| **PreventiveJobExecution** | Track scheduled jobs | scheduled_date, status, assigned_to |
| **Context Processor** | Gather data untuk navbar | overdue_count, overdue_list (10 items) |
| **List View** | Full listing page | All overdue items with filters |
| **Detail Pages** | Individual job details | Job info + overdue breakdown |
| **Navbar Bell** | Visual indicator | Icon + badge count |
| **WhatsApp Utils** | Send notifications | Fontte API integration |
| **Notification Model** | Log notifikasi | Type, user, read_at, message |

**Performance**: Cache 5 menit, optimized queries dengan select_related & prefetch_related.
