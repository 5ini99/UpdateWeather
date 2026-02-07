# app/tray_tooltip.py
import datetime
from app.state import STATE


def build_tooltip() -> str:
    with STATE.lock:
        if STATE.is_refreshing:
            status = "刷新中…"
            next_time = "—"
        else:
            status = "空闲"
            if STATE.next_refresh_time:
                next_time = STATE.next_refresh_time.strftime("%Y-%m-%d %H:%M")
            else:
                next_time = "未计划"

    return (
        "UpdateWeather\n"
        f"状态：{status}\n"
        f"下次刷新：{next_time}"
    )
