import protocol
from protocol import log
from smtplib import SMTP_SSL
from email.message import EmailMessage
from os import getenv


class Emailer:
    # One emailer for the entire server, same as converter
    def __init__(self):
        # Get login credentials
        self._email_address = getenv("EMAIL_ADDRESS")
        email_password = getenv("EMAIL_PASSWORD")  # Not a property to increase security
        if not self._email_address or not email_password:
            raise ValueError("Missing EMAIL_ADDRESS or EMAIL_PASSWORD environment variables")
        else:
            log("Loaded login credentials from .env")

        # Connect to Gmail's SMTP server
        self._smtp = SMTP_SSL("smtp.gmail.com", 465, timeout=protocol.TIMEOUT_LENGTH)
        try:
            self._smtp.login(self._email_address, email_password)
            log("Connected to Gmail's SMTP server, connection saved")
        except Exception as e:
            log(f"SMTP login failed: {e}")

    def send_email(self, email_dest, subject, content):
        try:
            # Create the email
            msg = EmailMessage()
            msg["From"] = f"{protocol.APP_NAME} <{self._email_address}>"
            msg["To"] = email_dest
            msg["Subject"] = subject
            msg.set_content(content)

            # Send the email
            self._smtp.send_message(msg)
            log(f"Email '{subject}' sent to {email_dest}")

        except Exception as e:
            log(f"Failed to send email: {e}")

    def close(self):
        # Close SMTP connection
        self._smtp.quit()
        log("SMTP connection closed")
