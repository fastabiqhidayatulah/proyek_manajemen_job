"""
Middleware untuk Maintenance Mode
"""
from django.shortcuts import render
from django.conf import settings
from .models import MaintenanceMode


class MaintenanceModeMiddleware:
    """
    Middleware untuk handle maintenance mode.
    Jika maintenance mode aktif, semua user (kecuali admin) akan diredirect ke halaman maintenance.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Admin URLs yang bisa diakses saat maintenance
        self.admin_paths = ['/admin/']
    
    def __call__(self, request):
        # Cek apakah maintenance mode aktif
        if MaintenanceMode.is_maintenance_active():
            # Admin bisa masuk, user biasa tidak
            if not request.user.is_staff:
                # Check apakah path admin (jangan redirect admin ke maintenance)
                if not any(request.path.startswith(path) for path in self.admin_paths):
                    return self.get_maintenance_response(request)
        
        response = self.get_response(request)
        return response
    
    def get_maintenance_response(self, request):
        """Render halaman maintenance"""
        try:
            maintenance = MaintenanceMode.objects.first()
            context = {
                'message': maintenance.message if maintenance else 'Aplikasi sedang dalam maintenance',
                'estimated_time': maintenance.estimated_time if maintenance else 'Estimasi selesai dalam 15 menit'
            }
        except:
            context = {
                'message': 'Aplikasi sedang dalam maintenance',
                'estimated_time': 'Estimasi selesai dalam 15 menit'
            }
        
        return render(request, 'maintenance.html', context, status=503)
