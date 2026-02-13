# app/refresh_impl.py
from pathlib import Path
import threading
import datetime
import os
import subprocess
from app.refresh_core import fetch_weather, update_cache, send_mail
from app.state_file import update_last_refresh_time 

LOG_DIR = Path.home() / ".update-weather"
LOG_FILE = LOG_DIR / "refresh.log"

_refresh_lock = threading.Lock()
_refresh_timeout_timer = None
_is_refreshing = False 


def notify_macos(title: str, message: str):
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "{message}" with title "{title}"'
            ],
            check=False,
            timeout=10
        )
    except Exception:
        pass


def _ensure_log_dir():
    LOG_DIR.mkdir(exist_ok=True)


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
    global _refresh_timeout_timer, _is_refreshing

    _is_refreshing = True  # ← 用全局标志

    # 启动超时定时器（30 秒后强制释放锁）
    def timeout_release():
        _log("警告：刷新超时 30 秒，强制释放锁")
        if _refresh_lock.locked():
            _refresh_lock.release()

    _refresh_timeout_timer = threading.Timer(30.0, timeout_release)
    _refresh_timeout_timer.start()

    try:
        fetch_weather()
        update_cache()
        send_mail()
        _log("刷新完成 ✔")
        notify_macos("UpdateWeather", "天气刷新完成")

        # 更新最后刷新时间到文件
        now = datetime.datetime.now()
        update_last_refresh_time(now)
        _log(f"最后刷新时间已更新: {now}")

    except Exception as e:
        _log(f"刷新失败 ✘ {e}")
        notify_macos("UpdateWeather", "天气刷新失败，请查看日志")

    finally:
        _is_refreshing = False
        if _refresh_timeout_timer:
            _refresh_timeout_timer.cancel()
        if _refresh_lock.locked():
            _refresh_lock.release()
        _log("刷新锁已释放")


def run_refresh_async():
    """
    异步刷新 - 带去重控制
    """
    global _is_refreshing
    
    # 首先检查是否已在执行
    if _is_refreshing:
        _log("⚠️ 刷新已在进行中，忽略本次请求")
        notify_macos("UpdateWeather", "刷新正在进行中，请稍候...")
        return
    
    try:
        # 尝试获取锁，最多等 2 秒
        if not _refresh_lock.acquire(timeout=2):
            _log("⚠️ 刷新请求被拒：已有刷新执行超过 2 秒")
            notify_macos("UpdateWeather", "刷新正在进行中，请稍候...")
            return

        _log("✓ 锁获取成功，开始刷新")

        def runner():
            try:
                _do_refresh()
            except Exception as e:
                _log(f"❌ 刷新线程异常: {e}")
            finally:
                if _refresh_lock.locked():
                    _refresh_lock.release()

        threading.Thread(target=runner, daemon=True).start()

    except Exception as e:
        _log(f"❌ 刷新启动失败: {e}")