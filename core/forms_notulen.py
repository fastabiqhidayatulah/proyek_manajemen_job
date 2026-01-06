# Form untuk create job dari notulen item

from django import forms
from .models import Job

class JobFromNotulenForm(forms.Form):
    """Form untuk create job dari notulen item dengan multi-date picker"""
    
    # Pre-filled fields (display only dalam modal)
    pokok_bahasan = forms.CharField(
        label='Pokok Bahasan (dari Notulen)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'readonly': True
        }),
        required=False
    )
    
    pic_notulen = forms.CharField(
        label='PIC Notulen',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True
        }),
        required=False
    )
    
    target_deadline_notulen = forms.DateField(
        label='Target Deadline Notulen',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'readonly': True
        }),
        required=False
    )
    
    # === EDITABLE FIELDS ===
    nama_pekerjaan = forms.CharField(
        label='Nama Pekerjaan',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama job (auto-filled dari notulen, bisa diubah)'
        })
    )
    
    tipe_job = forms.ChoiceField(
        label='Tipe Job',
        choices=[
            ('Daily', 'Daily Job'),
            ('Project', 'Project Job'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    assigned_to = forms.ModelChoiceField(
        label='Assign ke (User)',
        queryset=CustomUser.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Pilih user yang akan bertanggung jawab (dalam hierarchy PIC)',
        required=True
    )
    
    job_deadline = forms.DateField(
        label='Job Deadline',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Tanggal deadline job (independent dari notulen deadline)',
        required=True
    )
    
    # Multi-date picker untuk jadwal pelaksanaan (hanya untuk Daily Job)
    jadwal_pelaksanaan = forms.CharField(
        label='Jadwal Pelaksanaan (Multi-date)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'jadwal_pelaksanaan_picker',
            'placeholder': 'Pilih tanggal pelaksanaan (comma-separated)',
            'data-flatpickr': 'true',
            'data-mode': 'multiple'
        }),
        required=False,
        help_text='Untuk Daily Job: pilih tanggal-tanggal pelaksanaan'
    )
    
    # Optional fields
    deskripsi = forms.CharField(
        label='Deskripsi / Notes',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Deskripsi detail job (opsional)'
        }),
        required=False
    )
    
    prioritas = forms.ChoiceField(
        label='Prioritas',
        choices=Job.PRIORITAS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False
    )
    
    fokus = forms.ChoiceField(
        label='Fokus',
        choices=Job.FOKUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False
    )
    
    aset = forms.ModelChoiceField(
        label='Aset/Mesin (Opsional)',
        queryset=AsetMesin.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        help_text='Pilih sub-mesin yang terkait job ini'
    )
    
    project = forms.ModelChoiceField(
        label='Project (Opsional)',
        queryset=Project.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        help_text='Pilih project jika ini bagian dari project'
    )
    
    def __init__(self, *args, notulen_pic=None, allowed_users=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter assigned_to queryset hanya user dalam hierarchy
        if allowed_users:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                id__in=allowed_users,
                is_active=True
            )
    
    def clean(self):
        cleaned_data = super().clean()
        tipe_job = cleaned_data.get('tipe_job')
        jadwal_pelaksanaan = cleaned_data.get('jadwal_pelaksanaan')
        
        # Validasi: Daily job harus punya jadwal
        if tipe_job == 'Daily' and not jadwal_pelaksanaan:
            self.add_error('jadwal_pelaksanaan', 'Daily Job harus punya jadwal pelaksanaan')
        
        return cleaned_data
