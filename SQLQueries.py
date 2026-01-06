# This file is not part of the project and is only used by the developer to modify the table
import dbprotocol
import protocol
from protocol import log

# WARNING: The following functions (update_() and un_update_emails()) will DELETE any actual emails from the database
def update_emails():
    user_count: int = dbprotocol.cursor.execute(f"SELECT COUNT(*) FROM {protocol.USER_TBL}").fetchone()[0] + 1
    for user in range(1, user_count):
        dbprotocol.cursor.execute(f"UPDATE {protocol.USER_TBL} SET email = '{f'{user}@gmail.com'}' WHERE id = {user}")
        dbprotocol.conn.commit()

def un_update_emails():
    user_count: int = dbprotocol.cursor.execute(f"SELECT COUNT(*) FROM {protocol.USER_TBL}").fetchone()[0] + 1
    for user in range(1, user_count):
        dbprotocol.cursor.execute(f"UPDATE {protocol.USER_TBL} SET email = 'EXAMPLE' WHERE id = {user}")
        dbprotocol.conn.commit()

def set_password(user_id: int, password: str):
    dbprotocol.cursor.execute(f'''UPDATE {protocol.USER_TBL} SET password = '{protocol.get_hash(password)}'
        WHERE id = {user_id}''')
    dbprotocol.conn.commit()

def set_email(user_id: int, email: str):
    dbprotocol.cursor.execute(f'''UPDATE {protocol.USER_TBL} SET email = '{email}' WHERE id = {user_id}''')
    dbprotocol.conn.commit()

def see_entire_user_tbl():
    rows = dbprotocol.cursor.execute(f"SELECT * FROM {protocol.USER_TBL}").fetchall()
    for row in rows:
        print(row)


update_emails()
see_entire_user_tbl()
dbprotocol.conn.close()
log("DB connection closed")
