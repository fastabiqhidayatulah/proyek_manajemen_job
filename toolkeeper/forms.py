from django import forms
from django.forms import inlineformset_factory
from .models import Tool, Peminjaman, DetailPeminjaman, Pengembalian, DetailPengembalian
from core.models import Karyawan


class ToolForm(forms.ModelForm):
    """Form untuk create/edit Tool"""
    
    class Meta:
        model = Tool
        fields = ['nama', 'spesifikasi', 'jumlah_total']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama alat/tools'
            }),
            'spesifikasi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Spesifikasi detail'
            }),
            'jumlah_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah stok awal'
            }),
        }


class ToolImportForm(forms.Form):
    """Form untuk import tools dari Excel"""
    excel_file = forms.FileField(
        label='File Excel (.xlsx, .xls)',
        help_text='Upload file Excel dengan data alat',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
        })
    )


class DetailPeminjamanForm(forms.ModelForm):
    """Form untuk detail peminjaman"""
    
    tool = forms.ModelChoiceField(
        queryset=Tool.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False  # Allow empty rows (akan di-filter di view)
    )
    
    class Meta:
        model = DetailPeminjaman
        fields = ['tool', 'qty_pinjam', 'kondisi_pinjam']
        widgets = {
            'qty_pinjam': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah'
            }),
            'kondisi_pinjam': forms.Select(attrs={'class': 'form-control'}),
        }


class PeminjamanForm(forms.ModelForm):
    """Form untuk create peminjaman"""
    
    peminjam = forms.ModelChoiceField(
        queryset=Karyawan.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Nama Peminjam',
        required=False  # Validasi di JavaScript karena field hidden
    )
    
    class Meta:
        model = Peminjaman
        fields = ['peminjam', 'tgl_rencana_kembali', 'catatan']
        widgets = {
            'tgl_rencana_kembali': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'placeholder': 'Tanggal & jam rencana kembali'
            }),
            'catatan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan tambahan'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        peminjam = cleaned_data.get('peminjam')
        
        if not peminjam:
            self.add_error('peminjam', 'Pilih peminjam terlebih dahulu')
        
        return cleaned_data


# Formset untuk multiple detail peminjaman
DetailPeminjamanFormSet = inlineformset_factory(
    Peminjaman,
    DetailPeminjaman,
    form=DetailPeminjamanForm,
    extra=1,
    can_delete=True,
    validate_min=False  # Allow empty rows
)


# Custom formset dengan validasi stok
class DetailPeminjamanFormSetWithStockValidation(DetailPeminjamanFormSet):
    """Formset dengan validasi stok alat yang dipinjam"""
    
    def clean(self):
        super().clean()
        
        # Skip validation jika form error sudah ada
        if self.non_form_errors():
            return
        
        # Cek setiap tool yang dipinjam
        for form in self.forms:
            if form.cleaned_data.get('tool') and not form.cleaned_data.get('DELETE'):
                tool = form.cleaned_data['tool']
                qty_pinjam = form.cleaned_data.get('qty_pinjam', 0)
                
                # Get stok tersedia
                stok_tersedia = tool.jumlah_tersedia
                
                if qty_pinjam > stok_tersedia:
                    form.add_error('qty_pinjam', 
                        f'Stok "{tool.nama}" tidak mencukupi. '
                        f'Diminta: {qty_pinjam}, Tersedia: {stok_tersedia}')



class DetailPengembalianForm(forms.ModelForm):
    """Form untuk detail pengembalian"""
    
    class Meta:
        model = DetailPengembalian
        fields = ['tool', 'qty_kembali', 'kondisi_kembali']
        widgets = {
            'tool': forms.Select(attrs={'class': 'form-control'}),
            'qty_kembali': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah'
            }),
            'kondisi_kembali': forms.Select(attrs={'class': 'form-control'}),
        }


class PengembalianForm(forms.ModelForm):
    """Form untuk create pengembalian"""
    
    dikembalikan_oleh = forms.ModelChoiceField(
        queryset=Karyawan.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Dikembalikan Oleh'
    )
    
    class Meta:
        model = Pengembalian
        fields = ['dikembalikan_oleh', 'catatan']
        widgets = {
            'catatan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan (kondisi alat, kerusakan, dll)'
            }),
        }


# Formset untuk multiple detail pengembalian
DetailPengembalianFormSet = inlineformset_factory(
    Pengembalian,
    DetailPengembalian,
    form=DetailPengembalianForm,
    extra=1,
    can_delete=True
)
