"""
Google Calendar Service Helper
Untuk manage event creation di Google Calendar
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from datetime import datetime, timedelta

# Scopes untuk Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """
    Helper class untuk manage Google Calendar operations
    """
    
    def __init__(self):
        """Initialize Google Calendar service dengan Service Account"""
        try:
            # Load credentials dari JSON file
            self.credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CALENDAR_CREDENTIALS_FILE,
                scopes=SCOPES
            )
            
            # Build Google Calendar API client
            self.service = build('calendar', 'v3', credentials=self.credentials)
            self.calendar_id = settings.GOOGLE_CALENDAR_ID
            
        except Exception as e:
            print(f"Error initializing Google Calendar Service: {str(e)}")
            raise
    
    def create_event(self, nama_orang, tipe_ijin, tanggal_list, deskripsi=None):
        """
        Create event di Google Calendar
        Untuk multiple non-continuous dates, create individual all-day events
        
        Args:
            nama_orang (str): Nama orang yang ijin/cuti
            tipe_ijin (str): "Ijin" atau "Cuti"
            tanggal_list (list): List of date objects atau date strings
            deskripsi (str): Deskripsi tambahan (opsional)
        
        Returns:
            dict: Response dari Google Calendar API (berisi event_id, etc)
            or None jika gagal
        """
        try:
            # Event title selalu "{Nama} cuti" (sesuai requirement)
            event_title = f"{nama_orang} cuti"
            
            # Build description
            description = f"Tipe: {tipe_ijin}"
            if deskripsi:
                description += f"\nKeterangan: {deskripsi}"
            
            # Convert semua tanggal ke date objects dan sort
            tgl_list = []
            for tgl in tanggal_list:
                if isinstance(tgl, str):
                    tgl = datetime.strptime(tgl, '%Y-%m-%d').date()
                tgl_list.append(tgl)
            
            tgl_list.sort()
            
            # Create individual all-day events untuk setiap tanggal
            # (bukan 1 range event)
            created_events = []
            
            for tgl in tgl_list:
                event_body = {
                    'summary': event_title,
                    'description': description,
                    'start': {
                        'date': tgl.isoformat(),
                    },
                    'end': {
                        'date': (tgl + timedelta(days=1)).isoformat(),
                    },
                }
                
                # Create event
                event = self.service.events().insert(
                    calendarId=self.calendar_id,
                    body=event_body
                ).execute()
                
                created_events.append(event)
                print(f"Event created for {tgl}: {event.get('id')}")
            
            # Return object dengan semua event IDs (comma-separated)
            if created_events:
                event_ids = [e.get('id') for e in created_events]
                # Gabung semua IDs dengan koma
                combined_id = ','.join(event_ids)
                # Create response object dengan combined ID
                response = created_events[0].copy()
                response['id'] = combined_id  # Override dengan combined ID
                response['ids'] = event_ids   # Juga simpan list lengkap
                return response
            
            return None
            
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            return None
    
    def get_event(self, event_id):
        """
        Get event details dari Google Calendar
        
        Args:
            event_id (str): Event ID dari Google Calendar
        
        Returns:
            dict: Event details atau None jika tidak ditemukan
        """
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return event
        except Exception as e:
            print(f"Error getting event: {str(e)}")
            return None
    
    def delete_event(self, event_ids):
        """
        Delete event(s) dari Google Calendar
        Bisa single event_id atau comma-separated multiple event IDs
        
        Args:
            event_ids (str): Event ID (single) atau comma-separated IDs (multiple)
        
        Returns:
            bool: True jika semua sukses, False jika ada yang gagal
        """
        try:
            # Parse event_ids (bisa single atau comma-separated)
            ids_list = [eid.strip() for eid in str(event_ids).split(',') if eid.strip()]
            
            success_count = 0
            for event_id in ids_list:
                try:
                    self.service.events().delete(
                        calendarId=self.calendar_id,
                        eventId=event_id
                    ).execute()
                    print(f"Event deleted: {event_id}")
                    success_count += 1
                except Exception as e:
                    print(f"Error deleting event {event_id}: {str(e)}")
            
            # Return True jika semua berhasil
            return success_count == len(ids_list)
            
        except Exception as e:
            print(f"Error in delete_event: {str(e)}")
            return False
    
    def update_event(self, event_id, **kwargs):
        """
        Update event di Google Calendar
        
        Args:
            event_id (str): Event ID
            **kwargs: Field yang ingin di-update (summary, description, etc)
        
        Returns:
            dict: Updated event details atau None jika gagal
        """
        try:
            event = self.get_event(event_id)
            if not event:
                return None
            
            # Update fields
            for key, value in kwargs.items():
                if key in event:
                    event[key] = value
            
            # Update event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            print(f"Event updated: {event_id}")
            return updated_event
            
        except Exception as e:
            print(f"Error updating event: {str(e)}")
            return None


# Convenience function untuk quick access
def get_google_calendar_service():
    """
    Factory function untuk get Google Calendar service
    
    Returns:
        GoogleCalendarService: Initialized service instance
    """
    return GoogleCalendarService()
