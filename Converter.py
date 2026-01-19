import protocol
from protocol import log
from os import getenv
import requests
from datetime import datetime

class Converter:
    def __init__(self):
        # Get API key
        api_key = getenv("API_KEY")

        # Request data
        url = f"https://currencyapi.net/api/v1/rates?base={protocol.BASE_CURRENCY}&output=json&key={api_key}"
        response = requests.get(url)
        log("Received currency rates from API")

        self.status_code = response.status_code
        self._rates: dict = {}
        self.time: str = ''
        if self.status_code == 200: # 200 means success
            json_response: dict = response.json()  # Method response.json() returns dict, despite its name
            self._rates = json_response['rates']
            # Convert unix to datetime and then to string
            self.time = datetime.fromtimestamp(json_response['updated']).strftime("%Y-%m-%d %H:%M:%S")
            log(f"Turned currency rates into dictionary, update time {self.time}")
        else:
            raise OSError

    def convert_currencies(self, amount: float, source: str, dest: str) -> float:
        try:
            if source == protocol.BASE_CURRENCY:
                return float(amount) * self._rates[dest]
            if dest == protocol.BASE_CURRENCY:
                return float(amount) / self._rates[source]
            return float(amount) * self._rates[dest] / self._rates[source]
        except (ValueError, IndexError, TypeError, OSError):  # Signals something wrong with the input or the API
            return -1