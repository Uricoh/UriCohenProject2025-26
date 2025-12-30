import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get info
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_DEST = os.getenv("EMAIL_DEST")

# Create the email
msg = EmailMessage()
msg["From"] = f"Your App <{EMAIL_ADDRESS}>"
msg["To"] = f"{EMAIL_DEST}"
msg["Subject"] = "Test email from Python"

msg.set_content("Secure")

# Connect to Gmail's SMTP server
smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
smtp.login(f"{EMAIL_ADDRESS}", f"{EMAIL_PASSWORD}")

# Send the email
smtp.send_message(msg)

# Close the connection
smtp.quit()
