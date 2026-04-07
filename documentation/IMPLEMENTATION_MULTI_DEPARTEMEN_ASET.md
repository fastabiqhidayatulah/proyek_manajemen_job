# 📋 RENCANA IMPLEMENTASI: Multi-Departemen Aset & Fokus Pekerjaan

**Tanggal:** 4 Maret 2026  
**Approach:** OPTION B - Generic Scalable Solution  
**Status:** Planning Phase

---

## 🎯 OVERVIEW

Implementasi sistem untuk support multiple departemen dengan aset structure yang berbeda-beda. Setiap departemen punya:
1. **Tree Structure Aset** (Level 0, 1, 2) - generic via `AsetDepartemen` model
2. **Custom Fokus Pekerjaan** - list yang bisa customize per departemen

**Current State:**
- ✅ Teknik (AsetMesin - sudah ada)
- ✅ Operasional (belum ada)

**Target State:**
- ✅ Teknik + Operasional (consolidated ke AsetDepartemen)
- ✅ Scalable untuk departemen baru (HR, Marketing, Finance, dll)
- ✅ Backward compatible dengan job-job existing

---

## 📊 DATABASE ARCHITECTURE

### Models yang akan dimodifikasi/dibuat:

```
EXISTING (Tidak berubah):
├── Departemen
├── Bagian
├── CustomUser (departemen + bagian FK)
└── AsetMesin (tetap untuk backward compat)

BARU:
├── AsetDepartemen (MPTTModel - Generic Tree)
└── FokusPekerjaan (update - tambah departemen FK)

UPDATE:
└── Job (tambah aset_departemen FK + update fokus)
```

---

## 🔧 DETAIL IMPLEMENTATION

### 1. MODEL: AsetDepartemen (NEW)

**File:** `core/models.py`

```python
class AsetDepartemen(MPTTModel):
    """
    Generic tree-based asset untuk setiap departemen.
    Menggantikan AsetMesin untuk non-teknik departemen.
    
    Level 0: Wajib dipilih (Line, Unit, Tim, dll - tergantung departemen)
    Level 1: Opsional (Mesin, Bagian, Sub Tim, dll)
    Level 2: Opsional (Sub Mesin, Sub Bagian, Divisi, dll)
    """
    nama = CharField(max_length=100)
    parent = TreeForeignKey(
        'self',
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    departemen = ForeignKey(
        Departemen,
        on_delete=CASCADE,
        related_name='aset_departemen_set'
    )
    
    class MPTTMeta:
        order_insertion_by = ['nama']
    
    class Meta:
        verbose_name = "Aset Departemen"
        verbose_name_plural = "Daftar Aset Departemen"
        unique_together = [('departemen', 'nama', 'parent')]  # Prevent duplicate
        indexes = [
            models.Index(fields=['departemen', 'level']),
        ]
    
    def __str__(self):
        ancestors = self.get_ancestors(include_self=True)
        return ' > '.join([a.nama for a in ancestors])
    
    @property
    def level_display(self):
        """Return level (0, 1, 2) untuk current node"""
        return self.level
    
    def get_level_0_root(self):
        """Get Level 0 parent (akar/root)"""
        ancestors = self.get_ancestors()
        return ancestors.first() if ancestors.exists() else self
```

---

### 2. MODEL: Update FokusPekerjaan

**File:** `core/models.py`

**Current:**
```python
fokus = CharField(
    max_length=50, 
    choices=FOKUS_CHOICES,
    default='Perawatan'
)
```

**Update to:**
```python
class FokusPekerjaan(models.Model):
    """
    Fokus pekerjaan yang bisa customize per departemen.
    """
    nama = CharField(max_length=100)
    departemen = ForeignKey(
        Departemen,
        on_delete=CASCADE,
        related_name='fokus_pekerjaan_set'
    )
    urutan = IntegerField(default=0)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Fokus Pekerjaan"
        verbose_name_plural = "Daftar Fokus Pekerjaan"
        unique_together = [('departemen', 'nama')]
        ordering = ['departemen', 'urutan', 'nama']
        indexes = [
            models.Index(fields=['departemen', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.nama} ({self.departemen.nama_departemen})"
```

---

### 3. MODEL: Update Job

**File:** `core/models.py`

**Current (Teknik only):**
```python
aset = ForeignKey(AsetMesin, ...)
fokus = CharField(choices=FOKUS_CHOICES)
prioritas = CharField(choices=PRIORITAS_CHOICES)
```

**Update to:**
```python
# Keep for backward compat (Teknik)
aset_mesin = ForeignKey(
    AsetMesin,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='jobs_teknik'
)

# Generic untuk semua departemen (NEW)
aset_departemen = ForeignKey(
    AsetDepartemen,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='jobs'
)

# Replace CharField dengan FK
fokus = ForeignKey(
    FokusPekerjaan,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='jobs_fokus'
)

# Helper method
def get_aset_display(self):
    """Smart display aset based on departemen"""
    if self.aset_mesin:
        return str(self.aset_mesin)  # "Line > Mesin > Sub"
    elif self.aset_departemen:
        return str(self.aset_departemen)  # Generic
    return "-"

def get_departemen_aset_type(self):
    """Return tipe aset yang digunakan"""
    if self.aset_mesin:
        return 'mesin'
    elif self.aset_departemen:
        return 'departemen'
    return None
```

