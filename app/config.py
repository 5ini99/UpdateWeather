# app/config.py
from pathlib import Path
import configparser
import threading

USER_CONFIG_DIR = Path.home() / ".updateweather"
USER_CONFIG_DIR.mkdir(exist_ok=True)

CONFIG_PATH = USER_CONFIG_DIR / "config.ini"


class AppConfig:
    def __init__(self):
        self.lock = threading.RLock()
        self.parser = configparser.ConfigParser()

        self._load_or_init()

    # ---------- 初始化 ----------
    def _load_or_init(self):
        if not CONFIG_PATH.exists():
            self._init_default()
            self.save()
        else:
            self.parser.read(CONFIG_PATH, encoding="utf-8")
            self._ensure_defaults()

    def _init_default(self):
        self.parser["refresh"] = {
            "interval_minutes": "60",
        }
        self.parser["night"] = {
            "skip_night": "true",
            "night_start": "23",
            "night_end": "7",
        }
        self.parser["weather"] = {
            "key": "",
            "location": "",
        }
        self.parser["mail"] = {
            "enabled": "true",
        }

    def _ensure_defaults(self):
        """老版本配置自动补字段"""
        defaults = {
            "refresh": {
                "interval_minutes": "60",
            },
            "night": {
                "skip_night": "true",
                "night_start": "23",
                "night_end": "7",
            },
            "weather": {
                "key": "",
                "location": "",
            },
            "mail": {
                "enabled": "true",
            },
        }

        changed = False
        for section, items in defaults.items():
            if not self.parser.has_section(section):
                self.parser.add_section(section)
                changed = True
            for k, v in items.items():
                if not self.parser.has_option(section, k):
                    self.parser.set(section, k, v)
                    changed = True

        if changed:
            self.save()

    # ---------- 保存 ----------
    def save(self):
        with self.lock:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                self.parser.write(f)

    # ---------- 读取属性 ----------
    @property
    def refresh_interval_minutes(self) -> int:
        return self.parser.getint("refresh", "interval_minutes", fallback=60)

    @property
    def skip_night(self) -> bool:
        return self.parser.getboolean("night", "skip_night", fallback=True)

    @property
    def night_start(self) -> int:
        return self.parser.getint("night", "night_start", fallback=23)

    @property
    def night_end(self) -> int:
        return self.parser.getint("night", "night_end", fallback=7)

    @property
    def weather_key(self) -> str:
        return self.parser.get("weather", "key", fallback="")

    @property
    def location(self) -> str:
        return self.parser.get("weather", "location", fallback="")

    @property
    def mail_enabled(self) -> bool:
        return self.parser.getboolean("mail", "enabled", fallback=True)

    # ---------- 写入方法（给 GUI 用） ----------
    def set_refresh_interval(self, minutes: int):
        with self.lock:
            self.parser.set("refresh", "interval_minutes", str(minutes))
            self.save()

    def set_night_rule(self, skip: bool, start: int, end: int):
        with self.lock:
            self.parser.set("night", "skip_night", str(skip).lower())
            self.parser.set("night", "night_start", str(start))
            self.parser.set("night", "night_end", str(end))
            self.save()

    def set_weather(self, key: str, location: str):
        with self.lock:
            self.parser.set("weather", "key", key)
            self.parser.set("weather", "location", location)
            self.save()


# 单例
CONFIG = AppConfig()
