import protocol
import logging
import threading
import socket
import ClientHandler


class ServerBL:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="log.log")
        self._logger = logging.getLogger(__name__)
        self._socket = None
        self._client_handler_list = []
        self._client_handler_thread_list = []

    def on_click_start(self):
        self._logger.info("[SERVERBL] - Start button clicked")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger.info("[SERVERBL] - Socket created")
        self._socket.bind((protocol.SERVER_IP, protocol.PORT))
        self._logger.info("[SERVERBL] - Socket bound")
        self._socket.listen(5)
        self._logger.info("[SERVERBL] - Socket listening")
        accept_thread = threading.Thread(target=self.accept, daemon=True)
        self._logger.info("[SERVERBL] - Accept thread started")
        accept_thread.start()

    def accept(self):
        while True:
            try:
                (client_socket, client_address) = self._socket.accept()
                self._logger.info(f"[SERVERBL] - Client accepted, IP: {client_address}")
                self._client_handler_thread_list.append(threading.Thread(target=self.create_accept_thread, daemon=True, args=[client_socket]))
                self._client_handler_thread_list[-1].start()
            finally:
                break

    def create_accept_thread(self, client_socket):
        client_handler: ClientHandler = ClientHandler.ClientHandler(client_socket, self._logger)
        self._client_handler_list.append(client_handler)
        self._logger.info(f"[SERVERBL] - ClientHandler created")

    def on_click_stop(self):
        self._logger.info("[SERVERBL] - Stop button clicked")
        self._socket.close()
        self._logger.info("[SERVERBL] - Server closed")
