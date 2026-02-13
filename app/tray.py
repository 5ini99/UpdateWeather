import datetime
import pystray
import threading
import time
from app.icon import create_tray_image
from app.refresh_impl import run_refresh_async
from app.gui_process import launch_gui_process
from app.autostart import toggle_autostart, is_autostart_enabled
from app.state_file import get_next_refresh_time, get_last_refresh_time

# 防止点击时频繁触发
_last_refresh_click = 0
_last_settings_click = 0
_click_debounce_seconds = 2


def _build_tooltip_text() -> str:
    next_time = get_next_refresh_time()
    last_time = get_last_refresh_time()

    if next_time is None:
        next_line = "下次刷新：计算中..."
    else:
        now = datetime.datetime.now()
        time_str = next_time.strftime("%Y-%m-%d %H:%M")
        if next_time > now:
            remain = int((next_time - now).total_seconds() // 60)
            next_line = f"下次刷新：{time_str}（约 {remain} 分钟后）"
        else:
            next_line = f"下次刷新：{time_str}（即将执行）"

    if last_time is None:
        last_line = "上次刷新：暂无"
    else:
        last_line = f"上次刷新：{last_time.strftime('%Y-%m-%d %H:%M')}"

    return f"UpdateWeather\n{next_line}\n{last_line}"


def _start_tooltip_updater(icon: pystray.Icon):
    """后台定时更新托盘 tooltip。"""

    def worker():
        while True:
            try:
                icon.title = _build_tooltip_text()
            except Exception:
                pass
            time.sleep(10)

    threading.Thread(target=worker, daemon=True, name="TrayTooltipUpdater").start()

def debounced_refresh():
    """防抖的刷新函数 - 2秒内只能触发一次"""
    global _last_refresh_click
    now = time.time()
    
    if now - _last_refresh_click < _click_debounce_seconds:
        return  # 忽略重复点击
    
    _last_refresh_click = now
    # 在后台线程执行，不要阻塞 UI
    threading.Thread(target=run_refresh_async, daemon=True).start()


def debounced_settings():
    """防抖的设置函数 - 2秒内只能触发一次"""
    global _last_settings_click
    now = time.time()
    
    if now - _last_settings_click < _click_debounce_seconds:
        return  # 忽略重复点击
    
    _last_settings_click = now
    # 在后台线程执行，不要阻塞 UI
    threading.Thread(target=launch_gui_process, daemon=True).start()


def start_tray():
    image = create_tray_image("UW")

    menu = pystray.Menu(
        pystray.MenuItem("立即刷新", lambda i, _: debounced_refresh()),
        pystray.MenuItem("设置", lambda i, _: debounced_settings()),
        pystray.MenuItem(
            "开机自启",
            toggle_autostart,
            checked=lambda item: is_autostart_enabled()
        ),
        pystray.MenuItem("退出", lambda i, _: i.stop())
    )

    icon = pystray.Icon("UpdateWeather", image, _build_tooltip_text(), menu)

    # 启动 tooltip 定时更新
    _start_tooltip_updater(icon)

    icon.run()
