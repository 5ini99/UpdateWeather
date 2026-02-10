import sys
import os

def resource_path(relative_path: str) -> str:
    """
    获取资源的真实路径
    - 开发环境：当前工作目录
    - PyInstaller 打包后：_MEIPASS
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
