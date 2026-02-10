# app/refresh_impl.py
from pathlib import Path
import threading
import datetime
import os
import subprocess
from app.refresh_core import fetch_weather, update_cache, send_mail

LOG_DIR = Path.home() / ".update-weather"
LOG_FILE = os.path.join(LOG_DIR, "refresh.log")

_refresh_lock = threading.Lock()


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
    """
    真正的刷新逻辑（不碰线程锁）
    """
    _log("开始执行：立即刷新")

    try:
        fetch_weather()
        update_cache()
        send_mail()

        _log("刷新完成 ✔")
        notify_macos(
            title="UpdateWeather",
            message="天气刷新完成"
        )

    except Exception as e:
        _log(f"刷新失败 ✘ {e}")
        notify_macos(
            title="UpdateWeather",
            message="天气刷新失败，请查看日志"
        )

def run_refresh_async():
    """
    对外入口：托盘 / GUI / 定时任务
    同一时间只允许一个刷新
    """

    # 非阻塞抢锁
    if not _refresh_lock.acquire(blocking=False):
        _log("刷新请求被忽略：已有刷新正在执行")
        notify_macos(
            title="UpdateWeather",
            message="刷新正在进行中，请稍后再试"
        )
        return

    def runner():
        try:
            _do_refresh()
        finally:
            _refresh_lock.release()
            _log("刷新锁已释放")

    threading.Thread(
        target=runner,
        name="UpdateWeather-Refresh",
        daemon=True
    ).start()
