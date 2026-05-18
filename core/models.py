from django.db import models
from django.contrib.auth.models import AbstractUser
from mptt.models import MPTTModel, TreeForeignKey
import os 
import json 
from django.core.serializers.json import DjangoJSONEncoder
from django.core.cache import cache 

# ==============================================================================
# 1. MODEL AKUN / USER (UNTUK LOGIN)
# ==============================================================================
class Jabatan(models.Model):
    nama_jabatan = models.CharField(max_length=100, unique=True)
    class Meta:
        verbose_name = "Jabatan"
        verbose_name_plural = "Daftar Jabatan" 
    def __str__(self):
        return self.nama_jabatan


# ==============================================================================
# MODEL DEPARTEMEN & BAGIAN (UNTUK ROUTING UI/FITUR)
# ==============================================================================
class Departemen(models.Model):
    """
    Model Departemen - Level parent dalam hierarki organisasi.
    Misal: Departemen Teknik, Departemen Produksi, dll
    """
    nama_departemen = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Nama Departemen"
    )
    kepala_departemen = models.OneToOneField(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departemen_dipimpin',
        help_text="User yang menjadi kepala departemen ini"
    )
    deskripsi = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi fungsi departemen"
    )
    google_calendar_id = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name="Google Calendar ID",
        help_text="Calendar ID dari Google Workspace untuk departemen ini (cth: abc123@group.calendar.google.com)"
    )
    google_sheet_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Google Spreadsheet ID (Meeting Reminder)",
        help_text="ID spreadsheet untuk meeting reminder auto-sync (copy dari URL: docs.google.com/spreadsheets/d/{ID}/edit)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Departemen"
        verbose_name_plural = "Daftar Departemen"
        ordering = ['nama_departemen']
    
    def __str__(self):
        return self.nama_departemen


class Bagian(models.Model):
    """
    Model Bagian - Level child (subordinat) dari Departemen.
    Misal: Bagian Pemper, Bagian Elektrik (dalam Departemen Teknik)
    """
    nama_bagian = models.CharField(
        max_length=100,
        verbose_name="Nama Bagian"
    )
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.CASCADE,
        related_name='daftar_bagian',
        verbose_name="Departemen"
    )
    kepala_bagian = models.OneToOneField(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bagian_dipimpin',
        help_text="User yang menjadi kepala bagian ini"
    )
    deskripsi = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi fungsi bagian"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bagian"
        verbose_name_plural = "Daftar Bagian"
        unique_together = [('departemen', 'nama_bagian')]
        ordering = ['departemen', 'nama_bagian']
        indexes = [
            models.Index(fields=['departemen']),
        ]
    
    def __str__(self):
        return f"{self.nama_bagian} ({self.departemen.nama_departemen})"


# ==============================================================================
# MODEL DEPARTEMEN FEATURE (PERMISSION MANAGEMENT)
# ==============================================================================
class DepartemenFeature(models.Model):
    """
    Model untuk manage fitur/menu mana saja yang bisa diakses per departemen.
    Misal: Departemen Teknik bisa akses Dashboard, Report, tapi tidak Analytics
    """
    
    FEATURE_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('project', 'Project Management'),
        ('job', 'Job Management'),
        ('preventive_jobs', 'Preventive Jobs'),
        ('maintenance_report', 'Maintenance Report'),
        ('inventory', 'Inventory Management'),
        ('toolkeeper', 'Toolkeeper'),
        ('meetings', 'Meetings & Notulen'),
        ('analytics', 'Analytics & Reports'),
        ('settings', 'Settings'),
    ]
    
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.CASCADE,
        related_name='features_allowed'
    )
    
    feature_key = models.CharField(
        max_length=50,
        choices=FEATURE_CHOICES,
        verbose_name="Fitur/Menu"
    )
    
    is_enabled = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Departemen Feature Permission"
        verbose_name_plural = "Daftar Departemen Feature Permission"
        unique_together = [('departemen', 'feature_key')]
        ordering = ['departemen', 'feature_key']
        indexes = [
            models.Index(fields=['departemen', 'is_enabled']),
        ]
    
    def __str__(self):
        return f"{self.departemen.nama_departemen} - {self.get_feature_key_display()}"
    
    @staticmethod
    def get_feature_display_name(feature_key):
        """Get display name dari feature key"""
        feature_dict = dict(DepartemenFeature.FEATURE_CHOICES)
        return feature_dict.get(feature_key, feature_key)


