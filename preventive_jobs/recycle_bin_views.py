# Recycle Bin Views untuk Preventive Job Templates

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator

from .models import PreventiveJobTemplate, PreventiveJobExecution


@login_required(login_url='core:login')
def preventive_recycle_bin_view(request):
    """
    Halaman Recycle Bin - tampilkan semua template yang sudah soft-deleted
    User bisa melihat:
    - Template name
    - Tanggal dihapus
    - Dihapus oleh (user)
    - Jumlah executions yang terhapus
    - Tombol: Restore, Permanent Delete
    """
    
    # === FILTER PARAMETERS ===
    search_query = request.GET.get('q', '')
    sort_param = request.GET.get('sort', '-deleted_at')
    
    # === BUILD QUERY - hanya tampilkan yang is_deleted=True ===
    templates = PreventiveJobTemplate.objects.filter(is_deleted=True)
    
    if search_query:
        templates = templates.filter(
            Q(nama_pekerjaan__icontains=search_query) |
            Q(deskripsi__icontains=search_query)
        )
    
    templates = templates.select_related('deleted_by').order_by(sort_param)
    
    # === ENRICH DATA ===
    templates_with_executions = []
    for template in templates:
        execution_count = template.executions.filter(is_deleted=True).count()
        templates_with_executions.append({
            'template': template,
            'execution_count': execution_count,
        })
    
    # === PAGINATION ===
    paginator = Paginator(templates_with_executions, 10)
    page_number = request.GET.get('page')
    templates_page = paginator.get_page(page_number)
    
    context = {
        'templates': templates_page,
        'search_query': search_query,
        'sort_param': sort_param,
    }
    
    return render(request, 'preventive_jobs/recycle_bin.html', context)


@login_required(login_url='core:login')
@require_http_methods(["POST"])
def preventive_template_restore_view(request, template_id):
    """
    Restore template dari recycle bin
    Juga restore semua related executions
    """
    template = get_object_or_404(PreventiveJobTemplate, id=template_id, is_deleted=True)
    template_name = template.nama_pekerjaan
    
    # Restore template dan related executions
    template.restore()
    
    execution_count = template.executions.count()
    messages.success(
        request, 
        f"Template '{template_name}' dan {execution_count} execution records berhasil di-restore dari recycle bin."
    )
    
    return redirect('preventive_jobs:recycle_bin')


@login_required(login_url='core:login')
@require_http_methods(["POST"])
def preventive_template_permanent_delete_view(request, template_id):
    """
    Permanent delete (hard delete) - template dan semua executions-nya hilang selamanya
    Hanya bisa dilakukan untuk template yang sudah soft-deleted
    """
    template = get_object_or_404(PreventiveJobTemplate, id=template_id, is_deleted=True)
    template_name = template.nama_pekerjaan
    
    # Delete related executions first
    template.executions.all().delete()
    
    # Delete template
    template.delete()
    
    messages.success(
        request, 
        f"Template '{template_name}' dan semua data terkaitnya telah PERMANEN dihapus dari sistem."
    )
    
    return redirect('preventive_jobs:recycle_bin')


@login_required(login_url='core:login')
def recycle_bin_stats_api(request):
    """
    API endpoint untuk get stats recycle bin (jumlah template yang terhapus, dll)
    """
    deleted_templates_count = PreventiveJobTemplate.objects.filter(is_deleted=True).count()
    deleted_executions_count = PreventiveJobExecution.objects.filter(is_deleted=True).count()
    
    return JsonResponse({
        'deleted_templates': deleted_templates_count,
        'deleted_executions': deleted_executions_count,
    })
