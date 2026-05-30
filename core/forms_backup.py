from django import forms
from django.core.exceptions import ValidationError
import os

class DatabaseBackupForm(forms.Form):
    """Form untuk upload database backup file"""
    
    backup_file = forms.FileField(
        label='Pilih File Backup (.sql)',
        help_text='Upload file SQL backup (max 1GB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.sql',
        })
    )
    
    confirm_restore = forms.BooleanField(
        label='Saya yakin ingin restore database (DATA LAMA AKAN HILANG)',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
    
    database_name = forms.CharField(
        label='Nama Database',
        initial='proyek_management_job',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
        })
    )
    
    def clean_backup_file(self):
        file = self.cleaned_data.get('backup_file')
        
        if not file:
            raise ValidationError('Pilih file backup terlebih dahulu')
        
        # Check file extension
        if not file.name.endswith('.sql'):
            raise ValidationError('File harus berformat .sql')
        
        # Check file size (max 1GB)
        if file.size > 1024 * 1024 * 1024:
            raise ValidationError('File terlalu besar (max 1GB)')
        
        return file
    
    def clean_confirm_restore(self):
        confirm = self.cleaned_data.get('confirm_restore')
        
        if not confirm:
            raise ValidationError('Anda harus confirm untuk melanjutkan')
        
        return confirm


class DatabaseManagementForm(forms.Form):
    """Form untuk database management actions"""
    
    ACTIONS = [
        ('backup', 'Backup Database'),
        ('list', 'List Backups'),
        ('check', 'Check Database Health'),
    ]
    
    action = forms.ChoiceField(
        label='Pilih Action',
        choices=ACTIONS,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
