from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_remove_asetdepartemen_core_asetdepartemen_tree_i730a'),
    ]

    operations = [
        migrations.AddField(
            model_name='departemen',
            name='google_sheet_id',
            field=models.CharField(blank=True, help_text='ID spreadsheet untuk meeting reminder auto-sync (copy dari URL: docs.google.com/spreadsheets/d/{ID}/edit)', max_length=255, null=True, verbose_name='Google Spreadsheet ID (Meeting Reminder)'),
        ),
    ]
