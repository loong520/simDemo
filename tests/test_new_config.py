#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的配置文件结构
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    import config
except ImportError as e:
    print("Module import failed: {}".format(e))
    print("Please ensure all necessary Python packages are installed: pip install -r requirements.txt")
    sys.exit(1)


def test_system_config():
    """测试系统配置加载"""
    print("=" * 50)
    print("Testing System Configuration Loading")
    print("=" * 50)
    
    try:
        # 测试系统配置加载
        system_config = config.load_system_config()
        print("✓ System configuration loaded successfully")
        print("  Server URL: {}".format(system_config.server.url))
        print("  Spectre executable: {}".format(system_config.eda_tools.spectre.executable))
        print("  Virtuoso executable: {}".format(system_config.eda_tools.virtuoso.executable))
        return True
    except Exception as e:
        print("✗ System configuration loading failed: {}".format(e))
        return False


def test_task_config():
    """测试任务配置加载"""
    print("\n" + "=" * 50)
    print("Testing Task Configuration Loading")
    print("=" * 50)
    
    try:
        # 测试任务配置加载
        task_config_file = os.path.join(project_root, "simulation_task_config.yaml")
        if not os.path.exists(task_config_file):
            print("⚠ Task configuration file does not exist, creating a test one...")
            # 创建一个简单的测试配置
            test_config_content = """simulation:
  project_dir: "/tmp/test_project"
  library_name: "test_lib"
  cell_name: "test_cell"
  design_type: "schematic"
  simulator: "spectre"
  simulation_path: "/tmp/test_simulation"
  temperature: 27.0
  supply_voltage: 1.8

testbench_config: "testbench_config.yaml"
"""
            with open(task_config_file, 'w') as f:
                f.write(test_config_content)
        
        task_config = config.load_task_config(task_config_file)
        print("✓ Task configuration loaded successfully")
        print("  Project name: {}".format(task_config.project_name))
        print("  Simulator: {}".format(task_config.simulator))
        print("  Design path: {}".format(task_config.design_path))
        return True
    except Exception as e:
        print("✗ Task configuration loading failed: {}".format(e))
        return False


def main():
    """Main test function"""
    print("Testing New Configuration Structure")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    tests = [
        ("System Configuration", test_system_config),
        ("Task Configuration", test_task_config)
    ]
    
    for test_name, test_func in tests:
        print("\nRunning: {}".format(test_name))
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print("Test '{}' encountered exception: {}".format(test_name, e))
            test_results.append((test_name, False))
    
    # 显示测试结果摘要
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ Passed" if result else "✗ Failed"
        print("{:25s} : {}".format(test_name, status))
        if result:
            passed += 1
    
    print("\nTotal: {}/{} tests passed".format(passed, total))
    
    if passed == total:
        print("🎉 All tests passed! New configuration structure is working.")
        return True
    else:
        print("⚠️  Some tests failed, please check the configuration files.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)