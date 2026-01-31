import protocol
from protocol import log
from threading import Thread
from os import getenv
import requests
from datetime import datetime
import time

class Converter:
    # One converter for the entire server, same as emailer
    def __init__(self):
        self._status_code = None
        self._time: str = ''
        self._rates: dict = {}

        self._fetch_rates()
        log("Rates fetched")

        Thread(target=self.update_hourly, daemon=True).start()

    def _fetch_rates(self):
        # Get API key
        api_key = getenv("API_KEY")

        # Request data
        url = f"https://currencyapi.net/api/v1/rates?base={protocol.BASE_CURRENCY}&output=json&key={api_key}"
        response = requests.get(url)
        log("Received currency rates from API")

        self._status_code = response.status_code
        self._rates: dict = {}
        self._time: str = ''
        if self._status_code == 200: # 200 means success
            json_response: dict = response.json()  # Method response.json() returns dict, despite its name
            self._rates = json_response['rates']
            # Convert unix to datetime and then to string
            self._time = datetime.fromtimestamp(json_response['updated']).strftime("%Y-%m-%d %H:%M:%S")
            log(f"Turned currency rates into dictionary, local update time {self._time}")
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
        finally:
            log("Value message sent")

    def update_hourly(self):
        while True:
            current_unix_time: int = int(time.time())

            # Calculate next update time
            # Wait 5 minutes after next XX:00 so API has time to update
            next_update_time = current_unix_time // 3600 * 3600 + 3900

            diff = next_update_time - current_unix_time
            log(f"Converter will sleep for {diff // 60}:{diff % 60}")
            time.sleep(diff)
            self._fetch_rates()
