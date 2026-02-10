# app/autostart.py
"""
macOS 开机自启管理（使用 Launch Agents）
"""
import os
import subprocess
from pathlib import Path
import plistlib
import sys

# Launch Agents 路径
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_FILE = LAUNCH_AGENTS_DIR / "com.updateweather.plist"


def get_program_path():
    """
    获取要开机运行的程序路径
    - 开发时：main.py 的绝对路径
    - 打包后：sys.executable 或 .app 的路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的路径
        return sys.executable
    else:
        # 开发时用 main.py
        return str(Path(__file__).resolve().parent.parent / "main.py")


def is_autostart_enabled():
    """检查是否已启用开机自启"""
    return PLIST_FILE.exists() and subprocess.run(
        ["launchctl", "list", "com.updateweather"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ).returncode == 0


def toggle_autostart():
    """切换开机自启状态"""
    if is_autostart_enabled():
        disable_autostart()
    else:
        enable_autostart()


def enable_autostart():
    """启用开机自启"""
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    program_path = get_program_path()
    python_path = sys.executable if getattr(sys, 'frozen', False) else "/usr/bin/python3"

    plist_data = {
        "Label": "com.updateweather",
        "ProgramArguments": [python_path, program_path],
        "RunAtLoad": True,
        "KeepAlive": False,
        "StandardOutPath": str(Path.home() / ".updateweather" / "autostart.log"),
        "StandardErrorPath": str(Path.home() / ".updateweather" / "autostart.err"),
    }

    try:
        with open(PLIST_FILE, "wb") as f:
            plistlib.dump(plist_data, f)

        # 加载到 launchctl
        subprocess.run(["launchctl", "load", "-w", str(PLIST_FILE)], check=True)
        print("开机自启已启用")
    except Exception as e:
        print(f"启用开机自启失败: {e}")


def disable_autostart():
    """取消开机自启"""
    if not PLIST_FILE.exists():
        return

    try:
        subprocess.run(["launchctl", "unload", str(PLIST_FILE)], check=True)
        PLIST_FILE.unlink()
        print("开机自启已取消")
    except Exception as e:
        print(f"取消开机自启失败: {e}")