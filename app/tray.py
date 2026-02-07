import pystray
from app.icon import create_tray_image
from app.refresh_impl import run_refresh_async
from app.gui import open_gui
from app.autostart import toggle_autostart, is_autostart_enabled

def start_tray():
    image = create_tray_image("UW")

    menu = pystray.Menu(
        pystray.MenuItem("立即刷新", lambda i, _: run_refresh_async()),
        pystray.MenuItem("打开界面", lambda i, _: open_gui()),
        pystray.MenuItem(
            lambda _: "取消自启" if is_autostart_enabled() else "开机自启",
            toggle_autostart
        ),
        pystray.MenuItem("退出", lambda i, _: i.stop())
    )

    icon = pystray.Icon("UpdateWeather", image, "UpdateWeather", menu)
    icon.run()
