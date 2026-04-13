import protocol
from protocol import log
from os import getenv
import requests
from Provider import Provider
from threading import Thread
import base64

class StocksProvider(Provider):
    def __init__(self):
        # Constructor
        super().__init__()

        # Get API key
        self._api_key = getenv("STOCKS_API_KEY")

        self._received_data = False

        self.companies = [
            {"Symbol": "NVDA", "Name": "Nvidia"},
            {"Symbol": "AAPL", "Name": "Apple"},
            {"Symbol": "GOOGL", "Name": "Alphabet"},
            {"Symbol": "MSFT", "Name": "Microsoft"},
            {"Symbol": "AMZN", "Name": "Amazon"},
            {"Symbol": "META", "Name": "Meta"},
        ]

        self._fetch_data()

    def _fetch_data(self):
        threads = []

        for company in self.companies:
            thread = Thread(target=self._get_data, args=(company, ), daemon=True)
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

    def _get_data(self, company):
        # Request data
        company_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={company['Symbol']}&token={self._api_key}"
        company_response = requests.get(company_url).json()
        item_url = f"https://finnhub.io/api/v1/quote?symbol={company['Symbol']}&token={self._api_key}"
        item_response = requests.get(item_url).json()
        log(f"Received currency rates from both API pages, company {company['Symbol']}")

        # Save data
        company["Price"] = item_response["c"]
        company["Change"] = item_response["dp"]
        company["Market_cap"] = company_response["marketCapitalization"] # Appears in API as millions of US$
        response_logo = requests.get(company_response["logo"])
        bytes_logo = base64.b64encode(response_logo.content)
        company["Encoded_logo"] = bytes_logo.decode(protocol.ENCODE_FORMAT)
