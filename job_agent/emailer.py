"""
Job Search Agent — Email Sender

Sends HTML email reports via Gmail SMTP using an App Password.

Setup:
    1. Enable 2-Step Verification on your Google Account
       (myaccount.google.com > Security > 2-Step Verification)
    2. Generate an App Password
       (myaccount.google.com > Security > App passwords)
    3. Set the GMAIL_APP_PASSWORD environment variable
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, REPORT_RECIPIENT

logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_email(subject: str, html_body: str) -> bool:
    """
    Send an HTML email via Gmail SMTP.

    Returns True on success, False on failure.
    """
    if not GMAIL_APP_PASSWORD:
        logger.error(
            "GMAIL_APP_PASSWORD not set. Cannot send email. "
            "Generate an App Password at: myaccount.google.com > Security > App passwords"
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Job Search Agent <{GMAIL_ADDRESS}>"
    msg["To"] = REPORT_RECIPIENT
    msg["Subject"] = subject

    # Plain-text fallback
    plain_text = (
        f"{subject}\n\n"
        "This email is best viewed in an HTML-capable email client.\n"
        "Open this email in Gmail or another modern email client to see the full report."
    )
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, REPORT_RECIPIENT, msg.as_string())

        logger.info("Email sent successfully to %s", REPORT_RECIPIENT)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error(
            "Gmail authentication failed. Check that:\n"
            "  1. 2-Step Verification is enabled on your Google Account\n"
            "  2. GMAIL_APP_PASSWORD is a valid App Password (not your regular password)\n"
            "  3. GMAIL_ADDRESS is correct"
        )
        return False
    except smtplib.SMTPException as e:
        logger.error("SMTP error sending email: %s", e)
        return False
    except Exception as e:
        logger.error("Unexpected error sending email: %s", e)
        return False
