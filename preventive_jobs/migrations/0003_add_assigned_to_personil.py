# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('preventive_jobs', '0002_add_kategori'),
    ]

    operations = [
        migrations.AddField(
            model_name='preventivejobexecution',
            name='assigned_to_personil',
            field=models.ManyToManyField(blank=True, related_name='preventive_job_executions_assigned', to='core.personil', verbose_name='Ditugaskan ke (Personil)'),
        ),
    ]
