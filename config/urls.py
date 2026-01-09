"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include # Pastikan 'include' ada di sini
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core URLs (V1)
    path('', include('core.urls', namespace='core')),
    
    # Preventive Job URLs (V2)
    path('preventive/', include('preventive_jobs.urls', namespace='preventive_jobs')),
    
    # Meetings & Notulen URLs (V3)
    path('meetings/', include('meetings.urls', namespace='meetings')),
    
    # Inventory URLs (Spare Parts)
    path('inventory/', include('inventory.urls', namespace='inventory')),
    
    # Tool Keeper URLs (Tool Lending System)
    path('toolkeeper/', include('toolkeeper.urls', namespace='toolkeeper')),
]

# Baris ini tetap di bawah (tidak berubah)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)