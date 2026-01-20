import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Barang(models.Model):
    """Master Spare Parts / Inventory Items"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Category
    CATEGORY_CHOICES = [
        ('electrical', 'Electrical Components'),
        ('mechanical', 'Mechanical Components'),
        ('hydraulic', 'Hydraulic & Pneumatic'),
        ('seals', 'Seals & Gaskets'),
        ('fasteners', 'Fasteners & Hardware'),
        ('lubricants', 'Lubricants & Fluids'),
        ('consumables', 'Consumables'),
    ]
    kategori = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='mechanical',
        help_text="Pilih kategori barang sesuai tipenya"
    )
    
    # Basic Info
    kode = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Kode barang/SKU (auto-generated)"
    )
    nama = models.CharField(
        max_length=255,
        help_text="Nama barang"
    )
    spesifikasi = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi/spesifikasi teknis barang"
    )
    
    # Location
    lokasi_penyimpanan = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Lokasi penyimpanan (misal: Rak A1, Bin 3)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('discontinued', 'Discontinued'),
        ],
        default='active'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Auto-generate kode barang jika belum ada"""
        if not self.kode:
            # Cari barang terakhir dengan kode yang sudah ada
            last_barang = Barang.objects.filter(kode__startswith='INV-').order_by('-created_at').first()
            if last_barang:
                # Extract nomor dari kode terakhir (misal: INV-00001 → 1)
                last_num = int(last_barang.kode.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1
            # Generate kode baru dengan format INV-00001
            self.kode = f'INV-{new_num:05d}'
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Barang"
        verbose_name_plural = "Daftar Barang"
        ordering = ['kode']
        indexes = [
            models.Index(fields=['kode']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.kode} - {self.nama}"


class StockLevel(models.Model):
    """Current Stock Level for Each Item"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Reference
    barang = models.OneToOneField(
        Barang,
        on_delete=models.CASCADE,
        related_name='stock_level'
    )
    
    # Stock
    qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Jumlah stok sekarang"
    )
    
    # Audit
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_updates'
    )
    
    class Meta:
        verbose_name = "Stock Level"
        verbose_name_plural = "Stock Levels"
    
    def __str__(self):
        return f"{self.barang.nama} - {self.qty}"


# ==============================================================================
# 3. STOCK EXPORT SETTING MODEL
# ==============================================================================
class StockExportSetting(models.Model):
    """Setting untuk Export PDF Stok ke WA Otomatis"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Setiap Hari'),
        ('weekly', 'Setiap Minggu'),
        ('monthly', 'Setiap Bulan'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Pengaturan Jadwal
    is_active = models.BooleanField(
        default=False,
        help_text="Aktifkan untuk mengirim PDF otomatis"
    )
    
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='daily',
        help_text="Frekuensi pengiriman"
    )
    
    # Waktu pengiriman (dalam 24 jam format)
    send_time = models.TimeField(
        default='08:00:00',
        help_text="Jam pengiriman (format HH:MM:SS)"
    )
    
    # Hari untuk weekly
    day_of_week = models.IntegerField(
        default=0,  # 0=Monday, 6=Sunday
        choices=[
            (0, 'Senin'),
            (1, 'Selasa'),
            (2, 'Rabu'),
            (3, 'Kamis'),
            (4, 'Jumat'),
            (5, 'Sabtu'),
            (6, 'Minggu'),
        ],
        help_text="Hari untuk pengiriman mingguan"
    )
    
    # Tanggal untuk monthly
    day_of_month = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Tanggal untuk pengiriman bulanan (1-31)"
    )
    
    # Fontte Configuration
    fontte_token = models.CharField(
        max_length=255,
        blank=True,
        help_text="Token API WA Fontte (opsional, jika kosong menggunakan default dari settings)"
    )
    
    fontte_api_url = models.URLField(
        default='https://api.fontte.com/v1',
        help_text="Base URL untuk Fontte API"
    )
    
    fontte_connected = models.BooleanField(
        default=False,
        help_text="Status koneksi ke Fontte"
    )
    
    fontte_last_check = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Waktu pengecekan koneksi terakhir"
    )
    
    # Daftar Grup WA
    wa_groups = models.JSONField(
        default=list,
        blank=True,
        help_text="Daftar grup WA untuk menerima PDF (format: [{'group_id': 'xxx', 'group_name': 'Grup 1'}, ...])"
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_export_updates'
    )
    
    class Meta:
        verbose_name = "Stock Export Setting"
        verbose_name_plural = "Stock Export Settings"
    
    def __str__(self):
        status = "Aktif" if self.is_active else "Nonaktif"
        return f"Stock Export - {status} ({self.frequency})"


# ==============================================================================
# 4. STOCK EXPORT LOG MODEL
# ==============================================================================
class StockExportLog(models.Model):
    """Log history untuk export PDF ke WA"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Terkirim'),
        ('failed', 'Gagal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Reference
    setting = models.ForeignKey(
        StockExportSetting,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    
    # Pengiriman
    wa_group_id = models.CharField(
        max_length=255,
        help_text="ID grup WA yang dituju"
    )
    wa_group_name = models.CharField(
        max_length=255,
        help_text="Nama grup WA"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    pdf_file = models.CharField(
        max_length=255,
        blank=True,
        help_text="Nama file PDF yang dikirim"
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text="Pesan error jika pengiriman gagal"
    )
    
    # Audit
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Waktu pengiriman berhasil"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Stock Export Log"
        verbose_name_plural = "Stock Export Logs"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wa_group_name} - {self.status}"



class StockExportSchedule(models.Model):
    """Schedule untuk automatic stock export PDF ke WhatsApp Group"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient Group
    SCHEDULE_CHOICES = [
        ('daily', 'Harian (Setiap hari)'),
        ('weekly', 'Mingguan (Setiap Senin)'),
        ('monthly', 'Bulanan (Awal bulan)'),
        ('manual', 'Manual (Dipicu manual saja)'),
    ]
    
    nama_grup = models.CharField(
        max_length=255,
        help_text="Nama grup WA penerima (e.g., 'Warehouse Team', 'Management')"
    )
    
    nomor_grup_wa = models.CharField(
        max_length=20,
        help_text="Nomor grup WhatsApp (format: 628xx untuk personal, bisa juga group ID)"
    )
    
    jadwal = models.CharField(
        max_length=20,
        choices=SCHEDULE_CHOICES,
        default='manual',
        help_text="Jadwal pengiriman otomatis"
    )
    
    waktu_kirim = models.TimeField(
        default='09:00',
        help_text="Jam berapa laporan akan dikirim (format: HH:MM)"
    )
    
    # Configuration
    include_kategori = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Kategori yang disertakan (kosongkan untuk semua). Format: electrical,mechanical,hydraulic"
    )
    
    pesan_tambahan = models.TextField(
        blank=True,
        null=True,
        help_text="Pesan tambahan sebelum daftar stok (opsional)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Aktifkan/nonaktifkan pengiriman otomatis"
    )
    
    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_export_schedules',
        verbose_name="Dibuat oleh"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sent = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Terakhir dikirim"
    )
    
    class Meta:
        verbose_name = "Stock Export Schedule"
        verbose_name_plural = "Stock Export Schedules"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nama_grup} ({self.get_jadwal_display()})"
