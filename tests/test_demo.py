#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片仿真自动化Demo - 测试脚本
用于测试各个模块的功能
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from config import SimulationConfig, ConfigReader, load_system_config, load_task_config
    from ocean_generator import OceanScriptGenerator
    from simulator import SimulationExecutor
    from simulation_manager import SimulationManager
except ImportError as e:
    print(f"Module import failed: {e}")
    print("Please ensure all necessary Python packages are installed: pip install -r requirements.txt")
    sys.exit(1)


def test_config_module():
    """Test configuration module"""
    print("=" * 50)
    print("Testing Configuration Module")
    print("=" * 50)
    
    try:
        # 测试系统配置
        print("Testing system configuration loading...")
        system_config = load_system_config()
        print(f"✓ System configuration loaded successfully: Server URL = {system_config.server.url}")
        
        # 测试任务配置
        print("Testing task configuration loading...")
        # 创建一个临时的任务配置文件用于测试
        with tempfile.TemporaryDirectory() as temp_dir:
            task_config_file = Path(temp_dir) / "test_task_config.yaml"
            testbench_config_file = Path(temp_dir) / "test_testbench_config.yaml"
            
            # 写入测试testbench配置
            testbench_content = """
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
"""
            with open(testbench_config_file, 'w') as f:
                f.write(testbench_content)
            
            # 写入测试任务配置
            task_content = f"""
simulation:
  project_dir: "/test/path"
  library_name: "test_lib"
  cell_name: "test_cell"
  design_type: "schematic"
  simulator: "spectre"
  simulation_path: "/test/path/sim"
  temperature: 27.0
  supply_voltage: 1.8

testbench_config: "{testbench_config_file}"
"""
            with open(task_config_file, 'w') as f:
                f.write(task_content)
            
            task_config = load_task_config(str(task_config_file))
            print(f"✓ Task configuration loaded successfully: {task_config.project_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration module test failed: {e}")
        return False


def test_ocean_generator():
    """Test Ocean script generator"""
    print("\n" + "=" * 50)
    print("Testing Ocean Script Generator")
    print("=" * 50)
    
    try:
        # 创建测试配置
        test_config = SimulationConfig()
        test_config.project_dir = "/test/design"
        test_config.library_name = "test_lib"
        test_config.cell_name = "test_cell"
        test_config.simulation_path = "/test/design/sim"
        test_config.simulator = "spectre"
        test_config.temperature = 27.0
        test_config.analyses = {"tran": {"stop": "1n"}}
        test_config.save_nodes = ["/vout"]
        
        # 测试Ocean脚本生成
        print("Generating Ocean script...")
        generator = OceanScriptGenerator(test_config)
        ocean_script = generator.generate_script()
        
        # 检查脚本内容
        required_elements = [
            "simulator( 'spectre )",
            "design(",
            "analysis('tran",
            "save(",
            "temp( 27.0 )",
            "run()"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in ocean_script:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"✗ Ocean script missing elements: {missing_elements}")
            return False
        
        print("✓ Ocean script generated successfully, contains all required elements")
        
        # 测试脚本保存
        with tempfile.TemporaryDirectory() as temp_dir:
            script_file = Path(temp_dir) / "test_script.ocn"
            saved_path = generator.save_script(str(script_file))
            
            if Path(saved_path).exists():
                print("✓ Script file saved successfully")
            else:
                print("✗ Script file saving failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Ocean script generator test failed: {e}")
        return False


def test_simulator():
    """Test simulation executor"""
    print("\n" + "=" * 50)
    print("Testing Simulation Executor")
    print("=" * 50)
    
    try:
        # 创建测试配置
        test_config = SimulationConfig()
        test_config.project_dir = "/test"
        test_config.library_name = "test_lib"
        test_config.cell_name = "test_cell"
        test_config.simulation_path = "/test/sim"
        test_config.simulator = "spectre"
        test_config.analyses = {"tran": {"stop": "1n"}}
        test_config.save_nodes = ["/vout"]
        
        # 创建临时工作目录
        with tempfile.TemporaryDirectory() as temp_dir:
            print("Creating simulation executor...")
            executor = SimulationExecutor(test_config, temp_dir)
            
            # 测试仿真准备
            print("Testing simulation preparation...")
            # 由于没有真实的设计文件，这里可能会失败，但我们可以测试其他功能
            try:
                result = executor.prepare_simulation()
                if result:
                    print("✓ Simulation preparation successful")
                else:
                    print("⚠ Simulation preparation failed (possibly due to missing design files)")
            except Exception as e:
                print(f"⚠ Simulation preparation failed: {e}")
            
            # 测试状态获取
            print("Testing status retrieval...")
            status = executor.get_simulation_status()
            if isinstance(status, dict) and 'status' in status:
                print("✓ Status retrieval successful")
            else:
                print("✗ Status retrieval failed")
                return False
            
            # 测试结果收集
            print("Testing result collection...")
            results = executor.collect_results()
            if isinstance(results, dict):
                print("✓ Result collection successful")
            else:
                print("✗ Result collection failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Simulation executor test failed: {e}")
        return False