---

## 📝 MIGRATION PLAN

### Phase 1: Create New Models
**Files to Create:**
- Migration: `0XXX_create_aset_departemen.py`
- Migration: `0XXX_create_fokus_pekerjaan.py`

### Phase 2: Update Existing Models
**Files to Modify:**
- Migration: `0XXX_update_job_model.py` (add aset_departemen + fokus FK)

### Phase 3: Data Migration (Backward Compat)
**Files to Create:**
- Migration: `0XXX_auto_migrate_fokus_pekerjaan.py`
  - Teknik jobs: fokus='Perawatan' → fokus_id=<FokusPekerjaan.id>
  - Keep existing aset_mesin unchanged

---

## 🔄 BACKWARD COMPATIBILITY

**Existing Data:**
```
Jobs (Teknik):
├── aset_mesin = AsetMesin instance (tetap)
├── fokus = 'Perawatan' (string) → migrate to FokusPekerjaan.id
├── aset_departemen = NULL
```

**Migration Strategy:**
1. Create FokusPekerjaan records untuk Teknik (Perawatan, Perbaikan, Proyek, Lainnya)
2. Auto-migrate existing jobs' fokus string → FokusPekerjaan FK
3. Set aset_departemen = NULL untuk existing jobs (tetap use aset_mesin)

**Jobs tetap work:**
- ✅ Display job detail - aset_mesin still works
- ✅ List view - both aset_mesin & aset_departemen visible
- ✅ Edit job - aset_mesin still selectable

---

## 📋 FILES TO MODIFY/CREATE

### MODELS
- [ ] `core/models.py` - Add AsetDepartemen + Update Job + Update FokusPekerjaan

### FORMS
- [ ] `core/forms.py` - Update JobForm (dynamic field visibility)

### ADMIN
- [ ] `core/admin.py` - Add AsetDepartemenAdmin + Update FokusPekerjaanAdmin

### VIEWS
- [ ] `core/views.py` - Update job_form_view (pass aset context)
- [ ] `core/views.py` - Update job_list_view (group by departemen)
- [ ] `core/views.py` - Update job detail views

### TEMPLATES
- [ ] `templates/job_form.html` - Show/hide aset fields dynamically
- [ ] `templates/job_table.html` - Dynamic aset display
- [ ] `templates/core/daily_job_detail.html` - Display aset
- [ ] `templates/core/project_job_detail.html` - Display aset

### MIGRATIONS
- [ ] `0XXX_create_aset_departemen.py`
- [ ] `0XXX_create_fokus_pekerjaan.py`
- [ ] `0XXX_update_job_fields.py`
- [ ] `0XXX_migrate_fokus_data.py`

---

## 🎯 IMPLEMENTATION STEPS (EXECUTION ORDER)

### STEP 1: Create Models (Database Layer)
1. Add `AsetDepartemen` model ke `core/models.py`
2. Update `Job` model: add aset_departemen + update fokus (CharField → FK)
3. Create `FokusPekerjaan` model
4. Run: `makemigrations` 
5. Run: `migrate`

### STEP 2: Data Migration (Backward Compat)
1. Create manual migration untuk auto-populate FokusPekerjaan (Teknik)
2. Create migration untuk auto-migrate existing jobs' fokus
3. Run: `migrate`

### STEP 3: Forms & Validation
1. Update `JobForm.__init__()` - Dynamic field visibility
2. Add form logic untuk filter aset & fokus based on departemen
3. Test form validation

### STEP 4: Admin Interfaces
1. Create `AsetDepartemenAdmin` (tree view dengan department filter)
2. Create `FokusPekerjaanAdmin` (list per departemen)
3. Update `JobAdmin` (show aset_departemen field)
4. Test admin interfaces

### STEP 5: Views & Controllers
1. Update `job_form_view()` - pass aset context
2. Update `job_list_view()` - group by departemen
3. Update job detail views - display correct aset

### STEP 6: Templates
1. Update `job_form.html` - conditional field rendering
2. Update `job_table.html` - dynamic aset display
3. Update `job_detail.html` templates
4. Test responsive design

### STEP 7: Testing & Validation
1. Manual test: Create job untuk Teknik (aset_mesin selected)
2. Manual test: Create job untuk Operasional (aset_departemen selected)
3. Manual test: Verify backward compat (existing jobs still work)
4. Manual test: Focus pekerjaan filtering
5. Manual test: Top-level view tabbed by departemen
6. Manual test: Filter by departemen

### STEP 8: Documentation & Cleanup
1. Add data migration guide untuk future departemen
2. Add admin guide untuk manage aset & fokus
3. Update README if needed

---

## 🎨 UI/UX CHANGES

