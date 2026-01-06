from django import forms
from django.forms import inlineformset_factory 
from django.db.models import Q
from .models import Personil, Job, JobDate, Attachment, AsetMesin, Project, CustomUser, LeaveEvent, Karyawan 

# ==============================================================================
# FORM PERSONIL (Tidak berubah)
# ==============================================================================
class PersonilForm(forms.ModelForm):
    class Meta:
        model = Personil
        fields = ['nama_lengkap']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama lengkap anak buah'
            })
        }
        labels = {
            'nama_lengkap': 'Nama Lengkap Personil'
        }

# ==============================================================================
# FORM PROJECT (Tidak berubah)
# ==============================================================================
# ==============================================================================
# FORM PROJECT + SHARING (UPDATED)
# ==============================================================================
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['nama_project', 'deskripsi', 'is_shared']
        widgets = {
            'nama_project': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Misal: Project Instalasi Mesin Baru'
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4
            }),
            'is_shared': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'nama_project': 'Nama Project',
            'deskripsi': 'Deskripsi Singkat (Opsional)',
            'is_shared': 'Bagikan ke semua user (izinkan mereka lihat & tambah job)',
        }
        help_texts = {
            'is_shared': 'Jika dicentang, semua user dapat melihat dan menambah job di project ini',
        }


# ==============================================================================
# FORM MODAL STATUS TANGGAL (Tidak berubah)
# ==============================================================================
class JobDateStatusForm(forms.ModelForm):
    class Meta:
        model = JobDate
        fields = ['status', 'catatan']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'status': 'Ubah Status Menjadi',
            'catatan': 'Catatan (Opsional)',
        }


