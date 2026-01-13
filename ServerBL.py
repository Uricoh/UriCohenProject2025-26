# Imports
import protocol
from protocol import log
import threading
import socket
import requests
from os import getenv
from dotenv import load_dotenv
from ClientHandler import ClientHandler


class ServerBL:
    def __init__(self):
        self._socket = None
        self._currency_rates = None

    def on_click_start(self):
        # BLA - bind, listen, accept
        log("Start button clicked")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log("Socket created")
        self._socket.bind((protocol.SERVER_IP, protocol.PORT))
        log("Socket bound")
        self._socket.listen(5)
        log("Socket listening")
        threading.Thread(target=self.accept, daemon=True).start()
        log("Accept thread started")

        # Get currency rates
        self._currency_rates = self.request_from_api()

    def accept(self):
        # This runs in Thread A, not in main thread
        while True:
            try:
                (client_socket, client_address) = self._socket.accept()
                client_handler: ClientHandler = ClientHandler(client_socket, self._currency_rates)
                threading.Thread(target=client_handler.receive, daemon=True).start()
                log("ClientHandler created")
                log(f"Client accepted, IP: {client_address}")
            except OSError:
                pass

    def request_from_api(self) -> dict:
        # Load .env file
        load_dotenv()

        # Get API key
        api_key = getenv("API_KEY")

        # Request data
        url = f"https://currencyapi.net/api/v1/rates?base={protocol.BASE_CURRENCY}&output=json&key={api_key}"
        response = requests.get(url)
        log("Received currency rates from API")

        # Convert response to tuple
        if response.status_code == 200:  # 200 means success
            json_response: dict = response.json()  # Method response.json() returns dict, despite its name
            log("Turned currency rates into dictionary")
            return json_response
        else:
            raise OSError

    def on_click_stop(self):
        log("Stop button clicked")
        log("DB connection closed")
        self._socket.close()
        log("Server closed")
