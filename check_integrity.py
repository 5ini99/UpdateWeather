#!/usr/bin/env python3
"""
UpdateWeather 项目完整性检查脚本
检查所有必需文件和模块是否存在
"""

import sys
import os
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

# 必需文件列表
REQUIRED_FILES = [
    "main.py",
    "requirements.txt",
    "README.md",
    "app/__init__.py",
    "app/config.py",
    "app/state.py",
    "app/scheduler.py",
    "app/tray.py",
    "app/gui_process.py",
    "app/icon.py",
    "app/refresh_impl.py",
    "app/refresh_core.py",
    "app/autostart.py",
]

# 文档文件
DOC_FILES = [
    "GUIDE.md",
    "CHANGELOG.md",
    "LICENSE",
    ".gitignore",
]

# 启动脚本
SCRIPT_FILES = [
    "start.sh",
    "start.bat",
]

def check_python_version():
    """检查 Python 版本"""
    print_info("检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print_error("需要 Python 3.7 或更高版本")
        return False

def check_files(file_list, category_name):
    """检查文件列表"""
    print_info(f"检查{category_name}...")
    all_exist = True
    
    for file_path in file_list:
        if Path(file_path).exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - 缺失")
            all_exist = False
    
    return all_exist

def check_imports():
    """检查模块导入"""
    print_info("检查模块导入...")
    
    modules_to_check = [
        ("app.config", "配置模块"),
        ("app.state", "状态模块"),
        ("app.scheduler", "调度器"),
        ("app.tray", "托盘模块"),
        ("app.gui_process", "GUI 模块"),
    ]
    
    all_ok = True
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print_success(f"{display_name} ({module_name})")
        except ImportError as e:
            print_error(f"{display_name} ({module_name}) - 导入失败: {e}")
            all_ok = False
    
    return all_ok

def check_dependencies():
    """检查依赖包"""
    print_info("检查依赖包...")
    
    dependencies = [
        ("pystray", "系统托盘"),
        ("PIL", "图像处理"),
    ]
    
    all_ok = True
    for package, display_name in dependencies:
        try:
            __import__(package)
            print_success(f"{display_name} ({package})")
        except ImportError:
            print_warning(f"{display_name} ({package}) - 未安装")
            all_ok = False
    
    if not all_ok:
        print_warning("运行以下命令安装依赖:")
        print_warning("pip install -r requirements.txt")
    
    return all_ok

def main():
    print("\n" + "="*60)
    print(f"{Colors.BLUE}UpdateWeather 项目完整性检查{Colors.END}")
    print("="*60 + "\n")
    
    # 切换到项目根目录
    os.chdir(Path(__file__).parent)
    
    results = []
    
    # 1. 检查 Python 版本
    results.append(("Python 版本", check_python_version()))
    print()
    
    # 2. 检查必需文件
    results.append(("必需文件", check_files(REQUIRED_FILES, "必需文件")))
    print()
    
    # 3. 检查文档文件
    results.append(("文档文件", check_files(DOC_FILES, "文档文件")))
    print()
    
    # 4. 检查启动脚本
    results.append(("启动脚本", check_files(SCRIPT_FILES, "启动脚本")))
    print()
    
    # 5. 检查模块导入
    sys.path.insert(0, str(Path.cwd()))
    results.append(("模块导入", check_imports()))
    print()
    
    # 6. 检查依赖
    results.append(("依赖包", check_dependencies()))
    print()
    
    # 汇总结果
    print("="*60)
    print(f"{Colors.BLUE}检查结果汇总{Colors.END}")
    print("="*60)
    
    all_passed = True
    for category, passed in results:
        if passed:
            print_success(f"{category}: 通过")
        else:
            print_error(f"{category}: 失败")
            all_passed = False
    
    print()
    
    if all_passed:
        print(f"{Colors.GREEN}✓ 项目完整性检查通过！{Colors.END}")
        print(f"{Colors.GREEN}✓ 可以正常发布和使用{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}✗ 发现问题，请修复后再发布{Colors.END}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}检查已取消{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}检查失败: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