class CustomUser(AbstractUser):
    jabatan = models.ForeignKey(Jabatan, on_delete=models.SET_NULL, null=True, blank=True)
    atasan = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='bawahan' 
    )
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anggota_departemen',
        verbose_name="Departemen"
    )
    bagian = models.ForeignKey(
        Bagian,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anggota_bagian',
        verbose_name="Bagian"
    )
    nomor_telepon = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Nomor telepon untuk integrasi WA Fontte (e.g., 62812XXXXXXXX)"
    )
    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Daftar Pengguna"
        indexes = [
            models.Index(fields=['atasan', 'id']),  # For hierarchy traversal
            models.Index(fields=['username']),      # For user lookups
            models.Index(fields=['departemen']),    # For departemen filtering
            models.Index(fields=['bagian']),        # For bagian filtering
        ]
    def __str__(self):
        return self.username
    
    def normalize_nomor_telepon(self, nomor):
        """
        Normalize nomor telepon dari format lokal ke internasional
        0812345678 -> 628123456789
        628123456789 -> 628123456789 (already correct)
        """
        if not nomor:
            return None
        
        # Hapus semua karakter non-digit
        nomor_clean = ''.join(filter(str.isdigit, nomor))
        
        # Jika kosong setelah cleaning
        if not nomor_clean:
            return None
        
        # Jika sudah format internasional (dimulai dengan 62)
        if nomor_clean.startswith('62'):
            return nomor_clean
        
        # Jika format lokal (dimulai dengan 0)
        if nomor_clean.startswith('0'):
            # Hapus 0 di awal dan tambah 62
            return '62' + nomor_clean[1:]
        
        # Format tidak dikenali, return as is
        return nomor_clean
    
    def save(self, *args, **kwargs):
        """
        Override save untuk:
        1. Auto-normalize nomor telepon
        2. Auto-set departemen dari bagian
        3. Invalidate cache jika hierarchy berubah
        """
        # Track if atasan changed
        old_atasan = None
        if self.pk:
            try:
                old = CustomUser.objects.get(pk=self.pk)
                old_atasan = old.atasan_id
            except CustomUser.DoesNotExist:
                pass
        
        if self.nomor_telepon:
            self.nomor_telepon = self.normalize_nomor_telepon(self.nomor_telepon)
        
        # Auto-set departemen dari bagian jika bagian sudah set
        if self.bagian:
            self.departemen = self.bagian.departemen
        
        super().save(*args, **kwargs)
        
        # Invalidate cache if hierarchy changed
        if self.atasan_id != old_atasan:
            self._invalidate_subordinates_cache()
            if self.atasan:
                self.atasan._invalidate_subordinates_cache()
    
    def _invalidate_subordinates_cache(self):
        """Invalidate subordinates cache for this user and all supervisors"""
        cache_key = f"subordinates_{self.id}"
        cache.delete(cache_key)
        
        # Also invalidate cache for all supervisors up the chain
        current = self
        while current.atasan:
            supervisor_key = f"subordinates_{current.atasan.id}"
            cache.delete(supervisor_key)
            current = current.atasan
    
    def get_all_subordinates(self, _visited=None):
        """
        Get all subordinates recursively with circular reference prevention and caching.
        Args:
            _visited: Set of visited IDs (for internal recursion tracking)
        Returns:
            List of subordinate user IDs
        """
        # Try cache first (only when called without _visited, i.e., top-level call)
        if _visited is None:
            cache_key = f"subordinates_{self.id}"
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            _visited = set()
        
        # Prevent infinite loops due to circular organizational references
        if self.id in _visited:
            return []
        
        _visited.add(self.id)
        subordinates = []
        direct_subs = self.bawahan.all()
        
        for sub in direct_subs:
            if sub.id not in _visited:
                subordinates.append(sub.id)
                # Recursively get subordinates of this user
                # PENTING: Pass _visited directly (tidak copy) supaya bisa track semua visited nodes
                subordinates.extend(sub.get_all_subordinates(_visited=_visited))
        
        result = list(set(subordinates))
        
        # Cache only at top level (when _visited was None initially)
        if _visited and len(_visited) > 0:
            cache_key = f"subordinates_{self.id}"
            cache.set(cache_key, result, 3600)  # Cache for 1 hour
        
        return result 

