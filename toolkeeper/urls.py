from django.urls import path
from . import views

app_name = 'toolkeeper'

urlpatterns = [
    # Tool Master Data
    path('', views.PeminjamanListView.as_view(), name='peminjaman-list'),
    path('tools/', views.ToolListView.as_view(), name='tool-list'),
    path('tools/create/', views.ToolCreateView.as_view(), name='tool-create'),
    path('tools/import/', views.tool_import_view, name='tool-import'),
    path('tools/<uuid:pk>/edit/', views.ToolEditView.as_view(), name='tool-edit'),
    path('tools/<uuid:pk>/delete/', views.ToolDeleteView.as_view(), name='tool-delete'),
    
    # Peminjaman
    path('peminjaman/create/', views.PeminjamanCreateView.as_view(), name='peminjaman-create'),
    path('peminjaman/<uuid:pk>/', views.PeminjamanDetailView.as_view(), name='peminjaman-detail'),
    path('peminjaman/<uuid:pk>/edit/', views.PeminjamanEditView.as_view(), name='peminjaman-edit'),
    
    # Pengembalian
    path('peminjaman/<uuid:pk>/pengembalian/create/', views.PengembalianCreateView.as_view(), name='pengembalian-create'),
    path('pengembalian/<uuid:pk>/', views.PengembalianDetailView.as_view(), name='pengembalian-detail'),
    path('api/return-tool/', views.api_return_tool, name='api-return-tool'),
    path('api/add-karyawan/', views.api_add_karyawan, name='api-add-karyawan'),
    
    # Reports
    path('report/', views.ReportView.as_view(), name='report'),
]
