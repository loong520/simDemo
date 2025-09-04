#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片仿真自动化Demo - 安装脚本
检查和安装必要的依赖包
"""

import sys
import subprocess
import importlib

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python version too low: {version.major}.{version.minor}")
        print("Requires Python 3.7 or higher")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_and_install_package(package_name, import_name=None):
    """检查并安装包"""
    import_name = import_name or package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} already installed")
        return True
    except ImportError:
        print(f"⚠️ {package_name} not installed, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ {package_name} installation failed")
            return False

def main():
    """主函数"""
    print("Chip Simulation Automation Demo - Environment Check and Installation")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 必要的包列表
    required_packages = [
        ("pyyaml", "yaml"),
        ("jinja2", "jinja2"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
    ]
    
    # 可选的包列表
    optional_packages = [

    ]
    
    print("\nChecking required dependencies...")
    all_required_ok = True
    for package_name, import_name in required_packages:
        if not check_and_install_package(package_name, import_name):
            all_required_ok = False
    
    print("\nChecking optional dependencies...")
    for package_name, import_name in optional_packages:
        try:
            check_and_install_package(package_name, import_name)
        except Exception:
            print(f"⚠️ {package_name} installation failed (optional package, does not affect basic functionality)")
    
    print("\n" + "=" * 50)
    if all_required_ok:
        print("✅ Environment check completed, all required dependencies are installed")
        print("Ready to use Chip Simulation Automation Demo!")
        print("\nUsage:")
        print("  python main.py -i  # Interactive mode")
        print("  python test_demo.py  # Run tests")
    else:
        print("❌ Some required dependencies installation failed, please install manually")
        print("You can try running: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()