# ==============================================================================
# 2. MODEL PERSONIL (ANAK BUAH / BUKAN USER LOGIN)
# ==============================================================================
class Personil(models.Model):
    nama_lengkap = models.CharField(max_length=200)
    penanggung_jawab = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='personil_team' 
    )
    class Meta:
        verbose_name = "Personil"
        verbose_name_plural = "Daftar Personil" 
    def __str__(self):
        return f"{self.nama_lengkap} (Team: {self.penanggung_jawab.username})"

# ==============================================================================
# 3. MODEL ASET (LINE, MESIN, SUB MESIN)
# ==============================================================================
class AsetMesin(MPTTModel):
    nama = models.CharField(max_length=100)
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    class MPTTMeta:
        order_insertion_by = ['nama']
    class Meta:
        verbose_name = "Aset Mesin"
        verbose_name_plural = "Daftar Aset Mesin" 
    def __str__(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
            return ' > '.join([ancestor.nama for ancestor in ancestors])
        except:
            return self.nama


# ==============================================================================
# 3.5 MODEL ASET DEPARTEMEN (GENERIC - UNTUK SEMUA DEPARTEMEN NON-TEKNIK)
# ==============================================================================
class AsetDepartemen(MPTTModel):
    """
    Generic tree-based asset untuk setiap departemen.
    Menggantikan AsetMesin untuk departemen yang bukan Teknik.
    
    Level 0: Wajib dipilih (Unit, Tim, Bagian, dll - tergantung departemen)
    Level 1: Opsional (Sub Unit, Sub Tim, Sub Bagian, dll)
    Level 2: Opsional (Sub-Sub Unit, Divisi, dll)
    
    Example:
    OPERASIONAL:
    └── Bagian Produksi (Level 0)
        ├── Shift Pagi (Level 1)
        │   └── Station A (Level 2)
        └── Shift Sore (Level 1)
    
    MARKETING:
    └── Tim Digital (Level 0)
        ├── Sub Tim Social (Level 1)
        └── Sub Tim Content (Level 1)
    """
    nama = models.CharField(max_length=100)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.CASCADE,
        related_name='aset_departemen_set'
    )
    
    class MPTTMeta:
        order_insertion_by = ['nama']
    
    class Meta:
        verbose_name = "Aset Departemen"
        verbose_name_plural = "Daftar Aset Departemen"
        indexes = [
            models.Index(fields=['departemen']),
        ]
    
    def __str__(self):
        """
        Display name dengan indentasi berdasarkan level untuk hierarchy visual.
        Level 0: "Operasional"
        Level 1: "  └─ Exim" atau "  └─ HRD & Umum"
        Level 2: "    └─ Export &am Import"
        """
        if self.level == 0:
            return self.nama
        elif self.level == 1:
            return f"  └─ {self.nama}"
        elif self.level == 2:
            return f"    └─ {self.nama}"
        else:
            return f"{'  ' * self.level}└─ {self.nama}"
    
    @property
    def level_display(self):
        """Return level (0, 1, 2) untuk current node"""
        return self.level
    
    def get_level_0_root(self):
        """Get Level 0 parent (akar/root)"""
        ancestors = self.get_ancestors()
        return ancestors.first() if ancestors.exists() else self


