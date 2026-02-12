# pyinstaller_compat.py
"""
PyInstaller 兼容性模块
用于处理打包后的资源路径和模块导入问题
"""
import sys
import os
from pathlib import Path


def get_base_path():
    """
    获取应用基础路径，兼容开发和打包环境
    
    - 开发环境: 项目根目录
    - PyInstaller 打包: sys._MEIPASS 目录
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的环境
        return Path(sys._MEIPASS)
    else:
        # 开发环境：main.py 的上级目录
        return Path(__file__).resolve().parent.parent


def get_resource_path(relative_path):
    """
    获取资源文件的完整路径
    
    Args:
        relative_path: 相对于项目根目录的路径 (字符串或 Path)
    
    Returns:
        Path 对象
    
    Example:
        img_dir = get_resource_path("img")
        font_path = get_resource_path("font/Galmuri9.ttf")
    """
    base = get_base_path()
    full_path = base / relative_path
    
    if not full_path.exists():
        # 调试信息
        print(f"⚠️  警告: 资源文件不存在")
        print(f"  期望路径: {full_path}")
        print(f"  基础路径: {base}")
        print(f"  是否为打包环境: {getattr(sys, 'frozen', False)}")
    
    return full_path


def ensure_working_directory():
    """
    确保工作目录正确设置
    这对于访问相对路径的资源很重要
    """
    base = get_base_path()
    os.chdir(base)
    print(f"✓ 工作目录已设置: {os.getcwd()}")


def setup_module_paths():
    """
    设置 Python 模块搜索路径
    确保自定义模块能被正确导入
    """
    base = get_base_path()
    
    # 添加项目根目录到 sys.path（如果还没有）
    root_str = str(base)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
        print(f"✓ 已添加模块路径: {root_str}")


def initialize_pyinstaller_environment():
    """
    初始化 PyInstaller 环境
    在应用启动时最早调用此函数
    """
    print("=" * 50)
    print("PyInstaller 环境初始化")
    print("=" * 50)
    
    # 检查运行环境
    is_frozen = getattr(sys, 'frozen', False)
    print(f"运行环境: {'打包应用' if is_frozen else '开发环境'}")
    
    # 设置工作目录
    ensure_working_directory()
    
    # 设置模块路径
    setup_module_paths()
    
    # 打印调试信息
    print(f"Python 版本: {sys.version}")
    print(f"应用根目录: {get_base_path()}")
    print("=" * 50)
    print()


# ============== 文件夹管理辅助函数 ==============

def get_img_dir():
    """获取图片文件夹路径"""
    return get_resource_path("img")


def get_font_dir():
    """获取字体文件夹路径"""
    return get_resource_path("font")


def get_legacy_dir():
    """获取遗留文件夹路径"""
    return get_resource_path("legacy")


def list_resources(folder_name):
    """
    列出指定文件夹中的所有资源文件
    用于调试和验证资源是否正确打包
    """
    folder_path = get_resource_path(folder_name)
    
    if not folder_path.exists():
        print(f"文件夹不存在: {folder_path}")
        return []
    
    files = list(folder_path.glob("*"))
    print(f"\n{folder_name} 文件夹内容 ({len(files)} 项):")
    for f in sorted(files):
        if f.is_file():
            size = f.stat().st_size
            print(f"  📄 {f.name} ({size:,} bytes)")
        else:
            print(f"  📁 {f.name}/")
    
    return files


# ============== 调试辅助函数 ==============

def print_sys_info():
    """打印系统和环境信息（调试用）"""
    print("\n" + "=" * 50)
    print("系统信息")
    print("=" * 50)
    print(f"Python 可执行文件: {sys.executable}")
    print(f"Python 版本: {sys.version}")
    print(f"是否为 PyInstaller 打包应用: {getattr(sys, 'frozen', False)}")
    if getattr(sys, 'frozen', False):
        print(f"PyInstaller 基础路径 (MEIPASS): {sys._MEIPASS}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"sys.path:")
    for i, p in enumerate(sys.path):
        print(f"  {i}: {p}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    # 直接运行此模块进行测试
    initialize_pyinstaller_environment()
    print_sys_info()
    print("\n测试资源文件列表:")
    list_resources("img")
    list_resources("font")
    list_resources("legacy")
