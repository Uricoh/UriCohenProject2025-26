import protocol
import threading
import socket
from ClientHandler import ClientHandler
import dbprotocol


class ServerBL:
    def __init__(self):
        self._socket = None
        # These properties may be used in the future, if not please delete
        self._client_handler_list = []
        self._client_thread_list = []

    def on_click_start(self):
        # BLA - bind, listen, accept
        protocol.logger.info("[SERVERBL] - Start button clicked")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        protocol.logger.info("[SERVERBL] - Socket created")
        self._socket.bind((protocol.SERVER_IP, protocol.PORT))
        protocol.logger.info("[SERVERBL] - Socket bound")
        self._socket.listen(5)
        protocol.logger.info("[SERVERBL] - Socket listening")
        threading.Thread(target=self.accept, daemon=True).start()
        protocol.logger.info("[SERVERBL] - Accept thread started")

    def accept(self):
        # This runs in Thread A, not in main thread
        while True:
            try:
                (client_socket, client_address) = self._socket.accept()
                client_handler: ClientHandler = ClientHandler(client_socket)
                self._client_handler_list.append(client_handler)
                client_thread = threading.Thread(target=client_handler.receive, daemon=True).start()
                self._client_thread_list.append(client_thread)
                protocol.logger.info(f"[SERVERBL] - ClientHandler created")
                protocol.logger.info(f"[SERVERBL] - Client accepted, IP: {client_address}")
            except OSError:
                pass

    def on_click_stop(self):
        protocol.logger.info("[SERVERBL] - Stop button clicked")
        # Close DB connection, only time when connection is closed and only use of import dbprotocol
        dbprotocol.conn.close()
        protocol.logger.info("[SERVERBL] - DB connection closed")
        self._socket.close()
        protocol.logger.info("[SERVERBL] - Server closed")
