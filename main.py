#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片仿真自动化Demo - 主程序
提供命令行接口和图形界面来运行仿真
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config, SimulationConfig
from ocean_generator import OceanScriptGenerator
from shell_generator import ShellScriptGenerator


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
        self.work_dir = work_dir or "./.sim_work"
        self.config = None
        self.executor = None
        
        if config_file:
            self.load_configuration(config_file)
    
    def load_configuration(self, config_file: str):
        """Load configuration file"""
        try:
            print(f"Loading configuration file: {config_file}")
            self.config = load_config(config_file)
            self.config_file = config_file
            print("Configuration file loaded successfully!")
            
            self._print_config_summary()
        except Exception as e:
            print(f"Configuration file loading failed: {e}")
            raise
    
    def _generate_netlist_script(self):
        """Generate Ocean script for netlist creation"""
        if not self.config:
            return
            
        try:
            print("Generating netlist creation script...")
            
            # Create work directory if it doesn't exist
            work_path = Path(self.work_dir)
            work_path.mkdir(parents=True, exist_ok=True)
            
            # Generate netlist script directly in work_dir
            generator = OceanScriptGenerator(self.config)
            script_path = generator.save_netlist_script(str(work_path / "create_netlist.ocn"))
            
            print(f"Netlist creation script generated: {script_path}")
            print("Execute this script in Ocean to generate the netlist file:")
            print(f"  ocean < {script_path}")
            
        except Exception as e:
            print(f"Warning: Failed to generate netlist script: {e}")
    
    def _generate_netlist_shell_script(self):
        """Generate shell script to run the netlist creation script"""
        if not self.config:
            print("Please load configuration file first")
            return
            
        try:
            print("Generating netlist shell script...")
            
            # Create work directory if it doesn't exist
            work_path = Path(self.work_dir)
            work_path.mkdir(parents=True, exist_ok=True)
            
            # Generate shell script using ShellScriptGenerator
            shell_generator = ShellScriptGenerator(self.config)
            script_path = shell_generator.generate_netlist_script(output_dir=str(work_path))
            
            print(f"Netlist shell script generated: {script_path}")
            print("Execute this script to run the netlist creation:")
            print(f"  bash {script_path}")
            
        except Exception as e:
            print(f"Warning: Failed to generate netlist shell script: {e}")
    
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
    
    def generate_complete_scripts(self, 
                                 output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        生成完整的仿真包（一步式）
        
        Args:
            output_dir: 输出目录
            
        Returns:
            生成的脚本路径字典
        """
        if not self.config:
            raise ValueError("Please load configuration file first")
        
        output_dir = output_dir or str(Path(self.work_dir) / "scripts")
        
        print(f"Generating complete Ocean simulation package...")
        
        # 使用Shell生成器一步式生成所有脚本
        shell_generator = ShellScriptGenerator(self.config)
        script_paths = shell_generator.generate_complete_simulation_package(
            script_type="ocean",
            output_dir=output_dir
        )
        
        print(f"Simulation script generated: {script_paths['simulation_script']}")
        print(f"Executable shell script generated: {script_paths['shell_script']}")
        print("\nTo run the simulation, execute:")
        print(f"  bash {script_paths['shell_script']}")
        
        return script_paths

    
    def run_simulation_package(self, timeout: int = 3600) -> bool:
        """
        生成并运行完整的仿真包
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            仿真是否成功
        """
        if not self.config:
            raise ValueError("Please load configuration file first")
        
        try:
            # 第一步：生成完整的仿真包
            print(f"Step 1: Generating Ocean simulation package...")
            script_paths = self.generate_complete_scripts()
            
            # 第二步：执行shell脚本
            print(f"\nStep 2: Executing shell script...")
            shell_script_path = script_paths['shell_script']
            
            # 使用subprocess直接执行shell脚本
            cwd = Path(shell_script_path).parent
            print(f"Working directory: {cwd}")
            print(f"Executing: bash {shell_script_path}")
            
            # 运行shell脚本
            result = subprocess.run(
                ['bash', shell_script_path],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                print("\nSimulation completed successfully!")
                print("Output:")
                print(result.stdout)
                return True
            else:
                print("\nSimulation failed!")
                print("Error output:")
                print(result.stderr)
                print("Standard output:")
                print(result.stdout)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"\nSimulation timeout after {timeout} seconds")
            return False
        except Exception as e:
            print(f"\nError running simulation package: {e}")
            return False


    def run_simulation(self, timeout: int = 3600) -> bool:
        """
        运行仿真
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            仿真是否成功
        """
        if not self.config:
            raise ValueError("Please load configuration file first")
        
        print(f"\nStarting Ocean simulation...")
        print(f"Timeout setting: {timeout} seconds")
        
        # 创建执行器
        self.executor = SimulationExecutor(self.config, self.work_dir)
        
        try:
            # 准备仿真
            if not self.executor.prepare_simulation():
                print("Simulation preparation failed")
                return False
            
            # 运行仿真
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
            print("3. Generate netlist creation script")
            print("4. Generate netlist shell script")
            print("5. Generate Ocean simulation package")
            print("6. Run Ocean simulation (complete package)")
            print("7. Run legacy Ocean simulation")
            print("8. View simulation status")
            print("9. Exit")
            
            choice = input("\nPlease select operation (1-9): ").strip()
            
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
                    
                    self._generate_netlist_script()
                
                elif choice == '4':
                    if not self.config:
                        print("Please load configuration file first")
                        continue
                    
                    self._generate_netlist_shell_script()
                
                elif choice == '5':
                    if not self.config:
                        print("Please load configuration file first")
                        continue
                    
                    output_dir = input("Please enter output directory (press Enter for default): ").strip()
                    scripts = self.generate_complete_scripts(output_dir if output_dir else None)
                    print("Ocean simulation package generated!")
                
                elif choice == '6':
                    if not self.config:
                        print("Please load configuration file first")
                        continue
                    
                    timeout_str = input("Please enter timeout in seconds (press Enter for default 3600): ").strip()
                    timeout = int(timeout_str) if timeout_str else 3600
                    
                    self.run_simulation_package(timeout)
                
                elif choice == '7':
                    if not self.config:
                        print("Please load configuration file first")
                        continue
                    
                    timeout_str = input("Please enter timeout in seconds (press Enter for default 3600): ").strip()
                    timeout = int(timeout_str) if timeout_str else 3600
                    
                    self.run_simulation(timeout)
                
                elif choice == '8':
                    if self.executor:
                        status = self.executor.get_simulation_status()
                        print(json.dumps(status, indent=2, ensure_ascii=False))
                    else:
                        print("No simulation has been run yet")
                
                elif choice == '9':
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
                       default='./.sim_work',
                       help='Working directory (default: ./.sim_work)')
    
    parser.add_argument('-g', '--generate-only', 
                       action='store_true',
                       help='Generate scripts only, do not run simulation')
    
    parser.add_argument('--generate-netlist-script',
                       action='store_true',
                       help='Generate netlist creation script only')
    
    parser.add_argument('--generate-netlist-shell',
                       action='store_true',
                       help='Generate netlist shell script only')
    
    parser.add_argument('-r', '--run', 
                       choices=['ocean', 'package'],
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
        
        # 仅生成网表脚本
        if args.generate_netlist_script:
            manager._generate_netlist_script()
            print("Netlist script generation completed!")
            return
        
        # 仅生成网表shell脚本
        if args.generate_netlist_shell:
            manager._generate_netlist_shell_script()
            print("Netlist shell script generation completed!")
            return
        
        # 仅生成脚本
        if args.generate_only:
            scripts = manager.generate_complete_scripts(args.output)
            print("Script generation completed!")
            return
        
        # 运行仿真
        if args.run:
            if args.run == 'package':
                success = manager.run_simulation_package(args.timeout)
            else:
                success = manager.run_simulation(args.timeout)
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