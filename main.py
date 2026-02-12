# main.py
"""
UpdateWeather 主程序
支持开发环境和 PyInstaller 打包环境
"""

import os
import sys
import threading
import multiprocessing

def run_tray_mode():
    """主程序入口"""

    print("\n" + "=" * 50)
    print("UpdateWeather 启动")
    print("=" * 50 + "\n")

    try:
        # 延迟导入（防止子进程重复执行）
        from app.tray import start_tray
        from app.scheduler import start_scheduler

        # 后台调度线程
        scheduler_thread = threading.Thread(
            target=start_scheduler,
            daemon=True,
            name="SchedulerThread"
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
    print("[Main] 进入刷新模式")

    try:
        print("[Main] 准备 import refresh_impl")
        import app.refresh_impl
        print("[Main] refresh_impl import 成功")

        print("[Main] 获取 _do_refresh")
        _do_refresh = app.refresh_impl._do_refresh
        print("[Main] 获取成功")

        print("[Main] 开始执行刷新逻辑")
        _do_refresh()
        print("[Main] 刷新逻辑执行完成")

    except Exception as e:
        print(f"[Main] 刷新模式异常: {e}")
        import traceback
        traceback.print_exc()

    sys.exit(0)


if __name__ == "__main__":
    # ⭐ PyInstaller + multiprocessing 必须
    multiprocessing.freeze_support()

    if "--gui" in sys.argv:
        run_gui_mode()

    elif "--refresh" in sys.argv:
        run_refresh_mode()

    else:
        run_tray_mode()
