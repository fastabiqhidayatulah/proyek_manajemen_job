# Generated migration for adding kategori field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preventive_jobs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventivejobtemplate',
            name='kategori',
            field=models.CharField(
                choices=[('Mekanik', 'Mekanik'), ('Elektrik', 'Elektrik'), ('Utility', 'Utility')],
                default='Mekanik',
                help_text='Pilih kategori: Mekanik, Elektrik, atau Utility',
                max_length=20,
                verbose_name='Kategori Pekerjaan'
            ),
        ),
    ]
