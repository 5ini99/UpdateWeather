# app/tray_text.py
from app.state import STATE

def build_tooltip():
    with STATE.lock:
        if STATE.is_refreshing:
            status = "状态：刷新中…"
        else:
            status = "状态：空闲"

        if STATE.next_refresh_time:
            next_time = STATE.next_refresh_time.strftime("%H:%M")
            next_text = f"下次刷新：{next_time}"
        else:
            next_text = "下次刷新：未计划"

    return f"UpdateWeather\n{status}\n{next_text}"
