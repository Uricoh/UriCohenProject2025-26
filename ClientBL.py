import protocol
import logging
import socket


class ClientBL:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="log.log")
        self._logger = logging.getLogger(__name__)
        self._socket = None

    def on_click_start(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger.info("[CLIENTBL] - Client socket created")
        self._logger.info("[CLIENTBL] - Start button clicked")
        self._socket.connect((protocol.SERVER_IP, protocol.PORT))
        self._logger.info("[CLIENTBL] - Client connected to server")

    def on_click_stop(self):
        self._logger.info("[CLIENTBL] - Stop button clicked")
        self._socket.close()
        self._logger.info("[CLIENTBL] - Client socket closed")