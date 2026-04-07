"""Fonnte WA API Service - Handle WA message sending via Fonnte API

Fonnte API Format:
- POST: https://api.fonnte.com/send
- Auth: Authorization: {token}
- Body: form-data (target, message, countryCode optional)

Reference: https://fonnte.com/docs
"""

import requests
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


class FonteService:
    """
    Service untuk mengirim WA message via Fonnte API.
    
    Dokumentasi: https://fonnte.com/docs
    
    Usage:
        fonnte = FonteService(fonte_settings)
        response = fonnte.send_message(
            target='62812XXXXXX',  # atau 08123456789
            message='Hello World'
        )
    """
    
    API_URL = 'https://api.fonnte.com/send'
    
    def __init__(self, fonte_settings):
        """
        Initialize Fonnte service dengan settings.
        
        Args:
            fonte_settings: FonnteSettings instance (dari core.models)
        
        Raises:
            ValueError: Jika settings tidak valid
        """
        if not fonte_settings:
            raise ValueError("FonnteSettings is required")
        
        self.settings = fonte_settings
        self.token = fonte_settings.token
        self.country_code = fonte_settings.country_code
        self.timeout = 10
        
        if not self.token:
            raise ValueError("Fonnte token tidak ditemukan")
    
    def get_headers(self):
        """Return HTTP headers untuk Fonnte API"""
        return {
            'Authorization': self.token
        }
    
    def send_message(self, target, message):
        """
        Send WA message ke nomor HP via Fonnte API.
        
        Args:
            target (str): Nomor HP (format: 08123456789 atau 62812XXXXXX)
            message (str): Isi pesan WA
        
        Returns:
            dict: Response dari Fonnte API dengan keys:
                - 'success': bool
                - 'message_id': str (jika berhasil)
                - 'error': str (jika gagal)
                - 'status_code': int
                - 'raw_response': dict
        
        Example:
            >>> response = fontte.send_message(
            ...     target='08123456789',
            ...     message='Reminder: Meeting esok jam 10:00'
            ... )
            >>> if response['success']:
            ...     print(f"Message sent: {response['message_id']}")
        """
        
        # Validation
        if not self._validate_phone(target):
            return {
                'success': False,
                'error': f'Invalid phone number format: {target}',
                'status_code': 400
            }
        
        if not message or len(message.strip()) == 0:
            return {
                'success': False,
                'error': 'Message cannot be empty',
                'status_code': 400
            }
        
        # Normalize phone number
        target_normalized = self._normalize_phone(target)
        
        # Prepare payload (form-data)
        payload = {
            'target': target_normalized,
            'message': message,
            'countryCode': self.country_code
        }
        
        try:
            response = requests.post(
                self.API_URL,
                data=payload,  # form-data, bukan JSON
                headers=self.get_headers(),
                timeout=self.timeout
            )
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = {'raw': response.text}
            
            # Check status
            if response.status_code in [200, 201]:
                message_id = response_data.get('data', {}).get('message_id') or \
                             response_data.get('message_id') or \
                             response_data.get('id')
                logger.info(
                    f'[Fonnte] Message sent to {target_normalized}. '
                    f'Message ID: {message_id}. Status: {response.status_code}'
                )
                return {
                    'success': True,
                    'message_id': message_id,
                    'status_code': response.status_code,
                    'raw_response': response_data
                }
            else:
                error_msg = response_data.get('message') or response_data.get('error') or 'Unknown error'
                logger.warning(
                    f'[Fonnte] Failed to send to {target_normalized}. '
                    f'Status: {response.status_code}. Error: {error_msg}'
                )
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code,
                    'raw_response': response_data
                }
        
        except requests.exceptions.Timeout:
            error_msg = f'Request timeout ({self.timeout}s)'
            logger.error(f'[Fonnte] {error_msg} for {target_normalized}')
            return {
                'success': False,
                'error': error_msg,
                'status_code': 408
            }
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f'Connection error: {str(e)}'
            logger.error(f'[Fonnte] {error_msg}')
            return {
                'success': False,
                'error': error_msg,
                'status_code': 503
            }
        
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logger.exception(f'[Fonnte] {error_msg}')
            return {
                'success': False,
                'error': error_msg,
                'status_code': 500
            }
    
    def send_bulk_messages(self, recipients_messages):
        """
        Send multiple WA messages (with delay to avoid rate limiting).
        
        Args:
            recipients_messages (list): List of dicts
                [
                    {'target': '08123456789', 'message': 'Hello 1'},
                    {'target': '08129876543', 'message': 'Hello 2'},
                    ...
                ]
        
        Returns:
            dict: Summary of bulk send
                {
                    'total': int,
                    'sent': int,
                    'failed': int,
                    'results': [
                        {'target': '...', 'success': bool, 'message_id': '...', ...}
                    ]
                }
        """
        import time
        
        results = {
            'total': len(recipients_messages),
            'sent': 0,
            'failed': 0,
            'results': []
        }
        
        for idx, recipient in enumerate(recipients_messages):
            target = recipient.get('target')
            message = recipient.get('message')
            
            if not target or not message:
                results['failed'] += 1
                results['results'].append({
                    'target': target,
                    'success': False,
                    'error': 'Missing target or message'
                })
                continue
            
            # Send message
            response = self.send_message(target, message)
            
            if response['success']:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            # Add to results
            results['results'].append({
                'target': target,
                'message_id': response.get('message_id'),
                **response
            })
            
            # Delay antara requests (avoid rate limiting) - 0.5 detik
            if idx < len(recipients_messages) - 1:
                time.sleep(0.5)
        
        logger.info(
            f'[Fonnte] Bulk send completed. '
            f'Total: {results["total"]}, Sent: {results["sent"]}, Failed: {results["failed"]}'
        )
        
        return results
    
    def _validate_phone(self, phone_number):
        """
        Validate phone number format.
        
        Valid formats:
        - 08123456789 (format lokal)
        - 628123456789 (format internasional)
        - Min 10 digits, max 15 digits
        
        Args:
            phone_number (str): Phone number to validate
        
        Returns:
            bool: True jika valid
        """
        if not isinstance(phone_number, str):
            return False
        
        # Remove whitespace & special chars
        phone_clean = ''.join(filter(str.isdigit, phone_number))
        
        # Check length (valid Indonesia: 10-15 digits)
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            return False
        
        # Check start digit (0 atau 62)
        if not (phone_clean.startswith('0') or phone_clean.startswith('62')):
            return False
        
        return True
    
    def _normalize_phone(self, phone_number):
        """
        Normalize phone number ke format Fonnte (lokal atau internasional).
        
        Fonnte accept both 08123456789 dan 628123456789.
        Akan normalize sesuai input tapi hapus leading zero jika ada.
        
        Args:
            phone_number (str): Phone number to normalize
        
        Returns:
            str: Normalized phone number
        """
        # Remove whitespace & special chars
        phone_clean = ''.join(filter(str.isdigit, phone_number))
        
        # Return as-is (Fonnte support both lokal & internasional)
        return phone_clean
    
    def test_connection(self):
        """
        Test connection ke Fonnte API.
        
        Returns:
            bool: True jika connection OK
        """
        try:
            # Test dengan simple ping - kirim pesan test
            payload = {
                'target': '628123456789',  # Dummy number
                'message': 'Test',
                'countryCode': self.country_code
            }
            response = requests.post(
                self.API_URL,
                data=payload,  # form-data, bukan JSON!
                headers=self.get_headers(),
                timeout=5
            )
            # 200/201 = success, 400+ = API responds but validation error (still OK untuk test)
            # < 500 = API is reachable
            return response.status_code < 500
        except requests.exceptions.Timeout:
            logger.error(f'[Fonnte] Connection test timeout')
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f'[Fonnte] Connection test failed - cannot reach API')
            return False
        except Exception as e:
            logger.error(f'[Fonnte] Connection test error: {str(e)}')
            return False


def get_fonnte_service(departemen):
    """
    Helper function untuk get Fonnte service untuk departemen.
    
    Args:
        departemen: Departemen instance
    
    Returns:
        FonteService or None jika tidak ada FonnteSettings
    
    Example:
        >>> from core.fontte_service import get_fonnte_service
        >>> fonnte = get_fonnte_service(user.departemen)
        >>> if fonnte:
        ...     response = fonnte.send_message(phone, message)
    """
    try:
        from core.models import FonnteSettings
        settings = FonnteSettings.objects.get(
            departemen=departemen,
            is_active=True
        )
        return FonteService(settings)
    except:
        return None
