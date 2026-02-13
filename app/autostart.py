# app/autostart.py
"""
macOS 开机自启管理（使用 Launch Agents）
"""
import subprocess
from pathlib import Path
import plistlib
import sys

# Launch Agents 路径
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_FILE = LAUNCH_AGENTS_DIR / "com.updateweather.plist"
LOG_DIR = Path.home() / ".update-weather"


def get_program_arguments():
    """
    获取 LaunchAgent 的 ProgramArguments
    - 打包环境: [<app_executable>]
    - 开发环境: [python3, main.py]
    """
    if getattr(sys, 'frozen', False):
        return [sys.executable]

    main_py = str(Path(__file__).resolve().parent.parent / "main.py")
    return ["/usr/bin/python3", main_py]


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


def _unload_quiet():
    """静默卸载（允许未加载场景）"""
    result = subprocess.run(
        ["launchctl", "unload", str(PLIST_FILE)],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode


def enable_autostart():
    """启用开机自启"""
    LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    plist_data = {
        "Label": "com.updateweather",
        "ProgramArguments": get_program_arguments(),
        "RunAtLoad": True,
        "KeepAlive": False,
        "StandardOutPath": str(LOG_DIR / "autostart.log"),
        "StandardErrorPath": str(LOG_DIR / "autostart.err"),
    }

    try:
        with open(PLIST_FILE, "wb") as f:
            plistlib.dump(plist_data, f)

        # 先尝试卸载旧配置，避免重复加载报错（静默）
        _unload_quiet()

        # 加载到 launchctl
        subprocess.run(
            ["launchctl", "load", "-w", str(PLIST_FILE)],
            check=True,
            capture_output=True,
            text=True,
        )
        print("开机自启已启用")
    except Exception as e:
        print(f"启用开机自启失败: {e}")


def disable_autostart():
    """取消开机自启"""
    if not PLIST_FILE.exists():
        return

    try:
        _unload_quiet()
        PLIST_FILE.unlink(missing_ok=True)
        print("开机自启已取消")
    except Exception as e:
        print(f"取消开机自启失败: {e}")