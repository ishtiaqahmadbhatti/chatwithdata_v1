from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.app_core.config import settings
from pydantic import EmailStr
from typing import List, Optional

class EmailService:
    # Configure connection
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS
    )

    @staticmethod
    async def send_otp_email(email: EmailStr, otp: str):
        """
        Send an email with the OTP code.
        """
        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
                <h2 style="color: #00D4FF;">SmartConverter Verification</h2>
                <p>Hello,</p>
                <p>You requested a password reset. Use the code below to verify your identity.</p>
                <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                    <p style="margin: 0; font-size: 14px;">Verification Code:</p>
                    <p style="margin: 10px 0 0 0; font-size: 32px; font-weight: bold; color: #7C3AED; letter-spacing: 5px;">
                        {otp}
                    </p>
                </div>
                <p style="color: #666; font-size: 12px;">This code expires in 3 minutes.</p>
                <p>If you didn't request this, you can safely ignore this email.</p>
                <br>
                <p>Best regards,</p>
                <p><strong>SmartConverter Team</strong></p>
            </body>
        </html>
        """

        message = MessageSchema(
            subject="SmartConverter - Password Reset Code",
            recipients=[email],
            body=html,
            subtype=MessageType.html
        )

        try:
            fm = FastMail(EmailService.conf)
            await fm.send_message(message)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    async def send_helpdesk_email(subject: str, html_content: str, attachments: Optional[List[str]] = None):
        """
        Send a helpdesk notification email to admin with optional attachments.
        """
        target_email = settings.HELPDESK_EMAIL
        
        message_data = {
            "subject": subject,
            "recipients": [target_email],
            "body": html_content,
            "subtype": MessageType.html
        }
        
        # Add attachments if provided and exist
        import os
        if attachments:
            valid_attachments = [path for path in attachments if os.path.exists(path)]
            if valid_attachments:
                message_data["attachments"] = valid_attachments

        message = MessageSchema(**message_data)

        try:
            fm = FastMail(EmailService.conf)
            await fm.send_message(message)
            return True
        except Exception as e:
            print(f"Error sending helpdesk email: {e}")
            return False
