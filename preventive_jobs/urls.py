from django.urls import path
from . import views
from .recycle_bin_views import (
    preventive_recycle_bin_view,
    preventive_template_restore_view,
    preventive_template_permanent_delete_view,
    recycle_bin_stats_api,
)

app_name = 'preventive_jobs'

urlpatterns = [
    # INDEX/HUB
    path('', views.preventive_index_view, name='index'),
    
    # DASHBOARD
    path('dashboard/', views.preventive_dashboard_view, name='dashboard'),
    
    # TEMPLATE MANAGEMENT
    path('template/', views.preventive_template_list_view, name='template_list'),
    path('template/create/', views.preventive_template_create_view, name='template_create'),
    path('template/<int:template_id>/edit/', views.preventive_template_edit_view, name='template_edit'),
    path('template/<int:template_id>/detail/', views.preventive_template_detail_view, name='template_detail'),
    path('template/<int:template_id>/duplicate/', views.preventive_template_duplicate_view, name='template_duplicate'),
    path('template/<int:template_id>/delete/', views.preventive_template_delete_view, name='template_delete'),
    path('template/<int:template_id>/toggle/', views.preventive_template_toggle_view, name='template_toggle'),
    
    # RECYCLE BIN MANAGEMENT
    path('recycle-bin/', preventive_recycle_bin_view, name='recycle_bin'),
    path('recycle-bin/<int:template_id>/restore/', preventive_template_restore_view, name='template_restore'),
    path('recycle-bin/<int:template_id>/permanent-delete/', preventive_template_permanent_delete_view, name='template_permanent_delete'),
    path('recycle-bin/api/stats/', recycle_bin_stats_api, name='recycle_bin_stats_api'),
    
    # CHECKLIST MANAGEMENT (NEW)
    path('checklist-management/', views.checklist_management_view, name='checklist_management'),
    
    # MASTER CHECKLIST MANAGEMENT (OLD - KEEP FOR COMPATIBILITY)
    path('checklist/', views.checklist_list_view, name='checklist_list'),
    path('checklist/create/', views.checklist_create_view, name='checklist_create'),
    path('checklist/<int:pk>/detail/', views.checklist_detail_view, name='checklist_detail'),
    path('checklist/<int:pk>/delete/', views.checklist_delete_view, name='checklist_delete'),
    
    # CHECKLIST API ENDPOINTS
    path('checklist/api/create/', views.checklist_template_create_api, name='checklist_api_create'),
    path('checklist/<int:pk>/api/', views.checklist_template_api, name='checklist_api'),
    path('checklist/<int:pk>/api/delete/', views.checklist_template_api, name='checklist_api_delete'),
    path('checklist/api/update/', views.checklist_template_update_api, name='checklist_api_update'),
    path('checklist/<int:pk>/items-api/', views.checklist_items_api, name='checklist_items_api'),
    path('checklist/items-api/save/', views.checklist_items_save_api, name='checklist_items_save_api'),
    path('checklist/<int:pk>/download-template/', views.checklist_template_download_excel, name='checklist_download_template'),
    path('checklist/items-api/import/', views.checklist_items_import_excel, name='checklist_items_import'),
    
    # EXECUTION TRACKING
    path('execution/', views.preventive_execution_list_view, name='execution_list'),
    path('execution/<int:execution_id>/detail/', views.preventive_execution_detail_view, name='execution_detail'),
    path('execution/<int:execution_id>/assign/', views.execution_assign_view, name='execution_assign'),
    path('execution/<int:execution_id>/personil-list/', views.execution_get_personil_list, name='execution_personil_list'),
    
    # TRIAL: JOB PER DAY (HALAMAN BARU - EKSPERIMEN)
    path('job-per-day-trial/', views.job_per_day_trial_view, name='job_per_day_trial'),
    # Export endpoints - generic (backward compatible)
    path('job-per-day-trial/export/', views.export_unified_jobs_to_gas, name='export_unified_jobs_to_gas'),
    # Export endpoints - specific (recommended)
    path('job-per-day-trial/export/preventif/', views.export_unified_jobs_to_gas, {'export_type': 'preventif'}, name='export_preventif'),
    path('job-per-day-trial/export/evaluasi/', views.export_unified_jobs_to_gas, {'export_type': 'evaluasi'}, name='export_evaluasi'),
    
    # AJAX ENDPOINTS - CHECKLIST
    path('execution/<int:execution_id>/checklist-modal/', views.checklist_modal_api, name='checklist_modal_api'),
    path('execution/<int:execution_id>/checklist-items/', views.get_checklist_items_view, name='get_checklist_items'),
    path('execution/<int:execution_id>/save-checklist/', views.save_checklist_result_view, name='save_checklist_result'),
    path('execution/<int:execution_id>/delete-checklist/', views.delete_checklist_result_view, name='delete_checklist_result'),
    
    # WHATSAPP SHARE ENDPOINTS (NEW)
    path('execution/<int:execution_id>/generate-share-link/', views.generate_share_link, name='generate_share_link'),
    path('execution/<int:execution_id>/share-modal/', views.share_checklist_modal_view, name='share_checklist_modal'),
    path('checklist-fill/<str:token>/', views.checklist_fill_view, name='checklist_fill'),
    path('checklist-fill-save/', views.save_checklist_via_token, name='save_checklist_via_token'),
    
    # OLD ENDPOINTS (KEEP FOR COMPATIBILITY)
    
    # AJAX ENDPOINTS - ATTACHMENTS
    path('execution/<int:execution_id>/attachments/', views.get_execution_attachments, name='get_execution_attachments'),
    
    # AJAX ENDPOINTS - STATE MACHINE & UNDO (TESTING PHASE)
    path('execution/<int:execution_id>/undo-status/', views.execution_undo_status_change, name='execution_undo_status'),
    path('execution/<int:execution_id>/status-history/', views.execution_status_history, name='execution_status_history'),
    
    # MONITORING
    path('monitoring/mesin/', views.preventive_mesin_monitoring_view, name='mesin_monitoring'),
    
    # REPORTS
    path('report/compliance/', views.preventive_compliance_report_view, name='compliance_report'),
]
