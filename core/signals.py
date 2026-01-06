"""
Signals untuk auto-sync NotulenItem status dengan Job progress
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import JobDate, Job


@receiver(post_save, sender=JobDate)
def update_notulen_on_jobdate_save(sender, instance, created, **kwargs):
    """
    Ketika JobDate di-save, cek apakah job sudah 100% complete.
    Jika ya, update linked NotulenItem status ke 'done'.
    """
    job = instance.job
    
    # Cek progress job
    progress = job.get_progress_percent()
    
    # Jika 100% dan ada link ke notulen, update status
    if progress == 100 and job.notulen_item:
        if job.notulen_item.status != 'done':
            job.notulen_item.status = 'done'
            job.notulen_item.save()


@receiver(post_delete, sender=Job)
def revert_notulen_on_job_delete(sender, instance, **kwargs):
    """
    Ketika Job dihapus, revert NotulenItem status ke 'open'
    sehingga user bisa membuat job baru dari notulen item tsb.
    """
    if instance.notulen_item:
        instance.notulen_item.job_created = None
        instance.notulen_item.status = 'open'
        instance.notulen_item.save()
