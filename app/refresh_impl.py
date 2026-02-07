# app/refresh_impl.py
import threading
import time
import datetime
import os
import subprocess
import sys
import traceback
import subprocess
from app.state import STATE
from app.refresh_core import fetch_weather, update_cache, send_mail

LOG_DIR = os.path.expanduser("~/Library/Logs/UpdateWeather")
LOG_FILE = os.path.join(LOG_DIR, "refresh.log")

_refresh_lock = threading.Lock()
_is_refreshing = False

def notify_macos(title: str, message: str):
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "{message}" with title "{title}"'
            ],
            check=False
        )
    except Exception:
        pass

def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def _log(msg: str):
    _ensure_log_dir()
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _do_refresh():
    _log("开始执行：立即刷新")
    
    with STATE.lock:
        STATE.is_refreshing = True

    try:
        result = fetch_weather()
        update_cache()
        send_mail()
        
        _log("刷新完成 ✔")
        notify_macos(
            title="UpdateWeather",
            message="天气刷新完成"
        )

        with STATE.lock:
            STATE.last_refresh_time = datetime.datetime.now()

    except Exception as e:
        _log(f"刷新失败 ✘ {e}")
        notify_macos(
            title="UpdateWeather",
            message="天气刷新失败，请查看日志"
        )
    finally:
        with STATE.lock:
            STATE.is_refreshing = False
        _refresh_lock.release()

def run_refresh_async():
    """
    对外暴露的入口：异步刷新（给托盘 / GUI / 定时任务用）
    同一时间只允许一个刷新执行
    """
    global _is_refreshing

    # 非阻塞获取锁：如果已在刷新，直接拒绝
    if not _refresh_lock.acquire(blocking=False):
        _log("刷新请求被忽略：已有刷新正在执行")
        notify_macos(
            title="UpdateWeather",
            message="刷新正在进行中，请稍后再试"
        )
        return

    _is_refreshing = True

    def runner():
        global _is_refreshing
        try:
            _do_refresh()
        finally:
            _is_refreshing = False
            _refresh_lock.release()
            _log("刷新锁已释放")

    threading.Thread(
        target=runner,
        name="UpdateWeather-Refresh",
        daemon=True
    ).start()
