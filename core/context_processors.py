"""
Context Processors untuk global template variables
Saat ini digunakan untuk: Navbar bell (overdue jobs)
"""

from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache
from core.models import Job, JobDate
from preventive_jobs.models import PreventiveJobExecution


def overdue_jobs_context(request):
    """
    Context processor untuk provide overdue jobs info ke navbar
    Digunakan di navbar untuk menampilkan bell icon dengan badge count
    
    Returns:
    {
        'overdue_count': <int>,
        'overdue_list': [
            {
                'type': 'daily_job' | 'project_job' | 'preventive',
                'id': <int>,
                'name': <str>,
                'days_overdue': <int>,
                'url': <str>,
                'assigned_to': <str>
            },
            ...
        ]
    }
    """
    
    if not request.user.is_authenticated:
        return {
            'overdue_count': 0,
            'overdue_list': [],
        }
    
    user = request.user
    
    # Check cache first (5 minute TTL)
    cache_key = f'overdue_jobs_{user.id}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    subordinate_ids = user.get_all_subordinates()
    all_user_ids = [user.id] + subordinate_ids
    
    overdue_items = []
    
    # 1. GET OVERDUE DAILY JOBS (Optimized with select_related)
    daily_jobs_with_overdue = Job.objects.filter(
        Q(pic_id__in=all_user_ids) | Q(assigned_to_id__in=all_user_ids),
        tipe_job='Daily'
    ).select_related('pic', 'assigned_to').prefetch_related('tanggal_pelaksanaan')
    
    for job in daily_jobs_with_overdue:
        # Extra check: ensure job.tipe_job is actually 'Daily'
        if job.tipe_job != 'Daily':
            continue
        overdue_dates = job.get_overdue_dates()
        if overdue_dates.exists():
            first_overdue = overdue_dates.first()
            overdue_items.append({
                'type': 'daily_job',
                'id': job.id,
                'name': job.nama_pekerjaan,
                'days_overdue': first_overdue.days_overdue(),
                'url': f'/daily-job/{job.id}/',
                'assigned_to': job.assigned_to.get_full_name() if job.assigned_to else job.pic.get_full_name(),
                'total_overdue': overdue_dates.count(),
            })
    
    # 2. GET OVERDUE PROJECT JOBS (Optimized with select_related)
    project_jobs_with_overdue = Job.objects.filter(
        Q(pic_id__in=all_user_ids) | Q(assigned_to_id__in=all_user_ids),
        tipe_job='Project'
    ).select_related('pic', 'assigned_to').prefetch_related('tanggal_pelaksanaan')
    
    for job in project_jobs_with_overdue:
        # Extra check: ensure job.tipe_job is actually 'Project'
        if job.tipe_job != 'Project':
            continue
        overdue_dates = job.get_overdue_dates()
        if overdue_dates.exists():
            first_overdue = overdue_dates.first()
            overdue_items.append({
                'type': 'project_job',
                'id': job.id,
                'name': job.nama_pekerjaan,
                'days_overdue': first_overdue.days_overdue(),
                'url': f'/project-job/{job.id}/',
                'assigned_to': job.assigned_to.get_full_name() if job.assigned_to else job.pic.get_full_name(),
                'total_overdue': overdue_dates.count(),
            })
    
    # 3. GET OVERDUE PREVENTIVE JOB EXECUTIONS (Optimized with select_related)
    today = timezone.now().date()
    overdue_preventive = PreventiveJobExecution.objects.filter(
        Q(template__pic_id__in=all_user_ids) | Q(assigned_to_id__in=all_user_ids),
        status='Scheduled',
        scheduled_date__lt=today
    ).select_related('template__pic', 'assigned_to', 'aset')
    
    for execution in overdue_preventive:
        overdue_items.append({
            'type': 'preventive',
            'id': execution.id,
            'name': execution.template.nama_pekerjaan,
            'days_overdue': execution.days_overdue(),
            'url': f'/preventive/execution/{execution.id}/detail/',
            'assigned_to': execution.assigned_to.get_full_name() if execution.assigned_to else execution.template.pic.get_full_name(),
            'aset': execution.aset.nama if execution.aset else 'N/A',
        })
    
    # Sort by days overdue (descending)
    overdue_items = sorted(overdue_items, key=lambda x: x['days_overdue'], reverse=True)
    
    # Limit ke 10 items untuk dropdown
    short_overdue_list = overdue_items[:10]
    
    result = {
        'overdue_count': len(overdue_items),
        'overdue_list': short_overdue_list,
        'total_overdue_count': len(overdue_items),  # Total, tidak limited
    }
    
    # Cache untuk 5 menit (300 detik)
    cache.set(cache_key, result, 300)
    
    return result