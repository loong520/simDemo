#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置文件加载功能
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import config
except ImportError as e:
    print("Module import failed: {}".format(e))
    sys.exit(1)


def test_config_loading():
    """测试配置文件加载功能"""
    print("Testing configuration loading functionality")
    print("=" * 50)
    
    try:
        # 测试系统配置加载
        print("1. Testing system configuration loading...")
        system_config = config.load_system_config()
        print("   ✓ System configuration loaded successfully")
        print("   Server URL: {}".format(system_config.server.url))
        print("   Spectre executable: {}".format(system_config.eda_tools.spectre.executable))
        
        # 创建临时配置文件进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            print("\n2. Testing task configuration loading...")
            
            # 创建testbench配置文件
            testbench_file = os.path.join(temp_dir, "test_testbench.yaml")
            with open(testbench_file, 'w') as f:
                f.write("""
models:
  files: []

analyses:
  tran:
    stop: "1n"

outputs:
  save_nodes:
    - "/vout"
    
variables: {}

initial_conditions: {}

post_processing: {}
""")
            
            # 创建任务配置文件
            task_file = os.path.join(temp_dir, "test_task.yaml")
            with open(task_file, 'w') as f:
                f.write("""
simulation:
  project_dir: "/tmp/test_project"
  library_name: "test_lib"
  cell_name: "test_cell"
  design_type: "schematic"
  simulator: "spectre"
  simulation_path: "/tmp/test_simulation"
  temperature: 27.0

testbench_config: "test_testbench.yaml"
""")
            
            # 直接使用ConfigReader来测试配置加载而不进行验证
            reader = config.ConfigReader(task_file)
            task_config = reader.get_simulation_config()
            print("   ✓ Task configuration loaded successfully")
            print("   Project name: {}".format(task_config.project_name))
            print("   Simulator: {}".format(task_config.simulator))
            print("   Analysis types: {}".format(list(task_config.analyses.keys())))
            
        print("\n" + "=" * 50)
        print("All configuration loading tests passed!")
        return True
        
    except Exception as e:
        print("Configuration loading test failed: {}".format(e))
        return False


if __name__ == "__main__":
    success = test_config_loading()
    sys.exit(0 if success else 1)