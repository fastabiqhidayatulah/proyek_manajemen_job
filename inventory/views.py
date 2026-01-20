from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.db import models
from django.conf import settings
from weasyprint import HTML
from datetime import datetime
from .models import Barang, StockLevel, StockExportSetting, StockExportLog
import requests
import json


# ==============================================================================
# FONTTE WA HELPER FUNCTIONS
# ==============================================================================
def send_pdf_to_fontte(group_id, pdf_file_path, token=None, api_url=None):
    """
    Send PDF file ke grup WA via Fontte API
    Format API Fontte: POST https://api.fontte.com/v1/send
    Returns: (success: bool, message: str, log_id: str or None)
    """
    try:
        # Use provided token or default
        if not token:
            token = settings.FONTTE_API_TOKEN
        if not api_url:
            api_url = settings.FONTTE_API_BASE_URL
        
        if not token:
            return False, "Token API tidak dikonfigurasi", None
        
        # Open & read file
        with open(pdf_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'target': group_id,  # Format: nomor_wa atau group_id
                'caption': 'Stock Export Report'  # Caption untuk file
            }
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            # Send ke Fontte API endpoint /send
            url = f"{api_url}/send"
            response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
        
        response_data = response.json() if response.text else {}
        
        if response.status_code in [200, 201]:
            return True, "✓ PDF berhasil dikirim ke WA", None
        else:
            error_msg = response_data.get('message', response.text)
            return False, f"✗ Error: HTTP {response.status_code} - {error_msg}", None
    
    except FileNotFoundError:
        return False, "✗ File PDF tidak ditemukan", None
    except requests.exceptions.Timeout:
        return False, "✗ Request timeout - server Fontte tidak merespons", None
    except requests.exceptions.ConnectionError:
        return False, "✗ Tidak bisa terhubung ke server Fontte", None
    except Exception as e:
        return False, f"✗ Error: {str(e)}", None


def test_fontte_connection(token=None, api_url=None):
    """
    Test koneksi ke Fontte API
    Returns: (success: bool, message: str)
    """
    try:
        # Use provided token or default
        if not token:
            token = settings.FONTTE_API_TOKEN
        if not api_url:
            api_url = settings.FONTTE_API_BASE_URL
        
        if not token:
            return False, "Token API tidak dikonfigurasi"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{api_url}/chats"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "✓ Terhubung ke Fontte"
        elif response.status_code == 401:
            return False, "✗ Token tidak valid atau kadaluarsa"
        else:
            return False, f"✗ Error: HTTP {response.status_code}"
    
    except requests.exceptions.Timeout:
        return False, "✗ Request timeout - server Fontte tidak merespons"
    except requests.exceptions.ConnectionError:
        return False, "✗ Tidak bisa terhubung ke server Fontte"
    except Exception as e:
        return False, f"✗ Error: {str(e)}"


def get_fontte_groups(token=None, api_url=None):
    """
    Fetch daftar grup WA dari Fontte API
    Returns: list of {'group_id': 'xxx', 'group_name': 'Nama Grup'}
    """
    try:
        # Use provided token or default
        if not token:
            token = settings.FONTTE_API_TOKEN
        if not api_url:
            api_url = settings.FONTTE_API_BASE_URL
        
        if not token or not settings.FONTTE_API_ENABLED:
            return []
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{api_url}/chats"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            groups = []
            
            # Extract groups dari response
            if 'data' in data:
                for item in data['data']:
                    # Filter hanya grup (bukan personal chat)
                    if item.get('is_group') or 'group' in item.get('name', '').lower():
                        groups.append({
                            'group_id': item.get('id') or item.get('chat_id'),
                            'group_name': item.get('name') or item.get('title')
                        })
            
            return groups
        else:
            return []
    except Exception as e:
        print(f"Error fetching Fontte groups: {str(e)}")
        return []


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
        
        # Determine which token to use
        active_token = setting.fontte_token or settings.FONTTE_API_TOKEN
        active_url = setting.fontte_api_url or settings.FONTTE_API_BASE_URL
        
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
        
        # Test connection dan fetch available WA groups
        is_connected, connection_msg = test_fontte_connection(active_token, active_url)
        setting.fontte_connected = is_connected
        setting.fontte_last_check = datetime.now()
        setting.save(update_fields=['fontte_connected', 'fontte_last_check'])
        
        context['fontte_connected'] = is_connected
        context['connection_message'] = connection_msg
        context['available_groups'] = get_fontte_groups(active_token, active_url) if is_connected else []
        context['fontte_enabled'] = settings.FONTTE_API_ENABLED
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Update setting"""
        try:
            setting = StockExportSetting.objects.get(pk=1)
        except StockExportSetting.DoesNotExist:
            setting = StockExportSetting.objects.create(pk=1)
        
        # Handle Fontte token update
        new_token = request.POST.get('fontte_token', '').strip()
        if new_token and new_token != setting.fontte_token:
            setting.fontte_token = new_token
            # Test new token
            is_connected, msg = test_fontte_connection(new_token, setting.fontte_api_url)
            if is_connected:
                messages.success(request, f"Token Fontte valid! {msg}")
            else:
                messages.warning(request, f"Token Fontte tidak valid: {msg}")
        
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


# ==============================================================================
# API: Test Fontte Connection
# ==============================================================================
def api_test_fontte_connection(request):
    """AJAX endpoint untuk test Fontte connection"""
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
        
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        
        token = request.POST.get('token', '').strip()
        
        if not token:
            # Use default
            try:
                setting = StockExportSetting.objects.get(pk=1)
                token = setting.fontte_token or settings.FONTTE_API_TOKEN
            except:
                token = settings.FONTTE_API_TOKEN
        
        is_connected, message = test_fontte_connection(token)
        
        return JsonResponse({
            'success': is_connected,
            'message': message
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


# ==============================================================================
# API: Test Send PDF to Fontte
# ==============================================================================
def api_test_send_pdf(request):
    """AJAX endpoint untuk test send PDF ke Fontte"""
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
        
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)
        
        # Get group_id dari POST
        group_id = request.POST.get('group_id', '').strip()
        if not group_id:
            return JsonResponse({'success': False, 'message': 'Group ID tidak boleh kosong'})
        
        # Generate test PDF
        try:
            setting = StockExportSetting.objects.get(pk=1)
            token = setting.fontte_token or settings.FONTTE_API_TOKEN
            api_url = setting.fontte_api_url or settings.FONTTE_API_BASE_URL
        except:
            token = settings.FONTTE_API_TOKEN
            api_url = settings.FONTTE_API_BASE_URL
        
        # Get all active barang untuk PDF
        barang_list = Barang.objects.filter(status='active').select_related('stock_level').order_by('kode')
        
        # Generate PDF
        context = {
            'barang_list': barang_list,
            'tanggal_cetak': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'user_cetak': request.user.get_full_name() or request.user.username,
        }
        
        html_string = render_to_string('inventory/stock_export_pdf.html', context, request=request)
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        
        # Save to temp file
        import tempfile
        import os
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"Stock_Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf)
        
        # Send ke Fontte
        success, message, _ = send_pdf_to_fontte(group_id, pdf_path, token, api_url)
        
        # Cleanup
        try:
            os.unlink(pdf_path)
        except:
            pass
        
        return JsonResponse({
            'success': success,
            'message': message
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


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