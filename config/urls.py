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
]

# Baris ini tetap di bawah (tidak berubah)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)