from django.core.management.base import BaseCommand
from core.models import LeaveEvent

class Command(BaseCommand):
    help = 'Populate departemen field untuk LeaveEvent yang masih NULL'

    def handle(self, *args, **options):
        # Count sebelum
        null_events = LeaveEvent.objects.filter(departemen__isnull=True)
        null_count = null_events.count()
        self.stdout.write(f"Total LeaveEvent dengan departemen NULL: {null_count}")
        
        if null_count == 0:
            self.stdout.write(self.style.SUCCESS("✅ Tidak ada LeaveEvent yang perlu diupdate."))
            return
        
        # Loop dan update satu-satu
        updated = 0
        for event in null_events:
            if event.created_by and event.created_by.departemen:
                event.departemen = event.created_by.departemen
                event.save()
                updated += 1
        
        self.stdout.write(self.style.SUCCESS(f"✅ Berhasil update {updated} LeaveEvent"))
        
        # Handle yang masih NULL
        still_null = LeaveEvent.objects.filter(departemen__isnull=True).count()
        if still_null > 0:
            self.stdout.write(self.style.WARNING(f"⚠️  Masih ada {still_null} LeaveEvent yang tidak bisa auto-update (created_by atau departemen-nya NULL)"))
