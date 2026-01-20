from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Public View (tanpa login)
    path('public/', views.PublicInventoryView.as_view(), name='public-list'),
    
    # Barang Management (protected)
    path('', views.BarangListView.as_view(), name='barang-list'),
    path('create/', views.BarangCreateView.as_view(), name='barang-create'),
    path('<uuid:pk>/edit/', views.BarangEditView.as_view(), name='barang-edit'),
    path('<uuid:pk>/delete/', views.BarangDeleteView.as_view(), name='barang-delete'),
    
    # Import
    path('import/', views.BarangImportView.as_view(), name='barang-import'),
    
    # Stock Update
    path('<uuid:barang_id>/update-stock/', views.StockUpdateView.as_view(), name='update-stock'),
    
    # Export
    path('export-pdf/', views.StockExportPDFView.as_view(), name='export-pdf'),
    
    # Export Setting & Log
    path('export-setting/', views.StockExportSettingView.as_view(), name='export-setting'),
    path('export-log/', views.StockExportLogView.as_view(), name='export-log'),
    
    # API
    path('api/test-fontte/', views.api_test_fontte_connection, name='api-test-fontte'),
]
