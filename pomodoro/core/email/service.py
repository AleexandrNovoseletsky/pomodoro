"""Email sending service."""

from email.message import EmailMessage

from pomodoro.core.email.clients import SMTPClient
from pomodoro.core.email.templates import password_recovery_email
from pomodoro.core.settings import Settings

settings = Settings()


class EmailService:
    """Service responsible for sending application emails."""

    def __init__(self, smtp_client: SMTPClient):
        self.smtp_client = smtp_client

    async def send_password_recovery_email(
        self,
        recipient_email: str,
        recovery_code: int,
    ) -> None:
        """Send password recovery email."""
        message = EmailMessage()
        message["From"] = settings.EMAIL_FROM
        message["To"] = recipient_email
        message["Subject"] = "Восстановление пароля"
        message.set_content(password_recovery_email(recovery_code))

        await self.smtp_client.send_message(message)
