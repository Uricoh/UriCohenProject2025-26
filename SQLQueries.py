"""
THIS FILE IS NOT PART OF THE PROJECT AND IS ONLY USED BY THE DEVELOPER TO MODIFY THE TABLE FOR PRACTICE WITH SQL;
THIS FILE CONTAINS UNSAFE CODE AND HENCE IS NOT USED IN THE PROJECT
"""
import protocol
from protocol import log

# WARNING: The following functions (update_() and un_update_emails()) will DELETE any actual emails from the database
def update_emails():
    user_count: int = cursor.execute(f"SELECT COUNT(*) FROM {protocol.USER_TBL_NAME}").fetchone()[0] + 1
    for user in range(1, user_count):
        cursor.execute(f"UPDATE {protocol.USER_TBL_NAME} SET email = '{f'{user}@gmail.com'}' WHERE id = {user}")
        conn.commit()

def un_update_emails():
    user_count: int = cursor.execute(f"SELECT COUNT(*) FROM {protocol.USER_TBL_NAME}").fetchone()[0] + 1
    for user in range(1, user_count):
        cursor.execute(f"UPDATE {protocol.USER_TBL_NAME} SET email = 'EXAMPLE' WHERE id = {user}")
        conn.commit()

def set_field(user_id: int, field_name: str, field_value):
    # Get list of all field names
    field_names: list[str] = []
    data = cursor.execute(f"SELECT * FROM {protocol.USER_TBL_NAME}")
    for column in data.description:
        field_names.append(column[0])

    # Set the field value accordingly if it exists, else print error indicating it doesn't exist
    if field_name in field_names:
        cursor.execute(f'''UPDATE {protocol.USER_TBL_NAME} SET {field_name} = '{field_value}' WHERE id = {user_id}''')
        conn.commit()
    else:
        print("Field name does not exist")

def see_entire_user_tbl():
    rows = cursor.execute(f"SELECT * FROM {protocol.USER_TBL_NAME}").fetchall()
    for row in rows:
        print(row)


conn, cursor = protocol.connect_to_db()
update_emails()
see_entire_user_tbl()
conn.close()
log("DB connection closed")
