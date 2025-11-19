import json
import protocol
import dbprotocol
import LoginGUI

class ClientHandler:
    def __init__(self, _client_socket):
        self._client_socket = _client_socket
        self.receive()

    def receive(self):
        while True:
            data = self._client_socket.recv(1024).decode('utf-8')
            if data:
                user_data = json.loads(data)
                if user_data[0] == "SIGNUP":
                    protocol.logger.info(f"[CLIENTHANDLER] - Data received, Username: {user_data[1]}, Password: {user_data[2]}")
                    dbprotocol.cursor.execute(f'''INSERT INTO {protocol.tbl_name} ("username", "password", "datetime") VALUES
                        ('{user_data[1]}', '{user_data[2]}', '{protocol.gettimeastext()}')''')
                    dbprotocol.conn.commit()
                    protocol.logger.info(f"[CLIENTHANDLER] - Data entered, Username: {user_data[1]}, Password: {user_data[2]}")
                if user_data[0] == "LOGIN":
                    result = dbprotocol.cursor.execute(f'SELECT * FROM {protocol.tbl_name} WHERE username = ? AND password = ?',(user_data[1], user_data[2])).fetchone()
                    if result:
                        protocol.logger.info(f"Login successful, {user_data[1], user_data[2]}")
                        LoginGUI.runlogin()
