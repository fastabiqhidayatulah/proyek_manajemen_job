from django.contrib import admin
from .models import Meeting, MeetingPeserta, NotulenItem


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('no_dokumen', 'tanggal_meeting', 'hari', 'status', 'agenda_short', 'get_peserta_count')
    list_filter = ('status', 'tanggal_meeting', 'created_at')
    search_fields = ('no_dokumen', 'agenda', 'tempat')
    readonly_fields = ('no_dokumen', 'hari', 'qr_code_token', 'qr_code_created_at', 'created_at', 'updated_at', 'id')
    fieldsets = (
        ('Dokumen', {
            'fields': ('id', 'no_dokumen_base', 'no_urut', 'no_dokumen', 'revisi', 'terbitan')
        }),
        ('Meeting Details', {
            'fields': ('tanggal_dokumen', 'tanggal_meeting', 'hari', 'jam_mulai', 'jam_selesai', 'tempat', 'agenda')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('QR Code Presensi', {
            'fields': ('qr_code_token', 'qr_code_active', 'qr_code_created_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def agenda_short(self, obj):
        return obj.agenda[:50] if obj.agenda else ''
    agenda_short.short_description = 'Agenda'
    
    def get_peserta_count(self, obj):
        return obj.get_peserta_count()
    get_peserta_count.short_description = 'Jumlah Peserta'


class MeetingPesertaInline(admin.TabularInline):
    model = MeetingPeserta
    fields = ('nama', 'nik', 'bagian', 'tipe_peserta', 'status_kehadiran', 'waktu_check_in', 'catatan')
    extra = 1
    readonly_fields = ('tipe_peserta', 'waktu_check_in')


class NotulenItemInline(admin.TabularInline):
    model = NotulenItem
    fields = ('no', 'pokok_bahasan', 'pic', 'target_deadline', 'status', 'job_created')
    extra = 1
    readonly_fields = ('no',)


@admin.register(MeetingPeserta)
class MeetingPesertaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'meeting', 'tipe_peserta', 'status_kehadiran', 'waktu_check_in')
    list_filter = ('tipe_peserta', 'status_kehadiran', 'created_at')
    search_fields = ('nama', 'nik', 'bagian', 'meeting__no_dokumen')
    readonly_fields = ('tipe_peserta', 'created_at', 'updated_at', 'id')
    fieldsets = (
        ('Meeting', {
            'fields': ('meeting', 'id')
        }),
        ('Peserta Internal', {
            'fields': ('peserta',)
        }),
        ('Peserta External', {
            'fields': ('nama', 'nik', 'bagian')
        }),
        ('Kehadiran', {
            'fields': ('status_kehadiran', 'tipe_peserta', 'waktu_check_in', 'catatan')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotulenItem)
class NotulenItemAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'no', 'pokok_bahasan_short', 'pic', 'target_deadline', 'status', 'job_created')
    list_filter = ('status', 'target_deadline', 'created_at')
    search_fields = ('meeting__no_dokumen', 'pokok_bahasan', 'pic__username')
    readonly_fields = ('no', 'created_at', 'updated_at', 'id')
    fieldsets = (
        ('Meeting', {
            'fields': ('meeting', 'id', 'no')
        }),
        ('Detail Item', {
            'fields': ('pokok_bahasan', 'tanggapan', 'notes')
        }),
        ('Assignment', {
            'fields': ('pic', 'target_deadline')
        }),
        ('Status & Job Link', {
            'fields': ('status', 'job_created')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def pokok_bahasan_short(self, obj):
        return obj.pokok_bahasan[:50] if obj.pokok_bahasan else ''
    pokok_bahasan_short.short_description = 'Pokok Bahasan'
