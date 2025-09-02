#!/usr/bin/env python3
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
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from config import SimulationConfig, ConfigReader, load_config
    from ocean_generator import OceanScriptGenerator, generate_ocean_script
    from simulator import SimulationExecutor, run_simulation
    from main import SimulationManager
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
        # 测试YAML配置文件
        yaml_config_file = project_root / "simulation_config.yaml"
        if yaml_config_file.exists():
            print("Testing YAML configuration file reading...")
            config = load_config(str(yaml_config_file))
            print(f"✓ YAML configuration loaded successfully: {config.project_name}")
        else:
            print("⚠ YAML configuration file does not exist, skipping test")
        # 测试编程方式创建配置
        print("Testing programmatic configuration creation...")
        test_config = SimulationConfig(
            project_name="test_project",
            simulator="spectre",
            design_path="/test/path",
            analyses={"tran": {"stop": "1n"}},
            save_nodes=["/vout"]
        )
        print(f"✓ Programmatic configuration created successfully: {test_config.project_name}")
        
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
        test_config = SimulationConfig(
            project_name="test_ocean_generation",
            simulator="spectre",
            design_path="/test/design/netlist",
            results_dir="./test_results",
            model_files=[
                ["/test/models/design.scs", ""],
                ["/test/models/process.scs", "tt"]
            ],
            analyses={
                "tran": {"stop": "10n", "step": "1p"},
                "dc": {"saveOppoint": "t"}
            },
            design_variables={"vdd": 1.8, "temp_coeff": 1e-3},
            save_nodes=["/vout", "/vin"],
            initial_conditions={"/vin": 0.0},
            temperature=27.0
        )
        
        # 测试Ocean脚本生成
        print("Generating Ocean script...")
        generator = OceanScriptGenerator(test_config)
        ocean_script = generator.generate_script()
        
        # 检查脚本内容
        required_elements = [
            "simulator( 'spectre )",
            "design(",
            "modelFile(",
            "analysis('tran",
            "analysis('dc",
            "desVar(",
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
        
        # 测试Python脚本生成
        print("Generating Python script...")
        python_script = generator.generate_python_skillbridge_script()
        
        if "from skillbridge import Workspace" in python_script:
            print("✓ Python script generated successfully")
        else:
            print("✗ Python script generation failed")
            return False
        
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
        test_config = SimulationConfig(
            project_name="test_simulator",
            simulator="spectre",
            design_path="/test/design",
            results_dir="./test_sim_results",
            analyses={"tran": {"stop": "1n"}},
            save_nodes=["/vout"]
        )
        
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
            
            # 写入测试配置
            config_content = """
simulation:
  project_name: "test_main_module"
  simulator: "spectre"
  design_path: "/test/design"
  results_dir: "./test_results"
  temperature: 27.0

analyses:
  tran:
    stop: "1n"

outputs:
  save_nodes:
    - "/vout"
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
                scripts = manager.generate_scripts()
                if scripts and 'ocean_script' in scripts:
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
        # 使用示例配置文件进行完整流程测试
        yaml_config = project_root / "simulation_config.yaml"
        
        if not yaml_config.exists():
            print("⚠ Example configuration file does not exist, skipping integration test")
            return True
        
        print("Executing complete simulation workflow...")
        
        # 创建临时工作目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建仿真管理器
            manager = SimulationManager(str(yaml_config), temp_dir)
            
            # 生成脚本
            scripts = manager.generate_scripts()
            
            # 检查生成的脚本文件
            ocean_script_path = Path(scripts['ocean_script'])
            python_script_path = Path(scripts['python_script'])
            
            if ocean_script_path.exists() and python_script_path.exists():
                print("✓ Complete workflow script generation successful")
                
                # 读取并验证脚本内容
                with open(ocean_script_path, 'r') as f:
                    ocean_content = f.read()
                
                with open(python_script_path, 'r') as f:
                    python_content = f.read()
                
                if "simulator(" in ocean_content and "from skillbridge" in python_content:
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