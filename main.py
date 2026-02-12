# main.py
"""
UpdateWeather 主程序
支持开发环境和 PyInstaller 打包环境
"""

import sys
import threading
import multiprocessing
import runpy


def run_tray_mode():
    """托盘常驻模式"""
    print("\n" + "=" * 50)
    print("UpdateWeather 启动")
    print("=" * 50 + "\n")

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