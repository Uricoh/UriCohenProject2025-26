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
                data = self._client_socket.recv(protocol.BUFFER_SIZE).decode(protocol.ENCODE_FORMAT)
                if data:
                    user_data = json.loads(data)

                    if user_data[0] == "SIGNUP":
                        username = dbprotocol.cursor.execute(f'''SELECT * FROM {protocol.USER_TBL} WHERE username = ?
                        ''', (user_data[1], )).fetchone()

                        if username: # If username already exists
                            self._client_socket.sendall("SIGNUPFAIL".encode(protocol.ENCODE_FORMAT))
                            log("Signup fail message sent")

                        else:
                            # Prevent SQL injection
                            dbprotocol.cursor.execute(f'''INSERT INTO {protocol.USER_TBL}
                                                    ("username", "password", "datetime", "email") VALUES (?, ?, ?, ?)'''
                                                      , (user_data[1], user_data[2], protocol.get_time_as_text(),
                                                         user_data[3]))
                            dbprotocol.conn.commit()  # Commit after changing DB
                            self._client_socket.sendall("SIGNUP".encode(protocol.ENCODE_FORMAT))
                            log(f"Data entered, Username: {user_data[1]}")
                            log(f"Data entered, Password (hash): {user_data[2][:5]}...")
                            log(f"Data entered, Email: {user_data[3]}")

                    elif user_data[0] == "LOGIN":
                        # Prevent SQL injection
                        result = dbprotocol.cursor.execute(
                            f"SELECT * FROM {protocol.USER_TBL} WHERE username = ? AND password = ?",
                            (user_data[1], user_data[2])).fetchone()
                        # No need for commit because DB hasn't been changed

                        if result: # If such account found
                            log(f"Login done, Username: {user_data[1]}")
                            self._client_socket.sendall("LOGIN".encode(protocol.ENCODE_FORMAT))
                            log("Login success message sent")
                        else:
                            log("Login failed, Username: {user_data[1]}")
                            self._client_socket.sendall("LOGINFAIL".encode(protocol.ENCODE_FORMAT))
                            log("Login fail message sent")

                    elif user_data[0] == "FORGOTEMAIL":
                        # Forgot password, stage 1
                        # Get email
                        log("Server received forgot password: email part")
                        self._email = user_data[1]
                        log(f"Email logged, {self._email}")

                        # Search for account with the email
                        result = dbprotocol.cursor.execute(
                            f"SELECT * FROM {protocol.USER_TBL} WHERE email = ?",
                            (self._email,)).fetchone()
                        # No need for commit because DB hasn't been changed

                        if result: # If such account found
                            self._client_socket.sendall("FORGOTEMAIL".encode(protocol.ENCODE_FORMAT))

                            # Generate verification code
                            self._code = f"{randbelow(10 ** protocol.SEC_CODE_LENGTH)}"
                            while len(self._code) < 6:
                                self._code = "0" + self._code

                            # Create email message without exceeding 120-char best practice
                            email_msg = f"Hello. Your verification code is {self._code}"
                            email_msg += ". Enter this code to reset the password."
                            email_subject = "Reset password"

                            # Send email
                            protocol.send_email(self._email, email_subject, email_msg)
                            log("Forgot password email success message sent to client")
                            log("Password reset code sent to user by email")
                        else:
                            self._client_socket.sendall("FORGOTEMAILFAIL".encode(protocol.ENCODE_FORMAT))
                            log("Forgot password email fail message sent")

                    elif user_data[0] == "FORGOTCODE":
                        # Forgot password, stage 2
                        if user_data[1] == self._code:
                            self._client_socket.sendall("FORGOTCODE".encode(protocol.ENCODE_FORMAT))
                        else:
                            self._client_socket.sendall("FORGOTCODEFAIL".encode(protocol.ENCODE_FORMAT))
                            log("Forgot password code fail message sent")

                    elif user_data[0] == "FORGOTSETPASSWORD":
                        # Forgot password, stage 3
                        dbprotocol.cursor.execute(
                            f"UPDATE {protocol.USER_TBL} SET password = ? WHERE email = ?", (user_data[1], self._email))
                        self._client_socket.sendall("FORGOTSETPASSWORD".encode(protocol.ENCODE_FORMAT))
                        dbprotocol.conn.commit()
                        log("Password reset")

                    elif user_data[0] == "CONVERT":
                        log("Server received convert message")
                        result: str = f"{user_data[1]} {user_data[3]} ="
                        self._client_socket.sendall(result.encode(protocol.ENCODE_FORMAT))
                        log("Result message sent")

        except OSError:
            log("Client disconnected")
            self._client_socket.close()
