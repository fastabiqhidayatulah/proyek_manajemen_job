# 📋 RINGKASAN LOGIKA HIERARCHY & ACCESS CONTROL

## 1. STRUKTUR HIERARKI ORGANISASI

### User Hierarchy
```
                        DIREKSI
                           |
                     ---- ---- ----
                    |     |      |
                  MANAJER MANAJER MANAJER
                    |      |      |
               ---- ----  ----  ---- ----
              |    |     |    |  |    |
            FOREMAN ... (subordinates berjenjang)
              |
            OPERATOR / CREW
```

**Model:** `CustomUser.atasan` → recursive relationship
```python
atasan = ForeignKey('self', null=True, blank=True, related_name='bawahan')
```

**Method:** `CustomUser.get_all_subordinates()`
- Mengambil **SEMUA subordinate** secara recursive (tidak peduli level)
- Mencegah circular reference dengan `_visited` set
- Contoh: Jika Direksi query `get_all_subordinates()`, akan dapat seluruh karyawan di bawahnya

---

## 2. PROJECT ACCESS CONTROL (BIDIRECTIONAL HIERARCHY)

### Method: `Project.can_access(user)`

Seorang user bisa **MELIHAT & BEKERJA** di project jika memenuhi SALAH SATU kriteria:

| Kriteria | Deskripsi | Contoh |
|----------|-----------|---------|
| **1. Creator/Owner** | User adalah `manager_project` | Foreman membuat project → hanya Foreman yang bisa akses |
| **2. Project Di-Share** | `is_shared = True` | Admin share ke semua user → semua bisa lihat |
| **3. SUPERVISOR** | User adalah atasan (any level) dari `manager_project` | Manajer bisa lihat project milik Foreman (subordinatenya) |
| **4. SUBORDINATE** | User adalah bawahan dari `manager_project` | Foreman membuat project → Operatornya (anak buahnya) otomatis bisa lihat & edit |

**⭐ BIDIRECTIONAL:** Both supervisors AND subordinates dapat akses project

```python
def can_access(self, user):
    # 1. Pemilik project
    if self.manager_project == user:
        return True
    
    # 2. Project yang di-share ke semua
    if self.is_shared:
        return True
    
    # 3. Atasan dari pemilik (recursive hierarchy)
    if self.manager_project:
        user_subordinates = user.get_all_subordinates()
        if self.manager_project.id in user_subordinates:
            return True
    
    return False
```

### Scenario: Foreman membuat project (tidak di-share)

```
SITUASI:
- Foreman (Budi) membuat Project "Maintenance Rutin"
- is_shared = False (hanya private)
- Budi.atasan = Manajer (Rani)
- Rani.atasan = Direksi (Boedi)
- Operator Dadang adalah bawahan dari Budi

AKSES YANG BISA AKSES (BIDIRECTIONAL):
✅ Budi (creator/owner) - bisa lihat & edit semua jobs
✅ Rani (atasan Budi) - bisa lihat & edit semua jobs (SUPERVISOR)
✅ Boedi (atasan Rani) - bisa lihat & edit semua jobs (SUPERVISOR)
✅ Dadang (bawahan Budi) - bisa lihat & edit semua jobs (NEW - SUBORDINATE)
❌ Toni (foreman lain) - TIDAK bisa akses (different branch)
❌ Other users - TIDAK bisa akses
```

---

## 3. JOB VISIBILITY & PERMISSION RULES

### View: `project_detail_view()`

Setelah user lolos `can_access()`, job visibility tergantung role user di project:

#### **CASE 1: USER adalah Owner/Pemilik Project**
```
Akses: FULL - Lihat SEMUA jobs di project
Logika: project.manager_project == user
```

#### **CASE 2: Project di-Share**
```
Akses: FULL - Lihat SEMUA jobs di project (workspace sharing)
Logika: project.is_shared == True
```

#### **CASE 3: USER adalah Atasan dari Owner (Supervisor Mode)**
```
Akses: FULL - Lihat SEMUA jobs untuk review/oversight
Logika: user.get_all_subordinates() contains project.manager_project.id
Catatan: Ini untuk review & oversight oleh manajemen
```

#### **CASE 4: USER adalah Bawahan dari Owner (Subordinate Mode) - BIDIRECTIONAL**
```
Akses: FULL - Lihat SEMUA jobs untuk kolaborasi team
Logika: project.manager_project.get_all_subordinates() contains user.id
Catatan: Ini untuk memberikan akses team members yang bekerja di bawah project owner

Contoh:
- Foreman (Budi) membuat Project, Operator (Dadang) adalah bawahan Budi
- Dadang otomatis bisa lihat & edit SEMUA jobs di project Budi
```

