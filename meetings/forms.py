from django import forms
from django.contrib.auth import get_user_model
from .models import Meeting, MeetingPeserta, NotulenItem

User = get_user_model()


class MeetingForm(forms.ModelForm):
    """Form untuk create/edit Meeting"""
    peserta = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'style': 'display: none;'}),
        required=False,
        label='Peserta Internal'
    )
    
    class Meta:
        model = Meeting
        fields = ['tanggal_meeting', 'jam_mulai', 'jam_selesai', 'tempat', 'agenda', 'notes']
        widgets = {
            'tanggal_meeting': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'jam_mulai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}, format='%H:%M'),
            'jam_selesai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}, format='%H:%M'),
            'tempat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lokasi meeting'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Agenda meeting'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Catatan tambahan'}),
        }
    
    def clean(self):
        """Validasi jam_selesai > jam_mulai"""
        cleaned_data = super().clean()
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        
        if jam_mulai and jam_selesai:
            if jam_selesai <= jam_mulai:
                raise forms.ValidationError('Jam selesai harus lebih besar dari jam mulai')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            # Save M2M peserta
            peserta = self.cleaned_data.get('peserta', [])
            for user in peserta:
                MeetingPeserta.objects.get_or_create(
                    meeting=instance,
                    peserta=user,
                    defaults={'nama': user.get_full_name() or user.username}
                )
        
        return instance


class NotulenItemForm(forms.ModelForm):
    """Form untuk create/edit NotulenItem"""
    pic = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='PIC (Person In Charge)'
    )
    
    class Meta:
        model = NotulenItem
        fields = ['pokok_bahasan', 'tanggapan', 'pic', 'target_deadline']
        widgets = {
            'pokok_bahasan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hasil diskusi / keputusan'
            }),
            'tanggapan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Detail / penjelasan (optional)'
            }),
            'target_deadline': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class MeetingPesertaStatusForm(forms.ModelForm):
    """Form untuk update status kehadiran peserta (AJAX)"""
    class Meta:
        model = MeetingPeserta
        fields = ['status_kehadiran', 'catatan']
        widgets = {
            'status_kehadiran': forms.Select(attrs={'class': 'form-select'}),
            'catatan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan (optional)'
            }),
        }


class PresensiExternalForm(forms.ModelForm):
    """Form untuk presensi external via QR code (public form)"""
    
    # Explicit field definitions untuk control requirement
    nama = forms.CharField(
        label='Nama Lengkap',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nama lengkap Anda',
            'autocomplete': 'name'
        })
    )
    
    nik = forms.CharField(
        label='NIK / No. ID',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'NIK Karyawan (opsional)',
            'autocomplete': 'off',
            'maxlength': '20'
        })
    )
    
    bagian = forms.CharField(
        label='Divisi / Bagian',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan divisi/bagian Anda',
            'autocomplete': 'organization'
        })
    )
    
    class Meta:
        model = MeetingPeserta
        fields = ['nama', 'nik', 'bagian']
    
    def clean_nama(self):
        """Validasi nama tidak boleh kosong"""
        nama = self.cleaned_data.get('nama')
        if not nama or len(nama.strip()) == 0:
            raise forms.ValidationError('Nama tidak boleh kosong')
        return nama.strip()
    
    def clean_nik(self):
        """Validasi NIK - bebas format, hanya trim whitespace"""
        nik = self.cleaned_data.get('nik')
        if nik:
            # Just trim whitespace, jangan enforce format
            return nik.strip()
        return nik
    
    def clean(self):
        """Validasi duplicate entry"""
        cleaned_data = super().clean()
        
        # Get meeting from context (will be passed by view)
        meeting = getattr(self, 'meeting', None)
        nik = cleaned_data.get('nik')
        
        if meeting and nik:
            # Check jika sudah ada entry dengan NIK yang sama di meeting ini
            existing = MeetingPeserta.objects.filter(
                meeting=meeting,
                nik=nik,
                tipe_peserta='external'
            ).exists()
            
            if existing:
                raise forms.ValidationError('Anda sudah absen di meeting ini!')
        
        return cleaned_data


# ==============================================================================
# CONFIGURATION FORMS UNTUK MEETING REMINDER SETUP
# ==============================================================================

class DepartemenGoogleSettingsForm(forms.Form):
    """
    Form untuk konfigurasi Google Sheets ID per Departemen.
    Field: google_sheet_id
    """
    google_sheet_id = forms.CharField(
        label='Google Spreadsheet ID (Meeting Reminder)',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Copy dari URL: docs.google.com/spreadsheets/d/{ID}/edit',
            'pattern': '[a-zA-Z0-9-_]+',
        }),
        help_text='Copy ID dari URL spreadsheet. Contoh: 1kzzz_ABC123xyz'
    )
    
    def clean_google_sheet_id(self):
        """Validate spreadsheet ID format"""
        sheet_id = self.cleaned_data.get('google_sheet_id', '').strip()
        
        if not sheet_id:
            raise forms.ValidationError('Spreadsheet ID tidak boleh kosong')
        
        # Check format: alphanumeric, dash, underscore only
        import re
        if not re.match(r'^[a-zA-Z0-9\-_]+$', sheet_id):
            raise forms.ValidationError(
                'Spreadsheet ID hanya boleh mengandung: A-Z, 0-9, dash (-), underscore (_)'
            )
        
        # Optional: Can add actual validation dengan coba connect ke Google Sheets
        # Tapi untuk saat ini skip
        
        return sheet_id


class GoogleAPISettingsForm(forms.Form):
    """
    Form untuk global Google API settings.
    Fields: fonnte_api_token, reminder_send_time
    """
    fonnte_api_token = forms.CharField(
        label='Fonnte API Token',
        max_length=500,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Paste Fonnte API token dari https://dashboard.fonnte.com',
        }),
        help_text='Token dari Fonnte untuk WhatsApp API'
    )
    
    reminder_send_time = forms.TimeField(
        label='Waktu Kirim Reminder',
        required=True,
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
        }, format='%H:%M'),
        initial='08:00',
        help_text='Jam berapa reminder meeting dikirim setiap hari (format HH:MM)'
    )
    
    google_credentials_path = forms.CharField(
        label='Path ke Google Credentials JSON (Opsional)',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contoh: JSON GCP/credentials.json',
        }),
        help_text='Path relatif dari BASE_DIR. Default: JSON GCP/credentials.json'
    )
    
    def clean_fonnte_api_token(self):
        """Validate token tidak kosong"""
        token = self.cleaned_data.get('fonnte_api_token', '').strip()
        if not token:
            raise forms.ValidationError('Fonnte API Token tidak boleh kosong')
        return token
    
    def clean_reminder_send_time(self):
        """Validate time format"""
        send_time = self.cleaned_data.get('reminder_send_time')
        if not send_time:
            raise forms.ValidationError('Waktu kirim tidak boleh kosong')
        return send_time

