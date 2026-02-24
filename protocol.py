# Imports
from datetime import datetime
import logging
from pathlib import Path
import tkinter as tk
import sqlite3
from typing import Final, Iterable
from socket import socket
from inspect import currentframe
from hashlib import sha256
from dotenv import load_dotenv


# Network constants
# Port commonly used in school, computer firewalls are configured for it so don't change without good reason
PORT: Final[int] = 8822
# Means this computer, change on BOTH server and client to server IP in order to connect different devices
SERVER_IP: Final[str] = "172.16.5.22"
SERVER_ADDRESS: Final[tuple[str, int]] = (SERVER_IP, PORT)

# Other constants
SCREEN_WIDTH: Final[int] = 1500
SCREEN_HEIGHT: Final[int] = 750
SCREEN_AREA: Final[tuple[int, int]] = (SCREEN_WIDTH, SCREEN_HEIGHT)
FONT_NAME: Final[str] = 'Arial'
FONT_SIZE: Final[int] = 32 # Best to make it a number that divides evenly by many other numbers
FONT: Final[tuple[str, int]] = (FONT_NAME, FONT_SIZE)
TEXT_WIDTH: Final[int] = 20 # Best to make it a number that divides evenly by many other numbers
CURRENCY_WIDTH: Final[int] = 5 # Appropriate length that's enough for three uppercase letters, ISO 3-letter-code
LABELS_X: Final[int] = 50 # Left
BUTTONS_X: Final[int] = 1000 # Right
CENTER_Y: Final[int] = 300
SEC_CODE_LENGTH: Final[int] = 6
BUFFER_SIZE: Final[int] = 1024
TABLE_CAPACITY: Final[int] = 13 # Works for current table size and resolution, change constant if changing those
TABLE_HEADERS: Final[list[str]] = ["Source", "Dest", "Value", "Result"]
ENCODE_FORMAT: Final[str] = 'utf-8'
BASE_CURRENCY: Final[str] = "USD" # Must be set to USD in free plan
BG_PATH: Final[Path] = Path("background.jpg")
_LOG_PATH: Final[Path] = Path("log.log")
_DB_NAME: Final[Path] = Path("database.db")
USER_TBL_NAME: Final[str] = "USERTBL" # Variable name is USER_TBL_NAME because there may be more tables in the future
APP_NAME: Final[str] = "Currency Converter"


# Functions

# IMPORTANT: Function doesn't work with inheritance: if Class A calls a method from Class B from which it inherits,
# function will show A instead of B
def log(message: str) -> None:
    caller_frame = currentframe().f_back # Get caller frame object
    class_name_object = caller_frame.f_locals.get("self") # Get class name if it exists

    if class_name_object:
        display_name = class_name_object.__class__.__name__.upper()
    else:
        # Get __name__ variable. If __name__ is __main__, log() runs directly in the file, not as part of an import
        module_name = caller_frame.f_globals.get('__name__')
        if module_name == "__main__":
            # If log() runs directly, display name is file name
            display_name = Path(caller_frame.f_code.co_filename).stem # Get the name of the file that called log()
        else:
            # If log() runs as part of an import, display name is imported module name
            display_name = module_name

        # Configure display name format
        display_name = f"{display_name.upper()}.py"

    # Log class/module and message
    logging.info(f"[{display_name}] - {message}")

def get_time_as_text() -> str:
    # Gets timestamp as string down to the microsecond
    current_datetime = datetime.now()

    # %f responsible for microseconds, all the way up to %Y for the year
    formatted_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime_string

def color_button_text(button: tk.Button, color: str) -> None:
    button.config(fg=color, activeforeground=color)

def reverse_button(button: tk.Button) -> None:
    if button['state'] == tk.DISABLED:
        button['state'] = tk.NORMAL
    else:
        button['state'] = tk.DISABLED

def reverse_many_buttons(buttons: Iterable[tk.Button]) -> None:
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

def connect_to_db() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(_DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {USER_TBL_NAME} (
                                    id INTEGER PRIMARY KEY,
                                    username TEXT NOT NULL,
                                    password TEXT NOT NULL,
                                    datetime TEXT NOT NULL)
                                    ''')
    log("SQL connection established")
    return conn, cursor

def put_text_in_button(button: tk.Entry, text: str):
    button.delete(0, "end")
    button.insert(0, text)

def get_hash(password: str) -> str:
    encoded_password = password.encode(ENCODE_FORMAT)
    password_hash = sha256(encoded_password).hexdigest()
    log("Hash made")
    return password_hash

# Commands that should be executed at the start of each program

# Load .env file
load_dotenv()

# Clear log file if it exists
if _LOG_PATH.exists():
    _LOG_PATH.write_text('') # Overwrites file with empty string

# Create logger, a logger is created each time protocol is imported, i.e. for each process, server and client
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=_LOG_PATH)
log("Logger created")
