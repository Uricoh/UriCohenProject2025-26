import protocol
from protocol import log
from smtplib import SMTP_SSL
from email.message import EmailMessage
from os import getenv

class Emailer:
    def __init__(self):
        # Get login credentials
        self._email_address = getenv("EMAIL_ADDRESS")
        email_password = getenv("EMAIL_PASSWORD") # Not a property to increase security
        log("Loaded login credentials from .env")

        # Connect to Gmail's SMTP server
        self._smtp = SMTP_SSL("smtp.gmail.com", 465)
        self._smtp.login(self._email_address, email_password)
        log("Connected to Gmail's SMTP server, connection saved")

    def send_email(self, email_dest, subject, content):
        # Create the email
        msg = EmailMessage()
        msg["From"] = f"{protocol.APP_NAME} <{self._email_address}>"
        msg["To"] = email_dest
        msg["Subject"] = subject
        msg.set_content(content)

        # Send the email
        self._smtp.send_message(msg)
        log(f"Email {subject} sent to {email_dest}")

    def close(self):
        # Close SMTP connection
        self._smtp.close()
        log("SMTP connection closed")
