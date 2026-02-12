import aiosmtplib
from email.message import EmailMessage
from core.config import settings

async def send_password_reset_email(email :str, reset_link : str) :
    message = EmailMessage()
    message["From"] = settings.FROM_EMAIL
    message["To"] = settings.to_email
    message["Subject"] = "Password Reset Request"

    message.set_content(
        f"""
        You requested a password reset.

        Click the link below to reset your password:

        {reset_link}

        This link will expire in 10 minutes.

        If you did not request this, ignore this email.
        """
    )

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
