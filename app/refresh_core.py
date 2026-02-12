# app/refresh_core.py
import subprocess
import sys
import os
import time
import datetime

from app.utils import resource_path

LEGACY_SCRIPT = resource_path("legacy/update_weather.py")

def fetch_weather():
    """
    执行你原来的 update-weather 脚本
    = 真正干活的核心
    """
    if not os.path.exists(LEGACY_SCRIPT):
        raise RuntimeError(f"未找到原始脚本: {LEGACY_SCRIPT}")

    start = time.time()
    from pathlib import Path
    root_dir = Path(__file__).resolve().parent.parent  # gui_process.py → app → root

    gui_script = root_dir / "app" / "gui_process.py"

    # ✅ 关键修复：使用 -m 参数 + 模块名
    # 而不是直接传文件路径
    # 这样 Python 会正确识别 if __name__ == "__main__" 块
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir) + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, LEGACY_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(root_dir),
        env=env,
        start_new_session=True,
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
