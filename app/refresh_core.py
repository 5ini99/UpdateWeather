# app/refresh_core.py
from pathlib import Path
import subprocess
import sys
import time


def fetch_weather():
    """
    执行单次刷新子进程。

    关键点：
    - 不直接 subprocess legacy/update_weather.py（打包后容易参数解释异常）
    - 统一调用主程序的 --refresh-worker 模式，避免递归启动托盘
    """
    start = time.time()

    # 开发环境与打包环境参数不同：
    # - 开发环境: python main.py --refresh
    # - PyInstaller: <app_executable> --refresh
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, "--refresh"]
    else:
        project_root = Path(__file__).resolve().parent.parent
        cmd = [sys.executable, str(project_root / "main.py"), "--refresh"]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "刷新脚本执行失败\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"EXIT_CODE: {result.returncode}"
        )

    return {
        "duration": round(time.time() - start, 2),
        "stdout": result.stdout,
    }


def update_cache():
    """
    预留接口（目前旧脚本已完成全部工作）
    """
    return True


def send_mail():
    """
    预留接口（未来扩展）
    """
    return True