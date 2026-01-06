from django import forms
from .models import Barang, StockLevel


class BarangForm(forms.ModelForm):
    """Form untuk create/edit barang"""
    
    class Meta:
        model = Barang
        fields = ['kategori', 'nama', 'spesifikasi', 'lokasi_penyimpanan', 'status']
        widgets = {
            'kategori': forms.Select(attrs={
                'class': 'form-select',
            }),
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama barang'
            }),
            'spesifikasi': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi/spesifikasi teknis'
            }),
            'lokasi_penyimpanan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rak A1, Bin 3, dll'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class StockUpdateForm(forms.ModelForm):
    """Form untuk update stok"""
    
    keterangan = forms.CharField(
        required=False,
        label='Keterangan/Alasan Update',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Optional: Alasan update stok (misal: service selesai, pemakaian maintenance, dll)'
        })
    )
    
    class Meta:
        model = StockLevel
        fields = ['qty']
        widgets = {
            'qty': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jumlah stok baru',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qty'].label = 'Stok Baru'

class BarangImportForm(forms.Form):
    """Form untuk import barang dari Excel"""
    
    file = forms.FileField(
        label='File Excel (.xlsx)',
        required=True,
        help_text='Format: Excel dengan kolom: Nama Barang, Kategori, Spesifikasi, Lokasi Penyimpanan, Stok Awal',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('Format file harus .xlsx atau .xls')
            
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Ukuran file maksimal 5MB')
        
        return file