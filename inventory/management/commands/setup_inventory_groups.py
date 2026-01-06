"""
Management command untuk setup grup inventory dengan permissions.
Jalankan: python manage.py setup_inventory_groups
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Barang, StockLevel


class Command(BaseCommand):
    help = 'Setup grup inventory (Workshop, Warehouse) dengan permissions'

    def handle(self, *args, **options):
        # Get content types
        barang_ct = ContentType.objects.get_for_model(Barang)
        stock_ct = ContentType.objects.get_for_model(StockLevel)

        # Define Workshop permissions (dapat edit stok, tidak bisa delete/create barang)
        workshop_perms = [
            'change_barang',      # Dapat edit barang
            'change_stocklevel',  # Dapat edit stok
            'view_barang',        # Dapat lihat barang
            'view_stocklevel',    # Dapat lihat stok
        ]

        # Define Warehouse permissions (full access)
        warehouse_perms = [
            'add_barang',
            'change_barang',
            'delete_barang',
            'view_barang',
            'add_stocklevel',
            'change_stocklevel',
            'delete_stocklevel',
            'view_stocklevel',
        ]

        # Create/update Workshop group
        workshop_group, created = Group.objects.get_or_create(name='Workshop')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grup "Workshop" dibuat'))
        else:
            self.stdout.write(self.style.WARNING('> Grup "Workshop" sudah ada'))
            # Clear existing permissions
            workshop_group.permissions.clear()

        # Add Workshop permissions
        for perm_codename in workshop_perms:
            try:
                perm = Permission.objects.get(
                    codename=perm_codename,
                    content_type__in=[barang_ct, stock_ct]
                )
                workshop_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Permission "{perm_codename}" tidak ditemukan')
                )

        self.stdout.write(
            self.style.SUCCESS(f'✓ Grup "Workshop" diupdate dengan {workshop_group.permissions.count()} permissions')
        )

        # Create/update Warehouse group
        warehouse_group, created = Group.objects.get_or_create(name='Warehouse')
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Grup "Warehouse" dibuat'))
        else:
            self.stdout.write(self.style.WARNING('> Grup "Warehouse" sudah ada'))
            # Clear existing permissions
            warehouse_group.permissions.clear()

        # Add Warehouse permissions
        for perm_codename in warehouse_perms:
            try:
                perm = Permission.objects.get(
                    codename=perm_codename,
                    content_type__in=[barang_ct, stock_ct]
                )
                warehouse_group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Permission "{perm_codename}" tidak ditemukan')
                )

        self.stdout.write(
            self.style.SUCCESS(f'✓ Grup "Warehouse" diupdate dengan {warehouse_group.permissions.count()} permissions')
        )

        self.stdout.write(self.style.SUCCESS('\n✓ Setup inventory groups selesai!'))
        self.stdout.write(self.style.WARNING('\nUntuk menambah user ke group:\n'))
        self.stdout.write('  - Workshop: user.groups.add(Group.objects.get(name="Workshop"))')
        self.stdout.write('  - Warehouse: user.groups.add(Group.objects.get(name="Warehouse"))')
