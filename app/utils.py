# app/utils.py
import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """
    获取打包后的资源路径
    开发环境 & PyInstaller 都可用
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path
