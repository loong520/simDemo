"""
芯片仿真自动化Demo - 主程序
提供命令行接口和图形界面来运行仿真
"""

import argparse
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, SimulationConfig
from ocean_generator import OceanScriptGenerator, generate_ocean_script
from simulator import SimulationExecutor, run_simulation


class SimulationManager:
    """仿真管理器"""
    
    def __init__(self, config_file: Optional[str] = None, work_dir: Optional[str] = None):
        """
        初始化仿真管理器
        
        Args:
            config_file: 配置文件路径
            work_dir: 工作目录
        """
        self.config_file = config_file
        self.work_dir = work_dir or "./sim_work"
        self.config = None
        self.executor = None
        
        if config_file:
            self.load_configuration(config_file)
    
    def load_configuration(self, config_file: str):
        """加载配置文件"""
        try:
            print(f"Loading configuration file: {config_file}")
            self.config = load_config(config_file)
            self.config_file = config_file
            print("Configuration file loaded successfully!")
            self._print_config_summary()
        except Exception as e:
            print(f"Configuration file loading failed: {e}")
            raise
    
    def _print_config_summary(self):
        """打印配置摘要"""
        if not self.config:
            return
        
        print("\n" + "="*50)
        print("Simulation Configuration Summary")
        print("="*50)
        print(f"Project name: {self.config.project_name}")
        print(f"Simulator: {self.config.simulator}")
        print(f"Design path: {self.config.design_path}")
        print(f"Results directory: {self.config.results_dir}")
        print(f"Simulation temperature: {self.config.temperature}°C")
        
        if self.config.analyses:
            print(f"Analysis types: {', '.join(self.config.analyses.keys())}")
        
        if self.config.model_files:
            print(f"Number of model files: {len(self.config.model_files)}")
        
        if self.config.save_nodes:
            print(f"Number of saved nodes: {len(self.config.save_nodes)}")
        
        if self.config.design_variables:
            print(f"Number of design variables: {len(self.config.design_variables)}")
        
        print("="*50 + "\n")
    
    def generate_scripts(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        生成仿真脚本
        
        Args:
            output_dir: 输出目录
            
        Returns:
            生成的脚本路径字典
        """
        if not self.config:
            raise ValueError("Please load configuration file first")
        
        output_dir = output_dir or str(Path(self.work_dir) / "scripts")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("Generating simulation scripts...")
        
        generator = OceanScriptGenerator(self.config)
        
        # 生成Ocean脚本
        ocean_script = output_path / f"{self.config.project_name}.ocn"
        ocean_path = generator.save_script(str(ocean_script))
        
        # 生成Python脚本
        python_script = output_path / f"{self.config.project_name}_skillbridge.py"
        python_content = generator.generate_python_skillbridge_script()
        with open(python_script, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        script_paths = {
            'ocean_script': ocean_path,
            'python_script': str(python_script.absolute())
        }
        
        print(f"Ocean script generated: {ocean_path}")
        print(f"Python script generated: {python_script}")
        
        return script_paths
    
    def run_simulation(self, simulation_type: str = "ocean", timeout: int = 3600) -> bool:
        """
        运行仿真
        
        Args:
            simulation_type: 仿真类型 ("ocean" 或 "python")
            timeout: 超时时间（秒）
            
        Returns:
            仿真是否成功
        """
        if not self.config:
            raise ValueError("Please load configuration file first")
        
        print(f"\nStarting {simulation_type.upper()} simulation...")
        print(f"Timeout setting: {timeout} seconds")
        
        # 创建执行器
        self.executor = SimulationExecutor(self.config, self.work_dir)
        
        try:
            # 准备仿真
            if not self.executor.prepare_simulation():
                print("Simulation preparation failed")
                return False
            
            # 运行仿真
            if simulation_type.lower() == "python":
                success, output = self.executor.run_python_simulation(timeout)
            else:
                success, output = self.executor.run_ocean_simulation(timeout)
            
            # 打印结果
            if success:
                print("\nSimulation completed successfully!")
                self._print_simulation_results()
            else:
                print("\nSimulation failed!")
                print("Error output:")
                print(output)
            
            return success
            
        except Exception as e:
            print(f"Error running simulation: {e}")
            return False
    
    def _print_simulation_results(self):
        """打印仿真结果摘要"""
        if not self.executor:
            return
        
        status = self.executor.get_simulation_status()
        results = self.executor.collect_results()
        
        print("\n" + "="*50)
        print("Simulation Results Summary")
        print("="*50)
        print(f"Status: {status['status']}")
        
        if status['duration']:
            print(f"Duration: {status['duration']}")
        
        print(f"Results directory: {status['results_dir']}")
        
        if results['files']:
            print(f"Generated files count: {len(results['files'])}")
        
        if results['plots']:
            print(f"Generated plots count: {len(results['plots'])}")
        
        if results['data']:
            print(f"Data files count: {len(results['data'])}")
        
        print("="*50 + "\n")
    
    def interactive_mode(self):
        """交互式模式"""
        print("="*60)
        print("Chip Simulation Automation Demo - Interactive Mode")
        print("="*60)
        
        while True:
            print("\nAvailable operations:")
            print("1. Load configuration file")
            print("2. Display current configuration")
            print("3. Generate simulation scripts")
            print("4. Run Ocean simulation")
            print("5. Run Python simulation")
            print("6. View simulation status")
            print("7. Exit")
            
            choice = input("\nPlease select operation (1-7): ").strip()
            
            try:
                if choice == '1':
                    config_file = input("Please enter configuration file path: ").strip()
                    self.load_configuration(config_file)
                
                elif choice == '2':
                    if self.config:
                        self._print_config_summary()
                    else:
                        print("Please load configuration file first")
                
                elif choice == '3':
                    if not self.config:
                        print("Please load configuration file first")
                        continue
                    
                    output_dir = input("Please enter output directory (press Enter for default): ").strip()
                    scripts = self.generate_scripts(output_dir if output_dir else None)
                    print("Script generation completed!")
                
                elif choice == '4':
                    if not self.config:
                        print("Please load configuration file first")
                        continue
                    
                    timeout_str = input("Please enter timeout in seconds (press Enter for default 3600): ").strip()
                    timeout = int(timeout_str) if timeout_str else 3600
                    
                    self.run_simulation("ocean", timeout)
                
                elif choice == '5':
                    if not self.config:
                        print("Please load configuration file first")
                        continue
                    
                    timeout_str = input("Please enter timeout in seconds (press Enter for default 3600): ").strip()
                    timeout = int(timeout_str) if timeout_str else 3600
                    
                    self.run_simulation("python", timeout)
                
                elif choice == '6':
                    if self.executor:
                        status = self.executor.get_simulation_status()
                        print(json.dumps(status, indent=2, ensure_ascii=False))
                    else:
                        print("No simulation has been run yet")
                
                elif choice == '7':
                    print("Exiting program")
                    break
                
                else:
                    print("Invalid selection, please try again")
                    
            except Exception as e:
                print(f"Operation failed: {e}")
            
            input("\nPress Enter to continue...")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Analog Chip Simulation Automation Demo",
    )
    
    parser.add_argument('-c', '--config',
                       help='Configuration file path')
    
    parser.add_argument('-w', '--workdir', 
                       default='./sim_work',
                       help='Working directory (default: ./sim_work)')
    
    parser.add_argument('-g', '--generate-only', 
                       action='store_true',
                       help='Generate scripts only, do not run simulation')
    
    parser.add_argument('-r', '--run', 
                       choices=['ocean', 'python'],
                       help='Simulation type to run')
    
    parser.add_argument('-t', '--timeout', 
                       type=int, 
                       default=3600,
                       help='Simulation timeout in seconds (default: 3600)')
    
    parser.add_argument('-o', '--output',
                       help='Script output directory')
    
    parser.add_argument('-i', '--interactive', 
                       action='store_true',
                       help='Interactive mode')
    
    parser.add_argument('--version', 
                       action='version', 
                       version='Chip Simulation Automation Demo v1.0')
    
    args = parser.parse_args()
    
    try:
        # 交互式模式
        if args.interactive or not args.config:
            manager = SimulationManager(work_dir=args.workdir)
            manager.interactive_mode()
            return
        
        # 命令行模式
        manager = SimulationManager(args.config, args.workdir)
        
        # 仅生成脚本
        if args.generate_only:
            scripts = manager.generate_scripts(args.output)
            print("Script generation completed!")
            return
        
        # 运行仿真
        if args.run:
            success = manager.run_simulation(args.run, args.timeout)
            sys.exit(0 if success else 1)
        else:
            # 默认进入交互式模式
            manager.interactive_mode()
            
    except KeyboardInterrupt:
        print("\nUser interrupted operation")
        sys.exit(1)
    except Exception as e:
        print(f"Program execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()