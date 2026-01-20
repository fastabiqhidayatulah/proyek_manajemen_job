from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db import models
from weasyprint import HTML
from datetime import datetime


# ==============================================================================
# PERMISSION HELPER FUNCTIONS
# ==============================================================================
def can_edit_inventory(user):
    """
    Cek apakah user dapat edit inventory (stok, barang, dll).
    Akses diberikan ke:
    - Staff users (is_staff=True)
    - Users dalam grup 'Workshop'
    - Users dalam grup 'Warehouse'
    """
    if not user.is_authenticated:
        return False
    return user.is_staff or user.groups.filter(name__in=['Workshop', 'Warehouse']).exists()


def can_import_inventory(user):
    """
    Cek apakah user dapat import inventory.
    Hanya staff dan Warehouse group yang boleh import.
    """
    if not user.is_authenticated:
        return False
    return user.is_staff or user.groups.filter(name='Warehouse').exists()
import tempfile
import os

from .models import Barang, StockLevel
from .forms import BarangForm, StockUpdateForm, BarangImportForm
from .import_handler import BarangImporter


# ==============================================================================
# 1. BARANG LIST VIEW (Read-only untuk semua user)
# ==============================================================================
class BarangListView(LoginRequiredMixin, ListView):
    """List semua barang dengan stok level"""
    model = Barang
    template_name = 'inventory/barang_list.html'
    context_object_name = 'barang_list'
    paginate_by = 50
    login_url = 'login'
    
    def get_queryset(self):
        queryset = Barang.objects.filter(status='active').select_related('stock_level')
        
        # Search by kode atau nama
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(kode__icontains=search) | 
                models.Q(nama__icontains=search)
            )
        
        # Filter by kategori
        kategori = self.request.GET.get('kategori')
        if kategori:
            queryset = queryset.filter(kategori=kategori)
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'kode')
        order = self.request.GET.get('order', 'asc')
        
        if order == 'desc':
            sort_by = f'-{sort_by}'
        
        return queryset.order_by(sort_by)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_kategori'] = self.request.GET.get('kategori', '')
        context['current_sort'] = self.request.GET.get('sort', 'kode')
        context['current_order'] = self.request.GET.get('order', 'asc')
        context['kategori_choices'] = Barang.CATEGORY_CHOICES
        context['can_edit_stock'] = can_edit_inventory(self.request.user)
        return context


# ==============================================================================
# 2. BARANG CREATE VIEW (Admin only)
# ==============================================================================
class BarangCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create barang baru"""
    model = Barang
    form_class = BarangForm
    template_name = 'inventory/barang_form.html'
    success_url = reverse_lazy('inventory:barang-list')
    login_url = 'login'
    
    def test_func(self):
        return can_edit_inventory(self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create stock level automatically
        StockLevel.objects.create(barang=self.object, qty=0)
        
        messages.success(self.request, f"Barang '{self.object.nama}' berhasil dibuat")
        return response


# ==============================================================================
# 3. BARANG EDIT VIEW (Admin only)
# ==============================================================================
class BarangEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit barang"""
    model = Barang
    form_class = BarangForm
    template_name = 'inventory/barang_form.html'
    success_url = reverse_lazy('inventory:barang-list')
    login_url = 'login'
    
    def test_func(self):
        return can_edit_inventory(self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Barang '{self.object.nama}' berhasil diupdate")
        return response


# ==============================================================================
# 3B. BARANG DELETE VIEW (Admin only)
# ==============================================================================
class BarangDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete barang"""
    model = Barang
    template_name = 'inventory/barang_confirm_delete.html'
    success_url = reverse_lazy('inventory:barang-list')
    login_url = 'login'
    
    def test_func(self):
        return can_edit_inventory(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        barang_nama = self.object.nama
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Barang '{barang_nama}' berhasil dihapus")
        return response


# ==============================================================================
# 4. STOCK UPDATE VIEW (Via AJAX - Warehouse staff only)
# ==============================================================================
class StockUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Update stok via AJAX modal"""
    login_url = 'login'
    
    def test_func(self):
        return can_edit_inventory(self.request.user)
    
    def post(self, request, barang_id):
        try:
            barang = get_object_or_404(Barang, pk=barang_id)
            stock = barang.stock_level
            
            form = StockUpdateForm(request.POST, instance=stock)
            
            if form.is_valid():
                # Get old qty untuk audit
                old_qty = stock.qty
                new_qty = form.cleaned_data['qty']
                
                # Update stock
                stock.updated_by = request.user
                stock.save()
                
                # Log untuk referensi (could be extended ke transaction table)
                keterangan = form.cleaned_data.get('keterangan', '')
                
                return JsonResponse({
                    'success': True,
                    'message': f"Stok '{barang.nama}' berhasil diupdate dari {old_qty} menjadi {new_qty}",
                    'barang_id': str(barang.id),
                    'qty': new_qty,
                    'updated_at': stock.updated_at.strftime('%d-%m-%Y %H:%M:%S')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Form tidak valid: ' + str(form.errors)
                }, status=400)
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# ==============================================================================
# 5. PUBLIC INVENTORY VIEW (Accessible without login - Mobile friendly)
# ==============================================================================
class PublicInventoryView(ListView):
    """List stok barang untuk public (tanpa perlu login)"""
    model = Barang
    template_name = 'inventory/public_inventory.html'
    context_object_name = 'barang_list'
    paginate_by = 100
    
    def get_queryset(self):
        queryset = Barang.objects.filter(status='active').select_related('stock_level')
        
        # Search by kode atau nama
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(kode__icontains=search) | 
                models.Q(nama__icontains=search)
            )
        
        # Filter by kategori
        kategori = self.request.GET.get('kategori')
        if kategori:
            queryset = queryset.filter(kategori=kategori)
        
        return queryset.order_by('kode')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_search'] = self.request.GET.get('search', '')
        context['current_kategori'] = self.request.GET.get('kategori', '')
        return context


