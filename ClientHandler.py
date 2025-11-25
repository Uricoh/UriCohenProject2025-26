import json
import protocol
import dbprotocol


# One ClientHandler exists per client
# This class and create_accept_thread and create_client_handler methods of ServerBL run
# in Thread B, C... (as defined in ServerBL, one thread per client), not in main thread
class ClientHandler:
    def __init__(self, _client_socket):
        self._client_socket = _client_socket
        self.receive()

    def receive(self):
        while True:
            try:
                data = self._client_socket.recv(1024).decode('utf-8')
                if data:  # If socket received any data
                    user_data = json.loads(data)
                    if user_data[0] == "SIGNUP":
                        protocol.logger.info(f'''[CLIENTHANDLER] - Data received, Username: {user_data[1]}
                            , Password: {user_data[2]}, Email: {user_data[3]}''')
                        # Prevent SQL injection
                        dbprotocol.cursor.execute(f'''INSERT INTO {protocol.user_tbl}
                                                  ("username", "password", "datetime", "email") VALUES (?, ?, ?, ?)''',
                                                  (user_data[1], user_data[2], protocol.get_time_as_text(),
                                                   user_data[3]))
                        dbprotocol.conn.commit()  # Commit after changing DB
                        self._client_socket.sendall("SIGNUP".encode('utf-8'))
                        protocol.logger.info(f'''[CLIENTHANDLER] - Data entered, Username: {user_data[1]}
                            , Password: {user_data[2]}, Email: {user_data[3]}''')

                    if user_data[0] == "LOGIN":
                        # Prevent SQL injection
                        result = dbprotocol.cursor.execute(
                            f'SELECT * FROM {protocol.user_tbl} WHERE username = ? AND password = ?',
                            (user_data[1], user_data[2])).fetchone()
                        if result:
                            protocol.logger.info(
                                f"[CLIENTHANDLER] - Login attempt successful, Username: {user_data[1]}, Password: {user_data[2]}")
                            self._client_socket.sendall("LOGIN".encode('utf-8'))
                            protocol.logger.info(f"[CLIENTHANDLER] - Login message sent")
                            # No need for commit because DB hasn't been changed
            except OSError:
                # Exists to ignore the exception shown when the client is stopped but socket.recv() is still active
                break
