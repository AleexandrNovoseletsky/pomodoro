"""Core dependency injection providers."""

from pomodoro.core.email.clients import SMTPClient
from pomodoro.core.email.service import EmailService


async def get_email_service():
    """Get email service instance with SMTP client."""
    return EmailService(smtp_client=SMTPClient())