# ==============================================================================
# FORM PEKERJAAN (JOB) (DIPERBARUI)
# ==============================================================================
class JobForm(forms.ModelForm):
    
    line = forms.ModelChoiceField(
        queryset=AsetMesin.objects.filter(level=0), # Level 0 = Line
        label="Line",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_line'})
    )
    mesin = forms.ModelChoiceField(
        queryset=AsetMesin.objects.none(), # Kosong, diisi JS
        label="Mesin (Optional - kosongkan untuk semua mesin di line)",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_mesin'})
    )
    sub_mesin = forms.ModelChoiceField(
        queryset=AsetMesin.objects.none(), # Kosong, diisi JS
        label="Sub Mesin (Optional - kosongkan untuk semua sub mesin di mesin)",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_sub_mesin'})
    )

    tanggal_pelaksanaan = forms.CharField(
        label="Tanggal Pelaksanaan",
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_tanggal_pelaksanaan_hidden'})
    )
    
    assigned_to = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        label="Assign To (Pilih Bawahan)",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_assigned_to'})
    )

    class Meta:
        model = Job
        fields = [
            'nama_pekerjaan', 
            'tipe_job', 
            'project',
            'assigned_to',  # <-- TAMBAHKAN
            'fokus',
            'prioritas',
            'personil_ditugaskan',
            'tanggal_pelaksanaan' 
        ]
        labels = {
            'nama_pekerjaan': 'Nama Pekerjaan',
            'tipe_job': 'Tipe Pekerjaan',
            'project': 'Nama Project',
            'fokus': 'Fokus Pekerjaan',
            'prioritas': 'Prioritas',
            'personil_ditugaskan': 'Personil Yang Ditugaskan',
        }
        widgets = {
            'personil_ditugaskan': forms.SelectMultiple(
                attrs={'class': 'form-select', 'size': '5'}
            )
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        project = kwargs.pop('project', None) # Ambil project (jika ada)
        super().__init__(*args, **kwargs)

        # Style Bootstrap
        self.fields['nama_pekerjaan'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Misal: Pengecekan Harian Panel X'})
        self.fields['tipe_job'].widget.attrs.update({'class': 'form-select'})
        self.fields['project'].widget.attrs.update({'class': 'form-select'})
        self.fields['fokus'].widget.attrs.update({'class': 'form-select'})
        self.fields['prioritas'].widget.attrs.update({'class': 'form-select'})
        self.fields['assigned_to'].widget.attrs.update({'class': 'form-select'})  # <-- TAMBAHKAN
        
        self.fields['personil_ditugaskan'].required = False 
        self.fields['personil_ditugaskan'].help_text = "Tahan Ctrl (atau Cmd di Mac) untuk memilih lebih dari satu."

        # === LOGIKA ASSIGN_TO: Isi dengan daftar bawahan user ===
        if user:
            # Get all subordinates dari current user
            subordinate_ids = user.get_all_subordinates()
            
            # Jika ada subordinates, tampilkan di dropdown
            if subordinate_ids:
                self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                    id__in=subordinate_ids
                ).order_by('username')
            else:
                # Jika tidak ada subordinates, hide/kosongkan dropdown
                self.fields['assigned_to'].queryset = CustomUser.objects.none()
            
            # === SET DEFAULT PERSONIL QUERYSET (PENTING!) ===
            # Default: gunakan personil milik user sendiri (untuk initial load)
            default_personil = Personil.objects.filter(
                penanggung_jawab=user
            ).order_by('nama_lengkap')
            
            # Filter 'personil' berdasarkan 'assigned_to' atau user sendiri
            if self.data:
                # POST request - ada data dari form
                try:
                    assigned_to_id = int(self.data.get('assigned_to')) if self.data.get('assigned_to') else None
                    if assigned_to_id:
                        # Jika assigned_to dipilih, tampilkan personil milik bawahan itu
                        self.fields['personil_ditugaskan'].queryset = Personil.objects.filter(
                            penanggung_jawab_id=assigned_to_id
                        ).order_by('nama_lengkap')
                    else:
                        # Jika tidak dipilih, tampilkan personil milik user sendiri
                        self.fields['personil_ditugaskan'].queryset = default_personil
                except (ValueError, TypeError):
                    self.fields['personil_ditugaskan'].queryset = default_personil
            elif self.instance and self.instance.pk and self.instance.assigned_to:
                # GET request (Edit mode) - jika sudah ada assigned_to, gunakan personil milik mereka
                self.fields['personil_ditugaskan'].queryset = Personil.objects.filter(
                    penanggung_jawab=self.instance.assigned_to
                ).order_by('nama_lengkap')
                self.fields['assigned_to'].initial = self.instance.assigned_to.id
            else:
                # Default: gunakan personil milik user sendiri
                self.fields['personil_ditugaskan'].queryset = default_personil
        else:
            # Fallback jika user kosong (edge case)
            self.fields['assigned_to'].queryset = CustomUser.objects.none()
            self.fields['personil_ditugaskan'].queryset = Personil.objects.none()
        
        # Sembunyikan 'project' awalnya
        self.fields['project'].required = False
        
        # === LOGIKA FILTER PROJECT: Tampilkan project yang bisa diakses user (BIDIRECTIONAL) ===
        # User bisa akses project jika:
        # 1. User adalah owner/creator (manager_project)
        # 2. Project di-share (is_shared=True)
        # 3. Project dari subordinates (untuk supervisor oversight)
        # 4. Project dari supervisors/atasan (for collaborative work)
        if user:
            subordinate_ids = user.get_all_subordinates()
            
            # Get all supervisors (people above in hierarchy)
            supervisor_ids = []
            current_user = user
            while current_user.atasan:
                supervisor_ids.append(current_user.atasan.id)
                current_user = current_user.atasan
            
            accessible_projects = Project.objects.filter(
                Q(manager_project=user) |  # Owner
                Q(is_shared=True) |  # Shared to all
                Q(manager_project_id__in=subordinate_ids) |  # Subordinate projects
                Q(manager_project_id__in=supervisor_ids)  # Supervisor projects (BIDIRECTIONAL)
            ).order_by('nama_project').distinct()
            self.fields['project'].queryset = accessible_projects
        else:
            self.fields['project'].queryset = Project.objects.none()
        
        # === LOGIKA BARU: Jika menambah job dari halaman project ===
        if project:
            self.fields['project'].initial = project.id
            self.fields['project'].widget = forms.HiddenInput()
            self.fields['tipe_job'].initial = 'Project'
            self.fields['tipe_job'].widget = forms.HiddenInput()
        
        # === LOGIKA BARU: HIDE/DISABLE assigned_to field jika user bukan PIC (pembuat) ===
        # Saat EDIT mode dan user BUKAN pembuat job, jangan tampilkan assigned_to field
        if self.instance and self.instance.pk and user:
            if self.instance.pic != user:
                # User bukan PIC - HIDE assigned_to field dari form
                # Tapi tetap include di data supaya tidak error saat save
                self.fields['assigned_to'].widget = forms.HiddenInput()
                self.fields['assigned_to'].initial = self.instance.assigned_to.id if self.instance.assigned_to else None
        
        # 1. Jika ada data POST (terjadi saat validasi error)
        if self.data:
            try:
                line_id = int(self.data.get('line'))
                if line_id:
                    self.fields['mesin'].queryset = AsetMesin.objects.filter(parent_id=line_id).order_by('nama')
                
                mesin_id = int(self.data.get('mesin'))
                if mesin_id:
                     self.fields['sub_mesin'].queryset = AsetMesin.objects.filter(parent_id=mesin_id).order_by('nama')
            
            except (ValueError, TypeError):
                pass 
        
        # 2. Jika mode Edit (GET) dan TIDAK ada data POST
        elif self.instance and self.instance.pk and self.instance.aset:
            aset = self.instance.aset 
            if aset.level == 2: 
                mesin = aset.parent
                line = mesin.parent
                self.fields['line'].initial = line.id
                self.fields['mesin'].queryset = AsetMesin.objects.filter(parent=line)
                self.fields['mesin'].initial = mesin.id
                self.fields['sub_mesin'].queryset = AsetMesin.objects.filter(parent=mesin)
                self.fields['sub_mesin'].initial = aset.id
            elif aset.level == 1: 
                mesin = aset
                line = mesin.parent
                self.fields['line'].initial = line.id
                self.fields['mesin'].queryset = AsetMesin.objects.filter(parent=line)
                self.fields['mesin'].initial = mesin.id
            elif aset.level == 0: 
                line = aset
                self.fields['line'].initial = line.id

    def clean(self):
        """Override clean untuk handle assigned_to hidden field"""
        cleaned_data = super().clean()
        
        # Jika assigned_to widget adalah HiddenInput, gunakan initial value
        # Ini mencegah validation error untuk subordinate yang edit job
        if isinstance(self.fields['assigned_to'].widget, forms.HiddenInput):
            if 'assigned_to' in self.errors:
                # Remove error jika field adalah hidden input
                del self.errors['assigned_to']
            # Set value dari initial
            if self.instance and self.instance.assigned_to:
                cleaned_data['assigned_to'] = self.instance.assigned_to
            else:
                cleaned_data['assigned_to'] = None
        
        return cleaned_data

# ==============================================================================
# FORMSET UNTUK LAMPIRAN (Tidak berubah)
# ==============================================================================
class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file', 'deskripsi', 'tipe_file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Deskripsi file'}),
            'tipe_file': forms.Select(attrs={'class': 'form-select'}),
        }

