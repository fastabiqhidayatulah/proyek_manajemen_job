# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preventive_jobs', '0003_add_assigned_to_personil'),
    ]

    operations = [
        # Hapus field periode
        migrations.RemoveField(
            model_name='preventivejobtemplate',
            name='periode',
        ),
        
        # Rename interval menjadi interval_hari
        migrations.RenameField(
            model_name='preventivejobtemplate',
            old_name='interval',
            new_name='interval_hari',
        ),
        
        # Update field help_text
        migrations.AlterField(
            model_name='preventivejobtemplate',
            name='interval_hari',
            field=models.IntegerField(
                default=7,
                verbose_name='Interval (Hari)',
                help_text='Contoh: 1 (harian), 7 (mingguan), 30 (bulanan), 365 (tahunan)'
            ),
        ),
    ]
