import protocol
from protocol import log
import sqlite3

# One connection exists for the entire project, should only be imported and accessed by server files
# check_same_thread=False so the entire project can access from all threads
conn = sqlite3.connect(protocol.db_name, check_same_thread=False)
cursor = conn.cursor()
cursor.execute(f'''CREATE TABLE IF NOT EXISTS {protocol.user_tbl} (
                                id INTEGER PRIMARY KEY,
                                username TEXT NOT NULL,
                                password TEXT NOT NULL,
                                datetime TEXT NOT NULL)
                                ''')
log("SQL connection established")