# ==============================================================================
# 4. MODEL PROJECT
# ==============================================================================
class Project(models.Model):
    nama_project = models.CharField(max_length=255)
    deskripsi = models.TextField(blank=True, null=True)
    manager_project = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True, 
        related_name='projects_managed'
    )
    # === FIELD BARU: SHARED PROJECT ===
    is_shared = models.BooleanField(
        default=False,
        help_text="Jika ON, semua user bisa lihat & isi job di project ini"
    )
    # ===============================
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Daftar Project" 
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['manager_project', 'is_shared']),  # For access check
            models.Index(fields=['is_shared']),  # For shared projects query
        ]
    def __str__(self):
        return self.nama_project
    
    # === METHOD HELPER UNTUK SHARING ===
    def can_access(self, user):
        """
        Check apakah user bisa akses project ini
        BIDIRECTIONAL HIERARCHY:
        - Creator (owner)
        - Project yang di-share ke semua user
        - Atasan dari creator (for review/oversight)
        - Bawahan dari creator (for collaborative work)
        """
        if not user:
            return False
        
        # 1. Creator/Owner
        if self.manager_project == user:
            return True
        
        # 2. Project yang di-share ke semua user
        if self.is_shared:
            return True
        
        # 3. BIDIRECTIONAL: Cek hubungan hierarki
        if self.manager_project:
            # Case A: User adalah atasan dari project manager
            user_subordinates = user.get_all_subordinates()
            if self.manager_project.id in user_subordinates:
                return True
            
            # Case B: User adalah bawahan dari project manager
            # (supervisor membuat project, subordinate bisa akses)
            manager_subordinates = self.manager_project.get_all_subordinates()
            if user.id in manager_subordinates:
                return True
        
        return False
    
    def can_manage(self, user):
        """
        Check apakah user bisa manage (full edit) project ini
        BIDIRECTIONAL: Creator + Atasan + Bawahan dalam hierarchy
        """
        if not user:
            return False
        
        # 1. Creator/Owner - always can manage
        if self.manager_project == user:
            return True
        
        # 2. BIDIRECTIONAL: Supervisor dapat manage project subordinate dan sebaliknya
        if self.manager_project:
            # Case A: User adalah atasan dari project manager (supervisor)
            user_subordinates = user.get_all_subordinates()
            if self.manager_project.id in user_subordinates:
                return True
            
            # Case B: User adalah bawahan dari project manager
            # (subordinate dapat manage project dari supervisor mereka)
            manager_subordinates = self.manager_project.get_all_subordinates()
            if user.id in manager_subordinates:
                return True
        
        return False
    
    def save(self, *args, **kwargs):
        """Invalidate accessible projects cache when project changes"""
        super().save(*args, **kwargs)
        
        # Invalidate cache for manager and all supervisors
        if self.manager_project:
            self._invalidate_accessible_projects_cache(self.manager_project)
    
    def _invalidate_accessible_projects_cache(self, user):
        """Invalidate accessible projects cache for user and supervisors"""
        cache_key = f"accessible_projects_{user.id}"
        cache.delete(cache_key)
        
        # Also invalidate for all supervisors
        current = user
        while current.atasan:
            supervisor_key = f"accessible_projects_{current.atasan.id}"
            cache.delete(supervisor_key)
            current = current.atasan
    # ==================================

# ==============================================================================
# 5. MODEL FOKUS PEKERJAAN (CUSTOM PER DEPARTEMEN)
# ==============================================================================
class FokusPekerjaan(models.Model):
    """
    Fokus pekerjaan yang bisa customize per departemen.
    Menggantikan hardcoded FOKUS_CHOICES di Job model.
    
    Contoh:
    TEKNIK:
    - Perawatan (urutan: 1)
    - Perbaikan (urutan: 2)
    - Proyek (urutan: 3)
    - Lainnya (urutan: 4)
    
    OPERASIONAL:
    - Planning (urutan: 1)
    - Koordinasi (urutan: 2)
    - Monitoring (urutan: 3)
    - Laporan (urutan: 4)
    - Evaluasi (urutan: 5)
    """
    nama = models.CharField(max_length=100)
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.CASCADE,
        related_name='fokus_pekerjaan_set'
    )
    urutan = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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


