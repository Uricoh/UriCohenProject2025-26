# Imports
from os import getenv
from datetime import datetime
import json
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk
import sqlite3
from typing import Final, Iterable
from socket import socket
from inspect import currentframe
from hashlib import sha256
from dotenv import load_dotenv
from currencies import currencies

# This command MUST appear on top in order to load some constants
# Load .env file
load_dotenv()

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

def create_table(root: tk.Tk, headers: tuple, values: list[tuple]) -> ttk.Treeview:
    table = ttk.Treeview(root, columns=headers, show="headings")

    # Configure columns
    for col in headers:
        table.heading(col, text=col)
        table.column(col, width=100, anchor="center")

    # Insert data rows
    for row in values:
        table.insert("", "end", values=row)

    return table

def open_image(image_path: str | Path, area: tuple[int, int]) -> PhotoImage:
    image = Image.open(image_path)
    reimage = image.resize(area)
    pimage: PhotoImage = ImageTk.PhotoImage(reimage)
    return pimage

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
                                    userid INTEGER PRIMARY KEY,
                                    username TEXT NOT NULL,
                                    password TEXT NOT NULL,
                                    datetime TEXT NOT NULL)
                                    ''')
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {CONVERT_TBL_NAME} (
                                    convertid INTEGER PRIMARY KEY,
                                    userid INTEGER NOT NULL,
                                    amount INTEGER NOT NULL,
                                    source TEXT NOT NULL,
                                    result INTEGER NOT NULL,
                                    dest TEXT NOT NULL)
                                    ''')
    log("SQL connection established")
    return conn, cursor

def put_text_in_entry(entry: tk.Entry, text: str):
    entry.delete(0, "end")
    entry.insert(0, text)

def get_hash(password: str) -> str:
    encoded_pw = password.encode(ENCODE_FORMAT)
    pw_hash = sha256(encoded_pw).hexdigest()
    log("Hash made")
    return pw_hash

def make_json(data: Iterable) -> str:
    json_data = json.dumps(data)
    log("JSON made")
    return json_data

# Constants

# Network constants
# Port commonly used in school, computer firewalls are configured for it so don't change without good reason
PORT: Final[int] = 8822
# Means this computer, change on BOTH server and client to server IP in order to connect different devices
SERVER_IP: Final[str] = getenv("SERVER_IP") # Saved in .env file to protect privacy
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
LEFT_X: Final[int] = 50 # Left
RIGHT_X: Final[int] = int(0.65 * SCREEN_WIDTH) # Right
# Center variables are slightly higher and more left than mathematical centers, indicating start coordinates of elements
CENTER_X: Final[int] = int((RIGHT_X + LEFT_X) / 2)
CENTER_Y: Final[int] = int(0.4 * SCREEN_HEIGHT)
SEC_CODE_LENGTH: Final[int] = 6
BUFFER_SIZE: Final[int] = 1024
TBL_CAPACITY: Final[int] = 13 # Works for current table size and resolution, change constant if changing those
HISTORY_TBL_HEADERS: Final[tuple[str, str, str, str]] = ("Source", "Dest", "Value", "Result")
SERVER_TBL_HEADERS: Final[tuple[str, str, str]] = ("Client IP", "Port", "Time")
ENCODE_FORMAT: Final[str] = "utf-8"
BASE_CURRENCY: Final[str] = "USD" # Must be set to USD in free plan
BG_PATH: Final[Path] = Path("background.jpg")
SWITCH_PATH: Final[Path] = Path("switch.png")
_LOG_PATH: Final[Path] = Path("log.log")
_DB_NAME: Final[Path] = Path("database.db")
ERROR_MSG: Final[str] = "Error"
GUEST_USERNAME: Final[str] = "Guest"
CONVERT_TBL_NAME: Final[str] = "CONVERTTBL"
USER_TBL_NAME: Final[str] = "USERTBL" # Variable name is USER_TBL_NAME because there may be more tables in the future
APP_NAME: Final[str] = "Currency Converter"
CURRENCIES: Final[list[str]] = currencies

# Commands that should be executed at the start of each program

# Clear log file if it exists
if _LOG_PATH.exists():
    _LOG_PATH.write_text('') # Overwrites file with empty string

# Create logger, a logger is created each time protocol is imported, i.e. for each process, server and client
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=_LOG_PATH)
log("Logger created")
