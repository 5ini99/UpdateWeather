# main.py
from app.tray import start_tray
from app.scheduler import start_scheduler
import threading

def main():
    # 后台调度器（非 GUI / 非托盘）
    threading.Thread(
        target=start_scheduler,
        daemon=True
    ).start()

    # ⚠️ 托盘必须在主线程
    start_tray()

if __name__ == "__main__":
    main()