AttachmentFormSet = inlineformset_factory(
    Job,
    Attachment,
    form=AttachmentForm,
    extra=1,
    can_delete=True
)


# ==============================================================================
# FORM LEAVE EVENT (IJIN/CUTI) - BARU
# ==============================================================================
class LeaveEventForm(forms.ModelForm):
    """Form untuk create/edit Leave Event (Ijin/Cuti)"""
    
    # Input text dengan autocomplete (datalist) - lebih simple
    karyawan_search = forms.CharField(
        label="Nama Karyawan",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_karyawan_search',
            'placeholder': 'Cari nama atau NIK karyawan...',
            'list': 'karyawan_list',  # Refer ke datalist di template
            'autocomplete': 'off',
        }),
        help_text="Ketik nama atau NIK untuk mencari"
    )
    
    # Hidden field untuk store ID yang dipilih
    karyawan = forms.ModelChoiceField(
        queryset=Karyawan.objects.filter(status='Aktif').order_by('nama_lengkap'),
        required=True,
        widget=forms.HiddenInput(),
    )
    
    # Custom field untuk tanggal (akan handle single atau multiple)
    tanggal_picker = forms.CharField(
        label="Tanggal Ijin/Cuti",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_tanggal_picker',
            'placeholder': 'Pilih tanggal (single atau range)',
        }),
        help_text="Klik untuk memilih tanggal. Bisa single date atau range."
    )
    
    class Meta:
        model = LeaveEvent
        fields = ['karyawan', 'tipe_leave', 'deskripsi']
        widgets = {
            'tipe_leave': forms.Select(attrs={
                'class': 'form-select',
            }),
            'deskripsi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Keterangan tambahan (opsional)'
            }),
        }
        labels = {
            'tipe_leave': 'Tipe Ijin/Cuti',
            'deskripsi': 'Keterangan Tambahan',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Jika mode EDIT, populate tanggal_picker dengan data yang ada
        if self.instance and self.instance.pk and self.instance.tanggal:
            # Parse tanggal dari database
            tanggal_list = self.instance.get_tanggal_list()
            tanggal_str = ','.join(tanggal_list)
            self.fields['tanggal_picker'].initial = tanggal_str
            
            # Set initial karyawan search
            if self.instance.karyawan:
                self.fields['karyawan_search'].initial = f"{self.instance.karyawan.nik} - {self.instance.karyawan.nama_lengkap}"
    
    def clean(self):
        """Validate form"""
        cleaned_data = super().clean()
        
        tanggal_picker = cleaned_data.get('tanggal_picker', '').strip()
        
        if not tanggal_picker:
            self.add_error('tanggal_picker', "Tanggal harus dipilih!")
            raise forms.ValidationError("Tanggal harus dipilih!")
        
        # Validate format tanggal (simple check)
        tanggal_list = [tgl.strip() for tgl in tanggal_picker.split(',') if tgl.strip()]
        for tgl in tanggal_list:
            try:
                # Check if valid date format YYYY-MM-DD
                from datetime import datetime
                datetime.strptime(tgl, '%Y-%m-%d')
            except ValueError:
                self.add_error('tanggal_picker', f"Format tanggal tidak valid: {tgl}. Gunakan format YYYY-MM-DD")
                raise forms.ValidationError(f"Format tanggal tidak valid: {tgl}. Gunakan format YYYY-MM-DD")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Override save untuk handle tanggal_picker"""
        instance = super().save(commit=False)
        
        # Simpan tanggal dari tanggal_picker ke field tanggal
        tanggal_picker = self.cleaned_data.get('tanggal_picker', '').strip()
        instance.tanggal = tanggal_picker
        
        # Set nama_orang dari karyawan untuk backward compatibility
        if instance.karyawan:
            instance.nama_orang = instance.karyawan.nama_lengkap
        
        if commit:
            instance.save()
        
        return instance


# ==============================================================================
# FORM UNTUK CREATE JOB DARI NOTULEN ITEM
# ==============================================================================
class JobFromNotulenForm(forms.Form):
    """
    Form khusus untuk membuat job dari notulen item.
    Menampilkan data notulen sebagai reference (read-only) dan 
    memungkinkan user mengisi detail job dengan multi-date picker.
    """
    
    # ===== DISPLAY-ONLY FIELDS (dari notulen) =====
    pokok_bahasan_notulen = forms.CharField(
        label='Pokok Bahasan (dari Notulen)',
        widget=forms.Textarea(attrs={
            'class': 'form-control-plaintext',
            'rows': 2,
            'readonly': True
        }),
        required=False
    )
    
    pic_notulen = forms.CharField(
        label='PIC Notulen',
        widget=forms.TextInput(attrs={
            'class': 'form-control-plaintext',
            'readonly': True
        }),
        required=False
    )
    
    target_deadline_notulen = forms.DateField(
        label='Target Deadline Notulen (Referensi)',
        widget=forms.DateInput(attrs={
            'class': 'form-control-plaintext',
            'type': 'date',
            'readonly': True
        }),
        required=False
    )
    
    # ===== EDITABLE FIELDS (untuk job) =====
    nama_pekerjaan = forms.CharField(
        label='Nama Pekerjaan',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama job (default dari notulen, bisa diubah)'
        }),
        help_text='Deskripsi singkat job yang akan dibuat'
    )
    
    tipe_job = forms.ChoiceField(
        label='Tipe Pekerjaan',
        choices=Job.TIPE_JOB_CHOICES,
        initial='Daily',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    assigned_to = forms.ModelChoiceField(
        label='Assign ke User',
        queryset=CustomUser.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Pilih user yang bertanggung jawab (dalam hierarchy PIC)',
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
    
    # Multi-date picker untuk jadwal pelaksanaan (Daily Job)
    jadwal_pelaksanaan = forms.CharField(
        label='Jadwal Pelaksanaan',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'jadwal_pelaksanaan_picker',
            'placeholder': 'Pilih tanggal pelaksanaan (flatpickr multi-select)',
            'data-flatpickr': 'true',
            'data-mode': 'multiple'
        }),
        required=False,
        help_text='Untuk Daily Job: pilih satu atau lebih tanggal pelaksanaan'
    )
    
    # Optional fields
    deskripsi = forms.CharField(
        label='Deskripsi / Catatan Tambahan',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Deskripsi detail job dari hasil notulen (opsional)'
        }),
        required=False
    )
    
    prioritas = forms.ChoiceField(
        label='Prioritas',
        choices=[('', '--- Pilih Prioritas ---')] + list(Job.PRIORITAS_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False
    )
    
    fokus = forms.ChoiceField(
        label='Fokus',
        choices=[('', '--- Pilih Fokus ---')] + list(Job.FOKUS_CHOICES),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False
    )
    
    project = forms.ModelChoiceField(
        label='Project (Opsional)',
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        help_text='Pilih project jika job ini bagian dari project'
    )
    
    aset = forms.ModelChoiceField(
        label='Mesin/Sub Mesin (Opsional)',
        queryset=AsetMesin.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        help_text='Pilih mesin/sub-mesin yang terkait job'
    )
    
    def __init__(self, *args, notulen_pic_user=None, allowed_users=None, **kwargs):
        """
        Args:
            notulen_pic_user: CustomUser yang merupakan PIC dari notulen
            allowed_users: List of CustomUser IDs yang boleh di-assign
        """
        super().__init__(*args, **kwargs)
        
        # Filter assigned_to hanya user dalam hierarchy PIC
        if allowed_users:
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(
                id__in=allowed_users,
                is_active=True
            ).order_by('username')
        
        # Filter aset: hanya sub-mesin (level 2)
        self.fields['aset'].queryset = AsetMesin.objects.filter(
            level=2
        ).order_by('nama')
    
    def clean(self):
        cleaned_data = super().clean()
        tipe_job = cleaned_data.get('tipe_job')
        jadwal_pelaksanaan = cleaned_data.get('jadwal_pelaksanaan')
        
        # Validasi: Daily job harus punya jadwal
        if tipe_job == 'Daily' and not jadwal_pelaksanaan:
            self.add_error('jadwal_pelaksanaan', 
                          'Daily Job harus punya jadwal pelaksanaan. '
                          'Pilih minimal satu tanggal di field "Jadwal Pelaksanaan"')
        
        return cleaned_data