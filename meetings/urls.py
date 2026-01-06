from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    # Meeting Management
    path('', views.MeetingListView.as_view(), name='meeting-list'),
    path('create/', views.MeetingCreateView.as_view(), name='meeting-create'),
    path('<uuid:pk>/', views.MeetingDetailView.as_view(), name='meeting-detail'),
    path('<uuid:pk>/edit/', views.MeetingEditView.as_view(), name='meeting-edit'),
    path('<uuid:pk>/finalize/', views.MeetingFinalizeView.as_view(), name='meeting-finalize'),
    path('<uuid:pk>/close/', views.MeetingCloseView.as_view(), name='meeting-close'),
    path('<uuid:pk>/delete/', views.MeetingDeleteView.as_view(), name='meeting-delete'),
    
    # QR Code Management
    path('<uuid:pk>/qr-code/generate/', views.QRCodeGenerateView.as_view(), name='qr-generate'),
    path('<uuid:pk>/qr-code/toggle/', views.QRCodeToggleView.as_view(), name='qr-toggle'),
    path('qr-code/<str:token>/display/', views.QRCodeDisplayView.as_view(), name='qr-display'),
    path('qr-code/<str:token>/toggle/', views.QRCodeToggleView.as_view(), name='qr-toggle-token'),
    
    # Presensi External (Public - No Login Required)
    path('presensi/<str:token>/', views.PresensiExternalView.as_view(), name='presensi-external'),
    
    # Peserta Management
    path('<uuid:pk>/peserta/add/', views.MeetingAddPesertaView.as_view(), name='meeting-add-peserta'),
    path('peserta/<uuid:peserta_pk>/delete/', views.MeetingDeletePesertaView.as_view(), name='meeting-delete-peserta'),
    
    # Notulen Item Management
    path('<uuid:meeting_pk>/notulen/add/', views.NotulenItemAddView.as_view(), name='notulen-add'),
    path('<uuid:meeting_pk>/notulen/save/', views.NotulenItemSaveView.as_view(), name='notulen-save'),
    path('notulen/<uuid:pk>/edit/', views.NotulenItemEditView.as_view(), name='notulen-edit'),
    path('notulen/<uuid:pk>/delete/', views.NotulenItemDeleteView.as_view(), name='notulen-delete'),
    path('notulen/<uuid:pk>/delete-ajax/', views.NotulenItemDeleteAjaxView.as_view(), name='notulen-delete-ajax'),
    path('notulen/<uuid:pk>/', views.NotulenItemGetView.as_view(), name='notulen-get'),
    
    # Job Creation from Notulen
    path('notulen/<uuid:item_pk>/create-job/', 
         views.create_job_from_notulen_view, 
         name='create-job-from-notulen'),
    
    # Export Notulen ke PDF
    path('<uuid:pk>/export-pdf/', 
         views.ExportNotulenPDFView.as_view(), 
         name='export-pdf'),
    path('<uuid:pk>/export-pdf-v2/', 
         views.ExportNotulenPDFV2View.as_view(), 
         name='export-pdf-v2'),
    
    # AJAX Endpoints
    path('peserta/<uuid:peserta_pk>/status/', views.PesertaStatusUpdateView.as_view(), name='peserta-update-status'),
]
