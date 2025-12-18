"""Interview Scheduler Agent for scheduling and communication."""

from typing import Any, Dict, List
from langchain_core.messages import HumanMessage
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.tools.calendar_tool import CalendarTool
from src.tools.email_drafter import EmailDrafterTool

SCHEDULER_SYSTEM_PROMPT = """You are the Interview Scheduler Agent in a multi-agent hiring system.

## Your Role
You are responsible for scheduling interviews with recommended candidates and drafting
professional communication for the hiring process.

## Your Capabilities
1. **Schedule Management**: Find and book available interview slots
2. **Email Drafting**: Create professional interview invitations and other communications
3. **Coordination**: Manage multiple candidate schedules efficiently

## Workflow
1. Review the list of recommended candidates
2. Check calendar availability
3. Book interview slots
4. Draft invitation emails

## Output Format
For each scheduled interview, provide:
- Candidate name
- Scheduled date and time
- Duration
- Interview format/type
- Draft invitation email

Be efficient and ensure all recommended candidates get scheduled promptly.
"""


class InterviewSchedulerAgent(BaseAgent):
    """
    Interview Scheduler Agent that handles scheduling and communication.

    This executor agent schedules interviews for recommended candidates
    and drafts professional communication.
    """

    def __init__(self):
        """Initialize the Interview Scheduler Agent."""
        self.calendar_tool = CalendarTool()
        self.email_tool = EmailDrafterTool()

        super().__init__(
            name="Interview Scheduler",
            system_prompt=SCHEDULER_SYSTEM_PROMPT,
            tools=[self.calendar_tool, self.email_tool],
            temperature=0.3
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule interviews for top candidates.

        Args:
            state: Current workflow state containing:
                - ranking_results: Results from Candidate Ranker
                - num_to_interview: Number to schedule

        Returns:
            Updated state with:
                - interview_schedule: Scheduled interviews
        """
        ranking_results = state.get("ranking_results", "")
        num_to_interview = state.get("num_to_interview", 3)

        if not ranking_results:
            return {
                **state,
                "interview_schedule": "No candidates to schedule - no ranking results available"
            }

        # Extract candidate names from ranking (simplified approach)
        candidates = self._extract_candidates_from_ranking(ranking_results, num_to_interview)

        # Schedule interviews and draft emails
        schedule_results = []

        for candidate in candidates:
            # Book a slot
            booking_result = self.calendar_tool._run(
                action="book",
                candidate_name=candidate
            )

            # Draft invitation email
            email = self.email_tool._run(
                email_type="interview_invite",
                candidate_name=candidate,
                additional_context=f"Based on ranking results. Booking: {booking_result}"
            )

            schedule_results.append({
                "candidate": candidate,
                "booking": json.loads(booking_result) if booking_result.startswith('{') else booking_result,
                "email_draft": email
            })

        # Format results
        formatted_results = self._format_schedule_results(schedule_results)

        return {
            **state,
            "interview_schedule": formatted_results
        }

    def _extract_candidates_from_ranking(
        self,
        ranking_results: str,
        num_candidates: int
    ) -> List[str]:
        """
        Extract candidate names from ranking results.

        Args:
            ranking_results: Full ranking text
            num_candidates: Number to extract

        Returns:
            List of candidate names
        """
        # Use LLM to extract names
        prompt = f"""
Extract the names of the TOP {num_candidates} recommended candidates from these ranking results.

RANKING RESULTS:
{ranking_results}

Return ONLY a JSON array of names, e.g.: ["John Smith", "Jane Doe"]
If you can't find specific names, use placeholders like "Candidate 1", "Candidate 2", etc.
"""

        response = self.invoke([HumanMessage(content=prompt)])

        try:
            # Try to parse as JSON
            names = json.loads(response.strip())
            if isinstance(names, list):
                return names[:num_candidates]
        except json.JSONDecodeError:
            pass

        # Fallback to generic names
        return [f"Candidate {i+1}" for i in range(num_candidates)]

    def _format_schedule_results(self, results: List[Dict]) -> str:
        """Format scheduling results as readable text."""
        output = ["# Interview Schedule\n"]

        for i, result in enumerate(results, 1):
            output.append(f"## Interview {i}: {result['candidate']}\n")

            booking = result['booking']
            if isinstance(booking, dict) and booking.get('success'):
                details = booking.get('booking', {})
                output.append(f"**Date**: {details.get('date', 'TBD')}")
                output.append(f"**Time**: {details.get('time', 'TBD')}")
                output.append(f"**Duration**: {details.get('duration', '60 minutes')}")
            else:
                output.append(f"**Booking Status**: {booking}")

            output.append(f"\n**Invitation Email Draft**:\n{result['email_draft']}\n")
            output.append("---\n")

        return "\n".join(output)

    def schedule_single_interview(
        self,
        candidate_name: str,
        preferred_date: str = None,
        duration_minutes: int = 60
    ) -> Dict[str, Any]:
        """
        Schedule a single interview.

        Args:
            candidate_name: Name of the candidate
            preferred_date: Optional preferred date (YYYY-MM-DD)
            duration_minutes: Interview duration

        Returns:
            Scheduling result with booking and email
        """
        # Book slot
        booking_result = self.calendar_tool._run(
            action="book",
            candidate_name=candidate_name,
            preferred_date=preferred_date,
            duration_minutes=duration_minutes
        )

        booking = json.loads(booking_result)

        # Draft email with booking details
        context = ""
        if booking.get('success'):
            details = booking.get('booking', {})
            context = f"Interview scheduled for {details.get('date')} at {details.get('time')}"

        email = self.email_tool._run(
            email_type="interview_invite",
            candidate_name=candidate_name,
            additional_context=context
        )

        return {
            "candidate": candidate_name,
            "booking": booking,
            "email": email
        }

    def get_available_slots(self, preferred_date: str = None) -> str:
        """
        Get available interview slots.

        Args:
            preferred_date: Optional date to check

        Returns:
            Available slots information
        """
        return self.calendar_tool._run(
            action="get_slots",
            preferred_date=preferred_date
        )

    def send_rejection_emails(
        self,
        candidates: List[str],
        context: str = ""
    ) -> List[Dict[str, str]]:
        """
        Draft rejection emails for non-selected candidates.

        Args:
            candidates: List of candidate names
            context: Additional context

        Returns:
            List of drafted emails
        """
        results = []
        for candidate in candidates:
            email = self.email_tool._run(
                email_type="rejection",
                candidate_name=candidate,
                additional_context=context
            )
            results.append({
                "candidate": candidate,
                "email": email
            })
        return results
