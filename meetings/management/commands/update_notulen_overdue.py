"""
Management command untuk auto-update NotulenItem status ke 'overdue'
jika deadline sudah lewat dan status belum 'done'

Usage:
    python manage.py update_notulen_overdue

Bisa dijadwalkan via cron:
    0 * * * * cd /path/to/project && python manage.py update_notulen_overdue
"""

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from meetings.models import NotulenItem


class Command(BaseCommand):
    help = 'Update NotulenItem status to overdue if deadline has passed'

    def handle(self, *args, **options):
        """
        Cari semua NotulenItem yang:
        1. Status bukan 'done'
        2. Target deadline sudah lewat
        3. Update status ke 'overdue'
        """
        today = now().date()
        
        # Query: status != 'done' AND target_deadline < today
        overdue_items = NotulenItem.objects.filter(
            status__in=['open', 'progress'],
            target_deadline__lt=today
        )
        
        updated_count = 0
        for item in overdue_items:
            item.status = 'overdue'
            item.save()
            updated_count += 1
            self.stdout.write(
                f"✓ Updated: {item.meeting.no_dokumen} - Item {item.no} → OVERDUE"
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal {updated_count} items updated to OVERDUE status')
        )
