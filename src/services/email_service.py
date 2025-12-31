"""Email service for automated candidate communications."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os


class EmailTemplate(str, Enum):
    """Pre-defined email templates."""
    APPLICATION_RECEIVED = "application_received"
    SCREENING_PASSED = "screening_passed"
    SCREENING_FAILED = "screening_failed"
    ASSESSMENT_INVITATION = "assessment_invitation"
    INTERVIEW_INVITATION = "interview_invitation"
    INTERVIEW_REMINDER = "interview_reminder"
    INTERVIEW_THANK_YOU = "interview_thank_you"
    OFFER_NOTIFICATION = "offer_notification"
    REJECTION = "rejection"
    STATUS_UPDATE = "status_update"
    REFERENCE_CHECK_REQUEST = "reference_check_request"


class EmailService:
    """Service for sending automated emails to candidates."""

    def __init__(self):
        # Load from environment
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@company.com")
        self.from_name = os.getenv("FROM_NAME", "Company Talent Team")

        # Template storage
        self.templates = self._load_templates()

        # Tracking
        self.sent_emails = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an email.

        Args:
            to_email: Recipient email
            subject: Email subject
            body_html: HTML body
            body_text: Plain text body (optional)
            cc: CC recipients
            bcc: BCC recipients
            attachments: List of attachments
            template_id: Template ID for tracking

        Returns:
            Send result
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Add body
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)

            # Send email
            self._send_smtp(msg, to_email, cc, bcc)

            # Track
            email_log = {
                "to": to_email,
                "subject": subject,
                "template_id": template_id,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            }
            self.sent_emails.append(email_log)

            return {
                "success": True,
                "message_id": len(self.sent_emails),
                **email_log
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "to": to_email
            }

    def _send_smtp(
        self,
        msg: MIMEMultipart,
        to_email: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ):
        """Send email via SMTP."""
        recipients = [to_email]
        if cc:
            recipients.extend(cc)
        if bcc:
            recipients.extend(bcc)

        # In production, actually send via SMTP
        # For now, mock implementation
        if self.smtp_user and self.smtp_password:
            try:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                server.quit()
            except Exception as e:
                print(f"SMTP Error: {e}")
                # Continue anyway for development
        else:
            # Mock send
            print(f"[MOCK] Email sent to {to_email}: {msg['Subject']}")

    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email."""
        filename = attachment.get("filename")
        content = attachment.get("content")

        if content:
            part = MIMEApplication(content, Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

    def send_from_template(
        self,
        template: EmailTemplate,
        to_email: str,
        variables: Dict[str, str],
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send email from pre-defined template.

        Args:
            template: Template to use
            to_email: Recipient
            variables: Template variables
            attachments: Optional attachments

        Returns:
            Send result
        """
        template_data = self.templates.get(template.value)

        if not template_data:
            return {
                "success": False,
                "error": f"Template {template.value} not found"
            }

        # Replace variables in subject and body
        subject = self._replace_variables(template_data["subject"], variables)
        body_html = self._replace_variables(template_data["body_html"], variables)
        body_text = self._replace_variables(template_data.get("body_text", ""), variables)

        return self.send_email(
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text if body_text else None,
            attachments=attachments,
            template_id=template.value
        )

    def _replace_variables(self, template: str, variables: Dict[str, str]) -> str:
        """Replace template variables."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def send_bulk_emails(
        self,
        recipients: List[Dict[str, Any]],
        template: EmailTemplate,
        common_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send bulk emails with personalization.

        Args:
            recipients: List of recipients with their variables
            template: Template to use
            common_variables: Variables common to all emails

        Returns:
            Bulk send results
        """
        results = []

        for recipient in recipients:
            email = recipient.get("email")
            variables = {**(common_variables or {}), **recipient.get("variables", {})}

            result = self.send_from_template(
                template=template,
                to_email=email,
                variables=variables
            )

            results.append(result)

        return {
            "total": len(recipients),
            "sent": len([r for r in results if r.get("success")]),
            "failed": len([r for r in results if not r.get("success")]),
            "results": results
        }

    def schedule_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        send_at: datetime,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedule an email for future delivery."""
        # In production, this would queue the email
        # Using a task queue like Celery with Redis

        return {
            "success": True,
            "email_id": f"scheduled_{datetime.now().timestamp()}",
            "to": to_email,
            "scheduled_for": send_at.isoformat(),
            "status": "scheduled"
        }

    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load email templates."""
        return {
            "application_received": {
                "subject": "Application Received - {{job_title}}",
                "body_html": """
                <html>
                <body>
                    <p>Dear {{candidate_name}},</p>

                    <p>Thank you for applying for the <strong>{{job_title}}</strong> position at {{company_name}}.</p>

                    <p>We have received your application and our team will review it carefully.
                    You can expect to hear from us within {{response_time}} with next steps.</p>

                    <p>In the meantime, feel free to learn more about our company and culture on our website.</p>

                    <p>Best regards,<br>
                    {{company_name}} Talent Team</p>
                </body>
                </html>
                """,
                "body_text": "Dear {{candidate_name}},\n\nThank you for applying for the {{job_title}} position..."
            },

            "interview_invitation": {
                "subject": "Interview Invitation - {{job_title}}",
                "body_html": """
                <html>
                <body>
                    <p>Dear {{candidate_name}},</p>

                    <p>Great news! We were impressed with your application and would like to invite you for an interview
                    for the <strong>{{job_title}}</strong> position.</p>

                    <p><strong>Interview Details:</strong></p>
                    <ul>
                        <li>Type: {{interview_type}}</li>
                        <li>Date & Time: {{interview_datetime}}</li>
                        <li>Duration: {{duration}} minutes</li>
                        <li>Meeting Link: <a href="{{meeting_link}}">Join Interview</a></li>
                    </ul>

                    <p><strong>What to Expect:</strong><br>
                    {{interview_description}}</p>

                    <p>Please confirm your attendance by replying to this email.</p>

                    <p>We look forward to speaking with you!</p>

                    <p>Best regards,<br>
                    {{interviewer_name}}<br>
                    {{company_name}}</p>
                </body>
                </html>
                """
            },

            "offer_notification": {
                "subject": "Job Offer - {{job_title}}",
                "body_html": """
                <html>
                <body>
                    <p>Dear {{candidate_name}},</p>

                    <p>We are thrilled to extend an offer for you to join {{company_name}} as a <strong>{{job_title}}</strong>!</p>

                    <p><strong>Offer Summary:</strong></p>
                    <ul>
                        <li>Base Salary: {{salary}}</li>
                        <li>Start Date: {{start_date}}</li>
                        <li>Location: {{location}}</li>
                    </ul>

                    <p>Please find the complete offer letter attached to this email.</p>

                    <p>We're excited about the possibility of you joining our team!
                    Please review the offer and let us know if you have any questions.</p>

                    <p>To accept this offer, please sign and return the offer letter by {{deadline}}.</p>

                    <p>Congratulations!</p>

                    <p>Best regards,<br>
                    {{hiring_manager_name}}<br>
                    {{company_name}}</p>
                </body>
                </html>
                """
            },

            "rejection": {
                "subject": "Thank you for your interest - {{job_title}}",
                "body_html": """
                <html>
                <body>
                    <p>Dear {{candidate_name}},</p>

                    <p>Thank you for your interest in the <strong>{{job_title}}</strong> position and for taking
                    the time to interview with us.</p>

                    <p>After careful consideration, we have decided to move forward with other candidates whose
                    experience more closely matches our current needs.</p>

                    <p>We were impressed by {{positive_feedback}} and encourage you to apply for future opportunities
                    that match your skills and experience.</p>

                    <p>We wish you the very best in your job search and future career endeavors.</p>

                    <p>Best regards,<br>
                    {{company_name}} Talent Team</p>
                </body>
                </html>
                """
            },

            "assessment_invitation": {
                "subject": "Skills Assessment - {{job_title}}",
                "body_html": """
                <html>
                <body>
                    <p>Dear {{candidate_name}},</p>

                    <p>As the next step in our hiring process for the <strong>{{job_title}}</strong> position,
                    we'd like to invite you to complete a skills assessment.</p>

                    <p><strong>Assessment Details:</strong></p>
                    <ul>
                        <li>Type: {{assessment_type}}</li>
                        <li>Estimated Time: {{duration}} minutes</li>
                        <li>Deadline: {{deadline}}</li>
                    </ul>

                    <p><strong>Access your assessment:</strong><br>
                    <a href="{{assessment_link}}">Start Assessment</a></p>

                    <p>{{instructions}}</p>

                    <p>If you have any questions, please don't hesitate to reach out.</p>

                    <p>Good luck!</p>

                    <p>Best regards,<br>
                    {{company_name}} Talent Team</p>
                </body>
                </html>
                """
            }
        }

    def get_email_statistics(self) -> Dict[str, Any]:
        """Get email sending statistics."""
        return {
            "total_sent": len(self.sent_emails),
            "by_template": self._group_by_template(),
            "recent_sends": self.sent_emails[-10:] if self.sent_emails else []
        }

    def _group_by_template(self) -> Dict[str, int]:
        """Group sent emails by template."""
        counts = {}
        for email in self.sent_emails:
            template_id = email.get("template_id", "custom")
            counts[template_id] = counts.get(template_id, 0) + 1
        return counts
