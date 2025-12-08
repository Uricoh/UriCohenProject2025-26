# This file is not part of the project and is only used by the developer to modify the table
import dbprotocol
import protocol


def get_email_temp(num: int) -> str:
    return f"{num}@gmail.com"


def update_emails():
    for user in range(1, dbprotocol.cursor.execute(f"SELECT COUNT(*) FROM {protocol.user_tbl}").fetchone()[0] + 1):
        dbprotocol.cursor.execute(f"UPDATE {protocol.user_tbl} SET email = '{get_email_temp(user)}' WHERE id = {user}")
        dbprotocol.conn.commit()

def un_update_emails():
    for user in range(1, dbprotocol.cursor.execute(f"SELECT COUNT(*) FROM {protocol.user_tbl}").fetchone()[0] + 1):
        dbprotocol.cursor.execute(f"UPDATE {protocol.user_tbl} SET email = 'null' WHERE id = {user}")
        dbprotocol.conn.commit()

def set_password(user_id: int, password: str):
    dbprotocol.cursor.execute(f'''UPDATE {protocol.user_tbl} SET password = '{protocol.get_hash(password)}'
    WHERE id = {user_id}''')
    dbprotocol.conn.commit()

def see_entire_user_tbl():
    rows = dbprotocol.cursor.execute("SELECT * FROM USERTBL").fetchall()
    for row in rows:
        print(row)


update_emails()
see_entire_user_tbl()
