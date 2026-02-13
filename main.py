# main.py
"""
UpdateWeather 主程序
支持开发环境和 PyInstaller 打包环境
"""

import atexit
import os
from pathlib import Path
import signal
import sys
import threading
import multiprocessing
import runpy

LOCK_DIR = Path.home() / ".update-weather"
LOCK_FILE = LOCK_DIR / "app.lock"

def _is_pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def ensure_single_instance() -> bool:
    """确保只有一个托盘主实例在运行。返回 True 表示可继续启动。"""
    LOCK_DIR.mkdir(parents=True, exist_ok=True)

    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            if old_pid != os.getpid() and _is_pid_running(old_pid):
                print(f"[Main] 检测到已有实例运行 (pid={old_pid})，本次退出")
                return False
        except Exception:
            pass

    LOCK_FILE.write_text(str(os.getpid()))

    def cleanup_lock(*_):
        try:
            if LOCK_FILE.exists() and LOCK_FILE.read_text().strip() == str(os.getpid()):
                LOCK_FILE.unlink()
        except Exception:
            pass

    atexit.register(cleanup_lock)
    signal.signal(signal.SIGTERM, cleanup_lock)
    signal.signal(signal.SIGINT, cleanup_lock)
    return True

def run_tray_mode():
    """托盘常驻模式"""
    print("\n" + "=" * 50)
    print("UpdateWeather 启动")
    print("=" * 50 + "\n")

    if not ensure_single_instance():
        sys.exit(0)

    try:
        # 延迟导入（防止子进程模式不必要加载）
        from app.tray import start_tray
        from app.scheduler import start_scheduler

        # 后台调度线程
        scheduler_thread = threading.Thread(
            target=start_scheduler,
            daemon=True,
            name="SchedulerThread",
        )
        scheduler_thread.start()

        # ⚠️ 托盘必须在主线程（阻塞）
        start_tray()

    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def run_gui_mode():
    from app.gui_process import main
    main()


def run_refresh_mode():
    """
    单次刷新工作模式（子进程执行）
    - 不启动托盘
    - 不启动调度器
    - 仅执行 legacy/update_weather.py 然后退出
    """
    from app.utils import resource_path

    legacy_script = resource_path("legacy/update_weather.py")
    print(f"[Main] 进入刷新工作模式: {legacy_script}")

    if not legacy_script.exists():
        print(f"[Main] ❌ 未找到脚本: {legacy_script}")
        sys.exit(2)

    try:
        runpy.run_path(str(legacy_script), run_name="__main__")
        print("[Main] ✅ 单次刷新完成")
        sys.exit(0)
    except Exception as e:
        print(f"[Main] ❌ 刷新工作模式异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # ⭐ PyInstaller + multiprocessing 必须
    multiprocessing.freeze_support()

    # 兼容旧参数：--refresh
    if "--gui" in sys.argv:
        run_gui_mode()
    elif "--refresh" in sys.argv:
        run_refresh_mode()
    else:
        run_tray_mode()