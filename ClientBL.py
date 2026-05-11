import socket
import protocol
from protocol import log


class ClientBL:
    def __init__(self):
        self.socket = None

    def on_open(self):
        # When client window is open
        log("Client opened")

        # Create socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            log("Client socket created")
        except OSError as e:
            log(f"Socket creation failed: {e}")

        # Connect to server
        try:
            self.socket.connect(protocol.SERVER_ADDRESS)
            log(f"Client connected to server, at address {protocol.SERVER_ADDRESS}")
        except OSError as e:
            log(f"Connecting failed: {e}")

    def on_close(self):
        # When client window is closed
        if self.socket is not None:
            try:
                self.socket.close()
                self.socket = None
                log("Client socket closed")
            except OSError as e:
                log(f"Closing socket failed: {e}")

    def send_data(self, data: str):
        if self.socket is None:
            raise ConnectionError("Not connected")
        try:
            self.socket.sendall((data + "\n").encode(protocol.ENCODE_FORMAT))
            log("Data sent to server")
        except OSError as e:
            log(f"Sending data failed: {e}")
