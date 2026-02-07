import tkinter as tk
import os
import sys
import time
import subprocess
from pathlib import Path

LOCK_FILE = Path.home() / ".updateweather" / "gui.lock"
LOCK_FILE.parent.mkdir(exist_ok=True)


def activate_existing_gui(pid: int):
    """
    尝试把已有 GUI 窗口拉到前台（macOS）
    """
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "System Events" to set frontmost of the first process whose unix id is {pid} to true'
            ],
            check=False
        )
    except Exception:
        pass


def is_gui_running():
    """
    如果锁文件存在且 pid 存活，返回 pid
    """
    if not LOCK_FILE.exists():
        return None

    try:
        pid = int(LOCK_FILE.read_text().strip())
    except Exception:
        LOCK_FILE.unlink(missing_ok=True)
        return None

    try:
        os.kill(pid, 0)
        return pid
    except OSError:
        LOCK_FILE.unlink(missing_ok=True)
        return None


def write_lock():
    LOCK_FILE.write_text(str(os.getpid()))


def remove_lock():
    LOCK_FILE.unlink(missing_ok=True)


def center_window(root, width, height):
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")


def main():
    existing_pid = is_gui_running()
    if existing_pid:
        activate_existing_gui(existing_pid)
        sys.exit(0)

    write_lock()

    root = tk.Tk()
    root.withdraw()          # 👈 关键 1：先隐藏
    root.title("UpdateWeather")
    root.resizable(False, False)

    width, height = 360, 240
    center_window(root, width, height)

    root.deiconify()         # 👈 关键 2：再显示
    root.lift()
    root.focus_force()

    tk.Label(
        root,
        text="UpdateWeather",
        font=("Helvetica", 16, "bold")
    ).pack(pady=(30, 10))

    tk.Label(
        root,
        text="后台天气刷新服务运行中",
        font=("Helvetica", 12)
    ).pack(pady=10)

    def on_close():
        remove_lock()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


if __name__ == "__main__":
    main()
