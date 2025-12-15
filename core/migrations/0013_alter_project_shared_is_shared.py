# Generated migration for is_shared field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_customuser_nomor_telepon'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_shared',
            field=models.BooleanField(default=False, help_text='Jika ON, semua user bisa lihat & isi job di project ini'),
        ),
    ]
