import json
import protocol
import dbprotocol

class ClientHandler:
    def __init__(self, _client_socket):
        self._client_socket = _client_socket
        self.receive()

    def receive(self):
        while True:
            data = self._client_socket.recv(1024)
            if data:
                protocol.logger.info(f"[CLIENTHANDLER] - Data: {data}")
                user_data = json.loads(data.decode('utf-8'))
                protocol.logger.info(f"[CLIENTHANDLER] - Data received, Username: {user_data[0]}, Password: {user_data[1]}")
                dbprotocol.cursor.execute(f'''INSERT INTO USERTBL ("username", "password", "datetime") VALUES
                    ('{user_data[0]}', '{user_data[1]}', '{protocol.gettimeastext()}')''')
                dbprotocol.conn.commit()
                protocol.logger.info(f"[CLIENTHANDLER] - Data entered, Username: {user_data[0]}, Password: {user_data[1]}")
