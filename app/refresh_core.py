# app/refresh_core.py
import subprocess
import sys
import os
import time
import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 你原来的完整脚本路径（按你真实文件名改一次即可）
LEGACY_SCRIPT = os.path.join(BASE_DIR, "legacy", "update_weather.py")

def fetch_weather():
    """
    执行你原来的 update-weather 脚本
    = 真正干活的核心
    """
    if not os.path.exists(LEGACY_SCRIPT):
        raise RuntimeError(f"未找到原始脚本: {LEGACY_SCRIPT}")

    start = time.time()

    result = subprocess.run(
        [sys.executable, LEGACY_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            "刷新脚本执行失败\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return {
        "duration": round(time.time() - start, 2),
        "stdout": result.stdout
    }


def update_cache():
    """
    预留接口（目前你的旧脚本已完成全部工作）
    """
    # 现在什么都不用做，但必须存在
    return True


def send_mail():
    """
    预留接口（未来扩展）
    """
    return True
