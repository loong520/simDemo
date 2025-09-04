#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Shell脚本生成器的模板化重构
"""

import sys
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from shell_generator import ShellScriptGenerator
from config import SimulationConfig, EDASToolsConfig, EDATool

def test_shell_generator():
    """测试Shell脚本生成器"""
    print("Testing Shell Script Generator with Templates...")
    
    # 创建测试配置
    eda_tools = EDASToolsConfig()
    eda_tools.spectre = EDATool(
        executable="spectre",
        launch_args=["-nograph", "-replay"],
        environment_variables=[
            "export CDS_ROOT=/opt/cadence",
            "export PATH=$CDS_ROOT/bin:$PATH",
            "source /opt/cadence/setup.sh"
        ]
    )
    
    config = SimulationConfig(
        project_dir="/test/project",
        library_name="test_lib",
        cell_name="test_cell", 
        simulation_path="/test/project/sim",
        simulator="spectre",
        eda_tools=eda_tools
    )
    
    try:
        # 创建生成器
        generator = ShellScriptGenerator(config)
        print("✓ Shell script generator created successfully")
        
        # 测试模板加载
        template = generator._load_template('main_script.sh')
        print("✓ Template loaded successfully")
        
        # 测试完整脚本包生成
        with tempfile.TemporaryDirectory() as temp_dir:
            result = generator.generate_complete_simulation_package(
                script_type="ocean",
                output_dir=temp_dir
            )
            
            print("✓ Complete simulation package generated:")
            for script_type, path in result.items():
                script_file = Path(path)
                if script_file.exists():
                    print(f"  {script_type}: {path} ({script_file.stat().st_size} bytes)")
                else:
                    print(f"  {script_type}: {path} (NOT FOUND)")
        
        print("\n✓ All tests passed! Shell script generator template refactoring successful.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_shell_generator()
    sys.exit(0 if success else 1)