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
    
    class Meta:
        model = DetailPeminjaman
        fields = ['tool', 'qty_pinjam', 'kondisi_pinjam']
        widgets = {
            'tool': forms.Select(attrs={'class': 'form-control'}),
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
        label='Nama Peminjam'
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


# Formset untuk multiple detail peminjaman
DetailPeminjamanFormSet = inlineformset_factory(
    Peminjaman,
    DetailPeminjaman,
    form=DetailPeminjamanForm,
    extra=1,
    can_delete=True
)


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
