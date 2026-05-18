"""
Google Sheets Service untuk meeting reminder sync.

Auto-append meeting data ke Google Sheets untuk kemudian di-process oleh GAS.
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Google Sheets API constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Sheet names (harus match dengan GAS code)
SHEET_MEETINGS = "Meetings"


class GoogleSheetsService:
    """
    Service untuk berinteraksi dengan Google Sheets API.
    Untuk meeting reminder auto-sync dari Django ke Sheets.
    """
    
    def __init__(self, credentials_path=None):
        """
        Initialize service dengan credentials.
        
        Args:
            credentials_path: Full path ke JSON credentials file.
                            Jika None, gunakan dari GoogleAPISettings.
        """
        self.service = None
        self.credentials_path = credentials_path
        self._connect()
    
    def _connect(self):
        """
        Connect ke Google Sheets API menggunakan service account.
        """
        try:
            # Determine credentials path
            creds_path = self.credentials_path
            if not creds_path:
                from core.models import GoogleAPISettings
                settings_obj = GoogleAPISettings.get_instance()
                creds_path = settings_obj.google_credentials_path
            
            if not creds_path:
                raise ValueError(
                    "Google credentials path tidak ditemukan. "
                    "Set di GoogleAPISettings atau pass sebagai parameter."
                )
            
            # Convert relative path to absolute if needed
            if not os.path.isabs(creds_path):
                creds_path = os.path.join(settings.BASE_DIR, creds_path)
            
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Credentials file tidak ditemukan: {creds_path}")
            
            # Authenticate
            credentials = Credentials.from_service_account_file(
                creds_path,
                scopes=SCOPES
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info(f"✅ Google Sheets Service connected successfully")
            
        except Exception as e:
            logger.error(f"❌ Error connecting to Google Sheets: {str(e)}")
            raise
    
    def append_meeting_row(self, spreadsheet_id, meeting_data):
        """
        Append meeting row ke Meetings sheet di spreadsheet.
        
        Args:
            spreadsheet_id: ID dari Google Spreadsheet
            meeting_data: Dict dengan keys: no_dokumen, agenda, tanggal, 
                         waktu_mulai, waktu_selesai, lokasi, peserta
        
        Returns:
            Dict dengan result dari append operation
        """
        if not self.service:
            raise ValueError("Google Sheets service tidak terkoneksi")
        
        if not spreadsheet_id:
            raise ValueError("Spreadsheet ID harus diisi")
        
        try:
            # Extract data dari meeting_data dict
            no_dokumen = meeting_data.get('no_dokumen', '')
            agenda = meeting_data.get('agenda', '')
            tanggal = meeting_data.get('tanggal', '')  # format: YYYY-MM-DD
            waktu_mulai = meeting_data.get('waktu_mulai', '')  # format: HH:MM
            waktu_selesai = meeting_data.get('waktu_selesai', '')  # format: HH:MM
            lokasi = meeting_data.get('lokasi', '')
            peserta = meeting_data.get('peserta', '')  # comma-separated
            
            # Format tanggal jika Date object
            if hasattr(tanggal, 'strftime'):
                tanggal = tanggal.strftime('%Y-%m-%d')
            
            # Format waktu jika Time object
            if hasattr(waktu_mulai, 'strftime'):
                waktu_mulai = waktu_mulai.strftime('%H:%M')
            if hasattr(waktu_selesai, 'strftime'):
                waktu_selesai = waktu_selesai.strftime('%H:%M')
            
            # Prepare row: [No_Dokumen, Agenda, Tanggal, Waktu_Mulai, Waktu_Selesai, Lokasi, Peserta, "No"]
            # Col 7 (Sudah_Kirim) = "No" (not yet sent)
            row = [no_dokumen, agenda, tanggal, waktu_mulai, waktu_selesai, lokasi, peserta, "No"]
            
            # Append row ke Meetings sheet
            body = {
                'values': [row]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{SHEET_MEETINGS}!A:H",  # Append ke columns A-H
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"✅ Meeting {no_dokumen} appended to sheet {spreadsheet_id}")
            return result
            
        except HttpError as e:
            logger.error(f"❌ Google Sheets API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Error appending meeting row: {str(e)}")
            raise
    
    def test_connection(self, spreadsheet_id):
        """
        Test connection dengan membaca header dari Meetings sheet.
        
        Args:
            spreadsheet_id: ID dari Google Spreadsheet
        
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f"{SHEET_MEETINGS}!A1:H1"
            ).execute()
            
            values = result.get('values', [])
            if values:
                logger.info(f"✅ Test connection successful. Headers: {values[0]}")
                return True
            else:
                logger.warning(f"⚠️ Sheet {SHEET_MEETINGS} is empty or headers not found")
                return False
                
        except HttpError as e:
            logger.error(f"❌ Test connection failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during test: {str(e)}")
            return False
    
    def get_spreadsheet_id_from_url(self, url):
        """
        Extract spreadsheet ID dari Google Sheets URL.
        
        Args:
            url: URL dari Google Sheets (misal: https://docs.google.com/spreadsheets/d/ABC123/edit)
        
        Returns:
            str: Spreadsheet ID atau None jika invalid
        """
        try:
            # Format: https://docs.google.com/spreadsheets/d/{ID}/edit
            if 'docs.google.com/spreadsheets/d/' in url:
                parts = url.split('docs.google.com/spreadsheets/d/')
                if len(parts) > 1:
                    sheet_id = parts[1].split('/')[0]
                    return sheet_id
            return None
        except Exception as e:
            logger.error(f"❌ Error extracting spreadsheet ID: {str(e)}")
            return None


def get_sheets_service(credentials_path=None):
    """
    Convenience function untuk get GoogleSheetsService instance.
    
    Args:
        credentials_path: Optional path ke credentials JSON
    
    Returns:
        GoogleSheetsService instance atau None jika error
    """
    try:
        return GoogleSheetsService(credentials_path=credentials_path)
    except Exception as e:
        logger.error(f"❌ Failed to initialize sheets service: {str(e)}")
        return None