#### **CASE 5: USER adalah Non-Owner, Non-Supervisor, Non-Shared, Non-Subordinate**
```
Akses: FILTERED - Hanya lihat job yang relevan ke mereka

User bisa lihat job jika:
1. Dia adalah PIC (pembuat job) → Q(pic=user)
2. Dia adalah assigned_to (ditugaskan job) → Q(assigned_to=user)
3. Dia adalah supervisor dari PIC → Q(pic_id__in=subordinate_ids)
4. Dia adalah supervisor dari assigned_to → Q(assigned_to_id__in=subordinate_ids)

Query:
jobs_in_project.filter(
    Q(pic=user) |
    Q(assigned_to=user) |
    Q(pic_id__in=subordinate_ids) |
    Q(assigned_to_id__in=subordinate_ids)
)
```

---

## 4. JOB CREATION PERMISSION

### View: `job_form_view()` - Create Job

```python
# Hanya user yang bisa akses project yang bisa tambah job
if not project.can_access(user):
    return error("Tidak punya akses ke project ini")

# Filter PIC choices: Hanya bisa assign job ke diri sendiri atau subordinate
# PIC = Person In Charge (pembuat/yang bertanggung jawab)
```

**Logic:**
- Owner project bisa assign job ke siapa saja di subordinate-nya
- Subordinate project yang mendapat akses hanya bisa assign ke subordinate mereka
- Sharing users: Full access sesuai project role

---

## 5. EKSPORT PROJECT DETAIL (PDF/EXCEL)

### Akses Export
```python
def export_project_detail_pdf(request, project_id):
    # 1. Cek project.can_access(user)
    # 2. Cek project.can_manage(user) - hanya owner bisa export
    # 3. Jika tidak owner tapi supervisor → bisa readonly export
```

**Siapa yang bisa export:**
- ✅ Project owner
- ✅ Project atasan (supervisor) → bisa export untuk laporan
- ✅ Shared users jika is_shared=True
- ❌ Non-relevant users

---

## 6. CONTOH SKENARIO LENGKAP

### Scenario: Multi-Level Hierarchy

```
STRUKTUR ORGANISASI:
                    Direksi (Boedi)
                         |
                    Manajer (Rani)
                    /         \
                Foreman1     Foreman2
               (Budi)        (Toni)
                |              |
            Operator1      Operator2
            (Dadang)       (Eka)


PROJECT DIBUAT:
- Project "Maintenance AC" dibuat oleh Budi (Foreman1)
- is_shared = FALSE
- manager_project = Budi
- Ada 3 jobs: Job1, Job2, Job3

AKSES HASIL (BIDIRECTIONAL):
┌─────────────────────────────────────────────┐
│ User      │ Akses? │ Job Visibility        │
├─────────────────────────────────────────────┤
│ Budi      │ ✅ YES │ Lihat SEMUA (full)    │ Owner
│ Rani      │ ✅ YES │ Lihat SEMUA (full)    │ Supervisor
│ Boedi     │ ✅ YES │ Lihat SEMUA (full)    │ Supervisor (indirect)
│ Dadang    │ ✅ YES │ Lihat SEMUA (full)    │ Subordinate (NEW!)
│ Toni      │ ❌ NO  │ - BLOCKED -           │ Different branch
│ Eka       │ ❌ NO  │ - BLOCKED -           │ Different branch
│ Other User│ ❌ NO  │ - BLOCKED -           │ No relation
└─────────────────────────────────────────────┘

BIDIRECTIONAL FEATURE:
✅ Atasan (Rani, Boedi) bisa edit jobs di project bawahan (Budi)
✅ Bawahan (Dadang) bisa edit jobs di project atasannya (Budi)
✅ Semua bisa lihat & edit SEMUA jobs dalam project

JIKA is_shared = TRUE:
- SEMUA user dapat lihat project & SEMUA jobs
```

---

## 7. PERMISSION MATRIX

