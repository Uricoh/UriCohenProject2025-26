from datetime import datetime
import logging
from pathlib import Path
import tkinter as tk
from hashlib import sha256


# Port commonly used in school, computer firewalls are configured for it so don't change without good reason
PORT: int = 8822

# Means this computer, change to current server IP address to connect to server based in another computer
SERVER_IP: str = "127.0.0.1"


width: int = 1500
height: int = 750
font_name: str = 'Arial'
font_size: int = 32
font: tuple = (font_name, font_size)
text_width: int = 20
labels_x: int = 50 # Left
buttons_x: int = 1000 # Right
json_format: str = 'utf-8'
errors: tuple = (OSError, ConnectionResetError, BrokenPipeError)
bg_path: str = "background.jpg"
log_path: str = "log.log"
db_name: str = "database.db"
user_tbl: str = "USERTBL" # Variable name is user_tbl because there may be more tables in the future


def get_time_as_text() -> str:
    # Gets timestamp as string down to the microsecond
    current_datetime = datetime.now()
    # .%f responsible for microseconds, all the way up to %Y for the year
    formatted_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime_string

def reverse_button(button: tk.Button) -> None:
    if button['state'] == tk.NORMAL:
        button['state'] = tk.DISABLED
    else:
        button['state'] = tk.NORMAL

def reverse_many_buttons(buttons: tuple) -> None:
    for button in buttons:
        reverse_button(button)

# Check whether a socket still exists and active, and so can be contacted
# Don't add "my_socket: socket" because then we have to import module 'socket'

def socket_exists_and_active(my_socket) -> bool:
    if my_socket is None:
        return False
    else:
        try:
            my_socket.getpeername()
            # We don't actually need the peer name (other side-socket's name),
            # it will just throw an exception if the checked socket is closed
            return True
        except errors:
            return False

def get_hash(password: str) -> str:
    encoded_password = password.encode(json_format)
    password_hash = sha256(encoded_password).hexdigest()
    logger.info("[PROTOCOL] - Hash made")
    return password_hash


# Commands that should be executed at the start of each program

# Clear log file if it exists

# Define clearer function
def _clear_log():
    _log_file = Path(log_path)
    if _log_file.exists():
        _log_file.write_text('') # Overwrites file with empty string

# Call clearer function
_clear_log()

# Create logger, one logger exists for the entire project, client and server
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=log_path)
logger = logging.getLogger(__name__)
logger.info("[PROTOCOL] - Logger created")
