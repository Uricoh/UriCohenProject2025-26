# Imports
from datetime import datetime
import logging
from pathlib import Path
import tkinter as tk
from typing import Final, Iterable
from socket import socket
from inspect import currentframe
from hashlib import sha256
from smtplib import SMTP_SSL
from email.message import EmailMessage
from os import getenv
from dotenv import load_dotenv


# Network constants
# Port commonly used in school, computer firewalls are configured for it so don't change without good reason
PORT: Final[int] = 8822
# Means this computer, change to current server IP address to connect to server based in another computer
SERVER_IP: Final[str] = "127.0.0.1"

# Other constants
SCREEN_WIDTH: Final[int] = 1500
SCREEN_HEIGHT: Final[int] = 750
FONT_NAME: Final[str] = 'Arial'
FONT_SIZE: Final[int] = 32 # Best to make it a number that divides evenly by many other numbers
FONT: Final[tuple] = (FONT_NAME, FONT_SIZE)
TEXT_WIDTH: Final[int] = 20 # Best to make it a number that divides evenly by many other numbers
CURRENCY_WIDTH: Final[int] = 5 # Appropriate length that's enough for three uppercase letters, ISO 3-letter-code
LABELS_X: Final[int] = 50 # Left
BUTTONS_X: Final[int] = 1000 # Right
CENTER_Y: Final[int] = 300
SEC_CODE_LENGTH: Final[int] = 6
BUFFER_SIZE: Final[int] = 1024
ENCODE_FORMAT: Final[str] = 'utf-8'
BG_PATH: Final[str] = "background.jpg"
_LOG_PATH: Final[str] = "log.log"
DB_NAME: Final[str] = "database.db"
USER_TBL: Final[str] = "USERTBL" # Variable name is user_tbl because there may be more tables in the future
APP_NAME: Final[str] = "Currency Converter"


# Functions

# IMPORTANT: Function doesn't work with inheritance: if Class A calls a method from Class B from which it inherits,
# function will show A instead of B
def log(message: str) -> None:
    # Get class name
    caller_frame = currentframe().f_back
    caller_self = caller_frame.f_locals.get("self")

    if caller_self:
        module_or_class = caller_self.__class__.__name__.upper()
    else:
        # If class doesn't exist, get module name instead
        module_or_class = f"{caller_frame.f_globals.get('__name__').upper()}.py"

    # Log class/module and message
    logging.info(f"[{module_or_class}] - {message}")

def get_time_as_text() -> str:
    # Gets timestamp as string down to the microsecond
    current_datetime = datetime.now()

    # %f responsible for microseconds, all the way up to %Y for the year
    formatted_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime_string

def reverse_button(button: tk.Button) -> None:
    if button['state'] == tk.DISABLED:
        button['state'] = tk.NORMAL
    else:
        button['state'] = tk.DISABLED

def reverse_many_buttons(buttons: Iterable | tk.Button) -> None:
    for button in buttons:
        reverse_button(button)

# Check whether a socket still exists and active - "alive", and so can be contacted
def socket_alive(my_socket: socket) -> bool:
    if my_socket is None:
        return False
    else:
        try:
            my_socket.getpeername()
            # We don't actually need the peer name (other side-socket's name),
            # it will just throw an exception if the checked socket is closed
            return True
        except OSError:
            return False

def get_hash(password: str) -> str:
    encoded_password = password.encode(ENCODE_FORMAT)
    password_hash = sha256(encoded_password).hexdigest()
    log("Hash made")
    return password_hash

def send_email(email_dest: str, subject: str, content: str) -> None:
    # Load .env file
    load_dotenv()

    # Get login credentials
    email_address = getenv("EMAIL_ADDRESS")
    email_password = getenv("EMAIL_PASSWORD")

    # Create the email
    msg = EmailMessage()
    msg["From"] = f"{APP_NAME} <{email_address}>"
    msg["To"] = email_dest
    msg["Subject"] = subject
    msg.set_content(content)

    # Connect to Gmail's SMTP server
    smtp = SMTP_SSL("smtp.gmail.com", 465)
    smtp.login(email_address, email_password)

    # Send the email
    smtp.send_message(msg)

    # Close the connection
    smtp.quit()

# Commands that should be executed at the start of each program

# Clear log file if it exists

# 1. Define clearer function
def _clear_log():
    log_file = Path(_LOG_PATH)
    if log_file.exists():
        log_file.write_text('') # Overwrites file with empty string

# 2. Call clearer function
_clear_log()

# Create logger, a logger is created each time protocol is imported, i.e. for each process, server and client
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=_LOG_PATH)
log("Logger created")