# ==============================================================================
# 6. STOCK EXPORT PDF VIEW
# ==============================================================================
class StockExportPDFView(LoginRequiredMixin, View):
    """Export current stock level ke PDF"""
    login_url = 'login'
    
    def get(self, request):
        try:
            # Get all active barang dengan stock
            barang_list = Barang.objects.filter(
                status='active'
            ).select_related('stock_level').order_by('kode')
            
            # Build context
            context = {
                'barang_list': barang_list,
                'tanggal_cetak': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
                'user_cetak': request.user.get_full_name() or request.user.username,
            }
            
            # Render template to HTML
            html_string = render_to_string('inventory/stock_export_pdf.html', context, request=request)
            
            # Convert ke PDF
            html = HTML(string=html_string)
            pdf = html.write_pdf()
            
            # Generate filename
            filename = f"Stock_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Return PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('inventory:barang-list')

# ==============================================================================
# 7. BARANG IMPORT VIEW (Staff only)
# ==============================================================================
class BarangImportView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Import barang dari Excel file"""
    model = Barang
    template_name = 'inventory/barang_import.html'
    login_url = 'login'
    
    def test_func(self):
        return can_import_inventory(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BarangImportForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = BarangImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = request.FILES['file']
            
            # Save file temporarily
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            try:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file.close()
                
                # Import dari file
                importer = BarangImporter(temp_file.name)
                importer.import_data()
                result = importer.get_result()
                
                # Pass result ke context
                context = {
                    'form': form,
                    'result': result,
                    'has_result': True
                }
                
                if result['success'] > 0:
                    messages.success(
                        request, 
                        f"✓ Berhasil import {result['success']} barang"
                    )
                
                if result['failed'] > 0:
                    messages.warning(
                        request, 
                        f"⚠ {result['failed']} baris gagal di-import"
                    )
                
                if result['errors']:
                    for error in result['errors']:
                        messages.error(request, f"❌ {error}")
                
                return render(request, self.template_name, context)
            
            finally:
                # Cleanup temp file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
        
        context = {
            'form': form,
            'has_result': False
        }
        return render(request, self.template_name, context)


# ==============================================================================
# 8. STOCK EXPORT SETTING VIEW
# ==============================================================================
class StockExportSettingView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Halaman setting untuk export PDF ke WA otomatis"""
    model = StockExportSetting
    template_name = 'inventory/stock_export_setting.html'
    login_url = 'login'
    
    def test_func(self):
        """Hanya admin yang bisa akses"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('inventory:barang-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create setting
        setting, created = StockExportSetting.objects.get_or_create(pk=1)
        
        context['setting'] = setting
        context['logs'] = StockExportLog.objects.filter(setting=setting).order_by('-created_at')[:20]
        context['frequency_choices'] = StockExportSetting.FREQUENCY_CHOICES
        context['day_choices'] = [
            (0, 'Senin'),
            (1, 'Selasa'),
            (2, 'Rabu'),
            (3, 'Kamis'),
            (4, 'Jumat'),
            (5, 'Sabtu'),
            (6, 'Minggu'),
        ]
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Update setting"""
        try:
            setting = StockExportSetting.objects.get(pk=1)
        except StockExportSetting.DoesNotExist:
            setting = StockExportSetting.objects.create(pk=1)
        
        # Update fields
        setting.is_active = request.POST.get('is_active') == 'on'
        setting.frequency = request.POST.get('frequency', 'daily')
        setting.send_time = request.POST.get('send_time', '08:00:00')
        setting.day_of_week = int(request.POST.get('day_of_week', 0))
        setting.day_of_month = int(request.POST.get('day_of_month', 1))
        
        # Parse WA groups dari JSON form
        wa_groups_json = request.POST.get('wa_groups', '[]')
        try:
            import json
            setting.wa_groups = json.loads(wa_groups_json)
        except:
            setting.wa_groups = []
        
        setting.updated_by = request.user
        setting.save()
        
        messages.success(request, 'Setting export PDF berhasil disimpan!')
        return redirect('inventory:export-setting')


class StockExportLogView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Lihat history export PDF ke WA"""
    model = StockExportLog
    template_name = 'inventory/stock_export_log.html'
    context_object_name = 'logs'
    paginate_by = 50
    login_url = 'login'
    
    def test_func(self):
        """Hanya admin yang bisa akses"""
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('inventory:barang-list')
    
    def get_queryset(self):
        try:
            setting = StockExportSetting.objects.get(pk=1)
            return setting.logs.all().order_by('-created_at')
        except:
            return StockExportLog.objects.none()