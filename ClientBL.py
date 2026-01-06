import protocol
from protocol import log
import socket
from socket import socket


class ClientBL:
    def __init__(self):
        self.socket = None

    def on_click_start(self):
        # Login start button
        self.socket: socket = socket(socket.AF_INET, socket.SOCK_STREAM)
        log("Client socket created")
        log("Start button clicked")
        self.socket.connect((protocol.SERVER_IP, protocol.PORT))
        log("Client connected to server")

    def on_click_stop(self):
        # Both login and main stop buttons
        log("Stop button clicked")
        self.socket.close()
        log("Client socket closed")

    def send_data(self, data):
        self.socket.sendall(data.encode(protocol.ENCODE_FORMAT))
        log("Data sent to server")
