# Generated migration for adding item_type and text_options support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preventive_jobs', '0005_checklisttemplate_checklistresult_checklistitem_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklistitem',
            name='item_type',
            field=models.CharField(
                choices=[('numeric', 'Numeric (dengan Angka)'), ('text', 'Text/Qualitative (Observasi)')],
                default='numeric',
                max_length=20,
                verbose_name='Tipe Item'
            ),
        ),
        migrations.AddField(
            model_name='checklistitem',
            name='text_options',
            field=models.CharField(
                blank=True,
                help_text='Pisahkan dengan semicolon (;). Contoh: Normal;Kasar;Bising;Bergerak',
                max_length=500,
                null=True,
                verbose_name='Pilihan Text'
            ),
        ),
    ]