# ==============================================================================
# 6. MODEL PEKERJAAN (JOB) DAN LAMPIRANNYA
# ==============================================================================
class Job(models.Model):
    TIPE_JOB_CHOICES = [
        ('Daily', 'Daily Job'),
        ('Project', 'Project Job'),
    ]
    PRIORITAS_CHOICES = [
        ('P1', 'P1 - Mendesak'),
        ('P2', 'P2 - Tinggi'),
        ('P3', 'P3 - Normal'),
        ('P4', 'P4 - Rendah'),
    ]
    # =====================================
    
    nama_pekerjaan = models.CharField(max_length=255)
    tipe_job = models.CharField(max_length=10, choices=TIPE_JOB_CHOICES, default='Daily')
    
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='jobs' 
    )
    
    # Aset untuk Teknik (backward compat)
    aset = models.ForeignKey(
        AsetMesin, 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="Pilih Sub Mesin (level terendah) - Untuk Teknik"
    )
    
    # === BARU: Aset generic untuk semua departemen ===
    aset_departemen = models.ForeignKey(
        AsetDepartemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs',
        help_text="Aset departemen (generic untuk semua departemen non-Teknik)"
    )
    # =====================================================
    
    pic = models.ForeignKey(
        CustomUser, 
        on_delete=models.PROTECT, 
        related_name='jobs_created',
        help_text="User yang membuat/bertanggung jawab (Foreman, dll)"
    )
    
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs_assigned_to_me',
        help_text="Bawahan yang ditugaskan job ini (opsional)"
    )

    personil_ditugaskan = models.ManyToManyField(
        Personil, 
        related_name='jobs_assigned',
        blank=True, 
        help_text="Pilih satu atau beberapa personil"
    )
    
    status = models.CharField(
        max_length=50, 
        default='Open', 
        editable=True   
    )
    
    # === FOKUS TETAP CHARFIELD (TANPA HARDCODED CHOICES) ===
    # Choices dihandle oleh form (dari FokusPekerjaan model)
    fokus = models.CharField(
        max_length=100,  # Increased to support longer fokus names
        default='',
        null=True, blank=True,
        help_text="Fokus pekerjaan (diisi dari FokusPekerjaan model)"
    )
    # =====================================================
    
    prioritas = models.CharField(
        max_length=10, 
        choices=PRIORITAS_CHOICES, 
        default='P3',
        null=True, blank=True
    )
    
    # === FIELDS UNTUK NOTULEN INTEGRATION ===
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
    # ==========================================
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Pekerjaan (Job)"
        verbose_name_plural = "Daftar Pekerjaan (Job)" 
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['pic', 'tipe_job']),  # For dashboard filtering
            models.Index(fields=['project', 'status']),  # For project detail
            models.Index(fields=['aset', 'status']),  # For asset filtering
        ]

    def __str__(self):
        return self.nama_pekerjaan

    # === HELPER METHODS UNTUK MULTI-DEPARTEMEN ===
    def get_aset_display(self):
        """
        Smart display aset berdasarkan departemen.
        Return string untuk menampilkan hierarchy aset.
        """
        if self.aset_mesin:
            return str(self.aset_mesin)  # "Line > Mesin > Sub Mesin"
        elif self.aset_departemen:
            return str(self.aset_departemen)  # Generic hierarchy
        return "-"

    def get_departemen_aset_type(self):
        """
        Return tipe aset yang digunakan.
        'mesin' for Teknik, 'departemen' for others, or None
        """
        if self.aset_mesin:
            return 'mesin'
        elif self.aset_departemen:
            return 'departemen'
        return None

    def get_departemen(self):
        """
        Get departemen dari job.
        - Jika aset_mesin: ambil dari pic.departemen
        - Jika aset_departemen: ambil dari aset_departemen.departemen
        """
        if self.aset_departemen:
            return self.aset_departemen.departemen
        elif self.pic:
            return self.pic.departemen
        return None
    # ==============================================

        """ Helper untuk kalender Flatpickr. """
        dates = list(self.tanggal_pelaksanaan.all().values_list('tanggal', flat=True))
        return json.dumps(dates, cls=DjangoJSONEncoder)

    def get_progress_percent(self):
        """
        Menghitung persentase progres berdasarkan tanggal yang 'Done'.
        """
        total_dates = self.tanggal_pelaksanaan.count()
        if total_dates == 0:
            return 0 # Tidak ada tanggal, progres 0
            
        done_dates = self.tanggal_pelaksanaan.filter(status='Done').count()
        
        # Hitung persentase
        progress = (done_dates / total_dates) * 100
        return int(progress) # Kembalikan sebagai integer (misal: 50)
    
    def get_aset_level_display(self):
        """
        Return tingkat aset yang dipilih: 'Line', 'Mesin', atau 'Sub Mesin'
        """
        if not self.aset:
            return None
        return ['Line', 'Mesin', 'Sub Mesin'][self.aset.level]
    
    # ========== OVERDUE TRACKING METHODS ==========
    def get_overdue_dates(self):
        """
        Return queryset of overdue JobDate records (Open/Pending with tanggal < today)
        """
        from django.utils import timezone
        today = timezone.now().date()
        return self.tanggal_pelaksanaan.filter(
            tanggal__lt=today,
            status__in=['Open', 'Pending']
        )
    
    def get_overdue_count(self):
        """
        Return count of overdue dates
        """
        return self.get_overdue_dates().count()
    
    def has_overdue(self):
        """
        Check if job has any overdue dates
        """
        return self.get_overdue_count() > 0
    
    def get_summary_stats(self):
        """
        Return dict with job status summary
        {
            'total': 15,
            'done': 6,
            'pending': 1,
            'overdue': 3,
            'open': 5,
            'na': 0,
            'progress_percent': 40
        }
        """
        all_dates = self.tanggal_pelaksanaan.all()
        total = all_dates.count()
        
        if total == 0:
            return {
                'total': 0,
                'done': 0,
                'pending': 0,
                'overdue': 0,
                'open': 0,
                'na': 0,
                'progress_percent': 0
            }
        
        done = all_dates.filter(status='Done').count()
        pending = all_dates.filter(status='Pending').count()
        open_count = all_dates.filter(status='Open').count()
        na = all_dates.filter(status='N/A').count()
        overdue = self.get_overdue_count()
        
        progress_percent = int((done / total) * 100) if total > 0 else 0
        
        return {
            'total': total,
            'done': done,
            'pending': pending,
            'overdue': overdue,
            'open': open_count,
            'na': na,
            'progress_percent': progress_percent
        }


