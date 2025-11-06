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
        self._client_socket_list = []
        self._client_socket = None
        self._receive_thread_list = []

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
            (self._client_socket, client_address) = self._socket.accept()
            self._client_socket_list.append(self._client_socket)
            self._receive_thread_list.append(threading.Thread(target=self.receive, daemon=True, args=[self._client_socket_list.index(self._client_socket)]))
            self._receive_thread_list[-1].start()
            self._logger.info(f"[SERVERBL] - Client accepted, IP: {client_address}")

    def receive(self, client_id: int):
        while True:
            data = self._client_socket_list[client_id].recv(1024)
            user_data = json.loads(data.decode('utf-8'))
            self._logger.info(f"[SERVERBL] - Data received, Username: {user_data[0]}, Password: {user_data[1]}")

    def on_click_stop(self):
        self._logger.info("[SERVERBL] - Stop button clicked")
        self._socket.close()
        self._logger.info("[SERVERBL] - Server closed")
