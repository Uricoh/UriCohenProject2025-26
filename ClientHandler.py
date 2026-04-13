import json
import protocol
from protocol import log
from secrets import randbelow
from threading import Thread
import time


# One ClientHandler exists per client
class ClientHandler:
    def __init__(self, _client_ip, _client_socket, _server_bl):
        self._client_ip = _client_ip
        self.client_socket = _client_socket
        self._server_bl = _server_bl

        self._username = protocol.GUEST_USERNAME

        # self._email and self._code are used for resetting passwords
        self._email = None
        self._code = None

    def receive(self):
        # This method runs in a special thread, unique for each client, created by Thread A on ServerBL
        conn, cursor = protocol.connect_to_db()
        while True:
            try:
                data = self.client_socket.recv(protocol.BUFFER_SIZE).decode(protocol.ENCODE_FORMAT)
                if not data:
                    continue
                user_data = json.loads(data)

                if user_data[0] == "SIGNUP":
                    user_exists = cursor.execute(f'''SELECT * FROM {protocol.USER_TBL_NAME} WHERE username = ?
                    ''', (user_data[1], )).fetchone()

                    if user_exists:
                        self.client_socket.sendall("SIGNUPFAIL".encode(protocol.ENCODE_FORMAT))
                        log("Signup fail message sent")

                    else:
                        # Prevent SQL injection
                        cursor.execute(f'''INSERT INTO {protocol.USER_TBL_NAME}
                                           ("username", "password", "datetime", "email") VALUES (?, ?, ?, ?)''',
                                       (user_data[1], user_data[2], protocol.get_time_as_text(),
                                        user_data[3]))
                        conn.commit()  # Commit after changing DB

                        log(f"Signup done, Username: {user_data[1]}")
                        self._username = user_data[1]

                        history = self._get_history()
                        stocks = self._get_stocks()
                        return_data = ["SIGNUP", history, stocks]
                        json_data = protocol.make_json(return_data)
                        self.client_socket.sendall(json_data.encode(protocol.ENCODE_FORMAT))
                        log(f"Data entered, Username: {user_data[1]}")
                        log(f"Data entered, Password (hash): {user_data[2][:5]}...")
                        log(f"Data entered, Email: {user_data[3]}")

                elif user_data[0] == "LOGIN":
                    # Prevent SQL injection
                    result = cursor.execute(
                        f"SELECT * FROM {protocol.USER_TBL_NAME} WHERE username = ? AND password = ?",
                        (user_data[1], user_data[2])).fetchone()
                    # No need for commit because DB hasn't been changed

                    if result: # If such account found
                        log(f"Login done, Username: {user_data[1]}")
                        self._username = user_data[1]

                        history = self._get_history()
                        stocks = self._get_stocks()
                        return_data = ["LOGIN", history, stocks]
                        json_data = protocol.make_json(return_data)
                        self.client_socket.sendall(json_data.encode(protocol.ENCODE_FORMAT))
                        log("Login success message sent")
                    else:
                        log(f"Login failed, Username: {user_data[1]}")
                        self.client_socket.sendall("LOGINFAIL".encode(protocol.ENCODE_FORMAT))
                        log("Login fail message sent")

                elif user_data[0] == "FORGOTEMAIL":
                    # Forgot password, stage 1
                    # Get email
                    log("Server received forgot password: email part")
                    self._email = user_data[1]
                    log(f"Email logged, {self._email}")

                    # Search for account with the email
                    result = cursor.execute(
                        f"SELECT * FROM {protocol.USER_TBL_NAME} WHERE email = ?",
                        (self._email,)).fetchone()
                    # No need for commit because DB hasn't been changed

                    if not result: # If such account not found
                        self.client_socket.sendall("FORGOTEMAILFAIL".encode(protocol.ENCODE_FORMAT))
                        log("Forgot password email fail message sent")
                        continue

                    self.client_socket.sendall("FORGOTEMAIL".encode(protocol.ENCODE_FORMAT))

                    # Generate verification code
                    self._code = f"{randbelow(10 ** protocol.SEC_CODE_LENGTH)}"
                    while len(self._code) < protocol.SEC_CODE_LENGTH:
                        self._code = "0" + self._code

                    # Create email message without exceeding 120-char best practice
                    email_msg = f"Hello. Your verification code is {self._code}"
                    email_msg += ". Enter this code to reset the password."
                    email_subject = "Reset password"

                    # Send email
                    self._server_bl.emailer.send_email(self._email, email_subject, email_msg)
                    log("Forgot password email success message sent to client")
                    log("Password reset code sent to user by email")

                elif user_data[0] == "FORGOTCODE":
                    # Forgot password, stage 2
                    if user_data[1] == self._code:
                        self.client_socket.sendall("FORGOTCODE".encode(protocol.ENCODE_FORMAT))
                    else:
                        self.client_socket.sendall("FORGOTCODEFAIL".encode(protocol.ENCODE_FORMAT))
                        log("Forgot password code fail message sent")

                elif user_data[0] == "FORGOTSETPASSWORD":
                    # Forgot password, stage 3
                    cursor.execute(f"UPDATE {protocol.USER_TBL_NAME} SET password = ? WHERE email = ?",
                                   (user_data[1], self._email))
                    self.client_socket.sendall("FORGOTSETPASSWORD".encode(protocol.ENCODE_FORMAT))
                    conn.commit()
                    log("Password reset")

                elif user_data[0] == "STOCKS":
                    self._send_stocks()
                    Thread(target=self._send_stocks_hourly, daemon=True).start()


                elif user_data[0] == "BUY":
                    # Data
                    company_name = user_data[1]
                    user_id = cursor.execute(f"SELECT * FROM {protocol.USER_TBL_NAME} WHERE username = ?",
                                             (self._username,)).fetchone()[0]
                    entry = cursor.execute(
                        f"SELECT * FROM {protocol.STOCKS_TBL_NAME} WHERE userid = ? AND companyname = ?",

                        (user_id, company_name)).fetchone()

                    if entry: # Used to check if there is such stock exists for the user
                        cursor.execute(
                            f"UPDATE {protocol.STOCKS_TBL_NAME} SET amount = amount + 1 WHERE userid = ? AND companyname = ?",
                            (user_id, company_name))
                    else:
                        cursor.execute(
                            f"INSERT INTO {protocol.STOCKS_TBL_NAME} (userid, companyname, amount) VALUES (?, ?, 1)",
                            (user_id, company_name))

                    conn.commit()

                    log(f"Stock {company_name} bought successfully")

                elif user_data[0] == "SELL":
                    # Data
                    company_name = user_data[1]
                    user_id = cursor.execute(f"SELECT * FROM {protocol.USER_TBL_NAME} WHERE username = ?",
                                             (self._username,)).fetchone()[0]

                    # Used to check if there is such stocks exist for the user, and then check the amount of such stocks
                    entry = cursor.execute(
                        f"SELECT * FROM {protocol.STOCKS_TBL_NAME} WHERE userid = ? AND companyname = ?",
                        (user_id, company_name)).fetchone()

                    if entry:
                        if entry[3] == 1:
                            cursor.execute(f'''DELETE FROM {protocol.STOCKS_TBL_NAME}
                                               WHERE userid = ? AND companyname = ?''', (user_id, company_name))
                        else:
                            cursor.execute(f'''UPDATE {protocol.STOCKS_TBL_NAME} SET amount = amount - 1
                                                   WHERE userid = ? AND companyname = ?''', (user_id, company_name))
                        conn.commit()

                        log(f"Stock {company_name} sold successfully")

                elif user_data[0] == "CONVERT":
                    log("Server received convert message")

                    # Data
                    source = user_data[1]
                    dest = user_data[2]
                    amount = user_data[3]

                    # Calculate
                    rate = self._server_bl.currency_provider.convert_currencies(amount, source, dest)
                    if rate < 0:
                        result: str = protocol.ERROR_MSG
                    else:
                        result: str = f"{amount} {source} = {round(rate, 2)} {dest}"

                    # Add to convert table
                    if self._username != protocol.GUEST_USERNAME:
                        user_id = cursor.execute(f'''SELECT * FROM {protocol.USER_TBL_NAME} WHERE username = ?''',
                                                (self._username, )).fetchone()[0]
                        cursor.execute(f'''INSERT INTO {protocol.CONVERT_TBL_NAME}
                                        (userid, amount, source, result, dest) VALUES (?, ?, ?, ?, ?)''',
                                       (user_id, amount, source, rate, dest))
                        conn.commit()

                    self.client_socket.sendall(result.encode(protocol.ENCODE_FORMAT))
                    log(f"Result message sent: {result}")

            except OSError:
                log("Client disconnected")

                # Remove client from client list
                for client in self._server_bl.client_list.copy():
                    if self._client_ip in client:
                        self._server_bl.client_list.remove(client)
                        log("Stopped client removed from list")
                        break # Only one connection may exist per IP address

                self.client_socket.close()
                conn.close()
                log("DB connection closed")
                break

            except Exception as e:
                log(str(e))

    def _get_history(self) -> list[list]:
        cursor = protocol.connect_to_db()[1]
        user_id = cursor.execute(f'''SELECT * FROM {protocol.USER_TBL_NAME} WHERE username = ?''',
                                                (self._username, )).fetchone()[0]

        table_history = cursor.execute(f'''SELECT * FROM {protocol.CONVERT_TBL_NAME}
                                            WHERE userid = {user_id}''').fetchall()

        # Cut the first two columns, because they only represent IDs and are thus not needed
        cut_history = []
        for row in table_history:
            cut_history.append(row[2:])

        # Arrange columns by order shown in GUI
        arranged_history = []
        for row in cut_history:
            arranged_row = [row[1], row[3], row[0], row[2]]
            arranged_history.append(arranged_row)
        log(f"Fetched user #{user_id} history")

        return arranged_history

    def _get_stocks(self) -> list[list]:
        cursor = protocol.connect_to_db()[1]
        user_id = cursor.execute(f'''SELECT * FROM {protocol.USER_TBL_NAME} WHERE username = ?''',
                                 (self._username,)).fetchone()[0]

        table_stocks = cursor.execute(f'''SELECT * FROM {protocol.STOCKS_TBL_NAME}
                                                    WHERE userid = {user_id}''').fetchall()

        # Cut the first column, because it only represents ID and are thus not needed
        cut_stocks = []
        for row in table_stocks:
            cut_stocks.append(row[2:])

        log(f"Fetched user #{user_id} history")

        return cut_stocks

    def _send_stocks(self) -> None:
        stocks_data = ["STOCKS", self._server_bl.stocks_provider.companies]
        json_data = protocol.make_json(stocks_data)
        self.client_socket.sendall(f"{protocol.LARGE_SYMBOL}{json_data}{protocol.END_SYMBOL}"
                                   .encode(protocol.ENCODE_FORMAT))
        log("Stock values sent")

    def _send_stocks_hourly(self) -> None:
        current_unix_time: int = int(time.time())

        # Calculate next update time
        # Wait 6 minutes after next XX:00 so API has time to update
        next_update_time = current_unix_time // 3600 * 3600 + 3960

        diff = next_update_time - current_unix_time
        log(f"Stock data will be sent again in {diff // 60}:{diff % 60}")
        time.sleep(diff)
        self._send_stocks()
