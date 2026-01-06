from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.paginator import Paginator
from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import json
import qrcode
from io import BytesIO
import base64
import requests
from datetime import datetime

from .models import Meeting, MeetingPeserta, NotulenItem
from .forms import MeetingForm, NotulenItemForm, MeetingPesertaStatusForm, PresensiExternalForm
from core.models import Job, JobDate, CustomUser
from core.forms import JobFromNotulenForm


# ==============================================================================
# HELPER FUNCTION - Construct Public URL (untuk QR Code, ngrok, dll)
# ==============================================================================
def get_public_url(request, path):
    """
    Construct public URL untuk QR code dan external access.
    Gunakan DJANGO_PUBLIC_URL dari settings jika tersedia, else fallback ke request.build_absolute_uri()
    
    Args:
        request: Django request object
        path: URL path (reverse lazy result)
    
    Returns:
        Full public URL (https://ngrok-url atau http://localhost)
    """
    public_url_base = getattr(settings, 'DJANGO_PUBLIC_URL', None)
    
    if public_url_base:
        # Gunakan ngrok atau public URL dari settings
        # Ensure path dimulai dengan /
        if isinstance(path, str):
            path_str = path
        else:
            # Jika dari reverse_lazy, convert ke string
            path_str = str(path)
        
        if not path_str.startswith('/'):
            path_str = '/' + path_str
        
        # Remove trailing slash dari base URL
        public_url_base = public_url_base.rstrip('/')
        
        return f"{public_url_base}{path_str}"
    else:
        # Fallback ke request.build_absolute_uri
        return request.build_absolute_uri(path)


# ==============================================================================
# 1. MEETING LIST VIEW
# ==============================================================================
class MeetingListView(LoginRequiredMixin, ListView):
    """List semua meetings dengan filter dan pagination"""
    model = Meeting
    template_name = 'meetings/meeting_list.html'
    context_object_name = 'meetings'
    paginate_by = 20
    login_url = 'login'
    
    def get_queryset(self):
        queryset = Meeting.objects.all().order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by date range
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(tanggal_meeting__gte=date_from)
        if date_to:
            queryset = queryset.filter(tanggal_meeting__lte=date_to)
        
        # Search by agenda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(agenda__icontains=search)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Meeting.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_date_from'] = self.request.GET.get('date_from', '')
        context['current_date_to'] = self.request.GET.get('date_to', '')
        return context


