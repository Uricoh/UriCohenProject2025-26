import protocol
import threading
import socket
import ClientHandler
import dbprotocol


class ServerBL:
    def __init__(self):
        self._socket = None
        # These properties may be used in the future, if not please delete
        self._client_handler_list = []
        self._client_handler_thread_list = []

    def on_click_start(self):
        # BLA - bind, listen, accept
        protocol.logger.info("[SERVERBL] - Start button clicked")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        protocol.logger.info("[SERVERBL] - Socket created")
        self._socket.bind((protocol.SERVER_IP, protocol.PORT))
        protocol.logger.info("[SERVERBL] - Socket bound")
        self._socket.listen(5)
        protocol.logger.info("[SERVERBL] - Socket listening")
        accept_thread = threading.Thread(target=self.accept, daemon=True)
        protocol.logger.info("[SERVERBL] - Accept thread started")
        accept_thread.start()

    def accept(self):
        # This runs in Thread A, not in main thread
        while True:
            try:
                (client_socket, client_address) = self._socket.accept()
                self.create_accept_thread(client_socket)
                protocol.logger.info(f"[SERVERBL] - Client accepted, IP: {client_address}")
            finally:
                # Ignore errors
                break

    def create_accept_thread(self, client_socket):
        # This, create_client_handler, and ClientHandler run in Thread B, C...
        # (one thread per client), not in main thread
        self._client_handler_thread_list.append(threading.Thread(target=self.create_client_handler, daemon=True,
                                                                 args=[client_socket]))
        self._client_handler_thread_list[-1].start()
        protocol.logger.info(f"[SERVERBL] - ClientHandler created")

    def create_client_handler(self, client_socket):
        # This, create_accept_thread, and ClientHandler run in Thread B, C...
        # (one thread per client), not in main thread
        client_handler: ClientHandler = ClientHandler.ClientHandler(client_socket)
        self._client_handler_list.append(client_handler)

    def on_click_stop(self):
        protocol.logger.info("[SERVERBL] - Stop button clicked")
        # Close DB connection, only time when connection is closed and only use of import dbprotocol
        dbprotocol.conn.close()
        self._socket.close()
        protocol.logger.info("[SERVERBL] - Server closed")
