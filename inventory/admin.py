from django.contrib import admin
from .models import Barang, StockLevel


@admin.register(Barang)
class BarangAdmin(admin.ModelAdmin):
    list_display = ['kode', 'nama', 'status', 'lokasi_penyimpanan', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['kode', 'nama', 'spesifikasi']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('kode', 'nama', 'spesifikasi')
        }),
        ('Storage', {
            'fields': ('lokasi_penyimpanan',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ['barang', 'qty', 'updated_at', 'updated_by']
    list_filter = ['updated_at']
    search_fields = ['barang__kode', 'barang__nama']
    readonly_fields = ['id', 'updated_at']
    
    fieldsets = (
        ('Item', {
            'fields': ('barang',)
        }),
        ('Stock', {
            'fields': ('qty',)
        }),
        ('Audit', {
            'fields': ('updated_by', 'updated_at', 'id'),
        }),
    )
