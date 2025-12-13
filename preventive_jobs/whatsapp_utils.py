"""
Utilities untuk WhatsApp Integration via Fontte API atau Custom WABot API
"""

import requests
import logging
from django.conf import settings
from django.core import signing
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json

logger = logging.getLogger(__name__)


# ==============================================================================
# WHATSAPP API UTILITIES
# ==============================================================================

class WhatsAppAPI:
    """
    Client untuk WhatsApp API - support Fontte atau Custom WABot.
    Auto-detect berdasarkan settings.
    """
    
    def __init__(self):
        # Check if custom WABot API is configured
        self.use_wabot = hasattr(settings, 'WABOT_API_URL') and settings.WABOT_API_URL
        
        if self.use_wabot:
            self.api_type = 'wabot'
            self.base_url = settings.WABOT_API_URL
            self.api_key = settings.WABOT_API_KEY
            self.headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json',
            }
            logger.info(f"Using WABot API: {self.base_url}")
        else:
            self.api_type = 'fontte'
            self.base_url = settings.FONTTE_API_BASE_URL
            self.token = settings.FONTTE_API_TOKEN
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
            }
            logger.info(f"Using Fontte API: {self.base_url}")
    
    def send_message(self, phone_number, message):
        """
        Kirim pesan WhatsApp ke nomor tertentu.
        
        Args:
            phone_number: str, nomor dalam format 62xxxxxxxx
            message: str, isi pesan
        
        Returns:
            dict: Response dari API
        """
        try:
            # Normalize phone number
            phone = self._normalize_phone(phone_number)
            
            if self.api_type == 'wabot':
                return self._send_via_wabot(phone, message)
            else:
                return self._send_via_fontte(phone, message)
        
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Request error saat kirim WA: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error pada koneksi API'
            }
        except Exception as e:
            logger.error(f"✗ Error saat kirim WA: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Terjadi kesalahan'
            }
    
    def _send_via_wabot(self, phone, message):
        """Send via custom WABot API"""
        try:
            url = f"{self.base_url}/api/external/send-message"
            
            # WABot expects: targetType, target (phone number), message
            payload = {
                "targetType": "personal",
                "target": phone,
                "message": message,
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code in [200, 201]:
                logger.info(f"✓ Pesan WA berhasil dikirim ke {phone} via WABot")
                return {
                    'success': True,
                    'data': response.json() if response.text else {},
                    'message': 'Pesan berhasil dikirim'
                }
            else:
                error_msg = response.text
                logger.error(f"✗ Gagal kirim WA ke {phone} via WABot: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'message': f'Gagal kirim pesan: {response.status_code}'
                }
        
        except Exception as e:
            logger.error(f"✗ WABot error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Error WABot: {str(e)}'
            }
    
    def _send_via_fontte(self, phone, message):
        """Send via Fontte API"""
        try:
            url = f"{self.base_url}/chats/send"
            
            payload = {
                "phone": phone,
                "message": message,
                "secret": False,
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code in [200, 201]:
                logger.info(f"✓ Pesan WA berhasil dikirim ke {phone} via Fontte")
                return {
                    'success': True,
                    'data': response.json(),
                    'message': 'Pesan berhasil dikirim'
                }
            else:
                error_msg = response.text
                logger.error(f"✗ Gagal kirim WA ke {phone} via Fontte: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'message': f'Gagal kirim pesan: {response.status_code}'
                }
        
        except Exception as e:
            logger.error(f"✗ Fontte error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Error Fontte: {str(e)}'
            }
    
    def _normalize_phone(self, phone):
        """
        Normalize nomor telepon ke format 62xxxxxxxx
        """
        # Remove all non-digit characters
        phone_clean = ''.join(filter(str.isdigit, phone))
        
        if phone_clean.startswith('62'):
            return phone_clean
        elif phone_clean.startswith('0'):
            return '62' + phone_clean[1:]
        else:
            return '62' + phone_clean
    
    def test_connection(self):
        """Test koneksi ke API"""
        try:
            if self.api_type == 'wabot':
                # WABot biasanya tidak punya endpoint test, coba dengan dummy send
                return True
            else:
                # Fontte has test endpoint
                url = f"{self.base_url}/auth/test"
                response = requests.get(url, headers=self.headers, timeout=10)
                return response.status_code == 200
        except:
            return False


# Backward compatibility - alias
FontteAPI = WhatsAppAPI


# ==============================================================================
# TOKEN GENERATION & VERIFICATION
# ==============================================================================

def generate_checklist_share_token(execution_id, checklist_result_id):
    """
    Generate unique share token untuk checklist.
    
    Args:
        execution_id: int, ID dari PreventiveJobExecution
        checklist_result_id: int, ID dari ChecklistResult
    
    Returns:
        str: Signed token
    """
    data = {
        'execution_id': execution_id,
        'checklist_result_id': checklist_result_id,
        'timestamp': timezone.now().isoformat(),
    }
    
    token = signing.dumps(
        data,
        salt=settings.PREVENTIVE_SHARE_SIGN_SALT,
        compress=True
    )
    
    return token


def verify_checklist_share_token(token):
    """
    Verify & extract data dari share token.
    
    Args:
        token: str, signed token
    
    Returns:
        dict: Decoded data atau None jika invalid/expired
    """
    try:
        max_age = settings.PREVENTIVE_SHARE_TOKEN_MAX_AGE
        
        data = signing.loads(
            token,
            salt=settings.PREVENTIVE_SHARE_SIGN_SALT,
            max_age=max_age,
        )
        
        return data
    
    except signing.SignatureExpired:
        logger.warning(f"Share token expired: {token}")
        return None
    
    except signing.BadSignature:
        logger.warning(f"Invalid share token: {token}")
        return None
    
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None


# ==============================================================================
# BUILD WHATSAPP SHARE LINK & MESSAGE
# ==============================================================================

def build_share_url(token):
    """
    Build full public URL untuk share link.
    
    Args:
        token: str, share token
    
    Returns:
        str: Full URL
    """
    public_url = settings.DJANGO_PUBLIC_URL.rstrip('/')
    path = f"/preventive/checklist-fill/{token}/"
    return f"{public_url}{path}"


def build_whatsapp_message(execution, checklist_result, share_url, custom_msg=''):
    """
    Build WhatsApp message dengan link.
    
    Args:
        execution: PreventiveJobExecution object
        checklist_result: ChecklistResult object
        share_url: str, full share URL
        custom_msg: str, pesan tambahan dari user
    
    Returns:
        str: Formatted message
    """
    
    job_name = execution.template.nama_pekerjaan
    aset_name = execution.aset.nama if execution.aset else "N/A"
    scheduled_date = execution.scheduled_date.strftime('%d-%m-%Y')
    
    message = f"""
Halo! 👋

Berikut adalah *Checklist Preventive Job* yang perlu Anda isi:

📋 *Nama Job:* {job_name}
🔧 *Aset/Mesin:* {aset_name}
📅 *Tanggal:* {scheduled_date}

Silakan klik link di bawah untuk mengisi checklist:
🔗 {share_url}

⏰ Link ini berlaku selama 7 hari

Terima kasih! 🙏
"""
    
    if custom_msg:
        message += f"\n\n📝 *Catatan:*\n{custom_msg}"
    
    return message.strip()


def shorten_url(long_url):
    """
    Shorten URL menggunakan TinyURL service (gratis, no auth needed).
    
    Args:
        long_url: str, URL panjang yang ingin di-shorten
    
    Returns:
        str: Shortened URL, atau original URL jika gagal
    """
    try:
        import urllib.parse
        # TinyURL API: https://tinyurl.com/api-create.php?url=...
        tinyurl_api = f"https://tinyurl.com/api-create.php?url={urllib.parse.quote(long_url)}"
        response = requests.get(tinyurl_api, timeout=5)
        
        if response.status_code == 200:
            short_url = response.text.strip()
            logger.info(f"✓ URL shortened: {long_url[:50]}... → {short_url}")
            return short_url
        else:
            logger.warning(f"TinyURL service returned {response.status_code}, returning original URL")
            return long_url
    except Exception as e:
        logger.warning(f"Failed to shorten URL: {str(e)}, returning original URL")
        return long_url


def build_whatsapp_share_link_with_text(phone_number, message):
    """
    Build WhatsApp link yang auto-open chat dengan pesan.
    Format: https://wa.me/[PHONE]?text=[MESSAGE]
    
    Args:
        phone_number: str, nomor WA (format 62xxxxxxxx)
        message: str, pesan yang akan dikirim
    
    Returns:
        str: WhatsApp share link
    """
    import urllib.parse
    
    # Normalize phone
    fontte = FontteAPI()
    phone = fontte._normalize_phone(phone_number)
    
    # Encode message
    encoded_msg = urllib.parse.quote(message)
    
    return f"https://wa.me/{phone}?text={encoded_msg}"


# ==============================================================================
# NOTIFICATION HELPERS
# ==============================================================================

def send_checklist_filled_notification(execution, checklist_result, share_log=None):
    """
    Kirim notifikasi ke PIC bahwa checklist sudah diisi.
    
    Args:
        execution: PreventiveJobExecution object
        checklist_result: ChecklistResult object
        share_log: ChecklistShareLog object (optional)
    """
    try:
        from preventive_jobs.models import ChecklistShareLog
        
        pic = execution.template.pic
        job_name = execution.template.nama_pekerjaan
        aset_name = execution.aset.nama if execution.aset else "N/A"
        
        # Tentukan siapa yang isi checklist
        if share_log:
            filled_by = share_log.penerima_nama
        elif checklist_result.diisi_oleh:
            filled_by = checklist_result.diisi_oleh.get_full_name() or checklist_result.diisi_oleh.username
        elif checklist_result.accessed_by_name:
            # For WhatsApp submissions via share link
            filled_by = checklist_result.accessed_by_name
        else:
            filled_by = "Unknown"
        
        message = f"""
🎉 *Checklist Sudah Diisi!*

Job: {job_name}
Aset: {aset_name}
Diisi oleh: {filled_by}
Waktu: {checklist_result.tanggal_pengisian.strftime('%d-%m-%Y %H:%M')}

Status: {checklist_result.status_overall}

Terima kasih! ✅
"""
        
        # Kirim ke PIC jika punya nomor WA
        if pic.nomor_telepon:
            fontte = FontteAPI()
            result = fontte.send_message(pic.nomor_telepon, message)
            
            if result['success']:
                logger.info(f"Notifikasi berhasil dikirim ke PIC {pic.username}")
            else:
                logger.error(f"Gagal kirim notifikasi ke PIC: {result.get('error')}")
        else:
            logger.info(f"PIC {pic.username} tidak punya nomor WA")
    
    except Exception as e:
        logger.error(f"Error send_checklist_filled_notification: {str(e)}")


# ==============================================================================
# PREVIEW HELPERS
# ==============================================================================

def preview_whatsapp_message(phone, message):
    """
    Generate preview untuk WhatsApp message (untuk UI).
    
    Args:
        phone: str, nomor WA
        message: str, pesan
    
    Returns:
        dict: Info untuk preview
    """
    fontte = FontteAPI()
    normalized_phone = fontte._normalize_phone(phone)
    
    return {
        'to': normalized_phone,
        'message': message,
        'wa_link': build_whatsapp_share_link_with_text(normalized_phone, message),
        'length': len(message),
    }
