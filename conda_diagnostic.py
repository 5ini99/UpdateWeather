#!/usr/bin/env python3
"""
Conda 环境诊断脚本
用于检查你的 Conda 环境是否正确配置用于 PyInstaller 打包
"""

import sys
import os
import subprocess
from pathlib import Path


def print_header(text):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_conda_env():
    """检查 Conda 环境是否激活"""
    print_header("1. Conda 环境检查")
    
    env_name = os.environ.get('CONDA_DEFAULT_ENV')
    if not env_name:
        print("❌ 未检测到 Conda 环境")
        print("请运行: conda activate your_env_name")
        return False
    
    print(f"✓ Conda 环境: {env_name}")
    
    conda_prefix = os.environ.get('CONDA_PREFIX')
    print(f"✓ 环境路径: {conda_prefix}")
    
    return True


def check_python():
    """检查 Python 是否来自 Conda"""
    print_header("2. Python 版本和位置")
    
    executable = sys.executable
    print(f"Python 可执行文件: {executable}")
    
    # 检查是否来自 Conda
    if 'miniconda' in executable or 'anaconda' in executable or 'conda' in executable:
        print("✓ Python 来自 Conda 环境")
        return True
    else:
        print("❌ Python 不来自 Conda 环境！")
        print(f"   而是来自系统: {executable}")
        print("   这很可能是导致问题的原因！")
        return False


def check_dependencies():
    """检查必要的依赖库"""
    print_header("3. 依赖库检查")
    
    required_libs = [
        'pystray',
        'PIL',
        'psutil',
        'requests',
        'hid',
        'PyInstaller'
    ]
    
    all_installed = True
    
    for lib in required_libs:
        try:
            if lib == 'PIL':
                import PIL
            elif lib == 'hid':
                import hid
            elif lib == 'PyInstaller':
                import PyInstaller
            else:
                __import__(lib)
            print(f"✓ {lib}")
        except ImportError:
            print(f"❌ {lib} - 未安装")
            all_installed = False
    
    if not all_installed:
        print("\n安装缺失的库:")
        print("  pip install pystray pillow psutil requests hid pyinstaller")
    
    return all_installed


def check_pyinstaller():
    """检查 PyInstaller 版本和配置"""
    print_header("4. PyInstaller 检查")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--version'],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        print(f"✓ PyInstaller 版本: {version}")
        
        # 检查最低版本
        version_num = float(version.split()[0])
        if version_num >= 4.0:
            print("✓ 版本符合要求（>= 4.0）")
            return True
        else:
            print("⚠️  版本较旧，建议升级:")
            print("   pip install --upgrade PyInstaller")
            return False
    except Exception as e:
        print(f"❌ 无法检查 PyInstaller: {e}")
        return False


def check_python_path():
    """检查 Python 路径配置"""
    print_header("5. Python 路径和 site-packages")
    
    print("sys.path (前 3 个):")
    for i, p in enumerate(sys.path[:3]):
        marker = "✓" if 'conda' in p or 'miniconda' in p else "  "
        print(f"  {marker} {p}")
    
    print("\nsite-packages:")
    try:
        import site
        for p in site.getsitepackages():
            marker = "✓" if 'conda' in p or 'miniconda' in p else "  "
            print(f"  {marker} {p}")
    except Exception as e:
        print(f"  无法获取: {e}")
    
    return True


def check_project_structure():
    """检查项目结构"""
    print_header("6. 项目结构检查")
    
    required_folders = ['img', 'font', 'legacy', 'app']
    required_files = ['main.py', 'requirements.txt']
    
    all_good = True
    
    for folder in required_folders:
        if Path(folder).exists():
            print(f"✓ {folder}/")
        else:
            print(f"❌ {folder}/ - 缺失")
            all_good = False
    
    for file in required_files:
        if Path(file).exists():
            print(f"✓ {file}")
        else:
            print(f"❌ {file} - 缺失")
            all_good = False
    
    return all_good


def check_build_scripts():
    """检查构建脚本"""
    print_header("7. 构建脚本检查")
    
    scripts = ['build.sh', 'build_conda.sh']
    
    for script in scripts:
        if Path(script).exists():
            print(f"✓ {script}")
        else:
            print(f"❌ {script} - 缺失")


def main():
    """主诊断函数"""
    print("\n" + "="*60)
    print("  Conda 环境 PyInstaller 打包诊断")
    print("="*60)
    
    results = {
        'Conda 环境': check_conda_env(),
        'Python 来自 Conda': check_python(),
        '依赖库': check_dependencies(),
        'PyInstaller': check_pyinstaller(),
        'Python 路径': check_python_path(),
        '项目结构': check_project_structure(),
    }
    
    check_build_scripts()
    
    # 诊断总结
    print_header("诊断总结")
    
    critical_issues = [k for k, v in results.items() if not v and k != 'Python 路径']
    
    if critical_issues:
        print(f"❌ 发现 {len(critical_issues)} 个关键问题:")
        for issue in critical_issues:
            print(f"  - {issue}")
        
        print("\n建议修复步骤:")
        
        if not results['Conda 环境']:
            print("  1. 激活 Conda 环境: conda activate your_env_name")
        
        if not results['Python 来自 Conda']:
            print("  2. 确认 Python 来自 Conda")
        
        if not results['依赖库']:
            print("  3. 安装缺失的库: pip install pystray pillow psutil requests pyinstaller")
        
        if not results['PyInstaller']:
            print("  4. 升级 PyInstaller: pip install --upgrade pyinstaller")
        
        print("\n修复后重新运行此诊断脚本")
        return False
    else:
        print("✓ 所有检查都通过！")
        print("\n你可以安全地运行:")
        print("  ./build_conda.sh")
        print("\n如果仍有问题，请检查:")
        print("  - 打包脚本的详细输出")
        print("  - PyInstaller 的 hook 配置")
        print("  - 依赖库的版本兼容性")
        return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
