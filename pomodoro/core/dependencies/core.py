from pomodoro.core.email.clients import SMTPClient
from pomodoro.core.email.service import EmailService


async def get_email_service():
    return EmailService(smtp_client=SMTPClient())
