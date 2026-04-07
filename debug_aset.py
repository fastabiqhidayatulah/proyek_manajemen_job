#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CustomUser, Departemen, AsetDepartemen

# Check Operasional departemen
try:
    operasional = Departemen.objects.get(nama_departemen='Operasional')
    print(f"✓ Departemen Operasional found: {operasional}")
except Departemen.DoesNotExist:
    print("✗ Departemen Operasional NOT FOUND!")
    operasional = None

# Check user anisia
try:
    anisia = CustomUser.objects.get(username='anisia')
    print(f"✓ User anisia found: {anisia}, departemen={anisia.departemen}")
except CustomUser.DoesNotExist:
    print("✗ User anisia NOT FOUND!")
    anisia = None

# Check AsetDepartemen Level 0 for Operasional
if operasional:
    level0 = AsetDepartemen.objects.filter(departemen=operasional, level=0)
    print(f"\nAsetDepartemen Level 0 (Operasional): {level0.count()}")
    for item in level0:
        print(f"  - {item.id}: {item.nama}")
        
        # Check children
        children = AsetDepartemen.objects.filter(parent=item)
        print(f"    Children: {children.count()}")
        for child in children:
            print(f"      - {child.id}: {child.nama} (level={child.level})")
            
            # Check grandchildren
            grandchildren = AsetDepartemen.objects.filter(parent=child)
            for grandchild in grandchildren:
                print(f"        - {grandchild.id}: {grandchild.nama} (level={grandchild.level})")
