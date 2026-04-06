from .email import get_email_service
import os

smtp_host = os.getenv("SMTP_HOST")
smtp_port = os.getenv("SMTP_PORT")
smtp_user = os.getenv("SMTP_USER")
smtp_password = os.getenv("SMTP_PASSWORD")
smtp_from_name = os.getenv("SMTP_FROM_NAME")

email_sender = get_email_service(
    smtp_host=smtp_host, 
    smtp_port=smtp_port, 
    smtp_user=smtp_user, 
    smtp_password=smtp_password,
    smtp_from_name=smtp_from_name
)

__all__ = ["email_sender"]