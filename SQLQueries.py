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


update_emails()
