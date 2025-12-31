"""Communication Agent for automated candidate messaging."""

from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agents.base_agent import BaseAgent
from src.prompts.communication_prompts import COMMUNICATION_SYSTEM_PROMPT


class CommunicationAgent(BaseAgent):
    """Agent responsible for all candidate communications."""

    def __init__(self):
        super().__init__(
            name="CommunicationAgent",
            system_prompt=COMMUNICATION_SYSTEM_PROMPT,
            temperature=0.7
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute communication tasks.

        Args:
            state: Current workflow state

        Returns:
            Updated state with communication logs
        """
        state["execution_log"] = state.get("execution_log", [])
        state["execution_log"].append(f"[{self.name}] Processing communications")

        # Communication will be handled per-candidate
        state["communication_ready"] = True

        return state

    def generate_application_acknowledgment(
        self,
        candidate_name: str,
        job_title: str,
        company_name: str = "Our Company"
    ) -> str:
        """Generate application acknowledgment email."""
        prompt = f"""
        Generate a professional application acknowledgment email for:
        - Candidate: {candidate_name}
        - Position: {job_title}
        - Company: {company_name}

        Include:
        - Thank them for applying
        - Confirm receipt of application
        - Set expectations for next steps
        - Timeline for response (1-2 weeks)
        - Professional tone

        Keep it concise and warm.
        """
        return self.chat(prompt)

    def generate_rejection_email(
        self,
        candidate_name: str,
        job_title: str,
        include_feedback: bool = False,
        feedback: Optional[str] = None
    ) -> str:
        """Generate rejection email."""
        feedback_instruction = ""
        if include_feedback and feedback:
            feedback_instruction = f"\nInclude this constructive feedback: {feedback}"

        prompt = f"""
        Generate a professional, empathetic rejection email for:
        - Candidate: {candidate_name}
        - Position: {job_title}
        {feedback_instruction}

        Requirements:
        - Be respectful and kind
        - Thank them for their interest
        - Encourage future applications
        - Keep it brief but warm
        - Avoid generic corporate speak
        """
        return self.chat(prompt)

    def generate_interview_invitation(
        self,
        candidate_name: str,
        job_title: str,
        interview_type: str,
        interview_date: str,
        interview_duration: int = 60,
        meeting_link: Optional[str] = None
    ) -> str:
        """Generate interview invitation email."""
        link_info = f"\nMeeting Link: {meeting_link}" if meeting_link else ""

        prompt = f"""
        Generate an interview invitation email for:
        - Candidate: {candidate_name}
        - Position: {job_title}
        - Interview Type: {interview_type}
        - Date/Time: {interview_date}
        - Duration: {interview_duration} minutes
        {link_info}

        Include:
        - Congratulations on moving forward
        - Interview details (date, time, duration, type)
        - What to prepare/expect
        - Meeting link if provided
        - Contact for questions
        - Request confirmation of attendance
        """
        return self.chat(prompt)

    def generate_offer_notification(
        self,
        candidate_name: str,
        job_title: str,
        salary: float,
        start_date: Optional[str] = None
    ) -> str:
        """Generate offer notification email."""
        start_info = f"\nProposed Start Date: {start_date}" if start_date else ""

        prompt = f"""
        Generate an enthusiastic offer notification email for:
        - Candidate: {candidate_name}
        - Position: {job_title}
        - Base Salary: ${salary:,.2f}
        {start_info}

        Requirements:
        - Express excitement about extending an offer
        - Mention that formal offer letter is attached
        - Highlight key details
        - Provide next steps
        - Include contact for questions
        - Professional yet warm tone
        """
        return self.chat(prompt)

    def generate_status_update(
        self,
        candidate_name: str,
        job_title: str,
        current_status: str,
        next_steps: str
    ) -> str:
        """Generate status update email."""
        prompt = f"""
        Generate a status update email for:
        - Candidate: {candidate_name}
        - Position: {job_title}
        - Current Status: {current_status}
        - Next Steps: {next_steps}

        Keep candidate informed and engaged.
        Be transparent about timeline and process.
        """
        return self.chat(prompt)

    def generate_reminder_email(
        self,
        candidate_name: str,
        reminder_type: str,
        details: str
    ) -> str:
        """Generate reminder email (interview, assessment, etc.)."""
        prompt = f"""
        Generate a friendly reminder email for:
        - Candidate: {candidate_name}
        - Reminder Type: {reminder_type}
        - Details: {details}

        Be helpful and not pushy.
        """
        return self.chat(prompt)

    def personalize_template(
        self,
        template: str,
        variables: Dict[str, str]
    ) -> str:
        """Personalize email template with variables."""
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, value)
        return result
