from django import forms
from django.forms import inlineformset_factory, ModelChoiceField
from .models import (
    PreventiveJobTemplate,
    PreventiveJobExecution,
    PreventiveJobAttachment,
    ChecklistTemplate,
    ChecklistItem,
    ChecklistResult,
)
from core.models import AsetMesin, CustomUser, Personil


class PreventiveJobTemplateForm(forms.ModelForm):
    """
    Form untuk membuat/edit PreventiveJobTemplate
    """
    
    aset_mesin = forms.ModelMultipleChoiceField(
        queryset=AsetMesin.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control searchable-select',
            'size': 8,
            'id': 'aset_mesin_select',
        }),
        label="Pilih Mesin/Aset",
        help_text="Pilih satu atau lebih mesin yang akan di-apply preventive job ini"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter PIC: hanya diri sendiri dan subordinates
        if user:
            subordinate_ids = user.get_all_subordinates()
            allowed_user_ids = [user.id] + subordinate_ids
            self.fields['pic'].queryset = CustomUser.objects.filter(
                id__in=allowed_user_ids
            ).order_by('jabatan__nama_jabatan', 'username')
    
    class Meta:
        model = PreventiveJobTemplate
        fields = [
            'nama_pekerjaan',
            'deskripsi',
            'aset_mesin',
            'schedule_type',
            'interval_hari',
            'custom_dates',
            'tanggal_mulai',
            'tanggal_berakhir',
            'fokus',
            'kategori',
            'prioritas',
            'pic',
            'checklist_template',
            'notify_24h_before',
            'notify_2h_before',
            'notify_on_schedule',
            'is_active',
        ]
        widgets = {
            'nama_pekerjaan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Cek Oil Level, Ganti Filter, dll'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Deskripsi detail pekerjaan...'
            }),
            'schedule_type': forms.RadioSelect(attrs={
                'class': 'form-check-input',
            }),
            'interval_hari': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Contoh: 1 (harian), 7 (mingguan), 30 (bulanan), 365 (tahunan)',
                'id': 'interval_hari_input',
            }),
            'custom_dates': forms.HiddenInput(attrs={
                'id': 'custom_dates_input',
            }),
            'tanggal_mulai': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'tanggal_berakhir': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fokus': forms.Select(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-control'}),
            'prioritas': forms.Select(attrs={'class': 'form-control'}),
            'pic': forms.Select(attrs={'class': 'form-control'}),
            'checklist_template': forms.Select(attrs={
                'class': 'form-control',
                'id': 'checklist_template_select',
            }),
            'notify_24h_before': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_2h_before': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_on_schedule': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nama_pekerjaan': 'Nama Pekerjaan *',
            'deskripsi': 'Deskripsi',
            'aset_mesin': 'Pilih Mesin/Aset *',
            'schedule_type': 'Tipe Jadwal *',
            'interval_hari': 'Interval (Hari) *',
            'custom_dates': 'Tanggal Pilihan (untuk Custom Dates)',
            'tanggal_mulai': 'Tanggal Mulai *',
            'tanggal_berakhir': 'Tanggal Berakhir (Opsional)',
            'fokus': 'Fokus Pekerjaan *',
            'kategori': 'Kategori Pekerjaan *',
            'prioritas': 'Prioritas *',
            'pic': 'PIC (Penanggung Jawab) *',
            'checklist_template': 'Checklist Template (Opsional)',
            'notify_24h_before': 'Notifikasi 24 jam sebelumnya',
            'notify_2h_before': 'Notifikasi 2 jam sebelumnya',
            'notify_on_schedule': 'Notifikasi saat jadwal',
            'is_active': 'Status Aktif',
        }


class PreventiveJobExecutionForm(forms.ModelForm):
    """
    Form untuk update PreventiveJobExecution status
    """
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter assigned_to_personil: personil dari PIC template dan bawahannya
        if self.instance and self.instance.template:
            from core.models import CustomUser
            pic = self.instance.template.pic
            
            # Get PIC and all subordinates recursively
            all_users = [pic]
            
            # Add direct subordinates
            subordinates = CustomUser.objects.filter(atasan=pic)
            all_users.extend(subordinates)
            
            # Add subordinates of subordinates (recursive)
            for sub in subordinates:
                all_sub = CustomUser.objects.filter(atasan=sub)
                all_users.extend(all_sub)
            
            # Get personil managed by PIC and all subordinates
            personil_team = Personil.objects.filter(penanggung_jawab__in=all_users)
            self.fields['assigned_to_personil'].queryset = personil_team.order_by('nama_lengkap')
    
    class Meta:
        model = PreventiveJobExecution
        fields = [
            'status',
            'assigned_to_personil',
            'actual_date',
            'catatan',
            'compliance_type',
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to_personil': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 10}),
            'actual_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'catatan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Catatan atau findings dari job ini'
            }),
            'compliance_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'Status *',
            'assigned_to_personil': 'Ditugaskan ke (Bisa Multiple)',
            'actual_date': 'Tanggal Pelaksanaan Aktual',
            'catatan': 'Catatan/Findings',
            'compliance_type': 'Tipe Compliance',
        }


