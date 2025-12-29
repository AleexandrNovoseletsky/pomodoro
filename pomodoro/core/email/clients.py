"""SMTP email client."""
import ssl
from email.message import EmailMessage

import aiosmtplib
import certifi

from pomodoro.core.settings import Settings

settings = Settings()
ssl_context = ssl.create_default_context(cafile=certifi.where())

class SMTPClient:
    """Asynchronous SMTP client."""

    @staticmethod
    async def send_message(message: EmailMessage) -> None:
        """Send email message via SMTP."""
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
            tls_context=ssl_context,
        )