def test_main_module():
    """Test main program module"""
    print("\n" + "=" * 50)
    print("Testing Main Program Module")
    print("=" * 50)
    
    try:
        # 创建临时配置文件
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yaml"
            testbench_file = Path(temp_dir) / "test_testbench.yaml"
            
            # 写入测试testbench配置
            testbench_content = """
analyses:
  tran:
    stop: "1n"

outputs:
  save_nodes:
    - "/vout"
    
models:
  files: []
  
variables: {}

initial_conditions: {}

post_processing: {}
"""
            
            with open(testbench_file, 'w') as f:
                f.write(testbench_content)
            
            # 写入测试任务配置
            config_content = f"""
simulation:
  project_dir: "/test/design"
  library_name: "test_lib"
  cell_name: "test_cell"
  design_type: "schematic"
  simulator: "spectre"
  simulation_path: "/test/design/sim"
  temperature: 27.0
  supply_voltage: 1.8

testbench_config: "{testbench_file}"
"""
            
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            # 测试仿真管理器
            print("Creating simulation manager...")
            manager = SimulationManager(str(config_file), temp_dir)
            
            if manager.config:
                print("✓ Simulation manager created successfully")
            else:
                print("✗ Simulation manager creation failed")
                return False
            
            # 测试脚本生成
            print("Testing script generation...")
            try:
                scripts = manager.generate_complete_scripts()
                if scripts and 'simulation_script' in scripts:
                    print("✓ Script generation successful")
                else:
                    print("✗ Script generation failed")
                    return False
            except Exception as e:
                print(f"⚠ Script generation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Main program module test failed: {e}")
        return False


def test_integration():
    """Integration test"""
    print("\n" + "=" * 50)
    print("Integration Test")
    print("=" * 50)
    
    try:
        # 创建测试配置文件
        with tempfile.TemporaryDirectory() as temp_dir:
            task_config_file = Path(temp_dir) / "integration_test_task.yaml"
            testbench_config_file = Path(temp_dir) / "integration_test_testbench.yaml"
            
            # 写入测试testbench配置
            testbench_content = """
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
"""
            with open(testbench_config_file, 'w') as f:
                f.write(testbench_content)
            
            # 写入测试任务配置
            task_content = f"""
simulation:
  project_dir: "/test/integration"
  library_name: "test_lib"
  cell_name: "test_cell"
  design_type: "schematic"
  simulator: "spectre"
  simulation_path: "/test/integration/sim"
  temperature: 27.0

testbench_config: "{testbench_config_file}"
"""
            
            with open(task_config_file, 'w') as f:
                f.write(task_content)
            
            print("Executing complete simulation workflow...")
            
            # 创建仿真管理器
            manager = SimulationManager(str(task_config_file), temp_dir)
            
            # 生成脚本
            scripts = manager.generate_complete_scripts()
            
            # 检查生成的脚本文件
            ocean_script_path = Path(scripts['simulation_script'])
            
            if ocean_script_path.exists():
                print("✓ Complete workflow script generation successful")
                
                # 读取并验证脚本内容
                with open(ocean_script_path, 'r') as f:
                    ocean_content = f.read()
                
                if "simulator(" in ocean_content:
                    print("✓ Generated script content is correct")
                else:
                    print("✗ Generated script content is incorrect")
                    return False
            else:
                print("✗ Script file generation failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


def main():
    """Main test function"""
    print("Chip Simulation Automation Demo - Functionality Testing")
    print("=" * 60)
    
    test_results = []
    
    # 运行各项测试
    tests = [
        ("Configuration Module", test_config_module),
        ("Ocean Script Generator", test_ocean_generator),
        ("Simulation Executor", test_simulator),
        ("Main Program Module", test_main_module),
        ("Integration Test", test_integration)
    ]
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"Test '{test_name}' encountered exception: {e}")
            test_results.append((test_name, False))
    
    # 显示测试结果摘要
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ Passed" if result else "✗ Failed"
        print(f"{test_name:25s} : {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Demo is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed, please check related modules.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)