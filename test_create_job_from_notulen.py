#!/usr/bin/env python
"""
Validation script untuk Create Job from Notulen feature
Memverifikasi bahwa semua components terintegrasi dengan baik
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.test.client import Client
from django.contrib.auth import get_user_model
from core.models import Job, CustomUser
from meetings.models import Meeting, NotulenItem
from core.forms import JobFromNotulenForm
from meetings.views import CreateJobFromNotulenView
from django.urls import reverse

User = get_user_model()

def test_imports():
    """Test bahwa semua imports bekerja"""
    print("✓ Testing imports...")
    try:
        from core.forms import JobFromNotulenForm
        from meetings.views import CreateJobFromNotulenView
        print("  ✓ JobFromNotulenForm imported")
        print("  ✓ CreateJobFromNotulenView imported")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_form_fields():
    """Test bahwa form memiliki semua required fields"""
    print("\n✓ Testing form fields...")
    required_fields = [
        'pokok_bahasan_notulen',
        'pic_notulen',
        'target_deadline_notulen',
        'nama_pekerjaan',
        'tipe_job',
        'assigned_to',
        'job_deadline',
        'jadwal_pelaksanaan',
        'prioritas',
        'fokus',
        'project',
        'aset',
    ]
    
    form = JobFromNotulenForm()
    missing = [f for f in required_fields if f not in form.fields]
    
    if missing:
        print(f"  ✗ Missing fields: {missing}")
        return False
    else:
        print(f"  ✓ All {len(required_fields)} fields present")
        return True

def test_url_patterns():
    """Test bahwa URL pattern terdaftar"""
    print("\n✓ Testing URL patterns...")
    try:
        url = reverse('meetings:create-job-from-notulen', kwargs={'item_pk': '00000000-0000-0000-0000-000000000000'})
        if 'create-job' in url:
            print(f"  ✓ URL pattern found: {url}")
            return True
        else:
            print(f"  ✗ URL pattern incorrect: {url}")
            return False
    except Exception as e:
        print(f"  ✗ URL pattern error: {e}")
        return False

def test_view_methods():
    """Test bahwa view memiliki required methods"""
    print("\n✓ Testing view methods...")
    required_methods = [
        '_can_create_job',
        '_get_allowed_users',
        'get',
        'post',
    ]
    
    view = CreateJobFromNotulenView()
    missing = [m for m in required_methods if not hasattr(view, m)]
    
    if missing:
        print(f"  ✗ Missing methods: {missing}")
        return False
    else:
        print(f"  ✓ All {len(required_methods)} methods present")
        return True

def test_model_fields():
    """Test bahwa Job model memiliki notulen fields"""
    print("\n✓ Testing Job model fields...")
    try:
        # Check fields exist
        assert hasattr(Job, 'notulen_item'), "Job.notulen_item tidak ada"
        assert hasattr(Job, 'notulen_target_date'), "Job.notulen_target_date tidak ada"
        print("  ✓ Job.notulen_item field exists")
        print("  ✓ Job.notulen_target_date field exists")
        
        # Check NotulenItem
        assert hasattr(NotulenItem, 'job_created'), "NotulenItem.job_created tidak ada"
        print("  ✓ NotulenItem.job_created field exists")
        
        return True
    except AssertionError as e:
        print(f"  ✗ Model field error: {e}")
        return False

def test_template_exists():
    """Test bahwa template file exists"""
    print("\n✓ Testing template files...")
    template_path = 'templates/meetings/create_job_from_notulen.html'
    try:
        from django.template.loader import get_template
        template = get_template(template_path)
        print(f"  ✓ Template {template_path} loaded successfully")
        return True
    except Exception as e:
        print(f"  ✗ Template error: {e}")
        return False

def test_permission_logic():
    """Test hierarchy permission logic"""
    print("\n✓ Testing permission logic...")
    try:
        view = CreateJobFromNotulenView()
        
        # Create test user hierarchy
        admin = User.objects.create_user('admin', password='test')
        foreman = User.objects.create_user('foreman', password='test')
        tech = User.objects.create_user('tech', password='test')
        
        # Setup hierarchy
        foreman.atasan = admin
        foreman.save()
        tech.atasan = foreman
        tech.save()
        
        # Test permission checks
        # Admin can create (supervisor of foreman)
        assert view._can_create_job(admin, foreman) == True, "Admin should can_create"
        
        # Foreman can create (PIC self)
        assert view._can_create_job(foreman, foreman) == True, "PIC should can_create"
        
        # Tech can create (subordinate of foreman who is PIC)
        assert view._can_create_job(tech, foreman) == True, "Subordinate should can_create"
        
        print("  ✓ Hierarchy permission logic correct")
        
        # Cleanup
        admin.delete()
        return True
    except Exception as e:
        print(f"  ✗ Permission logic error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("VALIDASI: Create Job from Notulen Feature")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_form_fields,
        test_url_patterns,
        test_view_methods,
        test_model_fields,
        test_template_exists,
        test_permission_logic,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n  ✗ Test error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ SEMUA TESTS PASSED ({passed}/{total})")
        print("=" * 60)
        print("\n✓ Feature siap untuk testing & deployment!")
        return 0
    else:
        print(f"✗ BEBERAPA TESTS FAILED ({passed}/{total})")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
