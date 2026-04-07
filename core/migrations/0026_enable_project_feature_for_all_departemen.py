# Generated migration to enable features for all departemen

from django.db import migrations


def enable_features_for_all_departemen(apps, schema_editor):
    """Enable essential features for all departemen"""
    DepartemenFeature = apps.get_model('core', 'DepartemenFeature')
    Departemen = apps.get_model('core', 'Departemen')
    
    # Features yang harus enabled untuk semua departemen
    essential_features = ['dashboard', 'project', 'job', 'meetings']
    
    # Get all departemen
    departemen_list = Departemen.objects.all()
    
    for departemen in departemen_list:
        for feature_key in essential_features:
            DepartemenFeature.objects.update_or_create(
                departemen=departemen,
                feature_key=feature_key,
                defaults={'is_enabled': True}
            )
            print(f"✓ Enabled '{feature_key}' feature for {departemen.nama_departemen}")


def reverse_features(apps, schema_editor):
    """Reverse: disable features for non-Teknik departemen"""
    DepartemenFeature = apps.get_model('core', 'DepartemenFeature')
    Departemen = apps.get_model('core', 'Departemen')
    
    # Features yang akan di-disable
    essential_features = ['dashboard', 'project', 'job', 'meetings']
    
    # Get all departemen except Teknik
    departemen_list = Departemen.objects.exclude(nama_departemen__iexact='teknik')
    
    for departemen in departemen_list:
        for feature_key in essential_features:
            DepartemenFeature.objects.filter(
                departemen=departemen,
                feature_key=feature_key
            ).update(is_enabled=False)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_populate_fokus_pekerjaan_initial'),
    ]

    operations = [
        migrations.RunPython(enable_features_for_all_departemen, reverse_features),
    ]
