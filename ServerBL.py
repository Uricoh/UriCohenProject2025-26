# Imports
import protocol
from protocol import log
import threading
import socket
from ClientHandler import ClientHandler
from Converter import Converter
from Emailer import Emailer


class ServerBL:
    def __init__(self):
        self._socket = None
        self._conv = None
        self._emailer = None

    def on_click_start(self):
        # BLA - bind, listen, accept
        log("Start button clicked")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log("Socket created")
        self._socket.bind(protocol.SERVER_ADDRESS)
        log("Socket bound")
        self._socket.listen(5)
        log("Socket listening")
        threading.Thread(target=self.accept, daemon=True).start()
        log("Accept thread started")

        # Create converter and emailer object
        self._conv: Converter = Converter()
        log("Converter object creation complete")
        self._emailer: Emailer = Emailer()
        log("Emailer object creation complete")

    def accept(self):
        # This runs in Thread A, not in main thread
        while True:
            try:
                (client_socket, client_address) = self._socket.accept()
                client_handler: ClientHandler = ClientHandler(client_socket, self._conv, self._emailer)
                threading.Thread(target=client_handler.receive, daemon=True).start()
                log("ClientHandler created")
                log(f"Client accepted, IP: {client_address}")
            except OSError:
                pass

    def on_click_stop(self):
        log("Stop button clicked")
        log("DB connection closed")
        self._socket.close()
        self._emailer.close()
        log("Server closed")
