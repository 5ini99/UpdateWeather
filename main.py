# main.py
import time
from app.tray import start_tray
from app.scheduler import start_scheduler
import threading

def main():
    # 后台调度器（非 GUI / 非托盘）
    threading.Thread(
        target=start_scheduler,
        daemon=True
    ).start()

    time.sleep(0.5)  # 给调度器 0.5 秒初始化

    # ⚠️ 托盘必须在主线程
    start_tray()

if __name__ == "__main__":
    main()