class PreventiveJobExecutionQuickUpdateForm(forms.ModelForm):
    """
    Form sederhana untuk quick update execution status (dari dashboard)
    """
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter assigned_to_personil: personil dari PIC template dan bawahannya
        if self.instance and self.instance.template:
            from core.models import CustomUser
            pic = self.instance.template.pic
            
            # Get PIC and all subordinates recursively
            all_users = [pic]
            
            # Add direct subordinates
            subordinates = CustomUser.objects.filter(atasan=pic)
            all_users.extend(subordinates)
            
            # Add subordinates of subordinates (recursive)
            for sub in subordinates:
                all_sub = CustomUser.objects.filter(atasan=sub)
                all_users.extend(all_sub)
            
            # Get personil managed by PIC and all subordinates
            personil_team = Personil.objects.filter(penanggung_jawab__in=all_users)
            self.fields['assigned_to_personil'].queryset = personil_team.order_by('nama_lengkap')
    
    class Meta:
        model = PreventiveJobExecution
        fields = ['status', 'assigned_to_personil']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control form-control-sm',
            }),
            'assigned_to_personil': forms.SelectMultiple(attrs={
                'class': 'form-control form-control-sm',
                'size': 8,
            }),
        }


class PreventiveJobAttachmentForm(forms.ModelForm):
    """
    Form untuk upload attachment
    """
    
    class Meta:
        model = PreventiveJobAttachment
        fields = ['file', 'deskripsi', 'tipe_file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,application/pdf,.doc,.docx'
            }),
            'deskripsi': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Deskripsi file (opsional)'
            }),
            'tipe_file': forms.Select(attrs={'class': 'form-control'}),
        }


# Formset untuk multiple attachments
PreventiveJobAttachmentFormSet = inlineformset_factory(
    PreventiveJobExecution,
    PreventiveJobAttachment,
    form=PreventiveJobAttachmentForm,
    extra=1,
    can_delete=True
)


# ==============================================================================
# FORMS UNTUK MASTER CHECKLIST
# ==============================================================================

class ChecklistTemplateForm(forms.ModelForm):
    """
    Form untuk membuat/edit ChecklistTemplate
    """
    
    class Meta:
        model = ChecklistTemplate
        fields = [
            'nama',
            'kategori',
            'deskripsi',
            'file_template',
            'is_active',
        ]
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama checklist, contoh: Checklist Perawatan Motor 3 Fasa'
            }),
            'kategori': forms.Select(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi checklist (opsional)'
            }),
            'file_template': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.xlsx,.xls,.pdf'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChecklistItemForm(forms.ModelForm):
    """
    Form untuk membuat/edit ChecklistItem
    """
    
    class Meta:
        model = ChecklistItem
        fields = [
            'no_urut',
            'item_pemeriksaan',
            'standar_normal',
            'unit',
            'nilai_min',
            'nilai_max',
            'tindakan_remark',
        ]
        widgets = {
            'no_urut': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'item_pemeriksaan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Tegangan antar fasa'
            }),
            'standar_normal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 380±10% V'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: V, A, %, MΩ, Hz'
            }),
            'nilai_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Min value (opsional)'
            }),
            'nilai_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Max value (opsional)'
            }),
            'tindakan_remark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tindakan jika nilai abnormal (opsional)'
            }),
        }


# Formset untuk multiple items dalam checklist
ChecklistItemFormSet = inlineformset_factory(
    ChecklistTemplate,
    ChecklistItem,
    form=ChecklistItemForm,
    extra=5,
    can_delete=True
)


class ChecklistResultForm(forms.ModelForm):
    """
    Form untuk mengisi hasil checklist saat job selesai
    """
    
    class Meta:
        model = ChecklistResult
        fields = [
            'catatan_umum',
        ]
        widgets = {
            'catatan_umum': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan umum hasil checklist (opsional)'
            }),
        }


class PreventiveTemplateDuplicateForm(forms.Form):
    """
    Form untuk duplicate template dengan periode/jadwal berbeda
    Hanya perlu input tanggal_mulai dan tanggal_berakhir saja
    Semua field lain (nama, deskripsi, aset, checklist, dll) akan dicopy dari template original
    """
    
    tanggal_mulai = forms.DateField(
        label="Tanggal Mulai (Periode Baru) *",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True,
        }),
        help_text="Kapan template ini mulai aktif untuk periode baru"
    )
    
    tanggal_berakhir = forms.DateField(
        label="Tanggal Berakhir (Periode Baru) (Opsional)",
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        help_text="Kosongkan jika pengulangan tidak terbatas"
    )
    
    def clean(self):
        """Validate bahwa tanggal_mulai < tanggal_berakhir"""
        cleaned_data = super().clean()
        tanggal_mulai = cleaned_data.get('tanggal_mulai')
        tanggal_berakhir = cleaned_data.get('tanggal_berakhir')
        
        if tanggal_mulai and tanggal_berakhir:
            if tanggal_mulai >= tanggal_berakhir:
                raise forms.ValidationError(
                    "Tanggal Mulai harus lebih awal dari Tanggal Berakhir!"
                )
        
        return cleaned_data
