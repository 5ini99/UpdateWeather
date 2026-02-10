# app/state_file.py
"""
使用 JSON 文件共享运行状态（解决多进程问题）
"""
import json
from pathlib import Path
import datetime
import time
import os

STATE_DIR = Path.home() / ".update-weather"
STATE_DIR.mkdir(exist_ok=True)

STATE_FILE = STATE_DIR / "state.json"


def load_state():
    """读取状态文件，返回 dict"""
    if not STATE_FILE.exists():
        return {
            "next_refresh_time": None,
            "last_refresh_time": None,
            "config_changed": False,
            # 可加其他字段
        }

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 还原 datetime
        if data.get("next_refresh_time"):
            data["next_refresh_time"] = datetime.datetime.fromisoformat(data["next_refresh_time"])
        if data.get("last_refresh_time"):
            data["last_refresh_time"] = datetime.datetime.fromisoformat(data["last_refresh_time"])
        return data
    except Exception as e:
        print(f"[StateFile] 读取状态文件失败: {e}")
        return {
            "next_refresh_time": None,
            "last_refresh_time": None,
            "config_changed": False,
        }


def save_state(data):
    """保存状态到文件"""
    # 序列化 datetime
    serializable = data.copy()
    if serializable.get("next_refresh_time"):
        serializable["next_refresh_time"] = serializable["next_refresh_time"].isoformat()
    if serializable.get("last_refresh_time"):
        serializable["last_refresh_time"] = serializable["last_refresh_time"].isoformat()

    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)
        print(f"[StateFile] 状态已保存: next_refresh_time={data.get('next_refresh_time')}")
    except Exception as e:
        print(f"[StateFile] 保存状态失败: {e}")


def update_next_refresh_time(new_time: datetime.datetime | None):
    """更新下次刷新时间"""
    data = load_state()
    data["next_refresh_time"] = new_time
    save_state(data)


def get_next_refresh_time() -> datetime.datetime | None:
    """获取下次刷新时间"""
    data = load_state()
    return data.get("next_refresh_time")

# 加在 state_file.py 最后
def set_config_changed(value: bool):
    data = load_state()
    data["config_changed"] = value
    save_state(data)


def get_config_changed():
    data = load_state()
    return data.get("config_changed", False)