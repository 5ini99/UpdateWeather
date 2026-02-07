# app/scheduler.py
import time
import datetime
from app.state import STATE
from app.refresh_impl import run_refresh_async
from app.tray_text import build_tooltip

def _is_night(now):
    if not STATE.skip_night:
        return False
    return now.hour >= STATE.night_start or now.hour < STATE.night_end

def _calc_next_time(now):
    next_time = now.replace(minute=0, second=0, microsecond=0)
    next_time += datetime.timedelta(hours=1)
    return next_time

def start_scheduler():
    while True:
        now = datetime.datetime.now()

        # 0 点强制刷新
        if now.hour == 0 and now.minute == 0:
            run_refresh_async()

        if not _is_night(now):
            if STATE.next_refresh_time is None or now >= STATE.next_refresh_time:
                run_refresh_async()
                STATE.next_refresh_time = _calc_next_time(now)

        # 更新 tray tooltip
        # icon.title = build_tooltip()

        time.sleep(30)
