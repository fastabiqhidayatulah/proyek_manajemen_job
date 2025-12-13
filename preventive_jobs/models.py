from django.db import models
from django.contrib.auth import get_user_model
from core.models import AsetMesin
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta

CustomUser = get_user_model()

# ==============================================================================
# 1. MODEL TEMPLATE PREVENTIVE JOB
# ==============================================================================
class PreventiveJobTemplate(models.Model):
    """
    Master template untuk preventive job yang berulang.
    Dari template ini akan di-generate execution records secara otomatis.
    """
    
    FOKUS_CHOICES = [
        ('Perawatan', 'Perawatan'),
        ('Perbaikan', 'Perbaikan'),
        ('Inspeksi', 'Inspeksi'),
        ('Kalibrasi', 'Kalibrasi'),
        ('Cleaning', 'Cleaning'),
        ('Lainnya', 'Lainnya'),
    ]
    
    PRIORITAS_CHOICES = [
        ('P1', 'P1 - Mendesak'),
        ('P2', 'P2 - Tinggi'),
        ('P3', 'P3 - Normal'),
        ('P4', 'P4 - Rendah'),
    ]
    
    KATEGORI_CHOICES = [
        ('Mekanik', 'Mekanik'),
        ('Elektrik', 'Elektrik'),
        ('Utility', 'Utility'),
    ]
    
    # BASIC INFO
    nama_pekerjaan = models.CharField(
        max_length=255,
        verbose_name="Nama Pekerjaan",
        help_text="Contoh: Cek Oil Level, Ganti Filter, dll"
    )
    
    deskripsi = models.TextField(
        blank=True,
        null=True,
        verbose_name="Deskripsi"
    )
    
    # ASET/MESIN (BISA MULTIPLE)
    aset_mesin = models.ManyToManyField(
        AsetMesin,
        related_name='preventive_job_templates',
        help_text="Pilih satu atau lebih mesin/aset"
    )
    
    # JADWAL - CUSTOM INTERVAL DALAM HARI
    interval_hari = models.IntegerField(
        default=7,
        verbose_name="Interval (Hari)",
        help_text="Contoh: 1 (harian), 7 (mingguan), 30 (bulanan), 365 (tahunan)"
    )
    
    tanggal_mulai = models.DateField(
        verbose_name="Tanggal Mulai",
        help_text="Kapan template ini mulai aktif"
    )
    
    tanggal_berakhir = models.DateField(
        blank=True,
        null=True,
        verbose_name="Tanggal Berakhir (Opsional)",
        help_text="Kosongkan jika pengulangan tidak terbatas (ongoing)"
    )
    
    # CUSTOM SCHEDULE - TANGGAL SPESIFIK DALAM SEBULAN
    schedule_type = models.CharField(
        max_length=20,
        choices=[
            ('interval', 'Interval-Based (Setiap N hari)'),
            ('custom', 'Custom Dates (Tanggal tertentu setiap bulan)'),
        ],
        default='interval',
        verbose_name="Tipe Jadwal",
        help_text="Pilih interval regular atau custom dates"
    )
    
    custom_dates = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Custom Dates",
        help_text="List tanggal dalam sebulan: [2, 7, 14, 28] untuk tgl 2, 7, 14, 28 setiap bulan"
    )
    
    # FOKUS & PRIORITAS
    fokus = models.CharField(
        max_length=50,
        choices=FOKUS_CHOICES,
        default='Perawatan',
        verbose_name="Fokus Pekerjaan"
    )
    
    prioritas = models.CharField(
        max_length=10,
        choices=PRIORITAS_CHOICES,
        default='P3',
        verbose_name="Prioritas"
    )
    
    # KATEGORI
    kategori = models.CharField(
        max_length=20,
        choices=KATEGORI_CHOICES,
        default='Mekanik',
        verbose_name="Kategori Pekerjaan",
        help_text="Pilih kategori: Mekanik, Elektrik, atau Utility"
    )
    
    # PIC & NOTIFICATION
    pic = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='preventive_job_templates_created',
        verbose_name="PIC (Penanggung Jawab)",
        help_text="User yang bertanggung jawab template ini"
    )
    
    # NOTIFICATION PREFERENCES
    notify_24h_before = models.BooleanField(
        default=True,
        verbose_name="Notifikasi 24 jam sebelumnya"
    )
    notify_2h_before = models.BooleanField(
        default=True,
        verbose_name="Notifikasi 2 jam sebelumnya"
    )
    notify_on_schedule = models.BooleanField(
        default=False,
        verbose_name="Notifikasi saat jadwal"
    )
    
    # CHECKLIST TEMPLATE (LINK KE MASTER CHECKLIST)
    checklist_template = models.ForeignKey(
        'ChecklistTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preventive_job_templates',
        verbose_name="Checklist Template",
        help_text="Pilih checklist yang harus diisi saat job ditutup (opsional)"
    )
    
    # STATUS
    is_active = models.BooleanField(
        default=True,
        verbose_name="Status Aktif"
    )
    
    # SOFT DELETE FIELDS
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Terhapus (Soft)",
        help_text="Jika True berarti template dihapus dan berada di recycle bin"
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Waktu Dihapus"
    )
    
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_preventive_job_templates',
        verbose_name="Dihapus oleh"
    )
    
    # AUDIT FIELDS
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preventive_job_templates_created_by',
        verbose_name="Dibuat oleh"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preventive Job Template"
        verbose_name_plural = "Daftar Preventive Job Templates"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'tanggal_mulai']),
            models.Index(fields=['pic']),
        ]
    
    def __str__(self):
        return f"{self.nama_pekerjaan} (Interval: {self.interval_hari} hari)"
    
    def get_next_execution_date(self, from_date=None):
        """
        Hitung tanggal execution berikutnya dari tanggal tertentu.
        Support dua tipe: interval (setiap N hari) atau custom dates (tanggal spesifik setiap bulan)
        """
        if from_date is None:
            from_date = timezone.now().date()
        
        if from_date < self.tanggal_mulai:
            return self.tanggal_mulai
        
        if self.tanggal_berakhir and from_date > self.tanggal_berakhir:
            return None
        
        if self.schedule_type == 'custom' and self.custom_dates:
            # CUSTOM DATES: Cari tanggal terdekat di custom_dates bulan depan
            custom_dates_list = sorted(self.custom_dates)
            
            # Cek di bulan yang sama
            for day in custom_dates_list:
                if day > from_date.day:
                    try:
                        candidate = from_date.replace(day=day)
                        if candidate > from_date and (not self.tanggal_berakhir or candidate <= self.tanggal_berakhir):
                            return candidate
                    except ValueError:
                        # Hari tidak valid di bulan ini (misal 31 Februari)
                        pass
            
            # Tidak ada di bulan ini, cari di bulan depan
            next_month = from_date + relativedelta(months=1)
            for day in custom_dates_list:
                try:
                    candidate = next_month.replace(day=day)
                    if not self.tanggal_berakhir or candidate <= self.tanggal_berakhir:
                        return candidate
                except ValueError:
                    # Hari tidak valid di bulan ini
                    pass
            
            return None
        
        else:
            # INTERVAL-BASED: Tambah N hari
            next_date = from_date + timedelta(days=self.interval_hari)
            
            if self.tanggal_berakhir and next_date > self.tanggal_berakhir:
                return None
            
            return next_date
    
    def get_all_execution_dates(self, max_months=24):
        """
        Generate semua tanggal execution untuk template ini.
        max_months: Maksimal bulan di depan untuk generate (untuk custom dates, prevent infinite loop)
        """
        dates = []
        current_date = self.tanggal_mulai
        
        if self.schedule_type == 'custom' and self.custom_dates:
            # CUSTOM DATES: Generate sampai max_months ke depan atau tanggal_berakhir
            end_date = self.tanggal_berakhir or (self.tanggal_mulai + relativedelta(months=max_months))
            
            while current_date <= end_date:
                next_date = self.get_next_execution_date(current_date)
                if next_date is None or next_date > end_date:
                    break
                dates.append(next_date)
                current_date = next_date
        
        else:
            # INTERVAL-BASED: Regular interval
            while True:
                dates.append(current_date)
                next_date = self.get_next_execution_date(current_date)
                if next_date is None:
                    break
                current_date = next_date
        
        return dates
    
    def save(self, *args, **kwargs):
        """Override save untuk auto-generate execution records"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Auto-generate execution records jika template baru atau mesin berubah
        if is_new:
            self._generate_executions()
    
    def _generate_executions(self):
        """Generate execution records untuk semua mesin dan tanggal"""
        from preventive_jobs.models import PreventiveJobExecution
        
        execution_dates = self.get_all_execution_dates()
        mesin_list = self.aset_mesin.all()
        
        for scheduled_date in execution_dates:
            for mesin in mesin_list:
                # Avoid duplicate entries
                PreventiveJobExecution.objects.get_or_create(
                    template=self,
                    aset=mesin,
                    scheduled_date=scheduled_date,
                    defaults={
                        'status': 'Scheduled',
                        'compliance_type': 'None',
                    }
                )
    
    def soft_delete(self, deleted_by=None):
        """
        Soft-delete this template: mark as deleted and mark related executions as deleted.
        Executions tetap tersimpan di database untuk restore.
        """
        from django.utils import timezone
        
        if self.is_deleted:
            return
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if deleted_by:
            self.deleted_by = deleted_by
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
        
        # Soft-delete related executions
        self.executions.update(is_deleted=True, deleted_at=self.deleted_at, deleted_by=deleted_by)
    
    def restore(self):
        """
        Restore soft-deleted template dan semua executions-nya.
        """
        if not self.is_deleted:
            return
        
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])
        
        # Restore related executions
        self.executions.update(is_deleted=False, deleted_at=None, deleted_by=None)


# ==============================================================================
# 1.5. MODEL EXECUTION STATUS LOG (AUDIT TRAIL)
# ==============================================================================
class ExecutionStatusLog(models.Model):
    """
    Log setiap perubahan status execution untuk audit trail dan undo support.
    Berguna untuk tracking: siapa yang ubah, kapan, dari status apa ke apa, dengan reason apa.
    """
    
    execution = models.ForeignKey(
        'PreventiveJobExecution',
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name="Execution"
    )
    
    from_status = models.CharField(
        max_length=20,
        verbose_name="Status Sebelumnya"
    )
    
    to_status = models.CharField(
        max_length=20,
        verbose_name="Status Sesudahnya"
    )
    
    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Alasan Perubahan",
        help_text="e.g., 'Salah klik', 'Testing', 'Data fix', 'User request'"
    )
    
    changed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='execution_status_changes',
        verbose_name="Diubah oleh"
    )
    
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Waktu Perubahan"
    )
    
    # Snapshot dari execution saat status berubah (untuk audit detail)
    snapshot_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Snapshot Data",
        help_text="Simpan state execution saat status berubah"
    )
    
    class Meta:
        verbose_name = "Execution Status Log"
        verbose_name_plural = "Daftar Execution Status Logs"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['execution', '-changed_at']),
            models.Index(fields=['changed_by']),
        ]
    
    def __str__(self):
        return f"{self.execution} - {self.from_status} → {self.to_status} ({self.changed_at})"


# ==============================================================================
# 2. MODEL EXECUTION PREVENTIVE JOB
# ==============================================================================
class PreventiveJobExecution(models.Model):
    """
    Record individual untuk setiap execution/pelaksanaan preventive job.
    Dibuat otomatis dari template.
    """
    
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled (Terjadwal)'),
        ('Done', 'Done (Selesai)'),
        ('Skipped', 'Skipped (Dilewati)'),
        ('N/A', 'N/A (Tidak Berlaku)'),
    ]
    
    COMPLIANCE_CHOICES = [
        ('A', 'A - Selesai sesuai jadwal'),
        ('B', 'B - Selesai terlambat'),
        ('C', 'C - Selesai dengan bukti/foto'),
        ('None', 'None - Belum ditentukan'),
    ]
    
    # RELASI
    template = models.ForeignKey(
        PreventiveJobTemplate,
        on_delete=models.CASCADE,
        related_name='executions',
        verbose_name="Template"
    )
    
    aset = models.ForeignKey(
        AsetMesin,
        on_delete=models.SET_NULL,
        null=True,
        related_name='preventive_job_executions',
        verbose_name="Mesin/Aset"
    )
    
    # JADWAL
    scheduled_date = models.DateField(
        verbose_name="Tanggal Terjadwal",
        help_text="Tanggal yang dijadwalkan untuk pekerjaan ini"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Scheduled',
        verbose_name="Status"
    )
    
    # PELAKSANAAN
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preventive_job_executions_assigned',
        verbose_name="Ditugaskan ke"
    )
    
    # Personil yang ditugaskan (dari tim PIC) - bisa multiple
    assigned_to_personil = models.ManyToManyField(
        'core.Personil',
        blank=True,
        related_name='preventive_job_executions_assigned',
        verbose_name="Ditugaskan ke (Personil)"
    )
    
    actual_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Tanggal Pelaksanaan Aktual",
        help_text="Tanggal ketika job sebenarnya dilaksanakan"
    )
    
    # CATATAN & COMPLIANCE
    catatan = models.TextField(
        blank=True,
        null=True,
        verbose_name="Catatan/Findings"
    )
    
    compliance_type = models.CharField(
        max_length=10,
        choices=COMPLIANCE_CHOICES,
        default='None',
        verbose_name="Tipe Compliance",
        help_text="Kategori compliance: A (tepat waktu), B (terlambat), C (dengan bukti)"
    )
    
    has_attachment = models.BooleanField(
        default=False,
        verbose_name="Ada Lampiran"
    )
    
    # SOFT DELETE FIELDS
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Terhapus (Soft)",
        help_text="Jika True berarti execution dihapus beserta template-nya"
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Waktu Dihapus"
    )
    
    deleted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_preventive_job_executions',
        verbose_name="Dihapus oleh"
    )
    
    # AUDIT
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Preventive Job Execution"
        verbose_name_plural = "Daftar Preventive Job Executions"
        ordering = ['-scheduled_date']
        unique_together = ('template', 'aset', 'scheduled_date')
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['template']),
        ]
    
    def __str__(self):
        return f"{self.template.nama_pekerjaan} - {self.aset.nama} ({self.scheduled_date})"
    
    # STATE MACHINE - Define valid transitions
    VALID_STATUS_TRANSITIONS = {
        'Scheduled': ['Done', 'Skipped', 'N/A'],
        'Done': ['Scheduled', 'Skipped', 'N/A'],  # Allow reverting for testing phase
        'Skipped': ['Scheduled', 'Done', 'N/A'],  # Allow reverting for testing phase
        'N/A': ['Scheduled', 'Done', 'Skipped'],  # Allow reverting for testing phase
    }
    
    def can_transition_to(self, new_status):
        """
        Check apakah transisi status valid.
        Return: (is_valid: bool, message: str)
        """
        if new_status == self.status:
            return True, "Status sudah sama (no change needed)"
        
        allowed = self.VALID_STATUS_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            return False, f"Tidak bisa ubah dari {self.status} ke {new_status}"
        
        return True, f"Transisi valid: {self.status} → {new_status}"
    
    def transition_to(self, new_status, reason='', changed_by=None):
        """
        Lakukan state transition dengan audit trail.
        Raises ValueError jika transisi tidak valid.
        """
        is_valid, message = self.can_transition_to(new_status)
        
        if not is_valid:
            raise ValueError(message)
        
        old_status = self.status
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
        
        # Record log untuk audit trail
        ExecutionStatusLog.objects.create(
            execution=self,
            from_status=old_status,
            to_status=new_status,
            reason=reason,
            changed_by=changed_by,
            snapshot_data={
                'actual_date': str(self.actual_date) if self.actual_date else None,
                'compliance_type': self.compliance_type,
                'catatan': self.catatan,
            }
        )
    
    def get_status_history(self):
        """Get full history of status changes"""
        return self.status_logs.all()
    
    def undo_last_status_change(self, changed_by=None):
        """
        Undo last status change untuk 'salah klik' atau testing.
        Return: (success: bool, message: str)
        """
        last_log = self.status_logs.order_by('-changed_at').first()
        
        if not last_log:
            return False, "Tidak ada history untuk di-undo"
        
        # Transisi kembali ke status sebelumnya
        try:
            self.transition_to(
                last_log.from_status,
                reason=f"Undo: {last_log.reason or 'No reason given'}",
                changed_by=changed_by
            )
            return True, f"Status di-revert dari {last_log.to_status} ke {last_log.from_status}"
        except ValueError as e:
            return False, f"Undo failed: {str(e)}"
    
    def is_overdue(self):
        """Check apakah job ini overdue (belum selesai tapi sudah melewati jadwal)"""
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.status == 'Scheduled' and 
            self.scheduled_date < today
        )
    
    def days_overdue(self):
        """Return jumlah hari overdue (0 jika tidak overdue)"""
        from django.utils import timezone
        if not self.is_overdue():
            return 0
        today = timezone.now().date()
        delta = today - self.scheduled_date
        return delta.days
    
    def days_until_due(self):
        """Berapa hari lagi sampai jadwal (bisa negatif jika overdue)"""
        from django.utils import timezone
        today = timezone.now().date()
        if self.status in ['Done', 'Skipped', 'N/A']:
            return None  # Not applicable
        delta = (self.scheduled_date - today).days
        return delta
    
    def get_compliance_status(self):
        """Tentukan compliance status berdasarkan actual_date vs scheduled_date"""
        if self.status == 'Scheduled':
            return 'Pending'
        elif self.status == 'Skipped' or self.status == 'N/A':
            return 'N/A'
        elif self.status == 'Done':
            if self.actual_date is None:
                return 'Done (tanpa bukti)'
            elif self.actual_date <= self.scheduled_date:
                return 'Done (tepat waktu - Type A)'
            else:
                days_late = (self.actual_date - self.scheduled_date).days
                return f'Done (terlambat {days_late} hari - Type B)'
        return 'Unknown'


# ==============================================================================
# 3. MODEL ATTACHMENT UNTUK PREVENTIVE JOB EXECUTION
# ==============================================================================
class PreventiveJobAttachment(models.Model):
    """
    Lampiran (foto/dokumen) untuk setiap execution
    """
    
    TIPE_FILE_CHOICES = [
        ('Image', 'Gambar'),
        ('Document', 'Dokumen'),
        ('Video', 'Video'),
        ('Other', 'Lainnya'),
    ]
    
    execution = models.ForeignKey(
        PreventiveJobExecution,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Execution"
    )
    
    file = models.FileField(
        upload_to='preventive_jobs/attachments/%Y/%m/%d/',
        verbose_name="File"
    )
    
    deskripsi = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Deskripsi"
    )
    
    tipe_file = models.CharField(
        max_length=20,
        choices=TIPE_FILE_CHOICES,
        default='Image',
        verbose_name="Tipe File"
    )
    
    uploaded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preventive_job_attachments_uploaded',
        verbose_name="Diunggah oleh"
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Preventive Job Attachment"
        verbose_name_plural = "Daftar Preventive Job Attachments"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.execution} - {self.file.name}"


# ==============================================================================
# 4. MODEL NOTIFICATION (UNTUK TRACKING NOTIFIKASI)
# ==============================================================================
class PreventiveJobNotification(models.Model):
    """
    Log notifikasi yang sudah dikirim ke user
    """
    
    NOTIFICATION_TYPE_CHOICES = [
        ('24h_before', 'Notifikasi 24 jam sebelum'),
        ('2h_before', 'Notifikasi 2 jam sebelum'),
        ('on_schedule', 'Notifikasi saat jadwal'),
        ('overdue', 'Notifikasi job overdue'),
        ('completed', 'Notifikasi job selesai'),
    ]
    
    execution = models.ForeignKey(
        PreventiveJobExecution,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Execution"
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='preventive_job_notifications',
        verbose_name="User"
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='24h_before',
        verbose_name="Tipe Notifikasi"
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name="Sudah dibaca"
    )
    
    message = models.TextField(
        verbose_name="Pesan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu dibaca"
    )
    
    class Meta:
        verbose_name = "Preventive Job Notification"
        verbose_name_plural = "Daftar Preventive Job Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['execution']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.execution} ({self.get_notification_type_display()})"


# ==============================================================================
# 5. MODEL MASTER CHECKLIST TEMPLATE
# ==============================================================================
class ChecklistTemplate(models.Model):
    """
    Master template untuk checklist perawatan/inspeksi.
    Berisi struktur item-item yang akan dicek beserta standar/normalnya.
    Bisa di-link ke multiple PreventiveJobTemplate.
    """
    
    KATEGORI_CHOICES = [
        ('Mekanik', 'Mekanik'),
        ('Elektrik', 'Elektrik'),
        ('Utility', 'Utility'),
    ]
    
    # BASIC INFO
    nama = models.CharField(
        max_length=255,
        verbose_name="Nama Checklist",
        help_text="Contoh: Checklist Perawatan Motor 3 Fasa"
    )
    
    nomor = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nomor Checklist",
        help_text="Auto-generate: CHKL-YYYY-XXX",
        editable=False
    )
    
    kategori = models.CharField(
        max_length=20,
        choices=KATEGORI_CHOICES,
        verbose_name="Kategori"
    )
    
    deskripsi = models.TextField(
        blank=True,
        null=True,
        verbose_name="Deskripsi"
    )
    
    # FILE TEMPLATE (OPTIONAL)
    file_template = models.FileField(
        upload_to='checklist_templates/',
        blank=True,
        null=True,
        verbose_name="File Template (Excel/PDF)",
        help_text="File referensi checklist untuk download"
    )
    
    # STATUS
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_checklists'
    )
    
    class Meta:
        verbose_name = "Checklist Template"
        verbose_name_plural = "Daftar Checklist Templates"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['kategori', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.nomor} - {self.nama}"
    
    def save(self, *args, **kwargs):
        # Auto-generate nomor jika belum ada
        if not self.nomor:
            from datetime import datetime
            year = datetime.now().year
            
            # Find the highest sequence number for this year
            latest = ChecklistTemplate.objects.filter(
                nomor__startswith=f"CHKL-{year}-"
            ).order_by('nomor').last()
            
            if latest and latest.nomor:
                try:
                    # Extract sequence number from existing nomor
                    seq = int(latest.nomor.split('-')[-1])
                    next_seq = seq + 1
                except (ValueError, IndexError):
                    next_seq = 1
            else:
                next_seq = 1
            
            # Generate unique nomor
            self.nomor = f"CHKL-{year}-{next_seq:03d}"
            
            # Double-check for uniqueness (race condition prevention)
            while ChecklistTemplate.objects.filter(nomor=self.nomor).exists():
                next_seq += 1
                self.nomor = f"CHKL-{year}-{next_seq:03d}"
        
        super().save(*args, **kwargs)


# ==============================================================================
# 6. MODEL CHECKLIST ITEM (DETAIL SETIAP BARIS CHECKLIST)
# ==============================================================================
class ChecklistItem(models.Model):
    """
    Item-item yang ada dalam checklist template.
    Setiap item memiliki:
    - Nama item pemeriksaan
    - Standar/nilai normal yang diharapkan
    - Tipe item bisa:
      * numeric: Input dengan angka, Unit, Min-Max range untuk validasi
      * text: Dropdown dengan pilihan predefined (text_options)
      * free_text: Input text bebas tanpa pilihan predefined
    """
    
    ITEM_TYPE_CHOICES = [
        ('numeric', 'Numeric (dengan Angka)'),
        ('text', 'Text/Qualitative (Dropdown Pilihan)'),
        ('free_text', 'Free Text (Input Bebas)'),
    ]
    
    checklist_template = models.ForeignKey(
        ChecklistTemplate,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    no_urut = models.IntegerField(
        verbose_name="No Urut",
        help_text="Urutan item dalam checklist"
    )
    
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        default='numeric',
        verbose_name="Tipe Item",
        help_text="Numeric: untuk pengukuran angka | Text: untuk observasi visual/audio"
    )
    
    item_pemeriksaan = models.CharField(
        max_length=255,
        verbose_name="Item Pemeriksaan",
        help_text="Contoh: Tegangan antar fasa, Getaran, Suara abnormal, Warna cairan"
    )
    
    standar_normal = models.CharField(
        max_length=255,
        verbose_name="Standar/Normal",
        help_text="Contoh: 380±10% V, Halus, Bunyi normal, Jernih"
    )
    
    unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Unit",
        help_text="Contoh: V, A, %, MΩ, Hz, mm, dll. Kosongkan untuk item text"
    )
    
    # RANGE UNTUK VALIDASI (OPTIONAL - HANYA UNTUK NUMERIC ITEMS)
    nilai_min = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nilai Min",
        help_text="Untuk validasi range hasil pengukuran (numeric items saja)"
    )
    
    nilai_max = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Nilai Max",
        help_text="Untuk validasi range hasil pengukuran (numeric items saja)"
    )
    
    # PILIHAN TEXT UNTUK QUALITATIVE ITEMS
    text_options = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Pilihan Text",
        help_text="Untuk text items, pisahkan dengan semicolon (;). Contoh: Normal;Kasar;Bising;Bergerak"
    )
    
    tindakan_remark = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Tindakan/Remark",
        help_text="Kolom catatan atau tindakan jika nilai diluar normal"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Checklist Item"
        verbose_name_plural = "Daftar Checklist Items"
        ordering = ['checklist_template', 'no_urut']
        unique_together = [['checklist_template', 'no_urut']]
        indexes = [
            models.Index(fields=['checklist_template']),
        ]
    
    def __str__(self):
        return f"{self.checklist_template.nomor} - Item {self.no_urut}: {self.item_pemeriksaan}"
    
    def get_text_options_list(self):
        """Parse text_options menjadi list"""
        if self.text_options:
            return [opt.strip() for opt in self.text_options.split(';')]
        return []


# ==============================================================================
# 7. MODEL CHECKLIST RESULT (HASIL PENGISIAN CHECKLIST SAAT JOB DITUTUP)
# ==============================================================================
class ChecklistResult(models.Model):
    """
    Menyimpan hasil pengisian checklist saat execution selesai.
    Berisi hasil pengukuran untuk setiap item dari template checklist.
    """
    
    execution = models.OneToOneField(
        PreventiveJobExecution,
        on_delete=models.CASCADE,
        related_name='checklist_result',
        null=True,
        blank=True
    )
    
    checklist_template = models.ForeignKey(
        ChecklistTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='results'
    )
    
    # HASIL PENGUKURAN (JSON: mapping item_id -> hasil)
    # Format: {"item_1": {"nilai": 387, "status": "OK", "remark": ""}, ...}
    hasil_pengukuran = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Hasil Pengukuran"
    )
    
    # STATUS ITEM (JSON: mapping item_id -> status OK/NG)
    status_item = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Status Item",
        help_text="Mapping item_id ke status OK/NG"
    )
    
    status_overall = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending - Share Link Dibuat (Belum Dibuka)'),
            ('Partial', 'Partial - Sebagian Selesai'),
            ('OK', 'OK - Semua Normal'),
            ('NG', 'NG - Ada yang Abnormal'),
        ],
        default='Pending',
        verbose_name="Status Overall"
    )
    
    file_attachment = models.FileField(
        upload_to='checklist_results/',
        blank=True,
        null=True,
        verbose_name="File Checklist (PDF/Excel)"
    )
    
    tanggal_pengisian = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Tanggal Pengisian"
    )
    
    diisi_oleh = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='filled_checklists'
    )
    
    catatan_umum = models.TextField(
        blank=True,
        null=True,
        verbose_name="Catatan Umum"
    )
    
    catatan = models.TextField(
        blank=True,
        null=True,
        verbose_name="Catatan",
        help_text="Catatan hasil checklist"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    # SHARE LINK FIELDS (UNTUK WHATSAPP SHARING)
    share_token = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Share Token",
        help_text="Unique token untuk share link ke WA"
    )
    
    share_created_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu Share Link Dibuat"
    )
    
    accessed_by_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Nama Orang yang Akses",
        help_text="Nama orang yang mengakses link share"
    )
    
    accessed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu Akses Share Link"
    )
    
    submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu Submit Checklist via Share Link"
    )
    
    is_submitted_via_share = models.BooleanField(
        default=False,
        verbose_name="Submit via Share Link",
        help_text="True jika checklist diisi melalui share link WA"
    )
    
    class Meta:
        verbose_name = "Checklist Result"
        verbose_name_plural = "Daftar Checklist Results"
        ordering = ['-tanggal_pengisian']
        indexes = [
            models.Index(fields=['execution']),
            models.Index(fields=['checklist_template']),
            models.Index(fields=['share_token']),
        ]
    
    def __str__(self):
        return f"Checklist Result - {self.execution} ({self.status_overall})"


# ==============================================================================
# MODEL UNTUK MANAGE KONTAK WHATSAPP
# ==============================================================================
class WhatsAppContact(models.Model):
    """
    Master data untuk nomor WhatsApp yang bisa menerima share checklist.
    Admin bisa manage dari Django Admin.
    """
    
    CONTACT_TYPE_CHOICES = [
        ('Personal', 'Personal (User PIC)'),
        ('Team', 'Team (Personil Team)'),
        ('External', 'External (Kontraktor/Vendor)'),
    ]
    
    nama = models.CharField(
        max_length=255,
        verbose_name="Nama Kontak"
    )
    
    nomor_wa = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Nomor WhatsApp",
        help_text="Format: 628xx (dengan kode negara)"
    )
    
    tipe_kontak = models.CharField(
        max_length=20,
        choices=CONTACT_TYPE_CHOICES,
        default='Personal',
        verbose_name="Tipe Kontak"
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_contacts',
        verbose_name="User Terkait",
        help_text="User yang punya nomor ini (opsional)"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    
    keterangan = models.TextField(
        blank=True,
        null=True,
        verbose_name="Keterangan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "WhatsApp Contact"
        verbose_name_plural = "Daftar WhatsApp Contacts"
        ordering = ['nama']
    
    def __str__(self):
        return f"{self.nama} ({self.nomor_wa})"


# ==============================================================================
# MODEL UNTUK LOG PENGIRIMAN CHECKLIST VIA WHATSAPP
# ==============================================================================
class ChecklistShareLog(models.Model):
    """
    Log setiap kali checklist di-share via WhatsApp.
    Untuk tracking dan audit.
    """
    
    execution = models.ForeignKey(
        PreventiveJobExecution,
        on_delete=models.CASCADE,
        related_name='checklist_share_logs',
        verbose_name="Execution"
    )
    
    checklist_result = models.ForeignKey(
        ChecklistResult,
        on_delete=models.CASCADE,
        related_name='share_logs',
        verbose_name="Checklist Result"
    )
    
    penerima_nama = models.CharField(
        max_length=255,
        verbose_name="Nama Penerima"
    )
    
    penerima_wa = models.CharField(
        max_length=20,
        verbose_name="Nomor WA Penerima"
    )
    
    share_link = models.URLField(
        verbose_name="Share Link"
    )
    
    share_token = models.CharField(
        max_length=255,
        verbose_name="Share Token"
    )
    
    status_pengiriman = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
        ],
        default='pending',
        verbose_name="Status Pengiriman WA"
    )
    
    pesan_wa = models.TextField(
        blank=True,
        null=True,
        verbose_name="Pesan WA yang Dikirim"
    )
    
    dikirim_oleh = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checklist_shares_sent',
        verbose_name="Dikirim oleh"
    )
    
    dikirim_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Waktu Dikirim"
    )
    
    accessed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu Link Diakses"
    )
    
    submitted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu Checklist Disubmit"
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Pesan Error (jika ada)"
    )
    
    class Meta:
        verbose_name = "Checklist Share Log"
        verbose_name_plural = "Daftar Checklist Share Logs"
        ordering = ['-dikirim_at']
        indexes = [
            models.Index(fields=['execution']),
            models.Index(fields=['share_token']),
        ]
    
    def __str__(self):
        return f"Share to {self.penerima_nama} ({self.status_pengiriman})"

