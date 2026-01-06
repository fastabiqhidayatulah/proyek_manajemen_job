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

class CustomUser(AbstractUser):
    jabatan = models.ForeignKey(Jabatan, on_delete=models.SET_NULL, null=True, blank=True)
    atasan = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='bawahan' 
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
        """Override save untuk auto-normalize nomor telepon dan invalidate cache"""
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
# 5. MODEL PEKERJAAN (JOB) DAN LAMPIRANNYA
# ==============================================================================
class Job(models.Model):
    TIPE_JOB_CHOICES = [
        ('Daily', 'Daily Job'),
        ('Project', 'Project Job'),
    ]
    # === TAMBAHKAN 2 FIELD BARU INI ===
    FOKUS_CHOICES = [
        ('Perawatan', 'Perawatan'),
        ('Perbaikan', 'Perbaikan'),
        ('Proyek', 'Proyek'),
        ('Lainnya', 'Lainnya'),
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
    
    aset = models.ForeignKey(
        AsetMesin, 
        on_delete=models.SET_NULL, 
        null=True,
        help_text="Pilih Sub Mesin (level terendah)"
    )
    
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
    
    # === TAMBAHKAN 2 FIELD BARU INI ===
    fokus = models.CharField(
        max_length=50, 
        choices=FOKUS_CHOICES, 
        default='Perawatan',
        null=True, blank=True
    )
    prioritas = models.CharField(
        max_length=10, 
        choices=PRIORITAS_CHOICES, 
        default='P3',
        null=True, blank=True
    )
    # =====================================
    
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

    def get_dates_json(self):
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