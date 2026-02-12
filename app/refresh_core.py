# app/refresh_core.py
import time
import io
import contextlib
import runpy
from app.utils import resource_path

LEGACY_SCRIPT = resource_path("legacy/update_weather.py")


def fetch_weather():
    """
    执行原始 update_weather.py 脚本（进程内执行）

    为什么不再用 subprocess + sys.executable：
    - 在 PyInstaller 打包环境中，sys.executable 通常是主程序本体
    - 再次 subprocess 调用会递归拉起应用，导致“刷新卡住/进程堆积”

    改为 runpy.run_path(..., run_name="__main__") 可在当前进程内执行脚本，
    同时保留脚本里 __name__ == '__main__' 的刷新逻辑。
    """
    if not LEGACY_SCRIPT.exists():
        raise RuntimeError(f"未找到原始脚本: {LEGACY_SCRIPT}")

    start = time.time()
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            runpy.run_path(str(LEGACY_SCRIPT), run_name="__main__")
    except Exception as e:
        raise RuntimeError(
            "刷新脚本执行失败\n"
            f"STDOUT:\n{stdout_buf.getvalue()}\n"
            f"STDERR:\n{stderr_buf.getvalue()}\n"
            f"EXCEPTION:\n{e}"
        )

    return {
        "duration": round(time.time() - start, 2),
        "stdout": stdout_buf.getvalue(),
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