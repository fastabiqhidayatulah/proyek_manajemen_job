"""
Management command: send_meeting_reminders

Sends WA reminders untuk upcoming meetings:
- 1 hari sebelum pukul 08:00
- 10 menit sebelum meeting mulai

Usage:
    python manage.py send_meeting_reminders
    python manage.py send_meeting_reminders --dry-run
    python manage.py send_meeting_reminders --verbose
"""

import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.db.models import Q

from meetings.models import Meeting, MeetingReminder, MeetingPeserta
from core.models import FonnteSettings
from core.fontte_service import FonteService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send WA meeting reminders via Fonnte API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
        parser.add_argument(
            '--meeting-id',
            type=str,
            help='Send reminders for specific meeting (UUID)'
        )
    
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        meeting_id = options.get('meeting_id')
        
        self.stdout.write(self.style.SUCCESS('🚀 Starting Meeting Reminder Service...'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  DRY RUN MODE - no messages will be sent'))
        
        # Get pending reminders
        pending_reminders = self._get_pending_reminders()
        
        if meeting_id:
            pending_reminders = pending_reminders.filter(meeting__id=meeting_id)
        
        if verbose:
            self.stdout.write(f'📊 Found {pending_reminders.count()} pending reminders')
        
        if not pending_reminders.exists():
            self.stdout.write(self.style.SUCCESS('✅ No pending reminders at this time'))
            return
        
        # Process reminders
        sent_count = 0
        failed_count = 0
        
        for reminder in pending_reminders:
            try:
                success = self._send_reminder(reminder, dry_run=dry_run, verbose=verbose)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error processing reminder {reminder.id}: {str(e)}')
                )
                failed_count += 1
                logger.exception(f'Error sending reminder {reminder.id}')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Summary: {sent_count} sent, {failed_count} failed, '
                f'{pending_reminders.count() - sent_count - failed_count} pending'
            )
        )
    
    def _get_pending_reminders(self):
        """Get all pending reminders that are due to send"""
        now_time = now()
        return MeetingReminder.objects.filter(
            status='pending',
            scheduled_time__lte=now_time
        ).select_related('meeting', 'peserta')
    
    def _send_reminder(self, reminder, dry_run=False, verbose=False):
        """
        Send single reminder.
        
        Returns:
            bool: True jika berhasil atau dry-run, False jika gagal
        """
        meeting = reminder.meeting
        peserta = reminder.peserta
        
        # Validasi peserta punya nomor telepon
        if peserta.tipe_peserta == 'internal':
            phone_number = peserta.peserta.nomor_telepon
        else:
            # External peserta tidak bisa reminder via WA
            reminder.status = 'failed'
            reminder.error_log = 'External peserta: no phone number'
            reminder.save()
            return False
        
        if not phone_number:
            reminder.status = 'failed'
            reminder.error_log = 'Peserta tidak punya nomor telepon'
            reminder.save()
            if verbose:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Peserta {peserta.nama} tidak punya nomor telepon'
                    )
                )
            logger.warning(f'Peserta {peserta.nama} tidak punya nomor telepon')
            return False
        
        # Get Fonnte settings dari departemen meeting creator
        try:
            from core.models import FonnteSettings
            fontte_settings = FonnteSettings.objects.get(
                departemen=meeting.created_by.departemen,
                is_active=True
            )
        except FonnteSettings.DoesNotExist:
            reminder.status = 'failed'
            reminder.error_log = 'No Fonnte settings configured untuk departemen ini'
            reminder.save()
            if verbose:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ No Fonnte API configured untuk departemen {meeting.created_by.departemen}'
                    )
                )
            return False
        
        # Build message
        message = self._build_reminder_message(reminder)
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n📤 [DRY RUN] Would send to {phone_number}:\n{message}'
                )
            )
            return True
        
        if verbose:
            self.stdout.write(f'\n📤 Sending to {phone_number}...')
            self.stdout.write(f'Message:\n{message}\n')
        
        # Send via Fonnte
        try:
            fontte = FonteService(fontte_settings)
            response = fontte.send_message(target=phone_number, message=message)
            
            if response['success']:
                reminder.status = 'sent'
                reminder.sent_at = now()
                reminder.message_id = response.get('message_id')
                reminder.save()
                
                if verbose:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Sent! Message ID: {response.get("message_id")}')
                    )
                return True
            else:
                reminder.status = 'failed'
                reminder.error_log = response.get('error', 'Unknown error')
                reminder.save()
                
                if verbose:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Failed: {response.get("error")}')
                    )
                logger.warning(
                    f'Failed to send reminder {reminder.id}: {response.get("error")}'
                )
                return False
        
        except Exception as e:
            reminder.status = 'failed'
            reminder.error_log = str(e)
            reminder.save()
            
            if verbose:
                self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
            logger.exception(f'Error sending reminder {reminder.id}')
            return False
    
    def _build_reminder_message(self, reminder):
        """
        Build WA reminder message.
        
        Format:
        🔔 Reminder Meeting - [MEETING DOC]
        ⏰ Jam: [JAMULAI]
        📍 Lokasi: [TEMPAT]
        📌 Agenda: [AGENDA]
        
        Peserta: [NAMA]
        """
        meeting = reminder.meeting
        timing_type = reminder.get_timing_type_display()
        
        # Format jam
        jam_mulai = meeting.jam_mulai.strftime('%H:%M')
        
        # Shorten agenda jika terlalu panjang
        agenda = meeting.agenda[:100]
        if len(meeting.agenda) > 100:
            agenda += '...'
        
        message = (
            f'🔔 *REMINDER MEETING*\n'
            f'📄 Dokumen: {meeting.no_dokumen}\n'
            f'⏰ Waktu: {jam_mulai}\n'
            f'📍 Lokasi: {meeting.tempat}\n'
            f'📌 Agenda: {agenda}\n'
            f'👤 Peserta: {reminder.peserta.nama}\n'
        )
        
        return message.strip()
