from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.core.exceptions import ValidationError
import uuid

User = get_user_model()

# ==============================================================================
# 1. MEETING (HEADER NOTULEN)
# ==============================================================================
class Meeting(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('final', 'Final'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Penomoran dokumen
    no_dokumen_base = models.CharField(
        max_length=50,
        help_text="Format: F.93/WM/01/03 (tetap, dikonfigurasi di settings)",
        default='F.93/WM/01/03'
    )
    no_urut = models.IntegerField(
        help_text="Nomor urut otomatis per base (0001, 0002, dst)"
    )
    no_dokumen = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        help_text="Auto-generated: F.93/WM/01/03/0001"
    )
    
    # Metadata dokumen
    revisi = models.IntegerField(default=0)
    terbitan = models.IntegerField(default=1)
    
    # Meeting details
    tanggal_dokumen = models.DateField(auto_now_add=True)
    tanggal_meeting = models.DateField()
    hari = models.CharField(max_length=20, editable=False)
    jam_mulai = models.TimeField()
    jam_selesai = models.TimeField()
    tempat = models.CharField(max_length=255)
    agenda = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # QR Code untuk presensi eksternal
    qr_code_token = models.CharField(
        max_length=100,
        unique=True,
        editable=False,
        help_text="Unique token untuk QR code"
    )
    qr_code_active = models.BooleanField(
        default=False,
        help_text="QR code aktif/inactive"
    )
    qr_code_created_at = models.DateTimeField(null=True, blank=True)
    
    # Peserta (M2M via MeetingPeserta)
    peserta = models.ManyToManyField(
        User,
        through='MeetingPeserta',
        blank=True,
        related_name='meetings'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_created'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings_updated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Meeting/Notulen Rapat"
        verbose_name_plural = "Daftar Meeting/Notulen"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tanggal_meeting']),
            models.Index(fields=['status']),
            models.Index(fields=['qr_code_token']),
            models.Index(fields=['no_dokumen_base', 'no_urut']),
        ]
        unique_together = [['no_dokumen_base', 'no_urut']]
    
    def __str__(self):
        return f"{self.no_dokumen} - {self.agenda[:50]}"
    
    def save(self, *args, **kwargs):
        """Override save untuk auto-generate no_dokumen dan qr_code_token"""
        # Auto-generate hari dari tanggal_meeting
        if self.tanggal_meeting:
            hari_map = {
                0: 'Senin',
                1: 'Selasa',
                2: 'Rabu',
                3: 'Kamis',
                4: 'Jumat',
                5: 'Sabtu',
                6: 'Minggu'
            }
            self.hari = hari_map[self.tanggal_meeting.weekday()]
        
        # Auto-generate no_urut jika belum ada
        if not self.no_urut:
            last_meeting = Meeting.objects.filter(
                no_dokumen_base=self.no_dokumen_base
            ).order_by('-no_urut').first()
            
            if last_meeting:
                self.no_urut = last_meeting.no_urut + 1
            else:
                self.no_urut = 1
        
        # Auto-generate no_dokumen
        self.no_dokumen = f"{self.no_dokumen_base}/{self.no_urut:04d}"
        
        # Auto-generate qr_code_token jika belum ada
        if not self.qr_code_token:
            self.qr_code_token = str(uuid.uuid4())
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validasi jam_selesai > jam_mulai"""
        if self.jam_selesai <= self.jam_mulai:
            raise ValidationError("Jam selesai harus lebih besar dari jam mulai")
    
    def generate_qr_code(self):
        """Generate QR code untuk meeting ini"""
        if not self.qr_code_token:
            self.qr_code_token = str(uuid.uuid4())
        self.qr_code_active = True
        self.qr_code_created_at = now()
        self.save()
    
    def toggle_qr_code(self):
        """Toggle QR code aktif/inactive"""
        self.qr_code_active = not self.qr_code_active
        self.save()
    
    def get_peserta_count(self):
        """Hitung total peserta"""
        return self.peserta.count() + MeetingPeserta.objects.filter(
            meeting=self,
            tipe_peserta='external'
        ).count()
    
    def get_presensi_summary(self):
        """Summary presensi: hadir, izin, alpa"""
        peserta_list = MeetingPeserta.objects.filter(meeting=self)
        summary = {
            'hadir': peserta_list.filter(status_kehadiran='hadir').count(),
            'izin': peserta_list.filter(status_kehadiran='izin').count(),
            'alpa': peserta_list.filter(status_kehadiran='alpa').count(),
            'total': peserta_list.count(),
        }
        return summary


# ==============================================================================
# 2. MEETING PESERTA (THROUGH MODEL - INTERNAL & EXTERNAL)
# ==============================================================================
class MeetingPeserta(models.Model):
    TIPE_PESERTA_CHOICES = [
        ('internal', 'Internal User'),
        ('external', 'External Peserta'),
    ]
    
    STATUS_KEHADIRAN_CHOICES = [
        ('belum', 'Belum Diisi'),
        ('hadir', 'Hadir'),
        ('izin', 'Izin'),
        ('alpa', 'Alpa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    
    # Internal peserta (dari sistem)
    peserta = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='meeting_peserta'
    )
    
    # External peserta (scan QR)
    nama = models.CharField(max_length=255)
    nik = models.CharField(max_length=20, blank=True, null=True)
    bagian = models.CharField(max_length=255, blank=True, null=True)
    
    # Status kehadiran
    status_kehadiran = models.CharField(
        max_length=20,
        choices=STATUS_KEHADIRAN_CHOICES,
        default='belum'
    )
    tipe_peserta = models.CharField(
        max_length=20,
        choices=TIPE_PESERTA_CHOICES,
        editable=False
    )
    
    # Timestamp
    waktu_check_in = models.DateTimeField(null=True, blank=True)
    catatan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Meeting Peserta"
        verbose_name_plural = "Daftar Meeting Peserta"
        indexes = [
            models.Index(fields=['meeting', 'tipe_peserta']),
            models.Index(fields=['nik']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['meeting', 'peserta'],
                condition=models.Q(peserta__isnull=False),
                name='unique_internal_peserta'
            ),
        ]
    
    def __str__(self):
        return f"{self.nama} - {self.meeting.no_dokumen}"
    
    def save(self, *args, **kwargs):
        """Auto-set tipe_peserta dan nama"""
        if self.peserta:
            self.tipe_peserta = 'internal'
            self.nama = self.peserta.get_full_name() or self.peserta.username
        else:
            self.tipe_peserta = 'external'
        
        super().save(*args, **kwargs)


# ==============================================================================
# 3. NOTULEN ITEM (DETAIL ACTION ITEMS)
# ==============================================================================
class NotulenItem(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('progress', 'Progress'),
        ('done', 'Done'),
        ('overdue', 'Overdue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='notulen_items'
    )
    
    # Urutan item
    no = models.IntegerField(help_text="Nomor urut dalam 1 meeting")
    
    # Detail item
    pokok_bahasan = models.TextField(help_text="Hasil diskusi/keputusan")
    tanggapan = models.TextField(blank=True, null=True, help_text="Detail/penjelasan")
    
    # PIC (Person In Charge)
    pic = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notulen_items_assigned'
    )
    
    # PIC Eksternal (dari luar sistem - free text)
    pic_eksternal = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Nama PIC jika bukan dari sistem"
    )
    
    # Deadline
    target_deadline = models.DateField(help_text="Target deadline dari diskusi (soft deadline)")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    
    # Link ke Job jika sudah convert
    job_created = models.ForeignKey(
        'core.Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notulen_items',
        help_text="Job yang dibuat dari notulen item ini"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Notulen Item"
        verbose_name_plural = "Daftar Notulen Item"
        ordering = ['meeting', 'no']
        indexes = [
            models.Index(fields=['pic', 'status']),
            models.Index(fields=['target_deadline']),
            models.Index(fields=['job_created']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['meeting', 'no'],
                name='unique_notulen_item_per_meeting'
            ),
        ]
    
    def __str__(self):
        return f"{self.meeting.no_dokumen} - Item {self.no}: {self.pokok_bahasan[:50]}"
    
    def save(self, *args, **kwargs):
        """Override save untuk auto-numbering"""
        if not self.no:
            # Auto-number items dalam meeting ini
            last_item = NotulenItem.objects.filter(meeting=self.meeting).order_by('-no').first()
            self.no = (last_item.no + 1) if last_item else 1
        
        super().save(*args, **kwargs)
    
    def is_overdue(self):
        """Check apakah item sudah overdue"""
        if self.status == 'done':
            return False
        return self.target_deadline < now().date()
    
    def update_status_if_overdue(self):
        """Auto-update status ke overdue jika deadline sudah lewat"""
        if self.is_overdue() and self.status != 'done':
            self.status = 'overdue'
            self.save()
