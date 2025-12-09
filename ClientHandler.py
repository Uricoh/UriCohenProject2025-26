import json
import protocol
import dbprotocol


# One ClientHandler exists per client
class ClientHandler:
    def __init__(self, _client_socket):
        self._client_socket = _client_socket

    def receive(self):
        # This method runs in a special thread, unique for each client, created by Thread A on ServerBL
        try:
            while True:
                data = self._client_socket.recv(1024).decode(protocol.json_format)
                if data:
                    user_data = json.loads(data)

                    if user_data[0] == "SIGNUP":
                        # Prevent SQL injection
                        dbprotocol.cursor.execute(f'''INSERT INTO {protocol.user_tbl}
                                                  ("username", "password", "datetime", "email") VALUES (?, ?, ?, ?)''',
                                                  (user_data[1], user_data[2], protocol.get_time_as_text(),
                                                   user_data[3]))
                        dbprotocol.conn.commit()  # Commit after changing DB
                        self._client_socket.sendall("SIGNUP".encode(protocol.json_format))
                        protocol.logger.info(f"[CLIENTHANDLER] - Data entered, Username: {user_data[1]}")
                        protocol.logger.info(f"[CLIENTHANDLER] - Data entered, Password (hash): {user_data[2][:5]}...")
                        protocol.logger.info(f"[CLIENTHANDLER] - Data entered, Email: {user_data[3]}")

                    if user_data[0] == "LOGIN":
                        # Prevent SQL injection
                        result = dbprotocol.cursor.execute(
                            f"SELECT * FROM {protocol.user_tbl} WHERE username = ? AND password = ?",
                            (user_data[1], user_data[2])).fetchone()
                        if result:
                            protocol.logger.info(
                                f'''[CLIENTHANDLER] - Login attempt successful, Username: {user_data[1]}''')
                            self._client_socket.sendall("LOGIN".encode(protocol.json_format))
                            protocol.logger.info("[CLIENTHANDLER] - Login message sent")
                            # No need for commit because DB hasn't been changed

                else:
                    protocol.logger.info("[CLIENTHANDLER] - Client disconnected")
                    self._client_socket.close()
                    break

        except protocol.errors:
            # Exists to ignore the exception shown when the client is stopped but socket.recv() is still active
            pass
