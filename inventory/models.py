import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


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
