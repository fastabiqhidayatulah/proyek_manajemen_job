from django.contrib import admin
from django.utils.html import format_html
from .models import Tool, Peminjaman, DetailPeminjaman, Pengembalian, DetailPengembalian


# ============================================================
# TOOL ADMIN
# ============================================================
@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['nama', 'jumlah_total', 'get_jumlah_tersedia', 'spesifikasi']
    search_fields = ['nama', 'spesifikasi']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Informasi Alat', {
            'fields': ('id', 'nama', 'spesifikasi', 'jumlah_total')
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_jumlah_tersedia(self, obj):
        """Tampilkan jumlah alat yang tersedia"""
        tersedia = obj.jumlah_tersedia
        if tersedia <= 0:
            return format_html('<span style="color: red;">Tidak Ada</span>')
        elif tersedia <= 2:
            return format_html('<span style="color: orange;">{}</span>', tersedia)
        else:
            return format_html('<span style="color: green;">{}</span>', tersedia)
    get_jumlah_tersedia.short_description = 'Tersedia'


# ============================================================
# DETAIL PEMINJAMAN INLINE
# ============================================================
class DetailPeminjamanInline(admin.TabularInline):
    model = DetailPeminjaman
    extra = 1
    fields = ['tool', 'qty_pinjam', 'kondisi_pinjam']
    readonly_fields = ['id']


# ============================================================
# PEMINJAMAN ADMIN
# ============================================================
@admin.register(Peminjaman)
class PeminjamanAdmin(admin.ModelAdmin):
    list_display = ['peminjam', 'tgl_pinjam', 'tgl_rencana_kembali', 'get_status_display', 'get_is_complete']
    list_filter = ['status', 'tgl_pinjam']
    search_fields = ['peminjam__nama']
    readonly_fields = ['id', 'tgl_pinjam', 'is_complete']
    inlines = [DetailPeminjamanInline]
    fieldsets = (
        ('Informasi Peminjaman', {
            'fields': ('id', 'peminjam', 'tgl_pinjam', 'tgl_rencana_kembali', 'status')
        }),
        ('Detail Transaksi', {
            'fields': ('created_by', 'catatan', 'is_complete')
        }),
    )
    
    def get_status_display(self, obj):
        """Tampilkan status dengan warna"""
        colors = {
            'aktif': 'green',
            'selesai': 'blue',
            'overdue': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    get_status_display.short_description = 'Status'
    
    def get_is_complete(self, obj):
        """Tampilkan apakah peminjaman sudah lengkap dikembalikan"""
        if obj.is_complete:
            return format_html('<span style="color: green;">✓ Lengkap</span>')
        else:
            return format_html('<span style="color: orange;">Belum Lengkap</span>')
    get_is_complete.short_description = 'Status Pengembalian'


# ============================================================
# DETAIL PEMINJAMAN ADMIN
# ============================================================
@admin.register(DetailPeminjaman)
class DetailPeminjamanAdmin(admin.ModelAdmin):
    list_display = ['peminjaman', 'tool', 'qty_pinjam', 'get_qty_kembali', 'get_qty_belum_kembali']
    list_filter = ['peminjaman', 'tool']
    search_fields = ['peminjaman__peminjam__nama', 'tool__nama']
    readonly_fields = ['id', 'qty_kembali', 'qty_belum_kembali']
    
    def get_qty_kembali(self, obj):
        return obj.qty_kembali
    get_qty_kembali.short_description = 'Qty Kembali'
    
    def get_qty_belum_kembali(self, obj):
        qty_belum = obj.qty_belum_kembali
        if qty_belum == 0:
            return format_html('<span style="color: green;">0</span>')
        else:
            return format_html('<span style="color: red;">{}</span>', qty_belum)
    get_qty_belum_kembali.short_description = 'Qty Belum Kembali'


# ============================================================
# DETAIL PENGEMBALIAN INLINE
# ============================================================
class DetailPengembalianInline(admin.TabularInline):
    model = DetailPengembalian
    extra = 1
    fields = ['tool', 'qty_kembali', 'kondisi_kembali']
    readonly_fields = ['id']


# ============================================================
# PENGEMBALIAN ADMIN
# ============================================================
@admin.register(Pengembalian)
class PengembalianAdmin(admin.ModelAdmin):
    list_display = ['peminjaman', 'tgl_kembali', 'dikembalikan_oleh']
    list_filter = ['tgl_kembali', 'peminjaman__peminjam']
    search_fields = ['peminjaman__peminjam__nama', 'dikembalikan_oleh__nama']
    readonly_fields = ['id', 'tgl_kembali']
    inlines = [DetailPengembalianInline]
    fieldsets = (
        ('Informasi Pengembalian', {
            'fields': ('id', 'peminjaman', 'tgl_kembali', 'dikembalikan_oleh')
        }),
        ('Catatan', {
            'fields': ('catatan',),
            'classes': ('collapse',)
        }),
    )


# ============================================================
# DETAIL PENGEMBALIAN ADMIN
# ============================================================
@admin.register(DetailPengembalian)
class DetailPengembalianAdmin(admin.ModelAdmin):
    list_display = ['pengembalian', 'tool', 'qty_kembali', 'kondisi_kembali']
    list_filter = ['pengembalian', 'tool', 'kondisi_kembali']
    search_fields = ['pengembalian__peminjaman__peminjam__nama', 'tool__nama']
    readonly_fields = ['id']
