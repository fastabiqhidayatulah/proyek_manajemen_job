import openpyxl
from django.core.exceptions import ValidationError
from .models import Barang, StockLevel


class BarangImporter:
    """Handle Excel import untuk Barang"""
    
    REQUIRED_COLUMNS = ['Nama Barang', 'Kategori']
    OPTIONAL_COLUMNS = ['Spesifikasi', 'Lokasi Penyimpanan', 'Stok Awal']
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.workbook = None
        self.worksheet = None
        self.errors = []
        self.success_count = 0
        self.failed_rows = []
    
    def parse_file(self):
        """Parse Excel file"""
        try:
            self.workbook = openpyxl.load_workbook(self.file_path)
            self.worksheet = self.workbook.active
            return True
        except Exception as e:
            self.errors.append(f"Error membaca file Excel: {str(e)}")
            return False
    
    def validate_headers(self):
        """Validate header row"""
        headers = []
        for cell in self.worksheet[1]:
            if cell.value:
                headers.append(str(cell.value).strip())
        
        # Check required columns
        for required_col in self.REQUIRED_COLUMNS:
            if required_col not in headers:
                self.errors.append(f"Kolom '{required_col}' tidak ditemukan. Kolom wajib: {', '.join(self.REQUIRED_COLUMNS)}")
                return False
        
        return True
    
    def get_column_index(self, column_name):
        """Get column index by name"""
        for idx, cell in enumerate(self.worksheet[1], 1):
            if cell.value and str(cell.value).strip() == column_name:
                return idx
        return None
    
    def import_data(self):
        """Import data from Excel"""
        if not self.parse_file():
            return False
        
        if not self.validate_headers():
            return False
        
        # Get column indices
        nama_idx = self.get_column_index('Nama Barang')
        kategori_idx = self.get_column_index('Kategori')
        spek_idx = self.get_column_index('Spesifikasi')
        lokasi_idx = self.get_column_index('Lokasi Penyimpanan')
        stok_idx = self.get_column_index('Stok Awal')
        
        # Get valid kategori values
        valid_kategori = dict(Barang.CATEGORY_CHOICES)
        
        # Process rows (skip header)
        for row_num, row in enumerate(self.worksheet.iter_rows(min_row=2, values_only=False), start=2):
            try:
                # Get values
                nama = row[nama_idx - 1].value
                kategori = row[kategori_idx - 1].value
                spek = row[spek_idx - 1].value if spek_idx else None
                lokasi = row[lokasi_idx - 1].value if lokasi_idx else None
                stok = row[stok_idx - 1].value if stok_idx else 0
                
                # Validate nama
                if not nama or str(nama).strip() == '':
                    self.failed_rows.append({
                        'row': row_num,
                        'error': 'Nama Barang tidak boleh kosong'
                    })
                    continue
                
                nama = str(nama).strip()
                
                # Validate kategori
                if not kategori:
                    self.failed_rows.append({
                        'row': row_num,
                        'error': 'Kategori tidak boleh kosong'
                    })
                    continue
                
                kategori = str(kategori).strip().lower()
                
                # Check if kategori valid
                if kategori not in valid_kategori:
                    valid_options = ', '.join(dict(Barang.CATEGORY_CHOICES).keys())
                    self.failed_rows.append({
                        'row': row_num,
                        'error': f"Kategori '{kategori}' tidak valid. Pilih: {valid_options}"
                    })
                    continue
                
                # Validate stok (must be number)
                try:
                    stok = int(stok) if stok else 0
                    if stok < 0:
                        stok = 0
                except (ValueError, TypeError):
                    self.failed_rows.append({
                        'row': row_num,
                        'error': f"Stok harus berupa angka, dapat '{stok}'"
                    })
                    continue
                
                # Create Barang
                barang = Barang.objects.create(
                    nama=nama,
                    kategori=kategori,
                    spesifikasi=spek,
                    lokasi_penyimpanan=lokasi,
                    status='active'
                )
                
                # Create StockLevel
                StockLevel.objects.create(
                    barang=barang,
                    qty=stok
                )
                
                self.success_count += 1
            
            except Exception as e:
                self.failed_rows.append({
                    'row': row_num,
                    'error': str(e)
                })
        
        return True
    
    def get_result(self):
        """Get import result"""
        return {
            'success': self.success_count,
            'failed': len(self.failed_rows),
            'errors': self.errors,
            'failed_rows': self.failed_rows
        }
