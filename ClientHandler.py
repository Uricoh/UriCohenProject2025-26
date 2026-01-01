import json
import protocol
from protocol import log
from secrets import randbelow
import dbprotocol


# One ClientHandler exists per client
class ClientHandler:
    def __init__(self, _client_socket):
        self._client_socket = _client_socket
        # self._email and self._code are used for resetting passwords
        self._email = None
        self._code = None

    def receive(self):
        # This method runs in a special thread, unique for each client, created by Thread A on ServerBL
        try:
            while True:
                data = self._client_socket.recv(1024).decode(protocol.json_format)
                if data:
                    user_data = json.loads(data)

                    if user_data[0] == "SIGNUP":
                        username = dbprotocol.cursor.execute(f'''SELECT * FROM {protocol.user_tbl} WHERE username = ?
                        ''', (user_data[1], )).fetchone()

                        if username:
                            self._client_socket.sendall("SIGNUPFAIL".encode(protocol.json_format))
                            log("Signup fail message sent")

                        else:
                            # Prevent SQL injection
                            dbprotocol.cursor.execute(f'''INSERT INTO {protocol.user_tbl}
                                                    ("username", "password", "datetime", "email") VALUES (?, ?, ?, ?)'''
                                                      , (user_data[1], user_data[2], protocol.get_time_as_text(),
                                                         user_data[3]))
                            dbprotocol.conn.commit()  # Commit after changing DB
                            self._client_socket.sendall("SIGNUP".encode(protocol.json_format))
                            log(f"Data entered, Username: {user_data[1]}")
                            log(f"Data entered, Password (hash): {user_data[2][:5]}...")
                            log(f"Data entered, Email: {user_data[3]}")

                    elif user_data[0] == "LOGIN":
                        # Prevent SQL injection
                        result = dbprotocol.cursor.execute(
                            f"SELECT * FROM {protocol.user_tbl} WHERE username = ? AND password = ?",
                            (user_data[1], user_data[2])).fetchone()
                        # No need for commit because DB hasn't been changed

                        if result:
                            log(f"Login done, Username: {user_data[1]}")
                            self._client_socket.sendall("LOGIN".encode(protocol.json_format))
                            log("Login success message sent")
                        else:
                            log("Login failed, Username: {user_data[1]}")
                            self._client_socket.sendall("LOGINFAIL".encode(protocol.json_format))
                            log("Login fail message sent")

                    elif user_data[0] == "FORGOTEMAIL":
                        log("Server received forgot password: email part")
                        self._email = user_data[1]
                        log(f"Email logged, {self._email}")

                        result = dbprotocol.cursor.execute(
                            f"SELECT * FROM {protocol.user_tbl} WHERE email = ?",
                            (self._email,)).fetchone()
                        # No need for commit because DB hasn't been changed

                        if result:
                            self._client_socket.sendall("FORGOTEMAIL".encode(protocol.json_format))
                            self._code = f"{randbelow(1000000)}"
                            while len(self._code) < 6:
                                self._code = "0" + self._code
                            email_msg = f"Hello. Your verification code is {self._code}. Enter this code to reset the password."
                            email_subject = "Reset password"
                            protocol.send_email(self._email, email_subject, email_msg)
                            log("Forgot password email success message sent to client")
                            log("Password reset code sent to user by email")
                        else:
                            self._client_socket.sendall("FORGOTEMAILFAIL".encode(protocol.json_format))
                            log("Forgot password email fail message sent")

                    elif user_data[0] == "FORGOTCODE":
                        if user_data[1] == self._code:
                            self._client_socket.sendall("FORGOTCODE".encode(protocol.json_format))
                        else:
                            self._client_socket.sendall("FORGOTCODEFAIL".encode(protocol.json_format))
                            log("Forgot password code fail message sent")

                    elif user_data[0] == "FORGOTSETPASSWORD":
                        dbprotocol.cursor.execute(
                            f"UPDATE {protocol.user_tbl} SET password = ? WHERE email = ?", (user_data[1], self._email))
                        self._client_socket.sendall("FORGOTSETPASSWORD".encode(protocol.json_format))
                        dbprotocol.conn.commit()
                        log("Password reset")

                    elif user_data[0] == "CONVERT":
                        log("Server received convert message")
                        result: str = f"{user_data[1]} {user_data[3]} ="
                        self._client_socket.sendall(result.encode(protocol.json_format))
                        log("Result message sent")


        except OSError:
            log("Client disconnected")
            self._client_socket.close()
