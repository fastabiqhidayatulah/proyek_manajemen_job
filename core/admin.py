from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from mptt.admin import DraggableMPTTAdmin

# Library untuk Import/Export Excel
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import (
    CustomUser, 
    Jabatan, 
    Departemen,
    Bagian,
    DepartemenFeature,
    Personil, 
    AsetMesin,
    AsetDepartemen,
    FokusPekerjaan,
    Project, 
    Job, 
    JobDate, 
    Attachment,
    Karyawan,
    LeaveEvent,
    MaintenanceMode,
    FonnteSettings
)

# ============================================================
# 1. SETUP IMPORT/EXPORT ASET (MASSAL)
# ============================================================
class AsetMesinResource(resources.ModelResource):
    # Memungkinkan import parent berdasarkan 'nama', bukan ID
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=ForeignKeyWidget(AsetMesin, 'nama') 
    )

    class Meta:
        model = AsetMesin
        fields = ('id', 'nama', 'parent')
        import_id_fields = ('id',)

# ============================================================
# 2. SETUP ADMIN MODEL ASET (TREE VIEW + IMPORT)
# ============================================================
@admin.register(AsetMesin)
class AsetMesinAdmin(ImportExportModelAdmin, DraggableMPTTAdmin):
    resource_class = AsetMesinResource
    
    # Konfigurasi Tampilan Tree (Pohon)
    mptt_level_indent = 20
    list_display = ('tree_actions', 'indented_title')
    list_display_links = ('indented_title',)
    
    # Penting untuk autocomplete_fields di JobAdmin
    search_fields = ('nama',) 

# ============================================================
# 3. SETUP CUSTOM USER (DENGAN JABATAN & ATASAN)
# ============================================================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Menambahkan field custom ke form edit user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Groups: "Workshop" = edit stok barang, "Warehouse" = full access + import'
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Informasi Organisasi', {
            'fields': ('jabatan', 'atasan', 'departemen', 'bagian'),
            'description': 'Konfigurasi jabatan, atasan, departemen, dan bagian user'
        }),
        ('Kontak', {'fields': ('nomor_telepon',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
            'description': 'Groups: "Workshop" = edit stok barang, "Warehouse" = full access + import'
        }),
        ('Informasi Organisasi', {
            'fields': ('jabatan', 'atasan', 'departemen', 'bagian'),
            'description': 'Konfigurasi jabatan, atasan, departemen, dan bagian user'
        }),
        ('Kontak', {'fields': ('nomor_telepon',)}),
    )
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'jabatan', 'get_departemen_bagian', 'atasan', 'is_staff']
    list_filter = UserAdmin.list_filter + ('groups', 'jabatan', 'departemen', 'bagian', 'atasan',)
    
    # Penting untuk autocomplete_fields 'pic' di JobAdmin
    search_fields = ('username', 'first_name', 'last_name', 'departemen__nama_departemen', 'bagian__nama_bagian')
    
    def get_departemen_bagian(self, obj):
        """Tampilkan departemen dan bagian user di list view"""
        if obj.bagian:
            return format_html(
                '<span style="background: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 3px; font-size: 11px;"><strong>{}</strong></span> / <span style="background: #fef3c7; color: #92400e; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
                obj.departemen.nama_departemen if obj.departemen else '-',
                obj.bagian.nama_bagian
            )
        elif obj.departemen:
            return format_html(
                '<span style="background: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 3px; font-size: 11px;"><strong>{}</strong></span>',
                obj.departemen.nama_departemen
            )
        return '-'
    get_departemen_bagian.short_description = 'Departemen / Bagian'
    
    def get_groups(self, obj):
        """Tampilkan groups user di list view"""
        groups = obj.groups.all()
        if not groups:
            return '-'
        group_names = ', '.join([f'<span style="background: #e0e7ff; color: #3730a3; padding: 2px 6px; border-radius: 3px; margin: 2px; display: inline-block; font-size: 11px;">{g.name}</span>' for g in groups])
        return format_html(group_names)
    get_groups.short_description = 'Groups'

# ============================================================# SETUP DEPARTEMEN FEATURE PERMISSION (INLINE)
# ============================================================
class DepartemenFeatureInline(admin.TabularInline):
    """Inline untuk manage feature permission di dalam Departemen form"""
    model = DepartemenFeature
    extra = 0
    fields = ('feature_key', 'is_enabled')
    can_delete = True