### Job Form (JobForm View)
```
Before (Teknik only):
├── Line ▼
├── Mesin ▼
├── Sub Mesin ▼
├── Fokus: [Perawatan|Perbaikan|...]
├── Prioritas: [P1|P2|...]

After (Multi-departemen):
├── [IF TEKNIK]
│   ├── Line ▼ (required)
│   ├── Mesin ▼ (optional)
│   └── Sub Mesin ▼ (optional)
├── [IF OPERASIONAL]
│   ├── Unit/Bagian ▼ (required, from AsetDepartemen)
│   └── Sub Bagian ▼ (optional, from AsetDepartemen)
├── Fokus: ▼ [Dynamic list per departemen]
├── Prioritas: [P1|P2|...]
```

### Job List View (Top-Level)
```
Filter: ▼ [All / Teknik / Operasional]

📌 TAB: TEKNIK (45 Jobs)
┌─────────────────────────────────┐
│No│Name│Type│Aset (Line)│Focus│ │
├─────────────────────────────────┤
│1 │...  │... │Line 1      │Perw │ │
└─────────────────────────────────┘

📌 TAB: OPERASIONAL (32 Jobs)
┌─────────────────────────────────┐
│No│Name│Type│Aset (Unit)│Focus│ │
├─────────────────────────────────┤
│1 │...  │... │Unit Prod   │Plan │ │
└─────────────────────────────────┘
```

---

## ⚙️ ADMIN DATA SETUP

Setelah implementasi, admin perlu:

### 1. Populate AsetDepartemen untuk Teknik
```
Teknik/
├── Line 1
│   ├── CNC
│   │   ├── Motor
│   │   └── PLC
│   └── Welding
├── Line 2
└── ...
```

### 2. Populate AsetDepartemen untuk Operasional
```
Operasional/
├── Bagian Produksi
│   ├── Shift Pagi
│   │   └── Station A
│   └── Shift Sore
├── Bagian Administrasi
│   ├── Finance
│   └── HR
└── ...
```

### 3. Populate FokusPekerjaan
```
Teknik:
├── Perawatan (urutan: 1)
├── Perbaikan (urutan: 2)
├── Proyek (urutan: 3)
└── Lainnya (urutan: 4)

Operasional:
├── Planning (urutan: 1)
├── Koordinasi (urutan: 2)
├── Monitoring (urutan: 3)
├── Laporan (urutan: 4)
└── Evaluasi (urutan: 5)
```

---

## 🚀 FUTURE EXTENSIBILITY

Untuk tambah departemen baru (misal: HR, Marketing):

1. Admin: Create AsetDepartemen records dengan departemen=HR
   - HR/
     - Recruitment
       - Sourcing
     - Training
       - ...

2. Admin: Create FokusPekerjaan records dengan departemen=HR
   - Recruitment, Training, Compliance, ...

3. Zero code changes! ✅
   - Forms auto-filter based on user.departemen
   - Views auto-work dengan generic aset_departemen

---

## 📊 EFFORT ESTIMATE

| Phase | Task | Est. Time |
|-------|------|-----------|
| 1 | Models + Migrations | 2 hours |
| 2 | Data Migration & Testing | 1 hour |
| 3 | Forms & Validation | 1.5 hours |
| 4 | Admin Interfaces | 1 hour |
| 5 | Views & Controllers | 1.5 hours |
| 6 | Templates & UI | 2 hours |
| 7 | Testing & QA | 2 hours |
| 8 | Documentation | 1 hour |
| **TOTAL** | | **12 hours** |

---

## ✅ ACCEPTANCE CRITERIA

- [ ] AsetDepartemen model created & working
- [ ] FokusPekerjaan model created & working
- [ ] Job model updated dengan aset_departemen + fokus FK
- [ ] Backward compatible: existing jobs masih work
- [ ] Auto-migration fokus data successful
- [ ] JobForm dynamic field visibility works (Teknik vs Operasional)
- [ ] JobForm fokus filtering per departemen works
- [ ] Admin interfaces CRUD working (AsetDepartemen, FokusPekerjaan)
- [ ] Job list view grouped by departemen (tab view)
- [ ] Job detail page show correct aset
- [ ] Top-level user dapat filter & view semua jobs
- [ ] All manual tests passed
- [ ] Zero errors in migration
- [ ] Documentation complete

---

## 🛑 RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Data loss migration | HIGH | Create backup sebelum migrate |
| Backward compat broken | HIGH | Test existing jobs extensively |
| Performance (tree query) | MEDIUM | Add indexes di AsetDepartemen |
| Form validation fail | MEDIUM | Comprehensive unit tests |
| Admin complexity | LOW | Good UI + inline editing |

---

## 📞 QUESTIONS BEFORE START

**Akan ditanyakan sebelum implementasi dimulai:**
1. Approval dari timeline estimate?
2. Backup sudah siap sebelum migrate?
3. Testing environment ready?
4. Departemen Teknik & Operasional sudah siap di admin?

---

**NEXT ACTION:** Review & Approve plan ini, kemudian proceed dengan STEP 1.

