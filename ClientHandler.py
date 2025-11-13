import json
import protocol
import sqlite3


class ClientHandler:
    def __init__(self, _client_socket, _logger):
        self._client_socket = _client_socket
        self._logger = _logger
        self._conn = sqlite3.connect('database.db')
        self._cursor = self._conn.cursor()
        self._cursor.execute('''CREATE TABLE IF NOT EXISTS USERTBL (
                                     id INTEGER PRIMARY KEY,
                                     username TEXT NOT NULL,
                                     password TEXT NOT NULL,
                                     datetime TEXT NOT NULL)
                                     ''')
        self.receive()

    def receive(self):
        while True:
            data = self._client_socket.recv(1024)
            if data:
                self._logger.info(f"[CLIENTHANDLER] - Data: {data}")
                user_data = json.loads(data.decode('utf-8'))
                self._logger.info(f"[CLIENTHANDLER] - Data received, Username: {user_data[0]}, Password: {user_data[1]}")
                self._cursor.execute(f'''INSERT INTO USERTBL ("username", "password", "datetime") VALUES
                    ('{user_data[0]}', '{user_data[1]}', '{protocol.gettimeastext()}')''')
                self._conn.commit()
                self._logger.info(f"[CLIENTHANDLER] - Data entered, Username: {user_data[0]}, Password: {user_data[1]}")
