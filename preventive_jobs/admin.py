from django.contrib import admin
from .models import (
    PreventiveJobTemplate,
    PreventiveJobExecution,
    PreventiveJobAttachment,
    PreventiveJobNotification,
    ChecklistTemplate,
    ChecklistItem,
    ChecklistResult,
    WhatsAppContact,
    ChecklistShareLog,
)


@admin.register(PreventiveJobTemplate)
class PreventiveJobTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'nama_pekerjaan',
        'schedule_type',
        'interval_hari',
        'pic',
        'is_active',
        'tanggal_mulai',
        'tanggal_berakhir',
        'execution_count',
    ]
    list_filter = ['is_active', 'fokus', 'prioritas', 'created_at']
    search_fields = ['nama_pekerjaan', 'deskripsi', 'pic__username']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nama_pekerjaan', 'deskripsi', 'aset_mesin')
        }),
        ('Jadwal & Interval', {
            'fields': (
                'schedule_type',
                'interval_hari',
                'custom_dates',
                'tanggal_mulai',
                'tanggal_berakhir',
            )
        }),
        ('Fokus & Prioritas', {
            'fields': ('fokus', 'prioritas', 'kategori')
        }),
        ('Penugasan & Notifikasi', {
            'fields': (
                'pic',
                'notify_24h_before',
                'notify_2h_before',
                'notify_on_schedule',
            )
        }),
        ('Checklist Template', {
            'fields': ('checklist_template',),
            'description': 'Pilih checklist yang harus diisi saat job ditutup (opsional)'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def execution_count(self, obj):
        return obj.executions.count()
    execution_count.short_description = 'Jumlah Execution'


@admin.register(PreventiveJobExecution)
class PreventiveJobExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'template',
        'aset',
        'scheduled_date',
        'status',
        'assigned_to',
        'is_overdue_badge',
    ]
    list_filter = ['status', 'scheduled_date', 'template', 'aset']
    search_fields = ['template__nama_pekerjaan', 'aset__nama', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at', 'compliance_status']
    
    fieldsets = (
        ('Relasi', {
            'fields': ('template', 'aset')
        }),
        ('Jadwal', {
            'fields': ('scheduled_date', 'actual_date', 'status')
        }),
        ('Penugasan', {
            'fields': ('assigned_to',)
        }),
        ('Catatan & Compliance', {
            'fields': (
                'catatan',
                'compliance_type',
                'compliance_status',
                'has_attachment',
            )
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue():
            return '⚠️ OVERDUE'
        return '✓ OK'
    is_overdue_badge.short_description = 'Status'
    
    def compliance_status(self, obj):
        return obj.get_compliance_status()
    compliance_status.short_description = 'Compliance Status'


@admin.register(PreventiveJobAttachment)
class PreventiveJobAttachmentAdmin(admin.ModelAdmin):
    list_display = ['execution', 'tipe_file', 'uploaded_by', 'uploaded_at']
    list_filter = ['tipe_file', 'uploaded_at']
    search_fields = ['execution__template__nama_pekerjaan', 'uploaded_by__username']
    readonly_fields = ['uploaded_at']


@admin.register(PreventiveJobNotification)
class PreventiveJobNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'execution',
        'notification_type',
        'is_read_badge',
        'created_at',
    ]
    list_filter = ['is_read', 'notification_type', 'created_at']
    search_fields = ['user__username', 'execution__template__nama_pekerjaan']
    readonly_fields = ['created_at', 'read_at']
    
    def is_read_badge(self, obj):
        if obj.is_read:
            return '✓ Read'
        return 'Unread'
    is_read_badge.short_description = 'Status'


# ==============================================================================
# ADMIN REGISTRATIONS UNTUK CHECKLIST SYSTEM
# ==============================================================================

class ChecklistItemInline(admin.TabularInline):
    """
    Inline admin untuk ChecklistItem (dapat diedit langsung dari ChecklistTemplate admin)
    """
    model = ChecklistItem
    extra = 1
    fields = ['no_urut', 'item_pemeriksaan', 'standar_normal', 'unit', 'nilai_min', 'nilai_max', 'tindakan_remark']
    ordering = ['no_urut']


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    """
    Admin untuk master Checklist Template
    """
    list_display = ['nomor', 'nama', 'kategori', 'item_count', 'is_active', 'created_by', 'created_at']
    list_filter = ['kategori', 'is_active', 'created_at']
    search_fields = ['nama', 'nomor', 'deskripsi']
    readonly_fields = ['nomor', 'created_by', 'created_at', 'updated_at']
    inlines = [ChecklistItemInline]
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('nomor', 'nama', 'kategori', 'deskripsi')
        }),
        ('File Template', {
            'fields': ('file_template',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Jumlah Items'
    
    def save_model(self, request, obj, form, change):
        """Auto-set created_by saat create"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    """
    Admin untuk Checklist Items
    """
    list_display = ['no_urut', 'item_pemeriksaan', 'checklist_template', 'standar_normal', 'unit']
    list_filter = ['checklist_template', 'unit']
    search_fields = ['item_pemeriksaan', 'standar_normal', 'checklist_template__nama']
    
    fieldsets = (
        ('Relasi', {
            'fields': ('checklist_template',)
        }),
        ('Detail Item', {
            'fields': ('no_urut', 'item_pemeriksaan', 'standar_normal')
        }),
        ('Range & Unit', {
            'fields': ('unit', 'nilai_min', 'nilai_max'),
            'description': 'Isi nilai_min dan nilai_max untuk validasi otomatis range'
        }),
        ('Tindakan', {
            'fields': ('tindakan_remark',)
        }),
    )
    
    def get_queryset(self, request):
        """Order by checklist template dan no_urut"""
        qs = super().get_queryset(request)
        return qs.select_related('checklist_template').order_by('checklist_template', 'no_urut')


@admin.register(ChecklistResult)
class ChecklistResultAdmin(admin.ModelAdmin):
    """
    Admin untuk Hasil/Hasil Checklist
    """
    list_display = ['execution', 'checklist_template', 'status_overall', 'diisi_oleh', 'tanggal_pengisian']
    list_filter = ['status_overall', 'tanggal_pengisian', 'checklist_template']
    search_fields = ['execution__template__nama_pekerjaan', 'diisi_oleh__username', 'checklist_template__nama']
    readonly_fields = ['execution', 'checklist_template', 'diisi_oleh', 'tanggal_pengisian']
    
    fieldsets = (
        ('Relasi', {
            'fields': ('execution', 'checklist_template', 'diisi_oleh')
        }),
        ('Hasil Pengukuran', {
            'fields': ('hasil_pengukuran',),
            'description': 'Data hasil pengukuran dalam format JSON'
        }),
        ('Status', {
            'fields': ('status_overall',)
        }),
        ('Catatan & File', {
            'fields': ('catatan_umum', 'file_attachment')
        }),
        ('Tanggal', {
            'fields': ('tanggal_pengisian',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Jangan allow manual add, hanya bisa create via execution"""
        return False
    
    def get_queryset(self, request):
        """Order by tanggal_pengisian descending"""
        qs = super().get_queryset(request)
        return qs.select_related('execution', 'checklist_template', 'diisi_oleh').order_by('-tanggal_pengisian')


@admin.register(WhatsAppContact)
class WhatsAppContactAdmin(admin.ModelAdmin):
    list_display = ['nama', 'nomor_wa', 'tipe_kontak', 'user', 'is_active', 'created_at']
    list_filter = ['tipe_kontak', 'is_active', 'created_at']
    search_fields = ['nama', 'nomor_wa', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informasi Kontak', {
            'fields': ('nama', 'nomor_wa', 'tipe_kontak', 'user')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Keterangan', {
            'fields': ('keterangan',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChecklistShareLog)
class ChecklistShareLogAdmin(admin.ModelAdmin):
    list_display = [
        'penerima_nama',
        'penerima_wa',
        'status_pengiriman',
        'dikirim_oleh',
        'dikirim_at',
        'accessed_at',
        'submitted_at'
    ]
    list_filter = ['status_pengiriman', 'dikirim_at', 'submitted_at']
    search_fields = ['penerima_nama', 'penerima_wa', 'execution__template__nama_pekerjaan']
    readonly_fields = ['dikirim_at', 'share_token', 'share_link']
    
    fieldsets = (
        ('Informasi Pengiriman', {
            'fields': ('execution', 'checklist_result', 'penerima_nama', 'penerima_wa')
        }),
        ('Link & Token', {
            'fields': ('share_link', 'share_token')
        }),
        ('Pesan', {
            'fields': ('pesan_wa', 'error_message')
        }),
        ('Status', {
            'fields': ('status_pengiriman',)
        }),
        ('Timeline', {
            'fields': ('dikirim_oleh', 'dikirim_at', 'accessed_at', 'submitted_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('execution', 'checklist_result', 'dikirim_oleh').order_by('-dikirim_at')

