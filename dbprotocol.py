import protocol
import sqlite3

conn = sqlite3.connect(protocol.db_name, check_same_thread=False)
cursor = conn.cursor()
cursor.execute(f'''CREATE TABLE IF NOT EXISTS {protocol.tbl_name} (
                                id INTEGER PRIMARY KEY,
                                username TEXT NOT NULL,
                                password TEXT NOT NULL,
                                datetime TEXT NOT NULL)
                                ''')
protocol.logger.info("[DBPROTOCOL] - SQL connection established")