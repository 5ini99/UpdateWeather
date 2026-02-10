# app/config.py
from pathlib import Path
import configparser
import threading

# ================== 路径 ==================
USER_CONFIG_DIR = Path.home() / ".update-weather"
USER_CONFIG_DIR.mkdir(exist_ok=True)

CONFIG_PATH = USER_CONFIG_DIR / "config.ini"


# ================== 配置元数据（给 GUI 用） ==================
CONFIG_SCHEMA = {
    "refresh": {
        "interval_minutes": {
            "type": int,
            "default": 60,
            "label": "刷新间隔（分钟）",
            "min": 1,
            "max": 1440,
        },
        "force_refresh_at_midnight": {          # ← 新增这一块
            "type": bool,
            "default": True,                    # 默认开启
            "label": "每天 0 点强制刷新一次",
        }
    },
    "night": {
        "skip_night": {
            "type": bool,
            "default": True,
            "label": "夜间暂停刷新",
        },
        "night_start": {
            "type": int,
            "default": 23,
            "label": "夜间开始时间",
        },
        "night_end": {
            "type": int,
            "default": 7,
            "label": "夜间结束时间",
        },
    },
    "weather": {
        "key": {
            "type": str,
            "default": "",
            "label": "天气 API Key",
        },
        "location": {
            "type": str,
            "default": "",
            "label": "城市 / Location",
        },
    },
    "mail": {
        "enabled": {
            "type": bool,
            "default": False,
            "label": "启用邮件通知",
        },
    },
}


class AppConfig:
    def __init__(self):
        self.lock = threading.RLock()
        self.parser = configparser.ConfigParser()
        self._load_or_init()

    # ================== 初始化 & 兼容老配置 ==================
    def _load_or_init(self):
        if CONFIG_PATH.exists():
            self.parser.read(CONFIG_PATH, encoding="utf-8")

        changed = False
        for section, items in CONFIG_SCHEMA.items():
            if not self.parser.has_section(section):
                self.parser.add_section(section)
                changed = True
            for key, meta in items.items():
                if not self.parser.has_option(section, key):
                    self.parser.set(section, key, str(meta["default"]))
                    changed = True

        if changed:
            self.save()

    # ================== 保存 ==================
    def save(self):
        with self.lock:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                self.parser.write(f)

    # ================== 通用 get / set（GUI 用） ==================
    def get(self, section: str, key: str):
        meta = CONFIG_SCHEMA[section][key]
        with self.lock:
            if meta["type"] is bool:
                return self.parser.getboolean(section, key, fallback=meta["default"])
            if meta["type"] is int:
                return self.parser.getint(section, key, fallback=meta["default"])
            return self.parser.get(section, key, fallback=meta["default"])

    def set(self, section: str, key: str, value):
        with self.lock:
            if isinstance(value, bool):
                value = str(value).lower()
            self.parser.set(section, key, str(value))
            self.save()

    def as_dict(self) -> dict:
        """一次性导出全部配置（GUI 初始化用）"""
        data = {}
        for section, items in CONFIG_SCHEMA.items():
            data[section] = {}
            for key in items:
                data[section][key] = self.get(section, key)
        return data

    # ================== 你原来的 property（完全保留） ==================
    @property
    def refresh_interval_minutes(self) -> int:
        return self.get("refresh", "interval_minutes")

    @property
    def force_refresh_at_midnight(self) -> bool:
        return self.get("refresh", "force_refresh_at_midnight")

    @property
    def skip_night(self) -> bool:
        return self.get("night", "skip_night")

    @property
    def night_start(self) -> int:
        return self.get("night", "night_start")

    @property
    def night_end(self) -> int:
        return self.get("night", "night_end")

    @property
    def weather_key(self) -> str:
        return self.get("weather", "key")

    @property
    def location(self) -> str:
        return self.get("weather", "location")

    @property
    def mail_enabled(self) -> bool:
        return self.get("mail", "enabled")

    # ================== 你原来的 setter（完全保留） ==================
    def set_refresh_interval(self, minutes: int):
        self.set("refresh", "interval_minutes", minutes)

    def set_night_rule(self, skip: bool, start: int, end: int):
        self.set("night", "skip_night", skip)
        self.set("night", "night_start", start)
        self.set("night", "night_end", end)

    def set_weather(self, key: str, location: str):
        self.set("weather", "key", key)
        self.set("weather", "location", location)


# ================== 单例 ==================
CONFIG = AppConfig()
