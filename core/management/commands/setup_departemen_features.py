"""
Management command untuk setup default DepartemenFeature records.
Setiap departemen akan mendapat akses ke semua fitur secara default.
"""

from django.core.management.base import BaseCommand
from core.models import Departemen, DepartemenFeature


class Command(BaseCommand):
    help = 'Setup default DepartemenFeature untuk semua departemen yang ada'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting setup default DepartemenFeature...'))
        
        departemen_list = Departemen.objects.all()
        
        if not departemen_list.exists():
            self.stdout.write(self.style.WARNING('Tidak ada departemen yang ditemukan!'))
            return
        
        created_count = 0
        skipped_count = 0
        
        # Iterate setiap departemen
        for departemen in departemen_list:
            # Iterate setiap feature choice
            for feature_key, feature_name in DepartemenFeature.FEATURE_CHOICES:
                # Check apakah sudah ada
                obj, created = DepartemenFeature.objects.get_or_create(
                    departemen=departemen,
                    feature_key=feature_key,
                    defaults={'is_enabled': True}  # Default: semua fitur enabled
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        f'✓ Created: {departemen.nama_departemen} - {feature_name}'
                    )
                else:
                    skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Setup Complete!\n'
                f'Created: {created_count} records\n'
                f'Skipped: {skipped_count} records (already exist)'
            )
        )
