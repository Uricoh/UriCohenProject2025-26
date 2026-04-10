from abc import ABC, abstractmethod
from threading import Thread
from protocol import log
import time

class Provider(ABC): # Template for all classes that communicate with a data API
    # One provider of every type is always used
    def __init__(self):
        self._status_code = None
        self._time: str = ''

        Thread(target=self.update_hourly, daemon=True).start()

    @abstractmethod
    def _fetch_data(self):
        pass

    def update_hourly(self):
        while True:
            current_unix_time: int = int(time.time())

            # Calculate next update time
            # Wait 5 minutes after next XX:00 so API has time to update
            next_update_time = current_unix_time // 3600 * 3600 + 3900

            diff = next_update_time - current_unix_time
            log(f"Provider will sleep for {diff // 60}:{diff % 60}")
            time.sleep(diff)
            self._fetch_data()