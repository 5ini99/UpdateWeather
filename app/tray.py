import pystray
import threading
import time
from app.icon import create_tray_image
from app.refresh_impl import run_refresh_async
from app.gui_process import launch_gui_process
from app.autostart import toggle_autostart, is_autostart_enabled

# 防止点击时频繁触发
_last_refresh_click = 0
_last_settings_click = 0
_click_debounce_seconds = 2

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

    icon = pystray.Icon("UpdateWeather", image, "UpdateWeather", menu)
    icon.run()
