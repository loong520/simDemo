#!/usr/bin/env python3
"""
芯片仿真自动化Demo - 简单演示脚本
展示核心功能的使用方法
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_config_loading():
    """演示配置文件加载"""
    print("=" * 60)
    print("Demo 1: Configuration File Loading")
    print("=" * 60)
    
    try:
        from config import SimulationConfig, load_config
        
        # 方法1: 编程方式创建配置
        print("Method 1: Programmatic Configuration Creation")
        config = SimulationConfig(
            project_name="demo_amplifier",
            simulator="spectre",
            design_path="/demo/path/amplifier.scs",
            results_dir="./demo_results",
            temperature=27.0,
            supply_voltage=1.8
        )
        
        config.analyses = {
            "tran": {"stop": "10n", "step": "1p"},
            "dc": {"saveOppoint": "t"}
        }
        
        config.design_variables = {
            "vdd": 1.8,
            "load_cap": 100e-15,
            "bias_current": 10e-6
        }
        
        config.save_nodes = ["/vout", "/vin", "/vdd"]
        
        print(f"✅ Project name: {config.project_name}")
        print(f"✅ Simulator: {config.simulator}")
        print(f"✅ Analysis types: {list(config.analyses.keys())}")
        print(f"✅ Number of design variables: {len(config.design_variables)}")
        print(f"✅ Number of saved nodes: {len(config.save_nodes)}")
        
        # 方法2: 从YAML文件加载（如果存在）
        yaml_config_file = project_root / "simulation_config.yaml"
        if yaml_config_file.exists():
            print("\nMethod 2: Load Configuration from YAML File")
            yaml_config = load_config(str(yaml_config_file))
            print(f"✅ Successfully loaded from YAML: {yaml_config.project_name}")
        else:
            print("\n⚠️ YAML configuration file does not exist, skipping demo")
        
        return config
        
    except Exception as e:
        print(f"❌ Configuration loading demo failed: {e}")
        return None

def demo_ocean_script_generation(config):
    """演示Ocean脚本生成"""
    print("\n" + "=" * 60)
    print("Demo 2: Ocean Script Generation")
    print("=" * 60)
    
    try:
        from ocean_generator import OceanScriptGenerator
        
        # 创建脚本生成器
        generator = OceanScriptGenerator(config)
        
        # 生成Ocean脚本
        print("Generating Ocean script...")
        ocean_script = generator.generate_script()
        
        # 显示脚本预览
        lines = ocean_script.split('\n')
        print(f"✅ Ocean script generated successfully, {len(lines)} lines total")
        print("\n--- Ocean Script Preview (first 15 lines) ---")
        for i, line in enumerate(lines[:15]):
            print(f"{i+1:2d}: {line}")
        
        if len(lines) > 15:
            print(f"... ({len(lines)-15} more lines)")
        
        # 保存脚本到文件
        script_file = project_root / "demo_generated.ocn"
        generator.save_script(str(script_file))
        print(f"✅ Ocean script saved to: {script_file}")
        
        # 生成Python脚本
        print("\nGenerating Python skillbridge script...")
        python_script = generator.generate_python_skillbridge_script()
        python_lines = python_script.split('\n')
        print(f"✅ Python script generated successfully, {len(python_lines)} lines total")
        
        # 保存Python脚本
        python_file = project_root / "demo_generated_skillbridge.py"
        with open(python_file, 'w', encoding='utf-8') as f:
            f.write(python_script)
        print(f"✅ Python script saved to: {python_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Script generation demo failed: {e}")
        return False

def demo_simulation_manager():
    """演示仿真管理功能"""
    print("\n" + "=" * 60)
    print("Demo 3: Simulation Management")
    print("=" * 60)
    
    try:
        from simulator import SimulationExecutor
        from main import SimulationManager
        
        # 创建测试配置
        from config import SimulationConfig
        
        test_config = SimulationConfig(
            project_name="demo_manager_test",
            simulator="spectre",
            design_path="/demo/test/design",
            results_dir="./demo_test_results"
        )
        
        test_config.analyses = {"tran": {"stop": "1n"}}
        test_config.save_nodes = ["/vout"]
        
        print("Creating simulation executor...")
        executor = SimulationExecutor(test_config, "./demo_work")
        
        # 获取状态信息
        status = executor.get_simulation_status()
        print(f"✅ Simulation status: {status['status']}")
        print(f"✅ Work directory: {status['work_dir']}")
        print(f"✅ Results directory: {status['results_dir']}")
        
        # 演示仿真管理器
        print("\nCreating simulation manager...")
        manager = SimulationManager(work_dir="./demo_manager_work")
        
        # 加载配置
        manager.config = test_config
        print(f"✅ Manager created successfully")
        
        # 生成脚本（不运行仿真）
        print("\nGenerating script files...")
        scripts = manager.generate_scripts("./demo_scripts")
        print(f"✅ Script generation completed:")
        for script_type, script_path in scripts.items():
            print(f"   {script_type}: {script_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation management demo failed: {e}")
        return False

def demo_complete_workflow():
    """演示完整工作流程"""
    print("\n" + "=" * 60)
    print("Demo 4: Complete Workflow")
    print("=" * 60)
    
    try:
        from main import SimulationManager
        
        # 创建完整的仿真配置
        from config import SimulationConfig
        
        complete_config = SimulationConfig(
            project_name="complete_demo",
            simulator="spectre",
            design_path="/demo/complete/amplifier_netlist",
            results_dir="./complete_demo_results",
            temperature=27.0,
            supply_voltage=1.8
        )
        
        # 完整的分析配置
        complete_config.analyses = {
            "tran": {
                "stop": "100n",
                "step": "1p", 
                "maxstep": "10p"
            },
            "dc": {
                "saveOppoint": "t",
                "param1": "vin",
                "start1": 0,
                "stop1": 1.8,
                "step1": 0.1
            },
            "ac": {
                "start": "1",
                "stop": "1G",
                "dec": 10
            }
        }
        
        # 模型文件配置
        complete_config.model_files = [
            ["/demo/models/design.scs", ""],
            ["/demo/models/process.scs", "tt"],
            ["/demo/models/parasitic.scs", ""]
        ]
        
        # 设计变量
        complete_config.design_variables = {
            "vdd": 1.8,
            "vth": 0.4,
            "load_cap": 100e-15,
            "bias_current": 10e-6,
            "temperature_coeff": 1e-3
        }
        
        # 保存节点
        complete_config.save_nodes = [
            "/vout", "/vin", "/vdd", "/vss", "/ibias"
        ]
        
        # 初始条件
        complete_config.initial_conditions = {
            "/vout": 0.9,
            "/vin": 0.0
        }
        
        # 后处理配置
        complete_config.post_processing = {
            "plot_enabled": True,
            "save_data": True,
            "plots": [
                {"data": "v(\"/vout\")", "xlabel": "Time (s)", "ylabel": "Voltage (V)"},
                {"data": "v(\"/vin\")", "xlabel": "Time (s)", "ylabel": "Voltage (V)"}
            ],
            "save_items": [
                {"file": "vout_data.csv", "data": "v(\"/vout\")"},
                {"file": "vin_data.csv", "data": "v(\"/vin\")"}
            ]
        }
        
        print("Complete configuration created:")
        print(f"✅ Project name: {complete_config.project_name}")
        print(f"✅ Simulator: {complete_config.simulator}")
        print(f"✅ Analysis types: {list(complete_config.analyses.keys())}")
        print(f"✅ Model files count: {len(complete_config.model_files)}")
        print(f"✅ Design variables count: {len(complete_config.design_variables)}")
        print(f"✅ Save nodes count: {len(complete_config.save_nodes)}")
        print(f"✅ Initial conditions count: {len(complete_config.initial_conditions)}")
        
        # 创建管理器并生成脚本
        print("\nCreating simulation manager and generating scripts...")
        manager = SimulationManager(work_dir="./complete_demo_work")
        manager.config = complete_config
        
        scripts = manager.generate_scripts("./complete_demo_scripts")
        print(f"✅ Complete workflow scripts generated:")
        for script_type, script_path in scripts.items():
            script_file = Path(script_path)
            if script_file.exists():
                size = script_file.stat().st_size
                print(f"   {script_type}: {script_path} ({size} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow demo failed: {e}")
        return False

def main():
    """主演示函数"""
    print("🔬 Chip Simulation Automation Demo - Feature Demonstration")
    print("=" * 60)
    print("This demonstration will showcase the following features:")
    print("1. Configuration file loading and creation")
    print("2. Ocean script automatic generation")
    print("3. Simulation management functionality")
    print("4. Complete workflow")
    print("=" * 60)
    
    # 运行各项演示
    results = []
    
    # 演示1: 配置加载
    config = demo_config_loading()
    results.append(("Configuration Loading", config is not None))
    
    if config:
        # 演示2: 脚本生成
        script_result = demo_ocean_script_generation(config)
        results.append(("Script Generation", script_result))
    else:
        results.append(("Script Generation", False))
    
    # 演示3: 仿真管理
    manager_result = demo_simulation_manager()
    results.append(("Simulation Management", manager_result))
    
    # 演示4: 完整流程
    workflow_result = demo_complete_workflow()
    results.append(("Complete Workflow", workflow_result))
    
    # 显示演示结果
    print("\n" + "=" * 60)
    print("Demo Results Summary")
    print("=" * 60)
    
    success_count = 0
    for demo_name, success in results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"{demo_name:20s}: {status}")
        if success:
            success_count += 1
    
    print(f"\nTotal: {success_count}/{len(results)} demos succeeded")
    
    if success_count == len(results):
        print("\n🎉 All demos succeeded!")
        print("Chip Simulation Automation Demo is functioning properly and ready to use!")
        print("\nNext steps:")
        print("1. Modify simulation_config.yaml to configure your actual simulation parameters")
        print("2. Run python main.py -i to enter interactive mode")
        print("3. Or run python main.py -c your_config.yaml -r ocean for direct simulation")
    else:
        print("\n⚠️ Some demos failed, please check related modules")
    
    # 清理演示生成的文件
    cleanup_files = [
        "demo_generated.ocn",
        "demo_generated_skillbridge.py"
    ]
    
    print(f"\nCleaning up demo files...")
    for filename in cleanup_files:
        file_path = project_root / filename
        if file_path.exists():
            file_path.unlink()
            print(f"Deleted: {filename}")

if __name__ == "__main__":
    main()


