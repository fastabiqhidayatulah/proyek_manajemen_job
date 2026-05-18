"""
Django signals untuk meetings app.

Auto-create MeetingReminder ketika Meeting dibuat.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import timedelta, time
from django.utils.timezone import now, make_aware

from .models import Meeting, MeetingReminder, MeetingPeserta
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Meeting)
def auto_create_meeting_reminders(sender, instance, created, **kwargs):
    """
    Auto-create MeetingReminder untuk setiap peserta ketika Meeting dibuat.
    
    Membuat 2 reminders:
    1. H-1 jam 08:00 pagi
    2. 10 menit sebelum jam mulai
    """
    if not created:
        return  # Only for new meetings
    
    meeting = instance
    
    try:
        # Get all peserta untuk meeting ini
        peserta_list = MeetingPeserta.objects.filter(meeting=meeting)
        
        if not peserta_list.exists():
            logger.info(f'[MeetingReminder] No peserta untuk meeting {meeting.no_dokumen}')
            return
        
        reminders_to_create = []
        
        for peserta in peserta_list:
            # Reminder 1: H-1 jam 08:00
            reminder_1_time = _calculate_reminder_time_1day_08am(meeting.tanggal_meeting)
            
            # Reminder 2: 10 menit sebelum
            reminder_2_time = _calculate_reminder_time_10min_before(
                meeting.tanggal_meeting,
                meeting.jam_mulai
            )
            
            # Cek reminder 1 tidak di masa lalu
            if reminder_1_time > now():
                reminders_to_create.append(
                    MeetingReminder(
                        meeting=meeting,
                        peserta=peserta,
                        timing_type='1day_08am',
                        scheduled_time=reminder_1_time
                    )
                )
            
            # Cek reminder 2 tidak di masa lalu
            if reminder_2_time > now():
                reminders_to_create.append(
                    MeetingReminder(
                        meeting=meeting,
                        peserta=peserta,
                        timing_type='10min_before',
                        scheduled_time=reminder_2_time
                    )
                )
        
        # Bulk create
        if reminders_to_create:
            MeetingReminder.objects.bulk_create(reminders_to_create)
            logger.info(
                f'[MeetingReminder] Created {len(reminders_to_create)} reminders '
                f'untuk meeting {meeting.no_dokumen}'
            )
    
    except Exception as e:
        logger.exception(f'Error creating reminders untuk meeting {meeting.id}: {str(e)}')


@receiver(post_save, sender=MeetingPeserta)
def create_reminders_for_new_peserta(sender, instance, created, **kwargs):
    """
    Auto-create reminders ketika peserta baru ditambahkan ke meeting.
    
    Ini untuk handle kasus peserta ditambahkan setelah meeting dibuat.
    """
    if not created:
        return  # Only for new peserta
    
    peserta = instance
    meeting = peserta.meeting
    
    try:
        # Cek reminder sudah ada untuk peserta ini
        existing = MeetingReminder.objects.filter(
            meeting=meeting,
            peserta=peserta
        ).exists()
        
        if existing:
            return  # Sudah ada reminder untuk peserta ini
        
        reminders_to_create = []
        
        # Reminder 1: H-1 jam 08:00
        reminder_1_time = _calculate_reminder_time_1day_08am(meeting.tanggal_meeting)
        
        # Reminder 2: 10 menit sebelum
        reminder_2_time = _calculate_reminder_time_10min_before(
            meeting.tanggal_meeting,
            meeting.jam_mulai
        )
        
        # Cek reminder 1 tidak di masa lalu
        if reminder_1_time > now():
            reminders_to_create.append(
                MeetingReminder(
                    meeting=meeting,
                    peserta=peserta,
                    timing_type='1day_08am',
                    scheduled_time=reminder_1_time
                )
            )
        
        # Cek reminder 2 tidak di masa lalu
        if reminder_2_time > now():
            reminders_to_create.append(
                MeetingReminder(
                    meeting=meeting,
                    peserta=peserta,
                    timing_type='10min_before',
                    scheduled_time=reminder_2_time
                )
            )
        
        # Bulk create
        if reminders_to_create:
            MeetingReminder.objects.bulk_create(reminders_to_create)
            logger.info(
                f'[MeetingReminder] Created {len(reminders_to_create)} reminders '
                f'untuk peserta {peserta.nama} di meeting {meeting.no_dokumen}'
            )
    
    except Exception as e:
        logger.exception(
            f'Error creating reminders untuk peserta {peserta.id}: {str(e)}'
        )


@receiver(post_delete, sender=MeetingPeserta)
def delete_reminders_for_deleted_peserta(sender, instance, **kwargs):
    """Delete reminders ketika peserta dihapus dari meeting"""
    peserta = instance
    
    try:
        MeetingReminder.objects.filter(
            meeting=peserta.meeting,
            peserta=peserta
        ).delete()
        
        logger.info(
            f'[MeetingReminder] Deleted reminders untuk peserta {peserta.nama}'
        )
    except Exception as e:
        logger.exception(f'Error deleting reminders untuk peserta {peserta.id}: {str(e)}')


def _calculate_reminder_time_1day_08am(meeting_date):
    """
    Calculate reminder time untuk H-1 pukul 08:00.
    
    Args:
        meeting_date: Date object dari meeting.tanggal_meeting
    
    Returns:
        datetime: H-1 jam 08:00 dalam timezone Jakarta
    """
    from datetime import datetime
    from django.utils.timezone import make_aware
    
    # H-1 pada jam 08:00
    reminder_date = meeting_date - timedelta(days=1)
    reminder_time = time(8, 0, 0)
    
    # Combine date + time
    reminder_datetime = datetime.combine(reminder_date, reminder_time)
    
    # Make aware dengan timezone default (Asia/Jakarta dari settings)
    reminder_datetime = make_aware(reminder_datetime)
    
    return reminder_datetime


def _calculate_reminder_time_10min_before(meeting_date, meeting_time):
    """
    Calculate reminder time untuk 10 menit sebelum meeting mulai.
    
    Args:
        meeting_date: Date object dari meeting.tanggal_meeting
        meeting_time: Time object dari meeting.jam_mulai
    
    Returns:
        datetime: 10 menit sebelum meeting mulai dalam timezone Jakarta
    """
    from datetime import datetime
    from django.utils.timezone import make_aware
    
    # Combine date + time
    meeting_datetime = datetime.combine(meeting_date, meeting_time)
    
    # Make aware dengan timezone default
    meeting_datetime = make_aware(meeting_datetime)
    
    # Subtract 10 minutes
    reminder_datetime = meeting_datetime - timedelta(minutes=10)
    
    return reminder_datetime


# ==============================================================================
# GOOGLE SHEETS SYNC SIGNAL
# ==============================================================================

@receiver(post_save, sender=Meeting)
def sync_meeting_to_google_sheets(sender, instance, created, **kwargs):
    """
    Auto-sync meeting ke Google Sheets ketika meeting dibuat atau updated.
    
    Hanya sync jika:
    1. Meeting baru (created=True)
    2. Status meeting adalah 'final' (meeting sudah finalized)
    3. Departemen punya google_sheet_id yang dikonfigurasi
    
    Sync data: [No_Dokumen, Agenda, Tanggal, Waktu_Mulai, Waktu_Selesai, Lokasi, Peserta, "No"]
    """
    if not created:
        return  # Only sync untuk meeting baru
    
    meeting = instance
    
    # Check: Status meeting harus 'final' untuk di-sync ke sheets
    if meeting.status != 'final':
        logger.info(f'[GoogleSheets] Meeting {meeting.no_dokumen} berstatus {meeting.status}, skip sync')
        return
    
    try:
        # Get departemen dari pemilik meeting (created_by)
        if not meeting.created_by or not meeting.created_by.departemen:
            logger.warning(f'[GoogleSheets] Meeting {meeting.no_dokumen} tidak punya departemen info')
            return
        
        departemen = meeting.created_by.departemen
        
        # Check: Departemen harus punya google_sheet_id
        if not departemen.google_sheet_id:
            logger.warning(
                f'[GoogleSheets] Departemen {departemen.nama_departemen} '
                f'tidak punya google_sheet_id, skip sync'
            )
            return
        
        # Get list peserta sebagai comma-separated string
        peserta_names = list(
            meeting.peserta.values_list('username', flat=True)
        )
        peserta_str = ', '.join(peserta_names) if peserta_names else ''
        
        # Prepare meeting data untuk append ke sheets
        meeting_data = {
            'no_dokumen': meeting.no_dokumen,
            'agenda': meeting.agenda,
            'tanggal': meeting.tanggal_meeting,  # Date object, akan di-convert di service
            'waktu_mulai': meeting.jam_mulai,    # Time object, akan di-convert di service
            'waktu_selesai': meeting.jam_selesai,  # Time object
            'lokasi': meeting.tempat,
            'peserta': peserta_str
        }
        
        # Initialize Google Sheets service dan append
        from core.services import get_sheets_service
        sheets_service = get_sheets_service()
        
        if not sheets_service:
            logger.error(f'[GoogleSheets] Failed to initialize sheets service')
            return
        
        # Append meeting row ke sheets
        result = sheets_service.append_meeting_row(
            spreadsheet_id=departemen.google_sheet_id,
            meeting_data=meeting_data
        )
        
        logger.info(
            f'✅ [GoogleSheets] Meeting {meeting.no_dokumen} synced ke sheet '
            f'{departemen.google_sheet_id}'
        )
        
    except Exception as e:
        logger.exception(
            f'❌ [GoogleSheets] Error syncing meeting {meeting.no_dokumen}: {str(e)}'
        )
        # Don't raise - ini optional feature, don't break meeting creation


def ready():
    """Called when app is ready"""
    # Signals are auto-registered when this module is imported
    pass
