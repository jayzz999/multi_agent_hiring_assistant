"""Email drafting tool for hiring communications."""

from typing import Type, ClassVar, Dict
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class EmailDrafterInput(BaseModel):
    """Input schema for email drafter tool."""
    email_type: str = Field(
        description="Type of email: 'interview_invite', 'rejection', 'offer', 'followup', 'acknowledgment'"
    )
    candidate_name: str = Field(description="Name of the candidate")
    additional_context: str = Field(
        default="",
        description="Additional context or details to include in the email"
    )


class EmailDrafterTool(BaseTool):
    """Tool for drafting professional hiring-related emails."""

    name: str = "draft_email"
    description: str = """
    Draft professional emails for the hiring process.

    Email types:
    - 'interview_invite': Invitation to schedule an interview
    - 'rejection': Professional rejection with encouragement
    - 'offer': Job offer email
    - 'followup': Follow-up email to check on interest
    - 'acknowledgment': Application received acknowledgment

    Provide candidate name and any relevant context.
    """
    args_schema: Type[BaseModel] = EmailDrafterInput

    EMAIL_TEMPLATES: ClassVar[Dict[str, str]] = {
        "interview_invite": """Draft a professional interview invitation email that includes:
- Warm greeting using the candidate's name
- Expression of interest in their application
- Request to schedule an interview
- Mention of interview format (if provided in context)
- Next steps and timeline
- Professional closing""",

        "rejection": """Draft a kind and professional rejection email that includes:
- Respectful and warm greeting
- Appreciation for their interest and time
- Clear but gentle rejection
- Encouragement and positive note about their qualifications
- Offer to keep resume on file (if appropriate)
- Professional closing""",

        "offer": """Draft an enthusiastic job offer email that includes:
- Congratulatory opening
- Clear statement of the job offer
- Key details (position, start date, etc. from context)
- Expression of excitement about them joining
- Next steps for acceptance
- Professional closing""",

        "followup": """Draft a professional follow-up email that includes:
- Friendly greeting
- Reference to previous communication/interview
- Checking on their continued interest
- Offering to answer questions
- Clear call to action
- Professional closing""",

        "acknowledgment": """Draft an application acknowledgment email that includes:
- Thank you for applying
- Confirmation of application receipt
- Brief overview of next steps
- Timeline expectations
- Professional closing"""
    }

    SYSTEM_PROMPT: ClassVar[str] = """You are a professional HR communications specialist.
Write emails that are:
- Professional yet warm and personable
- Clear and concise
- Respectful of the candidate's time and effort
- Properly formatted with subject line included

Format your response as:
Subject: [subject line]

[email body]

Best regards,
[Company Name] Hiring Team"""

    def _run(
        self,
        email_type: str,
        candidate_name: str,
        additional_context: str = ""
    ) -> str:
        """
        Draft a professional email.

        Args:
            email_type: Type of email to draft
            candidate_name: Candidate's name
            additional_context: Additional details to include

        Returns:
            Formatted email with subject line and body
        """
        # Validate email type
        if email_type not in self.EMAIL_TEMPLATES:
            available_types = ", ".join(self.EMAIL_TEMPLATES.keys())
            return f"Unknown email type '{email_type}'. Available types: {available_types}"

        try:
            llm = ChatOpenAI(
                model=settings.LLM_MODEL,
                temperature=0.7,
                openai_api_key=settings.OPENAI_API_KEY
            )

            template = self.EMAIL_TEMPLATES[email_type]

            prompt = f"""
{template}

Candidate Name: {candidate_name}
Additional Context: {additional_context or "None provided"}

Write the email now, including the subject line.
"""

            response = llm.invoke([
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])

            return response.content

        except Exception as e:
            return f"Error drafting email: {str(e)}"

    def draft_batch_emails(
        self,
        email_type: str,
        candidates: list,
        additional_context: str = ""
    ) -> dict:
        """
        Draft emails for multiple candidates.

        Args:
            email_type: Type of email
            candidates: List of candidate names
            additional_context: Context for all emails

        Returns:
            Dictionary mapping candidate names to drafted emails
        """
        results = {}
        for candidate in candidates:
            results[candidate] = self._run(email_type, candidate, additional_context)
        return results

    async def _arun(
        self,
        email_type: str,
        candidate_name: str,
        additional_context: str = ""
    ) -> str:
        """Async version of _run."""
        return self._run(email_type, candidate_name, additional_context)
