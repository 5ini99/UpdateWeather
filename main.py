# main.py（改进版）
"""
UpdateWeather 主程序
支持开发环境和 PyInstaller 打包环境
"""
import time
import sys
import os
from pathlib import Path

# ============== PyInstaller 兼容性初始化（必须最先执行） ==============
# 导入兼容性模块
from pyinstaller_compat import (
    initialize_pyinstaller_environment,
    get_resource_path,
    print_sys_info
)

# 初始化环境（处理路径、模块导入等）
initialize_pyinstaller_environment()

# ============== 然后导入应用模块 ==============
from app.tray import start_tray
from app.scheduler import start_scheduler
import threading


def main():
    """主程序入口"""
    print("\n" + "="*50)
    print("UpdateWeather 启动")
    print("="*50 + "\n")
    
    try:
        # 后台调度器（非 GUI / 非托盘）
        print("启动后台调度器...")
        scheduler_thread = threading.Thread(
            target=start_scheduler,
            daemon=True,
            name="SchedulerThread"
        )
        scheduler_thread.start()

        time.sleep(0.5)  # 给调度器 0.5 秒初始化

        # ⚠️ 托盘必须在主线程
        print("启动托盘界面...")
        start_tray()
        
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