```
                   │ Owner │ Supervisor │ Shared │ Subordinate │ Other
─────────────────────────────────────────────────────────────────────────
Can Access Project │  ✅   │     ✅     │   ✅   │     ✅ NEW  │   ❌
View All Jobs      │  ✅   │     ✅     │   ✅   │     ✅ NEW  │   ❌
Create Job         │  ✅   │     ✅     │   ✅   │     ✅ NEW  │   ❌
Edit Job           │  ✅   │     ✅     │   ✅   │     ✅ NEW  │   ❌
Edit Project       │  ✅   │     ✅ NEW │   ❌   │     ✅ NEW  │   ❌
Assign to Self     │  ✅   │     ✅     │   ✅   │     ✅      │   ❌
Export PDF/Excel   │  ✅   │     ✅     │   ✅   │     ✅ NEW  │   ❌

NEW = Recently implemented bidirectional access
✅ = Full permission
❌ = No permission
```

---

## 8. BIDIRECTIONAL ACCESS - IMPLEMENTATION DETAILS

### What Was Fixed (Latest Session)

**Problem Identified:**
- Subordinates could NOT auto-access supervisor's projects
- Only supervisors could access subordinates' projects (one-way)

**Solution Implemented:**

1. **Updated `Project.can_access()` - Added Case B (Subordinate)**
   ```python
   # Case 4: BAWAHAN dari project manager (BIDIRECTIONAL)
   manager_subordinates = self.manager_project.get_all_subordinates()
   if user.id in manager_subordinates:
       return True
   ```
   - Location: [core/models.py](core/models.py#L165-L180)

2. **Updated `Project.can_manage()` - Bidirectional Management**
   ```python
   # Case 2B: Subordinate of project manager
   manager_subordinates = self.manager_project.get_all_subordinates()
   if user.id in manager_subordinates:
       return True
   ```
   - Location: [core/models.py](core/models.py#L181-L203)

3. **Updated `project_detail_view()` - Subordinate Job Visibility**
   ```python
   # NEW: Check if user is subordinate of project owner
   is_subordinate_of_owner = (
       project.manager_project and 
       user.id in project.manager_project.get_all_subordinates()
   )
   # Show ALL jobs to subordinates too
   if ... or is_subordinate_of_owner:
   ```
   - Location: [core/views.py](core/views.py#L405-L411)

### Results

✅ **IMPLEMENTED & TESTED:**
- Subordinates can NOW access supervisor's projects
- Subordinates can NOW edit/manage supervisor's projects
- Subordinates can NOW create jobs in supervisor's projects
- Both directions work (supervisor → subordinate, subordinate → supervisor)

---

## 9. CODE REFERENCES

### Model Access Control
- **File:** `core/models.py` Lines 145-203
- **Methods:** `Project.can_access()`, `Project.can_manage()`

### View Permission Logic
- **File:** `core/views.py` Lines 377-430 (`project_detail_view`)
- **File:** `core/views.py` Lines 487-598 (project list with hierarchy filter)

### User Hierarchy
- **File:** `core/models.py` Lines 13-94
- **Method:** `CustomUser.get_all_subordinates()` (recursive subordinate getter)

---

## 10. KESIMPULAN LOGIKA

✅ **SUDAH IMPLEMENTED (BIDIRECTIONAL):**
1. Hierarki org dengan recursive atasan-bawahan
2. Project access: creator + shared + atasan + **bawahan** (BIDIRECTIONAL)
3. Job filtering berdasarkan user role di project
4. Supervisor (atasan) bisa full view project milik bawahan
5. Subordinate (bawahan) bisa full view project milik supervisor (NEW)
6. Multilevel hierarchy support (atasan dari atasan, dll)
7. Full editing capability untuk both supervisor & subordinate
8. Job creation capability untuk both supervisor & subordinate

✅ **SUDAH VALIDATED:**
1. ✅ Supervisor BISA MENGEDIT job di project milik bawahan
2. ✅ Supervisor BISA TAMBAH job baru di project milik bawahan
3. ✅ Bawahan BISA MENGEDIT job di project milik supervisor
4. ✅ Bawahan BISA TAMBAH job baru di project milik supervisor
5. ✅ Django system check passing (no errors)

⚠️ **KNOWN LIMITATION:**
- Sibling karyawan (bukan atasan/bawahan) TIDAK bisa akses project (by design)
- Non-related users TIDAK bisa akses project (by design)
- Requires explicit sharing (is_shared=True) untuk general access

---

**Update Date:** 16 Dec 2025
**System Version:** Django 5.2.8 + PostgreSQL
**Latest Changes:** Bidirectional hierarchy access implementation (supervisor ↔ subordinate)
