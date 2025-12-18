"""Calendar tool for interview scheduling."""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Type, ClassVar
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import json


class CalendarInput(BaseModel):
    """Input schema for calendar tool."""
    action: str = Field(
        description="Action to perform: 'get_slots', 'book', 'cancel'"
    )
    candidate_name: str = Field(
        default="",
        description="Name of the candidate (required for booking)"
    )
    duration_minutes: int = Field(
        default=60,
        description="Interview duration in minutes"
    )
    preferred_date: Optional[str] = Field(
        default=None,
        description="Preferred date in YYYY-MM-DD format"
    )
    slot_id: Optional[str] = Field(
        default=None,
        description="Slot ID for booking or cancellation"
    )


class CalendarTool(BaseTool):
    """Mock calendar tool for interview scheduling."""

    name: str = "schedule_interview"
    description: str = """
    Calendar tool for scheduling interviews.

    Actions:
    - 'get_slots': Get available interview slots
    - 'book': Book a specific slot for a candidate
    - 'cancel': Cancel an existing booking

    For booking, provide candidate_name, duration_minutes, and optionally preferred_date.
    Returns available slots and booking confirmations.
    """
    args_schema: Type[BaseModel] = CalendarInput

    # Class-level storage for mock calendar data
    _available_slots: ClassVar[List[Dict[str, Any]]] = []
    _bookings: ClassVar[List[Dict[str, Any]]] = []
    _initialized: ClassVar[bool] = False

    def __init__(self, **kwargs):
        """Initialize the calendar tool."""
        super().__init__(**kwargs)
        if not CalendarTool._initialized:
            self._generate_mock_slots()
            CalendarTool._initialized = True

    def _generate_mock_slots(self):
        """Generate mock available time slots for the next 10 business days."""
        slots = []
        base_date = datetime.now()
        slot_id = 1

        for day_offset in range(1, 15):
            date = base_date + timedelta(days=day_offset)

            # Skip weekends
            if date.weekday() >= 5:
                continue

            # Generate slots for standard business hours
            for hour in [9, 10, 11, 14, 15, 16, 17]:
                slots.append({
                    "id": f"slot_{slot_id}",
                    "date": date.strftime("%Y-%m-%d"),
                    "day": date.strftime("%A"),
                    "time": f"{hour:02d}:00",
                    "end_time": f"{hour + 1:02d}:00",
                    "available": True,
                    "duration_minutes": 60
                })
                slot_id += 1

            # Stop after 10 business days of slots
            if slot_id > 70:
                break

        CalendarTool._available_slots = slots

    def _run(
        self,
        action: str,
        candidate_name: str = "",
        duration_minutes: int = 60,
        preferred_date: Optional[str] = None,
        slot_id: Optional[str] = None
    ) -> str:
        """
        Execute calendar action.

        Args:
            action: Action to perform
            candidate_name: Name of the candidate
            duration_minutes: Interview duration
            preferred_date: Preferred date
            slot_id: Slot ID for booking/cancellation

        Returns:
            JSON string with results
        """
        if action == "get_slots":
            return self._get_available_slots(preferred_date, duration_minutes)
        elif action == "book":
            return self._book_slot(candidate_name, slot_id, preferred_date, duration_minutes)
        elif action == "cancel":
            return self._cancel_booking(slot_id)
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}. Valid actions: get_slots, book, cancel"
            })

    def _get_available_slots(
        self,
        preferred_date: Optional[str] = None,
        duration_minutes: int = 60
    ) -> str:
        """Get available interview slots."""
        available = [s for s in CalendarTool._available_slots if s["available"]]

        if preferred_date:
            available = [s for s in available if s["date"] == preferred_date]

        if not available:
            # Get all unique dates with available slots
            all_dates = list(set(s["date"] for s in CalendarTool._available_slots if s["available"]))
            all_dates.sort()

            return json.dumps({
                "success": True,
                "message": "No slots available for the requested date.",
                "available_dates": all_dates[:5],
                "slots": []
            }, indent=2)

        # Return first 10 available slots
        return json.dumps({
            "success": True,
            "message": f"Found {len(available)} available slots",
            "slots": available[:10]
        }, indent=2)

    def _book_slot(
        self,
        candidate_name: str,
        slot_id: Optional[str] = None,
        preferred_date: Optional[str] = None,
        duration_minutes: int = 60
    ) -> str:
        """Book an interview slot."""
        if not candidate_name:
            return json.dumps({
                "success": False,
                "error": "Candidate name is required for booking"
            })

        # Find slot to book
        slot_to_book = None

        if slot_id:
            # Book specific slot
            for slot in CalendarTool._available_slots:
                if slot["id"] == slot_id and slot["available"]:
                    slot_to_book = slot
                    break
        else:
            # Find first available slot matching criteria
            for slot in CalendarTool._available_slots:
                if not slot["available"]:
                    continue
                if preferred_date and slot["date"] != preferred_date:
                    continue
                slot_to_book = slot
                break

        if not slot_to_book:
            return json.dumps({
                "success": False,
                "error": "No available slot found matching criteria",
                "suggestion": "Try get_slots action to see available times"
            })

        # Book the slot
        slot_to_book["available"] = False

        booking = {
            "booking_id": f"booking_{len(CalendarTool._bookings) + 1}",
            "candidate_name": candidate_name,
            "slot_id": slot_to_book["id"],
            "date": slot_to_book["date"],
            "day": slot_to_book["day"],
            "time": slot_to_book["time"],
            "duration_minutes": duration_minutes,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }

        CalendarTool._bookings.append(booking)

        return json.dumps({
            "success": True,
            "message": f"Interview scheduled for {candidate_name}",
            "booking": booking
        }, indent=2)

    def _cancel_booking(self, slot_id: Optional[str] = None) -> str:
        """Cancel a booking and free up the slot."""
        if not slot_id:
            return json.dumps({
                "success": False,
                "error": "Slot ID is required for cancellation"
            })

        # Find and cancel the booking
        booking_found = None
        for booking in CalendarTool._bookings:
            if booking["slot_id"] == slot_id and booking["status"] == "confirmed":
                booking["status"] = "cancelled"
                booking_found = booking
                break

        if not booking_found:
            return json.dumps({
                "success": False,
                "error": f"No confirmed booking found for slot {slot_id}"
            })

        # Free up the slot
        for slot in CalendarTool._available_slots:
            if slot["id"] == slot_id:
                slot["available"] = True
                break

        return json.dumps({
            "success": True,
            "message": f"Booking cancelled for {booking_found['candidate_name']}",
            "cancelled_booking": booking_found
        }, indent=2)

    def get_all_bookings(self) -> str:
        """Get all current bookings."""
        confirmed = [b for b in CalendarTool._bookings if b["status"] == "confirmed"]
        return json.dumps({
            "success": True,
            "total_bookings": len(confirmed),
            "bookings": confirmed
        }, indent=2)

    def reset(self):
        """Reset the calendar to initial state."""
        CalendarTool._bookings = []
        CalendarTool._initialized = False
        self._generate_mock_slots()
        CalendarTool._initialized = True

    async def _arun(
        self,
        action: str,
        candidate_name: str = "",
        duration_minutes: int = 60,
        preferred_date: Optional[str] = None,
        slot_id: Optional[str] = None
    ) -> str:
        """Async version of _run."""
        return self._run(action, candidate_name, duration_minutes, preferred_date, slot_id)
