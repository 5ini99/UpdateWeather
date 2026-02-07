# app/state.py
import threading
import datetime

class AppState:
    def __init__(self):
        self.lock = threading.RLock()

        self.is_refreshing = False
        self.last_refresh_time: datetime.datetime | None = None
        self.next_refresh_time: datetime.datetime | None = None

        self.refresh_interval_minutes = 60
        self.skip_night = True   # 23–7 点
        self.night_start = 23
        self.night_end = 7

        self.key = ""
        self.location = ""

    def snapshot(self):
        with self.lock:
            return {
                "is_refreshing": self.is_refreshing,
                "last_refresh_time": self.last_refresh_time,
                "next_refresh_time": self.next_refresh_time,
                "interval": self.refresh_interval_minutes,
                "skip_night": self.skip_night,
            }

STATE = AppState()
