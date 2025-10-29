import protocol
import logging
import threading
import socket
import json


class ServerBL:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="log.log")
        self._logger = logging.getLogger(__name__)
        self._socket = None
        self._client_socket = None
        self._receive_thread = None

    def on_click_start(self):
        self._logger.info("[SERVERBL] - Start button clicked")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger.info("[SERVERBL] - Socket created")
        self._socket.bind((protocol.SERVER_IP, protocol.PORT))
        self._logger.info("[SERVERBL] - Socket bound")
        self._socket.listen(5)
        self._logger.info("[SERVERBL] - Socket listening")
        accept_thread = threading.Thread(target=self.accept, daemon=True)
        accept_thread.start()
        self._logger.info("[SERVERBL] - Accept thread started")
        self._receive_thread = threading.Thread(target=self.receive, daemon=True)

    def accept(self):
        while True:
            (self._client_socket, client_address) = self._socket.accept()
            self._receive_thread.start()
            self._logger.info(f"[SERVERBL] - Client accepted, IP: {client_address}")

    def receive(self):
        while True:
            data = self._client_socket.recv(1024)
            self._logger.info("[SERVERBL] - Data received")
            user_data = json.loads(data.decode('utf-8'))
            self._logger.info(f"[SERVERBL] - Data received, Username: {user_data[0]}, Password: {user_data[1]}")

    def on_click_stop(self):
        self._logger.info("[SERVERBL] - Stop button clicked")
        self._socket.close()
        self._logger.info("[SERVERBL] - Server closed")
