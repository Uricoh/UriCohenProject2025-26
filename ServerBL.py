# Imports
import protocol
from StocksProvider import StocksProvider
from protocol import log
import threading
import socket
from ClientHandler import ClientHandler
from CurrencyProvider import CurrencyProvider
from Emailer import Emailer


class ServerBL:
    def __init__(self):
        self.client_list = []
        self._client_handler_list = []
        self._socket = None
        self.currency_provider = None
        self.stocks_provider = None
        self.emailer = None

    def on_click_start(self):
        # BLA - Bind, Listen, Accept
        log("Start button clicked")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log("Socket created")
        self._socket.bind(protocol.SERVER_ADDRESS)  # Bind
        log("Socket bound")
        self._socket.listen(5)  # Listen
        log("Socket listening")

        # Create providers and emailer objects
        self.currency_provider = CurrencyProvider()
        self.stocks_provider = StocksProvider()
        self.emailer = Emailer()
        log("Object creations complete")

        threading.Thread(target=self.accept, daemon=True).start()  # Accept
        log("Accept thread started")

    def accept(self):
        # This runs in Thread A, not in main thread
        while True:
            try:
                (client_socket, client_address) = self._socket.accept()
                self.client_list.append((client_address[0], client_address[1], protocol.get_time_as_text()))
                client_handler: ClientHandler = ClientHandler(client_address[0], client_socket, self)
                self._client_handler_list.append(client_handler)
                threading.Thread(target=client_handler.receive, daemon=True).start()
                log(f"ClientHandler created for {client_address}")
                log(f"Client accepted, IP: {client_address}")
            except OSError as e:
                pass

    def on_click_stop(self):
        log("Stop button click identified")
        for handler in self._client_handler_list:
            handler.client_socket.sendall("CLOSE\n".encode(protocol.ENCODE_FORMAT))
        self._socket.close()
        self.emailer.close()
        log("Server closed")
