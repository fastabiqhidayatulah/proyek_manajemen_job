import uuid
from django.db import models
from django.utils import timezone
from core.models import Karyawan


class Tool(models.Model):
    """Master data alat/tools yang bisa dipinjam"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=200, unique=True)
    spesifikasi = models.TextField(blank=True, null=True)
    jumlah_total = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nama']
        verbose_name = 'Alat/Tool'
        verbose_name_plural = 'Alat/Tools'
    
    def __str__(self):
        return f"{self.nama} (Stok: {self.jumlah_total})"
    
    @property
    def jumlah_tersedia(self):
        """Hitung jumlah alat yang tersedia (belum dipinjam)"""
        total_pinjam = DetailPeminjaman.objects.filter(
            peminjaman__status__in=['aktif', 'overdue'],
            tool=self
        ).aggregate(total=models.Sum('qty_pinjam'))['total'] or 0
        
        # Kurangi dengan yang sudah dikembalikan
        total_kembali = DetailPengembalian.objects.filter(
            tool=self
        ).aggregate(total=models.Sum('qty_kembali'))['total'] or 0
        
        return self.jumlah_total - (total_pinjam - total_kembali)


class Peminjaman(models.Model):
    """Transaksi peminjaman alat"""
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('selesai', 'Selesai'),
        ('overdue', 'Overdue'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peminjam = models.ForeignKey(Karyawan, on_delete=models.PROTECT, related_name='peminjaman_alat')
    tgl_pinjam = models.DateTimeField(auto_now_add=True)
    tgl_rencana_kembali = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aktif')
    
    catatan = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='peminjaman_dibuat')
    
    class Meta:
        ordering = ['-tgl_pinjam']
        verbose_name = 'Peminjaman'
        verbose_name_plural = 'Peminjaman'
    
    def __str__(self):
        return f"Peminjaman {self.peminjam.nama} ({self.tgl_pinjam.strftime('%d-%m-%Y')})"
    
    def save(self, *args, **kwargs):
        # Auto update status ke overdue jika tgl_rencana_kembali terlewat dan status masih aktif
        if self.status == 'aktif' and timezone.now() > self.tgl_rencana_kembali:
            self.status = 'overdue'
        super().save(*args, **kwargs)
    
    @property
    def is_complete(self):
        """Check apakah semua alat sudah dikembalikan"""
        for detail in self.detail_peminjaman.all():
            if detail.qty_kembali < detail.qty_pinjam:
                return False
        return True
    
    def check_and_update_status(self):
        """Check dan auto-update status ke selesai jika semua alat sudah kembali"""
        if self.is_complete:
            self.status = 'selesai'
            self.save()


class DetailPeminjaman(models.Model):
    """Detail alat yang dipinjam dalam 1 transaksi peminjaman"""
    
    KONDISI_CHOICES = [
        ('baik', 'Baik'),
        ('rusak_ringan', 'Rusak Ringan'),
        ('rusak_berat', 'Rusak Berat'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peminjaman = models.ForeignKey(Peminjaman, on_delete=models.CASCADE, related_name='detail_peminjaman')
    tool = models.ForeignKey(Tool, on_delete=models.PROTECT, related_name='detail_peminjaman')
    qty_pinjam = models.PositiveIntegerField()
    kondisi_pinjam = models.CharField(max_length=20, choices=KONDISI_CHOICES, default='baik')
    
    class Meta:
        unique_together = ['peminjaman', 'tool']
        verbose_name = 'Detail Peminjaman'
        verbose_name_plural = 'Detail Peminjaman'
    
    def __str__(self):
        return f"{self.tool.nama} x{self.qty_pinjam}"
    
    @property
    def qty_kembali(self):
        """Total qty yang sudah dikembalikan untuk alat ini"""
        return DetailPengembalian.objects.filter(
            pengembalian__peminjaman=self.peminjaman,
            tool=self.tool
        ).aggregate(total=models.Sum('qty_kembali'))['total'] or 0
    
    @property
    def qty_belum_kembali(self):
        """Qty yang masih belum dikembalikan"""
        return self.qty_pinjam - self.qty_kembali


class Pengembalian(models.Model):
    """Event pengembalian alat (bisa partial, banyak kali)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    peminjaman = models.ForeignKey(Peminjaman, on_delete=models.CASCADE, related_name='pengembalian')
    tgl_kembali = models.DateTimeField(auto_now_add=True)
    dikembalikan_oleh = models.ForeignKey(Karyawan, on_delete=models.SET_NULL, null=True, related_name='pengembalian_alat')
    catatan = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-tgl_kembali']
        verbose_name = 'Pengembalian'
        verbose_name_plural = 'Pengembalian'
    
    def __str__(self):
        return f"Pengembalian {self.peminjaman.peminjam.nama} ({self.tgl_kembali.strftime('%d-%m-%Y')})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto check dan update status peminjaman
        self.peminjaman.check_and_update_status()


class DetailPengembalian(models.Model):
    """Detail alat yang dikembalikan per event pengembalian"""
    
    KONDISI_CHOICES = [
        ('baik', 'Baik'),
        ('rusak_ringan', 'Rusak Ringan'),
        ('rusak_berat', 'Rusak Berat'),
        ('hilang', 'Hilang'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pengembalian = models.ForeignKey(Pengembalian, on_delete=models.CASCADE, related_name='detail_pengembalian')
    tool = models.ForeignKey(Tool, on_delete=models.PROTECT, related_name='detail_pengembalian')
    qty_kembali = models.PositiveIntegerField()
    kondisi_kembali = models.CharField(max_length=20, choices=KONDISI_CHOICES, default='baik')
    
    class Meta:
        verbose_name = 'Detail Pengembalian'
        verbose_name_plural = 'Detail Pengembalian'
    
    def __str__(self):
        return f"{self.tool.nama} x{self.qty_kembali}"
