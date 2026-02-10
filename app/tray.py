import pystray
from app.icon import create_tray_image
from app.refresh_impl import run_refresh_async
from app.gui_process import launch_gui_process
from app.autostart import toggle_autostart, is_autostart_enabled

def start_tray():
    image = create_tray_image("UW")

    menu = pystray.Menu(
        pystray.MenuItem("立即刷新", lambda i, _: run_refresh_async()),
        pystray.MenuItem("设置", lambda i, _: launch_gui_process()),
        pystray.MenuItem(
            "开机自启",
            toggle_autostart,
            checked=lambda item: is_autostart_enabled()
        ),
        pystray.MenuItem("退出", lambda i, _: i.stop())
    )

    icon = pystray.Icon("UpdateWeather", image, "UpdateWeather", menu)
    icon.run()
