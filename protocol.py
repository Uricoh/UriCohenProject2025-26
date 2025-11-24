import datetime
import logging
from pathlib import Path


# Port commonly used in school, computer firewalls are configured for it so don't change without good reason
PORT: int = 8822

# Means this computer, change to current server IP address to connect to server based in another computer
SERVER_IP: str = "127.0.0.1"


width: int = 1500
height: int = 750
font: tuple = ('Arial', 32)
text_width: int = 20
labels_x: int = 50 # Left
buttons_x: int = 1000 # Right
bg_path: str = "background.jpg"
log_path: str = "log.log"
db_name: str = "database.db"
user_tbl: str = "USERTBL" # Name is user_tbl because there may be more tables


def get_time_as_text() -> str:
    # Gets timestamp as string down to the microsecond
    current_datetime = datetime.datetime.now()
    # .%f responsible for microseconds, all the way up to %Y for the year
    formatted_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
    return formatted_datetime_string


# Commands that should be executed at the start of each program

# Clear log file if it exists
log_file = Path(log_path)
if log_file.exists():
    log_file.write_text("") # Overwrites file with empty string

# Create logger, one logger exists for the entire project, client and server
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename=log_path)
logger = logging.getLogger(__name__)
logger.info("[PROTOCOL] - Logger created")
