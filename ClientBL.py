import protocol
from protocol import log
import socket


class ClientBL:
    def __init__(self):
        self.socket = None

    def on_open(self):
        # When client window is open
        log("Client opened")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log("Client socket created")
        self.socket.connect(protocol.SERVER_ADDRESS)
        log("Client connected to server")

    def on_close(self):
        # When client window is closed
        self.socket.close()
        log("Client socket closed")

    def send_data(self, data):
        self.socket.sendall(data.encode(protocol.ENCODE_FORMAT))
        log("Data sent to server")
