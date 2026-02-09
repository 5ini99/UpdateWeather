# app/scheduler.py
import time
import datetime

from app.state import STATE
from app.config import CONFIG
from app.refresh_impl import run_refresh_async
from app.tray_text import build_tooltip


def _is_night(now: datetime.datetime) -> bool:
    """
    是否处于夜间免刷新时间段
    """
    if not CONFIG.skip_night:
        return False

    # 跨天规则（比如 23 -> 7）
    if CONFIG.night_start < CONFIG.night_end:
        return CONFIG.night_start <= now.hour < CONFIG.night_end
    else:
        return now.hour >= CONFIG.night_start or now.hour < CONFIG.night_end


def _calc_next_time(now: datetime.datetime) -> datetime.datetime:
    """
    根据配置计算下一次刷新时间
    """
    interval = CONFIG.refresh_interval_minutes
    return now + datetime.timedelta(minutes=interval)


def start_scheduler():
    """
    后台调度线程（常驻）
    """
    last_force_refresh_date = None

    while True:
        now = datetime.datetime.now()

        # ---------- 0 点强制刷新（每天一次） ----------
        if now.hour == 0:
            today = now.date()
            if last_force_refresh_date != today:
                run_refresh_async()
                last_force_refresh_date = today

        # ---------- 正常刷新逻辑 ----------
        if not _is_night(now):
            with STATE.lock:
                next_time = STATE.next_refresh_time

            if next_time is None or now >= next_time:
                run_refresh_async()
                with STATE.lock:
                    STATE.next_refresh_time = _calc_next_time(now)

        time.sleep(30)