# ============================================================# SETUP DEPARTEMEN & BAGIAN
# ============================================================
class BagianInline(admin.TabularInline):
    """Inline Bagian dalam Departemen"""
    model = Bagian
    extra = 1
    fields = ('nama_bagian', 'kepala_bagian', 'deskripsi')

@admin.register(Departemen)
class DepartemenAdmin(admin.ModelAdmin):
    list_display = ('nama_departemen', 'kepala_departemen', 'get_jumlah_bagian', 'get_jumlah_anggota', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nama_departemen', 'kepala_departemen__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informasi Departemen', {
            'fields': ('nama_departemen', 'deskripsi')
        }),
        ('Kepemimpinan', {
            'fields': ('kepala_departemen',)
        }),
        ('Google Calendar Integration', {
            'fields': ('google_calendar_id',),
            'description': 'Masukkan Google Calendar ID untuk departemen ini (cth: abc123@group.calendar.google.com). Digunakan untuk sinkronisasi ijin/cuti.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BagianInline, DepartemenFeatureInline]
    
    def get_jumlah_bagian(self, obj):
        """Hitung jumlah bagian dalam departemen"""
        count = obj.daftar_bagian.count()
        return format_html(
            '<span style="background: #d1d5db; color: #1f2937; padding: 2px 6px; border-radius: 3px; font-size: 11px;"><strong>{}</strong> Bagian</span>',
            count
        )
    get_jumlah_bagian.short_description = 'Bagian'
    
    def get_jumlah_anggota(self, obj):
        """Hitung jumlah anggota departemen"""
        count = obj.anggota_departemen.count()
        return format_html(
            '<span style="background: #dbeafe; color: #1e40af; padding: 2px 6px; border-radius: 3px; font-size: 11px;"><strong>{}</strong> User</span>',
            count
        )
    get_jumlah_anggota.short_description = 'Total User'

@admin.register(Bagian)
class BagianAdmin(admin.ModelAdmin):
    list_display = ('nama_bagian', 'departemen', 'kepala_bagian', 'get_jumlah_anggota', 'created_at')
    list_filter = ('departemen', 'created_at')
    search_fields = ('nama_bagian', 'departemen__nama_departemen', 'kepala_bagian__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informasi Bagian', {
            'fields': ('nama_bagian', 'departemen', 'deskripsi')
        }),
        ('Kepemimpinan', {
            'fields': ('kepala_bagian',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_jumlah_anggota(self, obj):
        """Hitung jumlah anggota bagian"""
        count = obj.anggota_bagian.count()
        return format_html(
            '<span style="background: #dbeafe; color: #1e40af; padding: 2px 6px; border-radius: 3px; font-size: 11px;"><strong>{}</strong> User</span>',
            count
        )
    get_jumlah_anggota.short_description = 'Total User'

# ============================================================
# SETUP DEPARTEMEN FEATURE PERMISSION
# ============================================================
@admin.register(DepartemenFeature)
class DepartemenFeatureAdmin(admin.ModelAdmin):
    """Admin untuk manage feature permission per departemen"""
    list_display = ('departemen', 'get_feature_name', 'is_enabled', 'created_at')
    list_filter = ('departemen', 'is_enabled', 'created_at')
    search_fields = ('departemen__nama_departemen', 'feature_key')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Feature Permission', {
            'fields': ('departemen', 'feature_key', 'is_enabled')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_feature_name(self, obj):
        """Display feature name yang lebih readable"""
        return format_html(
            '<span style="background: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 3px; font-size: 11px;"><strong>{}</strong></span>',
            obj.get_feature_key_display()
        )
    get_feature_name.short_description = 'Feature'

# ============================================================# 4. SETUP PROJECT & PERSONIL
# ============================================================
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('nama_project', 'deskripsi', 'created_at')
    search_fields = ('nama_project',)

@admin.register(Personil)
class PersonilAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'penanggung_jawab')
    list_filter = ('penanggung_jawab',)
    search_fields = ('nama_lengkap', 'penanggung_jawab__username')

# ============================================================
# SETUP KARYAWAN (MASTER DATA - IMPORT/EXPORT EXCEL)
# ============================================================
class KaryawanResource(resources.ModelResource):
    """Resource untuk import/export Karyawan dari Excel"""
    class Meta:
        model = Karyawan
        fields = ('nik', 'nama_lengkap', 'departemen', 'posisi', 'status')
        import_id_fields = ('nik',)

@admin.register(Karyawan)
class KaryawanAdmin(ImportExportModelAdmin):
    resource_class = KaryawanResource
    
    list_display = ('nik', 'nama_lengkap', 'departemen', 'posisi', 'status', 'created_at')
    list_filter = ('status', 'departemen')
    search_fields = ('nik', 'nama_lengkap', 'departemen')
    
    fieldsets = (
        ('Data Identitas', {
            'fields': ('nik', 'nama_lengkap')
        }),
        ('Informasi Pekerjaan', {
            'fields': ('departemen', 'posisi', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Jabatan)
class JabatanAdmin(admin.ModelAdmin):
    list_display = ('nama_jabatan',)

# ============================================================
# 5. SETUP JOB (KOMPLEKS)
# ============================================================

class JobDateInline(admin.TabularInline):
    model = JobDate
    extra = 1
    fields = ('tanggal', 'status', 'catatan')

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    
    # Method Custom: Menampilkan list personil
    def get_personil_ditugaskan(self, obj):
        # PERBAIKAN: Menggunakan 'personil_ditugaskan' sesuai error log
        personil_list = obj.personil_ditugaskan.all()[:3] 
        names = [p.nama_lengkap for p in personil_list]
        if obj.personil_ditugaskan.count() > 3:
            names.append("...")
        return ", ".join(names)
    get_personil_ditugaskan.short_description = 'Personil Ditugaskan'
    
    # Method Custom: Progress Bar Visual
    def progress_bar(self, obj):
        # Cek apakah method get_progress_percent ada di model
        progress = getattr(obj, 'get_progress_percent', lambda: 0)()
        
        # Warna bar berdasarkan persentase
        color = "red"
        if progress >= 50: color = "orange"
        if progress >= 100: color = "green"

        return format_html(
            '''
            <div style="width: 100px; background-color: #e0e0e0; border-radius: 3px;">
                <div style="width: {}%; background-color: {}; height: 15px; border-radius: 3px;"></div>
            </div>
            <small>{}%</small>
            ''',
            progress, color, progress
        )
    progress_bar.short_description = 'Progress'

    # List Columns
    list_display = (
        'nama_pekerjaan', 
        'project', 
        'pic',
        'fokus',      
        'prioritas',  
        'get_personil_ditugaskan', 
        'progress_bar',
        'updated_at'
    )
    
    # Filters
    list_filter = ('project', 'fokus', 'prioritas', 'pic') 
    
    # Search
    search_fields = ('nama_pekerjaan', 'project__nama_project')
    
    # Inlines
    inlines = [JobDateInline, AttachmentInline]
    
    # Widget Khusus
    # PERBAIKAN: Menggunakan 'personil_ditugaskan'
    filter_horizontal = ('personil_ditugaskan',) 
    
    # Autocomplete (Search dropdown)
    # PERBAIKAN: Menggunakan 'aset' (bukan mesin/line) sesuai error log
    autocomplete_fields = ['project', 'aset', 'pic'] 

# Header Admin Panel
admin.site.site_header = "Admin Panel Manajemen Pekerjaan"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Selamat Datang di Admin Panel"

# ============================================================
# 6. SETUP MAINTENANCE MODE (ADMIN CONTROL)
# ============================================================
@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    list_display = ('get_status', 'message', 'estimated_time', 'updated_at')
    
    fieldsets = (
        ('Status Maintenance', {
            'fields': ('is_active',)
        }),
        ('Pesan untuk User', {
            'fields': ('message', 'estimated_time')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_status(self, obj):
        """Tampilkan status dengan warna"""
        if obj.is_active:
            return format_html(
                '<span style="color: red; font-weight: bold;">🔴 MAINTENANCE AKTIF</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">🟢 NORMAL</span>'
            )
    get_status.short_description = 'Status'


# ============================================================
# FONNTE SETTINGS ADMIN - WA API Configuration
# ============================================================
@admin.register(FonnteSettings)
class FonnteSettingsAdmin(admin.ModelAdmin):
    """Admin untuk manage Fonnte API settings per departemen"""
    list_display = ('departemen', 'is_active', 'connexion_status', 'created_at')
    list_filter = ('is_active', 'departemen', 'created_at')
    search_fields = ('departemen__nama_departemen',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'connexion_test_result')
    
    fieldsets = (
        ('Departemen', {
            'fields': ('departemen',)
        }),
        ('Fonnte API', {
            'fields': ('token', 'country_code'),
            'description': '📱 Dapatkan token dari Fonnte dashboard'
        }),
        ('Status', {
            'fields': ('is_active', 'connexion_test_result'),
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def connexion_test_result(self, obj):
        """Test koneksi ke Fonnte API"""
        if obj.test_connection():
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ CONNECTED</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">❌ FAILED</span>'
            )
    connexion_test_result.short_description = 'Connection Status'
    
    def connexion_status(self, obj):
        """Tampilkan status koneksi di list view"""
        if obj.is_active and obj.test_connection():
            return format_html('<span style="color: green;">✅ Aktif & Connected</span>')
        elif obj.is_active:
            return format_html('<span style="color: orange;">⚠️ Aktif tapi Error</span>')
        else:
            return format_html('<span style="color: gray;">⏸️ Inactive</span>')
    connexion_status.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Set created_by saat create"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        """Hanya superuser yang bisa delete"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Hanya admin yang bisa add"""
        return request.user.is_staff and request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Hanya admin yang bisa change"""
        return request.user.is_staff and request.user.is_superuser


# ============================================================
# ADMIN UNTUK ASET DEPARTEMEN (Tree untuk non-Teknik)
# ============================================================
@admin.register(AsetDepartemen)
class AsetDepartemenAdmin(DraggableMPTTAdmin):
    """Admin untuk AsetDepartemen dengan tree view"""
    list_display = ('indented_title', 'departemen', 'get_full_path')
    list_filter = ('departemen__nama_departemen', 'level')
    search_fields = ('nama', 'departemen__nama_departemen')
    ordering = ('departemen', 'tree_id', 'lft')
    
    fieldsets = (
        ('Info Aset', {
            'fields': ('nama', 'departemen', 'parent')
        }),
        ('Tree Fields (Auto)', {
            'fields': ('level', 'lft', 'rght', 'tree_id'),
            'classes': ('collapse',),
            'description': 'Diisi otomatis oleh MPPT library'
        }),
    )
    
    readonly_fields = ('level', 'lft', 'rght', 'tree_id')
    
    def get_full_path(self, obj):
        """Tampilkan full path (parent > child > grandchild)"""
        return str(obj)
    get_full_path.short_description = 'Full Path'


# ============================================================
# ADMIN UNTUK FOKUS PEKERJAAN (per Departemen)
# ============================================================
@admin.register(FokusPekerjaan)
class FokusPekerjaanAdmin(admin.ModelAdmin):
    """Admin untuk FokusPekerjaan dengan grouping per departemen"""
    list_display = ('nama', 'departemen', 'urutan', 'is_active', 'get_created_date')
    list_filter = ('departemen__nama_departemen', 'is_active', 'created_at')
    search_fields = ('nama', 'departemen__nama_departemen')
    ordering = ('departemen__nama_departemen', 'urutan', 'nama')
    
    fieldsets = (
        ('Info Fokus', {
            'fields': ('nama', 'departemen', 'urutan', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_created_date(self, obj):
        """Tampilkan tanggal created"""
        return obj.created_at.strftime('%d/%m/%Y %H:%M')
    get_created_date.short_description = 'Dibuat Pada'
    
    def has_delete_permission(self, request, obj=None):
        """Batasi delete untuk fokus yang sudah digunakan"""
        if obj:
            # Check if fokus ini sudah digunakan di Job
            from .models import Job
            if Job.objects.filter(fokus=obj.nama).exists():
                return False
        return request.user.is_superuser


# ============================================================
# CUSTOM ADMIN INDEX WITH BACKUP/RESTORE LINK
# ============================================================
class CustomAdminSite(admin.AdminSite):
    """Custom admin site with additional links"""
    
    def index(self, request, extra_context=None):
        """Add custom links to admin index"""
        if extra_context is None:
            extra_context = {}
        
        # Add backup/restore link if user is superuser
        if request.user.is_superuser:
            extra_context['backup_restore_url'] = '/admin/backup-restore/'
            extra_context['database_health_url'] = '/admin/database-health/'
        
        return super().index(request, extra_context)


# Optional: Replace default admin site (uncomment if needed)
# admin.site.__class__ = CustomAdminSite