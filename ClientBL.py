import protocol
import socket


class ClientBL:
    def __init__(self):
        self._socket = None

    def on_click_start(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        protocol.logger.info("[CLIENTBL] - Client socket created")
        protocol.logger.info("[CLIENTBL] - Start button clicked")
        self._socket.connect((protocol.SERVER_IP, protocol.PORT))
        protocol.logger.info("[CLIENTBL] - Client connected to server")

    def on_click_stop(self):
        protocol.logger.info("[CLIENTBL] - Stop button clicked")
        self._socket.close()
        protocol.logger.info("[CLIENTBL] - Client socket closed")

    def get_socket(self):
        return self._socket