class JobDate(models.Model):
    """
    Model terpisah untuk menangani multi-tanggal yang tidak berurutan.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='tanggal_pelaksanaan')
    tanggal = models.DateField()

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Done', 'Done'),
        ('Pending', 'Pending'),
        ('N/A', 'N/A'), # Misal: Libur atau Mesin Rusak
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Open' # Saat tanggal dibuat, statusnya 'Open'
    )
    
    catatan = models.TextField(
        blank=True, 
        null=True,
        help_text="Catatan untuk pekerjaan di tanggal ini"
    )

    class Meta:
        unique_together = ('job', 'tanggal')
        ordering = ['tanggal']
        verbose_name = "Tanggal Pengerjaan"
        verbose_name_plural = "Tanggal Pengerjaan" 

    def __str__(self):
        return f"{self.job.nama_pekerjaan} - {self.tanggal} ({self.status})"
    
    # ========== OVERDUE TRACKING METHODS ==========
    def is_overdue(self):
        """
        Check if this date is overdue (tanggal < today AND status is Open/Pending)
        """
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.tanggal < today and 
            self.status in ['Open', 'Pending']
        )
    
    def days_overdue(self):
        """
        Return number of days overdue (0 if not overdue)
        """
        from django.utils import timezone
        if not self.is_overdue():
            return 0
        today = timezone.now().date()
        delta = today - self.tanggal
        return delta.days
    
    def days_until_overdue(self):
        """
        Return number of days until overdue (negative if already overdue)
        """
        from django.utils import timezone
        today = timezone.now().date()
        if self.status in ['Done', 'N/A']:
            return None  # Not applicable
        delta = self.tanggal - today
        return delta.days

class Attachment(models.Model):
    """
    Model terpisah untuk menangani multi-lampiran (Gambar, Dokumen).
    """
    TIPE_FILE_CHOICES = [
        ('Image', 'Gambar'),
        ('Document', 'Dokumen'),
    ]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    deskripsi = models.CharField(max_length=255, blank=True, null=True)
    tipe_file = models.CharField(max_length=10, choices=TIPE_FILE_CHOICES, default='Image')
    
    class Meta:
        verbose_name = "Lampiran"
        verbose_name_plural = "Daftar Lampiran" 

    def __str__(self):
        try:
            return os.path.basename(self.file.name)
        except:
            return "File Lampiran"


# ==============================================================================
# 6. MODEL KARYAWAN (MASTER DATA - BERBEDA DARI CUSTOM USER/LOGIN)
# ==============================================================================
class Karyawan(models.Model):
    """
    Model untuk master data Karyawan
    Berbeda dari CustomUser (akun login aplikasi)
    Bisa diimport dari Excel dengan NIK + Nama
    """
    nik = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name="NIK",
        help_text="Nomor Induk Karyawan"
    )
    nama_lengkap = models.CharField(
        max_length=255,
        verbose_name="Nama Lengkap"
    )
    departemen = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Departemen"
    )
    posisi = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Posisi"
    )
    status = models.CharField(
        max_length=50,
        default='Aktif',
        choices=[
            ('Aktif', 'Aktif'),
            ('Tidak Aktif', 'Tidak Aktif'),
            ('Cuti', 'Cuti'),
            ('Keluar', 'Keluar'),
        ],
        verbose_name="Status Karyawan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Karyawan"
        verbose_name_plural = "Daftar Karyawan"
        ordering = ['nik']
    
    def __str__(self):
        return f"{self.nik} - {self.nama_lengkap}"


# ==============================================================================
# 7. MODEL LEAVE EVENT (IJIN/CUTI KE GOOGLE CALENDAR)
# ==============================================================================
class LeaveEvent(models.Model):
    """
    Model untuk track Ijin/Cuti yang di-sync ke Google Calendar
    """
    TIPE_LEAVE_CHOICES = [
        ('Ijin', 'Ijin'),
        ('Cuti', 'Cuti'),
    ]
    
    # ForeignKey ke Karyawan (master data)
    karyawan = models.ForeignKey(
        Karyawan,
        on_delete=models.CASCADE,
        related_name='leave_events',
        verbose_name="Karyawan",
        null=True,
        blank=True
    )
    
    # ForeignKey ke Departemen untuk filtering per calendar
    departemen = models.ForeignKey(
        Departemen,
        on_delete=models.CASCADE,
        related_name='leave_events',
        verbose_name="Departemen",
        null=True,
        blank=True,
        help_text="Departemen yang punya calendar untuk event ini"
    )
    
    # Keep old field untuk backward compatibility (akan deprecated)
    nama_orang = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Deprecated - gunakan karyawan field"
    )
    
    tipe_leave = models.CharField(
        max_length=10, 
        choices=TIPE_LEAVE_CHOICES, 
        default='Ijin'
    )
    
    # Untuk support multi-date, simpan sebagai comma-separated
    # Format: YYYY-MM-DD,YYYY-MM-DD,...
    tanggal = models.TextField(
        help_text="Tanggal single atau range (comma-separated). Format: YYYY-MM-DD"
    )
    
    deskripsi = models.TextField(
        blank=True, 
        null=True,
        help_text="Keterangan tambahan"
    )
    
    # Link ke Google Calendar
    # Format: event_id1,event_id2,event_id3 (comma-separated untuk multiple events)
    google_event_id = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text="Event IDs dari Google Calendar (comma-separated untuk multiple events)"
    )
    
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_events_created'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Leave Event"
        verbose_name_plural = "Daftar Leave Events"
        ordering = ['-created_at']
    
    def __str__(self):
        nama = self.karyawan.nama_lengkap if self.karyawan else self.nama_orang
        return f"{nama} - {self.tipe_leave} ({self.tanggal})"
    
    def get_tanggal_list(self):
        """Parse comma-separated dates into list"""
        return [tgl.strip() for tgl in self.tanggal.split(',') if tgl.strip()]
    
    def get_google_event_ids(self):
        """Parse comma-separated event IDs into list"""
        if self.google_event_id:
            return [eid.strip() for eid in self.google_event_id.split(',') if eid.strip()]
        return []


# ==============================================================================
# 7. MODEL USER OVERDUE JOB PREFERENCE (UNTUK FILTER NOTIFIKASI)
# ==============================================================================
class UserOverdueJobPreference(models.Model):
    """
    Model untuk menyimpan user preferences tentang jenis-jenis overdue job
    yang ingin ditampilkan dalam notifikasi.
    
    Contoh:
    - User hanya ingin lihat Daily & Project Jobs (tidak Preventive)
    - Atau User hanya ingin lihat Preventive Jobs saja
    """
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='overdue_job_preference'
    )
    
    show_daily_jobs = models.BooleanField(
        default=True,
        verbose_name="Tampilkan Daily Jobs",
        help_text="Cek untuk menampilkan daily jobs dalam overdue notifications"
    )
    
    show_project_jobs = models.BooleanField(
        default=True,
        verbose_name="Tampilkan Project Jobs",
        help_text="Cek untuk menampilkan project jobs dalam overdue notifications"
    )
    
    show_preventive_jobs = models.BooleanField(
        default=True,
        verbose_name="Tampilkan Preventive Jobs",
        help_text="Cek untuk menampilkan preventive jobs dalam overdue notifications"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Overdue Job Preference"
        verbose_name_plural = "User Overdue Job Preferences"
    
    def __str__(self):
        types = []
        if self.show_daily_jobs:
            types.append('Daily')
        if self.show_project_jobs:
            types.append('Project')
        if self.show_preventive_jobs:
            types.append('Preventive')
        return f"{self.user.username} - {', '.join(types) if types else 'None'}"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """
        Get or create preference untuk user
        Returns preference object dengan default values jika belum ada
        """
        preference, created = cls.objects.get_or_create(user=user)
        return preference


# ==============================================================================
# 8. MODEL MAINTENANCE MODE
# ==============================================================================
class MaintenanceMode(models.Model):
    """
    Model untuk control Maintenance Mode aplikasi
    Admin bisa toggle on/off dari Django admin untuk menampilkan halaman maintenance
    """
    is_active = models.BooleanField(
        default=False,
        verbose_name="Aktifkan Maintenance Mode",
        help_text="Jika diaktifkan, user akan melihat halaman maintenance"
    )
    
    message = models.TextField(
        default="Aplikasi sedang dalam proses maintenance. Mohon tunggu beberapa saat...",
        verbose_name="Pesan Maintenance",
        help_text="Pesan yang ditampilkan ke user saat maintenance mode aktif"
    )
    
    estimated_time = models.CharField(
        max_length=100,
        blank=True,
        default="Estimasi selesai dalam 15 menit",
        verbose_name="Estimasi Waktu Selesai",
        help_text="Contoh: 'Estimasi selesai dalam 15 menit' atau '10:30 AM'"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Maintenance Mode"
        verbose_name_plural = "Maintenance Mode"
    
    def __str__(self):
        status = "AKTIF" if self.is_active else "NONAKTIF"
        return f"Maintenance Mode: {status}"
    
    @staticmethod
    def is_maintenance_active():
        """Cek apakah maintenance mode aktif"""
        try:
            mode = MaintenanceMode.objects.first()
            return mode.is_active if mode else False
        except:
            return False


# ==============================================================================
# FONNTE SETTINGS - WA API Configuration (Admin Access Only)
# ==============================================================================
class FonnteSettings(models.Model):
    """
    Model untuk menyimpan Fonnte API credentials per departemen.
    Hanya admin yang bisa manage settings ini.
    
    Fonnte API Format:
    - POST: https://api.fontte.com/send
    - Auth: Authorization: {token}
    - Body: form-data (target, message, countryCode)
    """
    departemen = models.OneToOneField(
        Departemen,
        on_delete=models.CASCADE,
        related_name='fontte_settings',
        verbose_name="Departemen"
    )
    
    token = models.CharField(
        max_length=255,
        verbose_name="API Token",
        help_text="Token dari Fontte dashboard (digunakan di Authorization header)"
    )
    
    country_code = models.CharField(
        max_length=5,
        default='62',
        help_text="Country code untuk nomor HP (default: 62 untuk Indonesia)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Enable/disable WA reminders untuk departemen ini"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fonnte_settings_created'
    )
    
    class Meta:
        verbose_name = "Fonnte Settings"
        verbose_name_plural = "Fonnte Settings"
        db_table = 'core_fonntesettings'  # Keep existing table name
        permissions = [
            ('can_manage_fonte', 'Can manage Fonnte API settings'),
        ]
    
    def __str__(self):
        return f"Fontte Settings - {self.departemen.nama_departemen}"
    
    def test_connection(self):
        """Test connection ke Fontte API"""
        import requests
        try:
            response = requests.post(
                'https://api.fontte.com/send',
                data={
                    'target': '628123456789',  # Test number
                    'message': 'Test dari sistem',
                    'countryCode': self.country_code
                },
                headers={
                    'Authorization': self.token
                },
                timeout=5
            )
            # Status 200, 201, 400 masih berarti API responding
            # 500+ berarti server error
            return response.status_code < 500
        except Exception as e:
            return False


# ==============================================================================
# 8. MODEL GOOGLE API SETTINGS (GLOBAL CONFIGURATION)
# ==============================================================================
class GoogleAPISettings(models.Model):
    """
    Model untuk menyimpan global Google API settings.
    Digunakan untuk konfigurasi Fonnte API token dan reminder send time.
    
    Singleton pattern: Hanya ada 1 record (pk=1)
    """
    
    fonnte_api_token = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Fonnte API Token",
        help_text="Token dari Fonnte untuk WhatsApp API"
    )
    
    reminder_send_time = models.TimeField(
        default='08:00',
        verbose_name="Waktu Kirim Reminder",
        help_text="Jam berapa reminder meeting dikirim (format HH:MM, timezone Asia/Jakarta)"
    )
    
    # JSON credentials untuk Google Sheets/Calendar
    google_credentials_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Path ke Google Credentials JSON",
        help_text="Path relatif ke file JSON credentials (misal: JSON GCP/credentials.json)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Google API Settings"
        verbose_name_plural = "Google API Settings"
    
    def __str__(self):
        return "Global Google API Settings"
    
    @classmethod
    def get_instance(cls):
        """
        Singleton getter: Selalu return instance dengan pk=1.
        Create jika tidak ada.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def save(self, *args, **kwargs):
        """Override save untuk ensure hanya ada 1 instance"""
        self.pk = 1
        super().save(*args, **kwargs)