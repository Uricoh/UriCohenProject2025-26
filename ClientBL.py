import protocol
import socket


class ClientBL:
    def __init__(self):
        self.socket: socket = None

    def on_click_start(self):
        # Login start button
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        protocol.logger.info("[CLIENTBL] - Client socket created")
        protocol.logger.info("[CLIENTBL] - Start button clicked")
        self.socket.connect((protocol.SERVER_IP, protocol.PORT))
        protocol.logger.info("[CLIENTBL] - Client connected to server")

    def on_click_stop(self):
        # Both login and main stop buttons
        protocol.logger.info("[CLIENTBL] - Stop button clicked")
        self.socket.close()
        protocol.logger.info("[CLIENTBL] - Client socket closed")

    def send_data(self, data):
        self.socket.sendall(data.encode(protocol.json_format))
        protocol.logger.info("[CLIENTBL] - Data sent to server")