# ==============================================================================
# 2. MEETING CREATE VIEW
# ==============================================================================
class MeetingCreateView(LoginRequiredMixin, CreateView):
    """Create meeting baru"""
    model = Meeting
    form_class = MeetingForm
    template_name = 'meetings/meeting_form.html'
    login_url = 'login'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        
        # Clear old peserta
        MeetingPeserta.objects.filter(meeting=self.object).delete()
        
        # Save peserta from form
        peserta_list = form.cleaned_data.get('peserta', [])
        for peserta in peserta_list:
            MeetingPeserta.objects.get_or_create(
                meeting=self.object,
                peserta=peserta,
                defaults={'nama': peserta.get_full_name() or peserta.username}
            )
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('meetings:meeting-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['peserta_list'] = CustomUser.objects.filter(is_active=True).order_by('first_name', 'last_name')
        return context


# ==============================================================================
# 3. MEETING DETAIL VIEW
# ==============================================================================
class MeetingDetailView(LoginRequiredMixin, DetailView):
    """Detail meeting dengan peserta dan notulen items"""
    model = Meeting
    template_name = 'meetings/meeting_detail.html'
    context_object_name = 'meeting'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = self.object
        
        # Peserta list
        context['peserta_list'] = MeetingPeserta.objects.filter(meeting=meeting)
        context['peserta_internal'] = context['peserta_list'].filter(tipe_peserta='internal')
        context['peserta_external'] = context['peserta_list'].filter(tipe_peserta='external')
        
        # Available users untuk tambah peserta (exclude yg sudah ada)
        existing_peserta_ids = context['peserta_internal'].filter(
            peserta__isnull=False
        ).values_list('peserta_id', flat=True)
        context['available_users'] = CustomUser.objects.filter(
            is_active=True
        ).exclude(
            id__in=existing_peserta_ids
        ).order_by('first_name', 'last_name')
        
        # All users untuk notulen items PIC (semua user aktif)
        context['all_users'] = CustomUser.objects.filter(
            is_active=True
        ).order_by('first_name', 'last_name')
        
        # Presensi summary
        context['presensi_summary'] = meeting.get_presensi_summary()
        
        # Notulen items
        context['notulen_items'] = NotulenItem.objects.filter(meeting=meeting).order_by('no')
        
        # QR Code info
        context['qr_code_active'] = meeting.qr_code_active
        context['qr_code_token'] = meeting.qr_code_token
        
        # Generate QR Code image jika token sudah ada
        if meeting.qr_code_token:
            # Use helper function untuk construct public URL (support ngrok, etc)
            presensi_path = reverse('meetings:presensi-external', kwargs={'token': meeting.qr_code_token})
            qr_data = get_public_url(self.request, presensi_path)
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            context['qr_image'] = f'data:image/png;base64,{img_str}'
        
        # Check permission untuk edit
        context['can_edit'] = meeting.status == 'draft' and self.request.user == meeting.created_by
        context['can_finalize'] = meeting.status == 'draft' and self.request.user == meeting.created_by
        context['can_close'] = meeting.status == 'final' and self.request.user == meeting.created_by
        context['can_delete'] = meeting.status == 'draft' and self.request.user == meeting.created_by
        
        return context


# ==============================================================================
# 4. MEETING EDIT VIEW
# ==============================================================================
class MeetingEditView(LoginRequiredMixin, UpdateView):
    """Edit meeting (hanya jika draft)"""
    model = Meeting
    form_class = MeetingForm
    template_name = 'meetings/meeting_form.html'
    login_url = 'login'
    
    def get_object(self):
        meeting = super().get_object()
        # Check permission
        if meeting.status != 'draft' or self.request.user != meeting.created_by:
            raise HttpResponseForbidden('Anda tidak boleh edit meeting ini')
        return meeting
    
    def get_form_kwargs(self):
        """Pre-populate peserta field dengan peserta yang sudah dipilih"""
        kwargs = super().get_form_kwargs()
        if self.object:
            # Get peserta yang sudah ada
            selected_peserta = MeetingPeserta.objects.filter(
                meeting=self.object
            ).values_list('peserta_id', flat=True)
            
            # Set initial data
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['peserta'] = list(selected_peserta)
        return kwargs
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        
        # Clear old peserta
        MeetingPeserta.objects.filter(meeting=self.object).delete()
        
        # Save peserta from form
        peserta_list = form.cleaned_data.get('peserta', [])
        for peserta in peserta_list:
            MeetingPeserta.objects.get_or_create(
                meeting=self.object,
                peserta=peserta,
                defaults={'nama': peserta.get_full_name() or peserta.username}
            )
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('meetings:meeting-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['peserta_list'] = CustomUser.objects.filter(is_active=True).order_by('first_name', 'last_name')
        return context


# ==============================================================================
# 5. MEETING FINALIZE VIEW
# ==============================================================================
class MeetingFinalizeView(LoginRequiredMixin, View):
    """Finalize meeting (draft -> final)"""
    login_url = 'login'
    
    def post(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        
        # Check permission
        if meeting.status != 'draft' or request.user != meeting.created_by:
            return HttpResponseForbidden('Anda tidak boleh finalize meeting ini')
        
        meeting.status = 'final'
        meeting.updated_by = request.user
        meeting.save()
        
        # Redirect to detail
        return redirect('meetings:meeting-detail', pk=meeting.pk)


# ==============================================================================
# 6. MEETING CLOSE VIEW
# ==============================================================================
class MeetingCloseView(LoginRequiredMixin, View):
    """Close meeting (final -> closed)"""
    login_url = 'login'
    
    def post(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        
        # Check permission
        if meeting.status != 'final' or request.user != meeting.created_by:
            return HttpResponseForbidden('Anda tidak boleh close meeting ini')
        
        # Check apakah semua notulen items done
        pending_items = NotulenItem.objects.filter(meeting=meeting).exclude(status='done')
        if pending_items.exists():
            # Return error jika masih ada pending items
            return redirect('meetings:meeting-detail', pk=meeting.pk)
        
        meeting.status = 'closed'
        meeting.updated_by = request.user
        meeting.save()
        
        return redirect('meetings:meeting-detail', pk=meeting.pk)


# ==============================================================================
# 7. MEETING DELETE VIEW
# ==============================================================================
class MeetingDeleteView(LoginRequiredMixin, DeleteView):
    """Delete meeting (hanya draft)"""
    model = Meeting
    template_name = 'meetings/meeting_confirm_delete.html'
    success_url = reverse_lazy('meetings:meeting-list')
    login_url = 'login'
    
    def get_object(self):
        meeting = super().get_object()
        if meeting.status != 'draft' or self.request.user != meeting.created_by:
            raise HttpResponseForbidden('Anda tidak boleh delete meeting ini')
        return meeting

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_delete'] = self.object.status == 'draft' and self.request.user == self.object.created_by
        return context


# ==============================================================================
# 8. QR CODE GENERATE VIEW
# ==============================================================================
class QRCodeGenerateView(LoginRequiredMixin, View):
    """Generate QR code untuk meeting"""
    login_url = 'login'
    
    def post(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        
        # Check permission
        if request.user != meeting.created_by:
            return JsonResponse({'error': 'Anda tidak boleh generate QR code'}, status=403)
        
        # Generate QR code
        meeting.generate_qr_code()
        
        # Use helper function untuk construct public URLs
        presensi_path = reverse('meetings:presensi-external', kwargs={'token': meeting.qr_code_token})
        presensi_url = get_public_url(request, presensi_path)
        
        return JsonResponse({
            'success': True,
            'qr_code_token': meeting.qr_code_token,
            'qr_code_url': reverse_lazy('meetings:qr-display', kwargs={'token': meeting.qr_code_token}),
            'presensi_url': presensi_url
        })


# ==============================================================================
# 9. QR CODE DISPLAY VIEW (Full Screen)
# ==============================================================================
class QRCodeDisplayView(LoginRequiredMixin, TemplateView):
    """Display full-screen QR code"""
    template_name = 'meetings/qr_code_display.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get('token')
        
        # Get meeting by QR token
        meeting = get_object_or_404(Meeting, qr_code_token=token)
        
        # Check permission
        if self.request.user != meeting.created_by:
            raise HttpResponseForbidden('Anda tidak boleh view QR code ini')
        
        # Generate QR code image - use helper function untuk ngrok support
        presensi_path = reverse('meetings:presensi-external', kwargs={'token': token})
        qr_data = get_public_url(self.request, presensi_path)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        context['meeting'] = meeting
        context['qr_code_img'] = f'data:image/png;base64,{img_str}'
        context['presensi_count'] = MeetingPeserta.objects.filter(
            meeting=meeting,
            tipe_peserta='external',
            waktu_check_in__isnull=False
        ).count()
        
        return context


# ==============================================================================
# 10. PRESENSI EXTERNAL VIEW (Public Form)
# ==============================================================================
class PresensiExternalView(TemplateView):
    """Public form untuk presensi external via QR code"""
    template_name = 'meetings/presensi_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get('token')
        
        # Get meeting by QR token
        meeting = get_object_or_404(Meeting, qr_code_token=token)
        
        # Check apakah QR code masih aktif
        if not meeting.qr_code_active:
            context['error'] = 'QR Code tidak aktif. Hubungi penyelenggara meeting.'
            return context
        
        # Check apakah meeting masih berlangsung (time validation)
        now_time = now()
        if not (meeting.tanggal_meeting <= now_time.date() <= meeting.tanggal_meeting):
            context['warning'] = 'Meeting tidak berlangsung hari ini'
        
        context['meeting'] = meeting
        context['form'] = PresensiExternalForm()
        
        return context
    
    def post(self, request, token):
        meeting = get_object_or_404(Meeting, qr_code_token=token)
        
        # Check QR code aktif
        if not meeting.qr_code_active:
            return render(request, self.template_name, {
                'meeting': meeting,
                'error': 'QR Code tidak aktif'
            })
        
        form = PresensiExternalForm(request.POST)
        form.meeting = meeting  # Pass meeting untuk validation
        
        if form.is_valid():
            # Create MeetingPeserta
            peserta = form.save(commit=False)
            peserta.meeting = meeting
            peserta.tipe_peserta = 'external'
            peserta.status_kehadiran = 'hadir'
            peserta.waktu_check_in = now()
            peserta.save()
            
            context = {
                'meeting': meeting,
                'success': True,
                'peserta_name': peserta.nama,
                'check_in_time': peserta.waktu_check_in.strftime('%H:%M:%S')
            }
            return render(request, self.template_name, context)
        else:
            context = {
                'meeting': meeting,
                'form': form,
                'error': form.errors
            }
            return render(request, self.template_name, context)


# ==============================================================================
# 11. NOTULEN ITEM ADD VIEW
# ==============================================================================
class NotulenItemAddView(LoginRequiredMixin, CreateView):
    """Add notulen item (hanya jika meeting draft)"""
    model = NotulenItem
    form_class = NotulenItemForm
    template_name = 'meetings/notulen_form.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting, pk=self.kwargs['meeting_pk'])
        
        # Check permission
        if meeting.status != 'draft' or self.request.user != meeting.created_by:
            raise HttpResponseForbidden('Anda tidak boleh add notulen item')
        
        context['meeting'] = meeting
        return context
    
    def form_valid(self, form):
        meeting = get_object_or_404(Meeting, pk=self.kwargs['meeting_pk'])
        form.instance.meeting = meeting
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('meetings:meeting-detail', kwargs={'pk': self.kwargs['meeting_pk']})


# ==============================================================================
# 11A. NOTULEN ITEM SAVE (AJAX)
# ==============================================================================
class NotulenItemSaveView(LoginRequiredMixin, View):
    """Save notulen item via AJAX (add or edit)"""
    login_url = 'login'
    
    def post(self, request, meeting_pk):
        try:
            meeting = get_object_or_404(Meeting, pk=meeting_pk)
            
            # Check permission
            if meeting.status != 'draft' or request.user != meeting.created_by:
                return JsonResponse({'error': 'Anda tidak boleh add notulen item'}, status=403)
            
            item_id = request.POST.get('item_id')
            pokok_bahasan = request.POST.get('pokok_bahasan', '').strip()
            tanggapan = request.POST.get('tanggapan', '').strip()
            pic_id = request.POST.get('pic', '').strip()
            pic_eksternal = request.POST.get('pic_eksternal', '').strip()
            target_deadline = request.POST.get('target_deadline')
            
            # Validasi
            if not pokok_bahasan:
                return JsonResponse({'error': 'Pokok bahasan tidak boleh kosong'}, status=400)
            
            # Validasi: PIC harus isi salah satu (dari sistem atau eksternal)
            if not pic_id and not pic_eksternal:
                return JsonResponse({'error': 'PIC harus diisi (pilih dari sistem atau input nama lainnya)'}, status=400)
            
            if not target_deadline:
                return JsonResponse({'error': 'Target deadline harus diisi'}, status=400)
            
            # Get PIC jika dari sistem
            pic = None
            if pic_id:
                try:
                    pic = CustomUser.objects.get(pk=pic_id)
                except CustomUser.DoesNotExist:
                    return JsonResponse({'error': 'PIC tidak valid'}, status=400)
            
            # Add atau Edit
            if item_id:
                # Edit
                try:
                    item = NotulenItem.objects.get(pk=item_id, meeting=meeting)
                except NotulenItem.DoesNotExist:
                    return JsonResponse({'error': 'Item tidak ditemukan'}, status=404)
            else:
                # Add - hitung no urut
                last_item = NotulenItem.objects.filter(meeting=meeting).order_by('-no').first()
                next_no = (last_item.no + 1) if last_item else 1
                item = NotulenItem(meeting=meeting, no=next_no)
            
            # Update fields
            item.pokok_bahasan = pokok_bahasan
            item.tanggapan = tanggapan
            item.pic = pic
            item.pic_eksternal = pic_eksternal if pic_eksternal else None
            # Parse target_deadline dari string
            from datetime import datetime
            if isinstance(target_deadline, str):
                item.target_deadline = datetime.strptime(target_deadline, '%Y-%m-%d').date()
            else:
                item.target_deadline = target_deadline
            item.save()
            
            # Format deadline untuk response
            target_deadline_formatted = item.target_deadline.strftime('%d %b %Y')
            
            # Tentukan nama PIC untuk response
            pic_username = None
            if pic:
                pic_name = pic.get_full_name()
                pic_username = pic.username
            elif pic_eksternal:
                pic_name = f"{pic_eksternal} (Eksternal)"
            else:
                pic_name = "-"
            
            response_data = {
                'success': True,
                'item_id': str(item.pk),
                'no': item.no,
                'pokok_bahasan': item.pokok_bahasan,
                'tanggapan': item.tanggapan or '',
                'pic_name': pic_name,
                'target_deadline': target_deadline_formatted,
                'status': item.get_status_display(),
                'status_badge_color': {
                    'open': 'warning',
                    'progress': 'info',
                    'done': 'success',
                    'overdue': 'danger'
                }.get(item.status, 'secondary')
            }
            
            # Tambahkan pic_username hanya jika ada (untuk PIC sistem)
            if pic_username:
                response_data['pic_username'] = pic_username
            
            return JsonResponse(response_data)
        
        except Exception as e:
            import traceback
            print(f"Error in NotulenItemSaveView: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)


# ==============================================================================
# 11B. NOTULEN ITEM DELETE (AJAX)
# ==============================================================================
class NotulenItemDeleteAjaxView(LoginRequiredMixin, View):
    """Delete notulen item via AJAX"""
    login_url = 'login'
    
    def post(self, request, pk):
        try:
            item = NotulenItem.objects.get(pk=pk)
        except NotulenItem.DoesNotExist:
            return JsonResponse({'error': 'Item tidak ditemukan'}, status=404)
        
        meeting = item.meeting
        
        # Check permission
        if meeting.status != 'draft' or request.user != meeting.created_by:
            return JsonResponse({'error': 'Anda tidak boleh delete notulen item'}, status=403)
        
        item.delete()
        
        return JsonResponse({'success': True})


# ==============================================================================
# 12. NOTULEN ITEM EDIT VIEW
# ==============================================================================
class NotulenItemEditView(LoginRequiredMixin, UpdateView):
    """Edit notulen item (hanya jika meeting draft)"""
    model = NotulenItem
    form_class = NotulenItemForm
    template_name = 'meetings/notulen_form.html'
    login_url = 'login'
    
    def get_object(self):
        item = super().get_object()
        meeting = item.meeting
        
        # Check permission
        if meeting.status != 'draft' or self.request.user != meeting.created_by:
            raise HttpResponseForbidden('Anda tidak boleh edit notulen item')
        
        return item
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meeting'] = self.object.meeting
        return context
    
    def get_success_url(self):
        return reverse_lazy('meetings:meeting-detail', kwargs={'pk': self.object.meeting.pk})


# ==============================================================================
# 13. NOTULEN ITEM DELETE VIEW
# ==============================================================================
class NotulenItemDeleteView(LoginRequiredMixin, DeleteView):
    """Delete notulen item (hanya jika meeting draft)"""
    model = NotulenItem
    template_name = 'meetings/notulen_confirm_delete.html'
    login_url = 'login'
    
    def get_object(self):
        item = super().get_object()
        meeting = item.meeting
        
        # Check permission
        if meeting.status != 'draft' or self.request.user != meeting.created_by:
            raise HttpResponseForbidden('Anda tidak boleh delete notulen item')
        
        return item
    
    def get_success_url(self):
        return reverse_lazy('meetings:meeting-detail', kwargs={'pk': self.object.meeting.pk})


# ==============================================================================
# 14. CREATE JOB FROM NOTULEN VIEW
# ==============================================================================
def create_job_from_notulen_view(request, item_pk):
    """
    Function-based view untuk create job dari notulen item.
    Mengikuti pattern job_form_view yang sudah working.
    
    Permission Model:
    - Hanya users dalam hierarchy notulen PIC yang bisa create
    """
    user = request.user
    notulen_item = get_object_or_404(NotulenItem, pk=item_pk)
    meeting = notulen_item.meeting
    
    # ===== PERMISSION CHECK =====
    # Admin/superuser bypass
    if not (user.is_superuser or user.is_staff):
        # Check hierarchy
        pic = notulen_item.pic
        
        # PIC sendiri bisa
        if user.id != pic.id:
            # Check jika user supervisor dari PIC (PIC di bawah user)
            pic_supervisors = []
            current = pic
            while current.atasan:
                pic_supervisors.append(current.atasan.id)
                current = current.atasan
            
            # Check jika user subordinate dari PIC (PIC di atas user)
            user_supervisors = []
            current = user
            while current.atasan:
                user_supervisors.append(current.atasan.id)
                current = current.atasan
            
            # User valid hanya jika:
            # - User adalah supervisor PIC (PIC di subordinates user)
            # - User adalah subordinate PIC (user id di supervisors PIC)
            is_supervisor = pic.id in user.get_all_subordinates()
            is_subordinate = pic.id in user_supervisors
            
            if not (is_supervisor or is_subordinate):
                messages.error(request, 
                    "Anda tidak memiliki akses untuk membuat job dari notulen ini. "
                    "Hanya PIC dan user dalam hierarchy mereka yang dapat membuat job.")
                return redirect('meetings:meeting-detail', pk=meeting.pk)
    
    # ===== BUILD ALLOWED USERS FOR DROPDOWN =====
    # PIC + all supervisors + all subordinates
    allowed_ids = [notulen_item.pic.id]
    allowed_ids.extend(notulen_item.pic.get_all_subordinates())
    
    current = notulen_item.pic
    while current.atasan:
        allowed_ids.append(current.atasan.id)
        current = current.atasan
    
    allowed_users = CustomUser.objects.filter(id__in=set(allowed_ids), is_active=True)
    
    if request.method == 'POST':
        # ===== CREATE JOB =====
        try:
            with transaction.atomic():
                # Extract data dari POST
                nama_pekerjaan = request.POST.get('nama_pekerjaan', '').strip()
                tipe_job = request.POST.get('tipe_job', 'Daily')
                assigned_to_id = request.POST.get('assigned_to')
                job_deadline = request.POST.get('job_deadline')
                jadwal_pelaksanaan = request.POST.get('jadwal_pelaksanaan', '').strip()
                deskripsi = request.POST.get('deskripsi', '').strip()
                prioritas = request.POST.get('prioritas', 'P3')
                fokus = request.POST.get('fokus', 'Lainnya')
                project_id = request.POST.get('project')
                line_id = request.POST.get('line')
                mesin_id = request.POST.get('mesin')
                sub_mesin_id = request.POST.get('sub_mesin')
                
                # Validation
                if not nama_pekerjaan:
                    messages.error(request, "Nama pekerjaan harus diisi.")
                    from core.models import Project, AsetMesin
                    projects = Project.objects.all().order_by('nama_project')
                    lines = AsetMesin.objects.filter(level=0).order_by('nama')
                    context = {
                        'notulen_item': notulen_item,
                        'meeting': meeting,
                        'allowed_users': allowed_users,
                        'projects': projects,
                        'lines': lines,
                    }
                    return render(request, 'meetings/create_job_from_notulen.html', context)
                
                if not assigned_to_id:
                    messages.error(request, "Penugasan ke user harus dipilih.")
                    from core.models import Project, AsetMesin
                    projects = Project.objects.all().order_by('nama_project')
                    lines = AsetMesin.objects.filter(level=0).order_by('nama')
                    context = {
                        'notulen_item': notulen_item,
                        'meeting': meeting,
                        'allowed_users': allowed_users,
                        'projects': projects,
                        'lines': lines,
                    }
                    return render(request, 'meetings/create_job_from_notulen.html', context)
                
                if not job_deadline:
                    messages.error(request, "Job deadline harus dipilih.")
                    from core.models import Project, AsetMesin
                    projects = Project.objects.all().order_by('nama_project')
                    lines = AsetMesin.objects.filter(level=0).order_by('nama')
                    context = {
                        'notulen_item': notulen_item,
                        'meeting': meeting,
                        'allowed_users': allowed_users,
                        'projects': projects,
                        'lines': lines,
                    }
                    return render(request, 'meetings/create_job_from_notulen.html', context)
                
                # Daily job harus punya jadwal
                if tipe_job == 'Daily' and not jadwal_pelaksanaan:
                    messages.error(request, "Daily Job harus punya jadwal pelaksanaan. Pilih minimal satu tanggal.")
                    from core.models import Project, AsetMesin
                    projects = Project.objects.all().order_by('nama_project')
                    lines = AsetMesin.objects.filter(level=0).order_by('nama')
                    context = {
                        'notulen_item': notulen_item,
                        'meeting': meeting,
                        'allowed_users': allowed_users,
                        'projects': projects,
                        'lines': lines,
                    }
                    return render(request, 'meetings/create_job_from_notulen.html', context)
                
                # Get assigned_to user
                try:
                    assigned_to = CustomUser.objects.get(id=int(assigned_to_id))
                except (CustomUser.DoesNotExist, ValueError, TypeError):
                    messages.error(request, "User yang dipilih tidak valid.")
                    from core.models import Project, AsetMesin
                    projects = Project.objects.all().order_by('nama_project')
                    lines = AsetMesin.objects.filter(level=0).order_by('nama')
                    context = {
                        'notulen_item': notulen_item,
                        'meeting': meeting,
                        'allowed_users': allowed_users,
                        'projects': projects,
                        'lines': lines,
                    }
                    return render(request, 'meetings/create_job_from_notulen.html', context)
                
                # Create Job
                job = Job.objects.create(
                    nama_pekerjaan=nama_pekerjaan,
                    tipe_job=tipe_job,
                    pic=assigned_to,  # PIC = assigned to user
                    status='Open',
                    notulen_item=notulen_item,
                    notulen_target_date=notulen_item.target_deadline,
                    prioritas=prioritas,
                    fokus=fokus,
                    project_id=project_id if project_id else None,
                    aset_id=sub_mesin_id if sub_mesin_id else None,  # Use sub_mesin as aset
                )
                
                # Create JobDate entries
                if jadwal_pelaksanaan:
                    # Format: "2025-01-21,2025-01-22,2025-01-23"
                    dates = [d.strip() for d in jadwal_pelaksanaan.split(',') if d.strip()]
                    for date_str in dates:
                        try:
                            JobDate.objects.create(
                                job=job,
                                tanggal=date_str,
                                status='Open'
                            )
                        except Exception:
                            pass  # Skip invalid dates
                else:
                    # Fallback: create one JobDate with job_deadline
                    JobDate.objects.create(
                        job=job,
                        tanggal=job_deadline,
                        status='Open'
                    )
                
                # Update notulen status
                notulen_item.job_created = job
                notulen_item.status = 'progress'
                notulen_item.save()
                
                messages.success(request, f"Job '{nama_pekerjaan}' berhasil dibuat dari notulen.")
                return redirect('meetings:meeting-detail', pk=meeting.pk)
        
        except Exception as e:
            messages.error(request, f"Error membuat job: {str(e)}")
            from core.models import Project, AsetMesin
            projects = Project.objects.all().order_by('nama_project')
            lines = AsetMesin.objects.filter(level=0).order_by('nama')
            context = {
                'notulen_item': notulen_item,
                'meeting': meeting,
                'allowed_users': allowed_users,
                'projects': projects,
                'lines': lines,
            }
            return render(request, 'meetings/create_job_from_notulen.html', context)
    
    # ===== GET: SHOW FORM =====
    # Get projects and lines for dropdowns
    from core.models import Project, AsetMesin
    projects = Project.objects.all().order_by('nama_project')
    lines = AsetMesin.objects.filter(level=0).order_by('nama')  # Level 0 = Line
    
    context = {
        'notulen_item': notulen_item,
        'meeting': meeting,
        'allowed_users': allowed_users,
        'projects': projects,
        'lines': lines,
    }
    return render(request, 'meetings/create_job_from_notulen.html', context)


# ==============================================================================
# ==============================================================================
# 14A. MEETING ADD PESERTA VIEW
# ==============================================================================
class MeetingAddPesertaView(LoginRequiredMixin, View):
    """Add peserta ke meeting (dari modal di detail page)"""
    login_url = 'login'
    
    def post(self, request, pk):
        meeting = get_object_or_404(Meeting, pk=pk)
        
        # Check permission
        if meeting.status != 'draft' or request.user != meeting.created_by:
            return HttpResponseForbidden('Anda tidak boleh tambah peserta')
        
        peserta_id = request.POST.get('peserta')
        if not peserta_id:
            return HttpResponseBadRequest('Peserta harus dipilih')
        
        # Get user
        peserta = get_object_or_404(CustomUser, pk=peserta_id)
        
        # Create MeetingPeserta
        meeting_peserta, created = MeetingPeserta.objects.get_or_create(
            meeting=meeting,
            peserta=peserta,
            defaults={
                'tipe_peserta': 'internal',
                'nama': peserta.get_full_name() or peserta.username
            }
        )
        
        return redirect('meetings:meeting-detail', pk=meeting.pk)


# ==============================================================================
# 14B. MEETING DELETE PESERTA VIEW
# ==============================================================================
class MeetingDeletePesertaView(LoginRequiredMixin, View):
    """Delete peserta dari meeting"""
    login_url = 'login'
    
    def post(self, request, peserta_pk):
        peserta = get_object_or_404(MeetingPeserta, pk=peserta_pk)
        meeting = peserta.meeting
        
        # Check permission
        if meeting.status != 'draft' or request.user != meeting.created_by:
            return HttpResponseForbidden('Anda tidak boleh hapus peserta')
        
        peserta.delete()
        return redirect('meetings:meeting-detail', pk=meeting.pk)


# 15. PESERTA STATUS UPDATE (AJAX)
# ==============================================================================
class PesertaStatusUpdateView(LoginRequiredMixin, View):
    """Update peserta status via AJAX"""
    login_url = 'login'
    
    def post(self, request, peserta_pk):
        peserta = get_object_or_404(MeetingPeserta, pk=peserta_pk)
        meeting = peserta.meeting
        
        # Check permission
        if request.user != meeting.created_by:
            return JsonResponse({'error': 'Anda tidak boleh update status'}, status=403)
        
        status = request.POST.get('status_kehadiran')
        catatan = request.POST.get('catatan', '')
        
        if status in dict(MeetingPeserta.STATUS_KEHADIRAN_CHOICES):
            peserta.status_kehadiran = status
            peserta.catatan = catatan
            peserta.save()
            
            return JsonResponse({
                'success': True,
                'status': status,
                'presensi_summary': meeting.get_presensi_summary()
            })
        
        return JsonResponse({'error': 'Invalid status'}, status=400)


# ==============================================================================
# 16. QR CODE TOGGLE VIEW
# ==============================================================================
class QRCodeToggleView(LoginRequiredMixin, View):
    """Toggle QR code aktif/inactive - support both meeting_pk dan token"""
    login_url = 'login'
    
    def post(self, request, pk=None, token=None):
        # Handle both pk (meeting_pk) dan token (qr_code_token)
        if pk:
            meeting = get_object_or_404(Meeting, pk=pk)
        elif token:
            meeting = get_object_or_404(Meeting, qr_code_token=token)
        else:
            return JsonResponse({'error': 'Meeting not found'}, status=404)
        
        # Check permission
        if request.user != meeting.created_by:
            return JsonResponse({'error': 'Anda tidak boleh toggle QR code'}, status=403)
        
        meeting.toggle_qr_code()
        
        return JsonResponse({
            'success': True,
            'qr_code_active': meeting.qr_code_active
        })


# ==============================================================================
# 17. NOTULEN ITEM GET VIEW (AJAX)
# ==============================================================================
class NotulenItemGetView(LoginRequiredMixin, View):
    """Get notulen item data via AJAX for editing"""
    login_url = 'login'
    
    def get(self, request, pk):
        try:
            item = NotulenItem.objects.get(pk=pk)
        except NotulenItem.DoesNotExist:
            return JsonResponse({'error': 'Item tidak ditemukan'}, status=404)
        
        meeting = item.meeting
        
        # Check permission
        if meeting.status != 'draft' or request.user != meeting.created_by:
            return JsonResponse({'error': 'Anda tidak boleh edit notulen item'}, status=403)
        
        # Format date untuk input date field (YYYY-MM-DD)
        target_deadline_formatted = item.target_deadline.strftime('%Y-%m-%d')
        
        return JsonResponse({
            'success': True,
            'item_id': str(item.pk),
            'no': item.no,
            'pokok_bahasan': item.pokok_bahasan,
            'tanggapan': item.tanggapan,
            'pic_id': str(item.pic.pk) if item.pic else '',
            'pic_eksternal': item.pic_eksternal or '',
            'target_deadline': target_deadline_formatted,
            'status': item.status
        })


# ==============================================================================
# 13. EXPORT NOTULEN KE GOOGLE SHEETS
# ==============================================================================
@method_decorator(require_http_methods(["GET"]), name='dispatch')
class ExportNotulenPDFView(LoginRequiredMixin, View):
    """Export meeting notulen ke PDF menggunakan WeasyPrint"""
    login_url = 'login'
    
    def get(self, request, pk):
        """Generate & download PDF"""
        try:
            meeting = get_object_or_404(Meeting, pk=pk)
            
            # Check permission
            if request.user != meeting.created_by and not request.user.is_staff:
                return HttpResponseForbidden('Anda tidak memiliki akses untuk export meeting ini')
            
            # Get notulen items
            notulen_items = NotulenItem.objects.filter(meeting=meeting).order_by('no')
            
            # Get peserta
            peserta_list = MeetingPeserta.objects.filter(meeting=meeting).select_related('peserta')
            
            # Calculate empty rows untuk total 15 baris
            items_count = notulen_items.count()
            empty_rows_count = max(0, 15 - items_count)
            
            # Build context
            context = {
                'meeting': meeting,
                'notulen_items': notulen_items,
                'peserta': peserta_list,
                'empty_rows': range(empty_rows_count),  # Generate empty rows
                'company_name': settings.COMPANY_NAME if hasattr(settings, 'COMPANY_NAME') else 'PT. NUSANTARA BUILDING INDUSTRIES',
                'print_date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
            
            # Render template to HTML
            html_string = render_to_string('meetings/report_notulen.html', context, request=request)
            
            # Convert ke PDF
            html = HTML(string=html_string)
            pdf = html.write_pdf()
            
            # Generate filename
            filename = f"Notulen_{meeting.no_dokumen}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Return PDF sebagai download
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Meeting.DoesNotExist:
            return HttpResponseForbidden('Meeting tidak ditemukan')
        except Exception as e:
            return HttpResponseForbidden(f'Error: {str(e)}')


# ==============================================================================
# 18. EXPORT NOTULEN KE PDF V2 (Lebih lengkap)
# ==============================================================================
@method_decorator(require_http_methods(["GET"]), name='dispatch')
class ExportNotulenPDFV2View(LoginRequiredMixin, View):
    """Export meeting notulen ke PDF v2 (dengan peserta, action items lengkap)"""
    login_url = 'login'
    
    def get(self, request, pk):
        """Generate & download PDF v2"""
        try:
            meeting = get_object_or_404(Meeting, pk=pk)
            
            # Check permission
            if request.user != meeting.created_by and not request.user.is_staff:
                return HttpResponseForbidden('Anda tidak memiliki akses untuk export meeting ini')
            
            # Get notulen items
            notulen_items = NotulenItem.objects.filter(meeting=meeting).order_by('no')
            
            # Get peserta
            peserta_list = MeetingPeserta.objects.filter(meeting=meeting).select_related('peserta')
            
            # Get presensi summary
            presensi_summary = meeting.get_presensi_summary()
            
            # Count action items by status
            open_count = notulen_items.filter(status='open').count()
            progress_count = notulen_items.filter(status='progress').count()
            done_count = notulen_items.filter(status='done').count()
            
            # Build context
            context = {
                'meeting': meeting,
                'notulen_items': notulen_items,
                'peserta_list': peserta_list,
                'presensi_summary': presensi_summary,
                'open_count': open_count,
                'progress_count': progress_count,
                'done_count': done_count,
                'company_name': settings.COMPANY_NAME if hasattr(settings, 'COMPANY_NAME') else 'PT. NUSANTARA BUILDING INDUSTRIES',
                'print_date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
            
            # Render template to HTML
            html_string = render_to_string('meetings/report_notulen_v2.html', context, request=request)
            
            # Convert ke PDF
            html = HTML(string=html_string)
            pdf = html.write_pdf()
            
            # Generate filename
            filename = f"Notulen_v2_{meeting.no_dokumen}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Return PDF sebagai download
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        except Meeting.DoesNotExist:
            return HttpResponseForbidden('Meeting tidak ditemukan')
        except Exception as e:
            import traceback
            print(f"Error in ExportNotulenPDFV2View: {str(e)}")
            print(traceback.format_exc())
            return HttpResponseForbidden(f'Error: {str(e)}')

