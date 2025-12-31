"""Calendar integration service for interview scheduling."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid


class CalendarProvider(str, Enum):
    """Supported calendar providers."""
    GOOGLE = "google"
    OUTLOOK = "outlook"
    OFFICE365 = "office365"


class CalendarService:
    """Service for calendar integration and meeting scheduling."""

    def __init__(self):
        # In production, load credentials for calendar APIs
        self.google_credentials = None
        self.outlook_credentials = None

    def create_meeting(
        self,
        title: str,
        start_time: datetime,
        duration_minutes: int,
        attendees: List[str],
        description: Optional[str] = None,
        location: Optional[str] = None,
        meeting_link: Optional[str] = None,
        organizer_email: str = "recruiter@company.com",
        provider: CalendarProvider = CalendarProvider.GOOGLE
    ) -> Dict[str, Any]:
        """
        Create a calendar meeting/event.

        Args:
            title: Meeting title
            start_time: Start datetime
            duration_minutes: Duration in minutes
            attendees: List of attendee emails
            description: Meeting description
            location: Physical location or "Video Call"
            meeting_link: Video call link
            organizer_email: Organizer email
            provider: Calendar provider

        Returns:
            Created event details
        """
        end_time = start_time + timedelta(minutes=duration_minutes)

        event_data = {
            "summary": title,
            "description": description or "",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
            "attendees": [{"email": email} for email in attendees],
            "organizer": {"email": organizer_email},
            "conferenceData": self._create_video_conference(meeting_link) if meeting_link else None,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},  # 1 day before
                    {"method": "popup", "minutes": 60},  # 1 hour before
                ]
            }
        }

        if provider == CalendarProvider.GOOGLE:
            return self._create_google_event(event_data)
        elif provider in [CalendarProvider.OUTLOOK, CalendarProvider.OFFICE365]:
            return self._create_outlook_event(event_data)
        else:
            raise ValueError(f"Unsupported calendar provider: {provider}")

    def _create_google_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Google Calendar event."""
        # In production, use Google Calendar API
        # from googleapiclient.discovery import build
        # service = build('calendar', 'v3', credentials=self.google_credentials)
        # event = service.events().insert(calendarId='primary', body=event_data).execute()

        # Mock implementation
        event_id = f"google_{uuid.uuid4().hex[:16]}"

        return {
            "event_id": event_id,
            "provider": "google",
            "html_link": f"https://calendar.google.com/event?eid={event_id}",
            "status": "created",
            "created_at": datetime.now().isoformat()
        }

    def _create_outlook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Outlook/Office365 calendar event."""
        # In production, use Microsoft Graph API
        # Mock implementation
        event_id = f"outlook_{uuid.uuid4().hex[:16]}"

        return {
            "event_id": event_id,
            "provider": "outlook",
            "web_link": f"https://outlook.office365.com/owa/?itemid={event_id}",
            "status": "created",
            "created_at": datetime.now().isoformat()
        }

    def _create_video_conference(self, meeting_link: Optional[str]) -> Dict[str, Any]:
        """Create video conference data."""
        if meeting_link:
            return {
                "entryPoints": [
                    {
                        "entryPointType": "video",
                        "uri": meeting_link,
                        "label": "Join Video Call"
                    }
                ]
            }
        return {}

    def get_free_busy(
        self,
        emails: List[str],
        start_time: datetime,
        end_time: datetime,
        provider: CalendarProvider = CalendarProvider.GOOGLE
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Get free/busy information for users.

        Args:
            emails: List of user emails
            start_time: Start of time range
            end_time: End of time range
            provider: Calendar provider

        Returns:
            Dict mapping emails to busy time slots
        """
        # In production, call calendar API
        # Mock response
        free_busy = {}

        for email in emails:
            # Mock some busy times
            free_busy[email] = [
                {
                    "start": (start_time + timedelta(hours=2)).isoformat(),
                    "end": (start_time + timedelta(hours=3)).isoformat()
                },
                {
                    "start": (start_time + timedelta(hours=5)).isoformat(),
                    "end": (start_time + timedelta(hours=6)).isoformat()
                }
            ]

        return free_busy

    def find_available_slots(
        self,
        attendee_emails: List[str],
        duration_minutes: int,
        search_start: datetime,
        search_end: datetime,
        business_hours_only: bool = True,
        timezone: str = "UTC"
    ) -> List[datetime]:
        """
        Find available time slots for all attendees.

        Args:
            attendee_emails: List of attendee emails
            duration_minutes: Required duration
            search_start: Start of search range
            search_end: End of search range
            business_hours_only: Only return business hour slots
            timezone: Timezone for results

        Returns:
            List of available start times
        """
        # Get free/busy for all attendees
        free_busy = self.get_free_busy(attendee_emails, search_start, search_end)

        # Find common free time
        available_slots = []

        current = search_start
        while current < search_end:
            slot_end = current + timedelta(minutes=duration_minutes)

            # Check if this slot works for everyone
            if self._is_slot_available(current, slot_end, free_busy, business_hours_only):
                available_slots.append(current)

            # Move to next 30-minute slot
            current += timedelta(minutes=30)

        return available_slots[:10]  # Return top 10 slots

    def _is_slot_available(
        self,
        start: datetime,
        end: datetime,
        free_busy: Dict[str, List[Dict[str, str]]],
        business_hours_only: bool
    ) -> bool:
        """Check if a time slot is available for all attendees."""
        # Check business hours
        if business_hours_only:
            if start.hour < 9 or start.hour >= 17:  # 9 AM - 5 PM
                return False

            if start.weekday() >= 5:  # Skip weekends
                return False

        # Check all attendees
        for email, busy_times in free_busy.items():
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy["start"])
                busy_end = datetime.fromisoformat(busy["end"])

                # Check for overlap
                if start < busy_end and end > busy_start:
                    return False

        return True

    def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any],
        provider: CalendarProvider = CalendarProvider.GOOGLE
    ) -> Dict[str, Any]:
        """Update an existing calendar event."""
        # In production, call calendar API to update
        return {
            "event_id": event_id,
            "provider": provider.value,
            "updated": True,
            "updated_at": datetime.now().isoformat()
        }

    def cancel_event(
        self,
        event_id: str,
        provider: CalendarProvider = CalendarProvider.GOOGLE,
        send_updates: bool = True
    ) -> Dict[str, Any]:
        """Cancel a calendar event."""
        # In production, call calendar API to delete/cancel
        return {
            "event_id": event_id,
            "provider": provider.value,
            "cancelled": True,
            "cancelled_at": datetime.now().isoformat(),
            "notifications_sent": send_updates
        }

    def generate_zoom_link(self, title: str, start_time: datetime, duration_minutes: int) -> str:
        """Generate Zoom meeting link."""
        # In production, use Zoom API
        # Mock implementation
        meeting_id = uuid.uuid4().hex[:10]
        return f"https://zoom.us/j/{meeting_id}"

    def generate_google_meet_link(self) -> str:
        """Generate Google Meet link."""
        # In production, request through Google Calendar API when creating event
        # Mock implementation
        code = uuid.uuid4().hex[:10]
        return f"https://meet.google.com/{code}"

    def generate_teams_link(self, title: str, start_time: datetime) -> str:
        """Generate Microsoft Teams meeting link."""
        # In production, use Microsoft Graph API
        # Mock implementation
        code = uuid.uuid4().hex[:12]
        return f"https://teams.microsoft.com/l/meetup-join/{code}"
