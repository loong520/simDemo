#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片仿真管理器模块
提供仿真配置管理、脚本生成和仿真执行功能
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

import config
from ocean_generator import OceanScriptGenerator
from shell_generator import ShellScriptGenerator
from simulator import SimulationExecutor


def add_simulation_arguments_legacy(subparsers):
    """
    添加仿真管理命令 (旧版本备份)
    
    Args:
        subparsers: 子命令解析器
    """
    # 仿真管理父命令
    simulation_parser = subparsers.add_parser('simulation', help='Simulation management')
    
    # 仿真相关参数
    simulation_parser.add_argument('-c', '--config',
                       help='Configuration file path')
    
    simulation_parser.add_argument('-w', '--workdir', 
                       default='./.sim_work',
                       help='Working directory (default: ./.sim_work)')
    
    simulation_parser.add_argument('-g', '--generate-only', 
                       action='store_true',
                       help='Generate scripts only, do not run simulation')
    
    simulation_parser.add_argument('--generate-netlist-script',
                       action='store_true',
                       help='Generate netlist creation script only')
    
    simulation_parser.add_argument('--generate-netlist-shell',
                       action='store_true',
                       help='Generate netlist shell script only')
    
    simulation_parser.add_argument('-r', '--run', 
                       choices=['ocean', 'package'],
                       help='Simulation type to run')
    
    simulation_parser.add_argument('-t', '--timeout', 
                       type=int, 
                       default=3600,
                       help='Simulation timeout in seconds (default: 3600)')
    
    simulation_parser.add_argument('-o', '--output',
                       help='Script output directory')
    
    simulation_parser.add_argument('-i', '--interactive', 
                       action='store_true',
                       help='Interactive mode')
    
    simulation_parser.add_argument('--version', 
                       action='version', 
                       version='Chip Simulation Automation Demo v1.0')


def handle_simulation_command_legacy(args):
    """
    处理仿真管理命令 (旧版本备份)
    
    Args:
        args: 解析后的命令行参数
        
    Returns:
        bool: 是否成功处理命令
    """
    try:
        # 交互式模式
        if args.interactive or not args.config:
            manager = SimulationManager()
            manager.work_dir = args.workdir
            manager.interactive_mode()
            return True
        
        # 命令行模式
        manager = SimulationManager()
        if args.config:
            manager.load_simulation_configuration(args.config)
        manager.work_dir = args.workdir
        
        # 仅生成网表脚本
        if args.generate_netlist_script:
            manager._generate_netlist_script(args.workdir)
            print("Netlist script generation completed!")
            return True
        
        # 仅生成网表shell脚本
        if args.generate_netlist_shell:
            manager._generate_netlist_shell_script(args.workdir)
            print("Netlist shell script generation completed!")
            return True
        
        # 仅生成脚本
        if args.generate_only:
            scripts = manager.generate_complete_scripts(args.output)
            print("Script generation completed!")
            return True
        
        # 运行仿真
        if args.run:
            if args.run == 'package':
                success = manager.run_simulation_package(args.timeout, args.workdir)
            else:
                success = manager.run_simulation(args.timeout, args.workdir)
            sys.exit(0 if success else 1)
        else:
            # 默认进入交互式模式
            manager.interactive_mode()
            return True
            
    except KeyboardInterrupt:
        print("\nUser interrupted operation")
        sys.exit(1)
    except Exception as e:
        print("Program execution failed: {}".format(e))
        sys.exit(1)


def register_simulation_commands(subparsers):
    """
    添加仿真管理命令 (新版本)
    
    Args:
        subparsers: 子命令解析器
    """
    # 仿真管理父命令
    simulation_parser = subparsers.add_parser('simulation', help='Simulation management')
    
    # 创建仿真管理子命令的子解析器
    simulation_subparsers = simulation_parser.add_subparsers(dest='simulation_action', help='Simulation management actions')
    
    # 查询所有仿真任务运行状态命令
    show_task_parser = simulation_subparsers.add_parser('show-task', help='Show all simulation task statuses')
    show_task_parser.add_argument('--project-name', help='Filter by project name')
    show_task_parser.add_argument('--library-name', help='Filter by library name')
    show_task_parser.add_argument('--cell-name', help='Filter by cell name')
    
    # 运行仿真命令
    run_task_parser = simulation_subparsers.add_parser('run-task', help='Run simulation task')
    run_task_parser.add_argument('-c', '--config', required=True, help='Configuration file path')
    
    # 创建testbench命令
    create_tb_parser = simulation_subparsers.add_parser('create-testbench', help='Create a new testbench')
    create_tb_parser.add_argument('--name', required=True, help='Testbench name')
    create_tb_parser.add_argument('--config-file', required=True, help='Configuration file path for the testbench')
    create_tb_parser.add_argument('--description', help='Testbench description')
    
    # 删除testbench命令
    delete_tb_parser = simulation_subparsers.add_parser('delete-testbench', help='Delete a testbench')
    delete_tb_parser.add_argument('--name', required=True, help='Testbench name to delete')
    
    # 更新testbench命令
    update_tb_parser = simulation_subparsers.add_parser('update-testbench', help='Update a testbench')
    update_tb_parser.add_argument('--name', required=True, help='Testbench name to update')
    update_tb_parser.add_argument('--config-file', help='New configuration file path for the testbench')
    update_tb_parser.add_argument('--description', help='New testbench description')
    
    # 列出所有testbench命令
    list_tb_parser = simulation_subparsers.add_parser('list-testbench', help='List all testbenches')


def handle_simulation_command(args):
    """
    处理仿真管理命令 (新版本)
    
    Args:
        args: 解析后的命令行参数
        
    Returns:
        bool: 是否成功处理命令
    """
    try:
        # 创建SimulationManager实例
        manager = SimulationManager()
        
        # 根据不同的操作调用相应的函数
        if args.simulation_action == 'show-task':
            # 查询所有仿真任务运行状态
            manager.list_simulation_tasks(
                project_name=args.project_name,
                library_name=args.library_name,
                cell_name=args.cell_name
            )
        elif args.simulation_action == 'run-task':
            # 运行仿真
            # 由于-c是必选参数，直接加载配置
            manager.load_simulation_configuration(args.config)
            manager.run_simulation_task(
                config_file=args.config
            )
        elif args.simulation_action == 'create-testbench':
            # 创建testbench
            manager.create_testbench(
                name=args.name,
                config_file=args.config_file,
                description=args.description
            )
        elif args.simulation_action == 'delete-testbench':
            # 删除testbench
            manager.delete_testbench(
                name=args.name
            )
        elif args.simulation_action == 'update-testbench':
            # 更新testbench
            manager.update_testbench(
                name=args.name,
                config_file=args.config_file,
                description=args.description
            )
        elif args.simulation_action == 'list-testbench':
            # 列出所有testbench
            manager.list_testbenches()
        else:
            # 默认进入交互式模式
            interactive_manager = SimulationManager()
            interactive_manager.work_dir = "./.sim_work"
            interactive_manager.interactive_mode()
            return True
            
    except KeyboardInterrupt:
        print("\nUser interrupted operation")
        sys.exit(1)
    except Exception as e:
        print("Program execution failed: {}".format(e))
        sys.exit(1)


class SimulationManager:
    """仿真管理器"""
    
    def __init__(self):
        """
        初始化仿真管理器
        """
        self.work_dir = "./.sim_work"
        self.config = None
        self.executor = None
    
    def load_simulation_configuration(self, config_file: str):
        """
        Load simulation configuration file
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            加载的配置对象
        """
        try:
            print("Loading configuration file: {}".format(config_file))
            reader = config.ConfigReader(config_file)
            self.config = reader.load_task_config(config_file)
            print("Configuration file loaded successfully!")
            
            self._print_config_summary()
        except Exception as e:
            print("Configuration file loading failed: {}".format(e))
            raise
    
    def _generate_netlist_script(self, work_dir: Optional[str] = None):
        """Generate Ocean script for netlist creation"""
        if not self.config:
            return
            
        try:
            print("Generating netlist creation script...")
            
            # Use provided work_dir or default
            work_path = Path(work_dir) if work_dir else Path(self.work_dir)
            work_path.mkdir(parents=True, exist_ok=True)
            
            # Generate netlist script directly in work_dir
            generator = OceanScriptGenerator(self.config)
            script_path = generator.save_netlist_script(str(work_path / "create_netlist.ocn"))
            
            print("Netlist creation script generated: {}".format(script_path))
            print("Execute this script in Ocean to generate the netlist file:")
            print("  ocean < {}".format(script_path))
            
        except Exception as e:
            print("Warning: Failed to generate netlist script: {}".format(e))
    
    def _generate_netlist_shell_script(self, work_dir: Optional[str] = None):
        """Generate shell script to run the netlist creation script"""
        if not self.config:
            print("Please load configuration file first")
            return
            
        try:
            print("Generating netlist shell script...")
            
            # Use provided work_dir or default
            work_path = Path(work_dir) if work_dir else Path(self.work_dir)
            work_path.mkdir(parents=True, exist_ok=True)
            
            # Generate shell script using ShellScriptGenerator
            shell_generator = ShellScriptGenerator(self.config)
            script_path = shell_generator.generate_netlist_script(output_dir=str(work_path))
            
            print("Netlist shell script generated: {}".format(script_path))
            print("Execute this script to run the netlist creation:")
            print("  bash {}".format(script_path))
            
        except Exception as e:
            print("Warning: Failed to generate netlist shell script: {}".format(e))
    
    def _print_config_summary(self):
        """打印配置摘要"""
        if not self.config:
            return
        
        print("\n" + "="*50)
        print("Simulation Configuration Summary")
        print("="*50)
        print("Project name: {}".format(self.config.project_name))
        print("Simulator: {}".format(self.config.simulator))
        print("Design path: {}".format(self.config.design_path))
        print("Results directory: {}".format(self.config.results_dir))
        print("Simulation temperature: {}°C".format(self.config.temperature))
        
        if self.config.analyses:
            print("Analysis types: {}".format(', '.join(self.config.analyses.keys())))
        
        if self.config.model_files:
            print("Number of model files: {}".format(len(self.config.model_files)))
        
        if self.config.save_nodes:
            print("Number of saved nodes: {}".format(len(self.config.save_nodes)))
        
        if self.config.design_variables:
            print("Number of design variables: {}".format(len(self.config.design_variables)))
        
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
        
        print("Generating complete Ocean simulation package...")
        
        # 使用Shell生成器一步式生成所有脚本
        shell_generator = ShellScriptGenerator(self.config)
        script_paths = shell_generator.generate_complete_simulation_package(
            script_type="ocean",
            output_dir=output_dir
        )
        
        print("Simulation script generated: {}".format(script_paths['simulation_script']))
        print("Executable shell script generated: {}".format(script_paths['shell_script']))
        print("\nTo run the simulation, execute:")
        print("  bash {}".format(script_paths['shell_script']))
        
        return script_paths

    
    def run_simulation_package(self, timeout: int = 3600, work_dir: Optional[str] = None) -> bool:
        """
        生成并运行完整的仿真包
        
        Args:
            timeout: 超时时间（秒）
            work_dir: 工作目录
            
        Returns:
            仿真是否成功
        """
        if not self.config:
            raise ValueError("Please load configuration file first")
        
        # Use provided work_dir or default
        actual_work_dir = work_dir or self.work_dir
        
        try:
            # 第一步：生成完整的仿真包
            print("Step 1: Generating Ocean simulation package...")
            script_paths = self.generate_complete_scripts()
            
            # 第二步：执行shell脚本
            print("\nStep 2: Executing shell script...")
            shell_script_path = script_paths['shell_script']
            
            # 使用subprocess直接执行shell脚本
            cwd = Path(shell_script_path).parent
            print("Working directory: {}".format(cwd))
            print("Executing: bash {}".format(shell_script_path))
            
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
            print("\nSimulation timeout after {} seconds".format(timeout))
            return False
        except Exception as e:
            print("\nError running simulation package: {}".format(e))
            return False


    def run_simulation(self, timeout: int = 3600, work_dir: Optional[str] = None) -> bool:
        """
        运行仿真
        
        Args:
            timeout: 超时时间（秒）
            work_dir: 工作目录
            
        Returns:
            仿真是否成功
        """
        if not self.config:
            raise ValueError("Please load configuration file first")
        
        print("\nStarting Ocean simulation...")
        print("Timeout setting: {} seconds".format(timeout))
        
        # Use provided work_dir or default
        actual_work_dir = work_dir or self.work_dir
        
        # 创建执行器
        self.executor = SimulationExecutor(self.config, actual_work_dir)
        
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
            print("Error running simulation: {}".format(e))
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
        print("Status: {}".format(status['status']))
        
        if status['duration']:
            print("Duration: {}".format(status['duration']))
        
        print("Results directory: {}".format(status['results_dir']))
        
        if results['files']:
            print("Generated files count: {}".format(len(results['files'])))
        
        if results['plots']:
            print("Generated plots count: {}".format(len(results['plots'])))
        
        if results['data']:
            print("Data files count: {}".format(len(results['data'])))
        
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
                    self.load_simulation_configuration(config_file)
                
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
                print("Operation failed: {}".format(e))
            
            input("\nPress Enter to continue...")
    
    def list_simulation_tasks(self, project_name: Optional[str] = None, 
                             library_name: Optional[str] = None, 
                             cell_name: Optional[str] = None):
        """
        查询所有仿真任务运行状态（伪代码接口）
        
        Args:
            project_name: 项目名（可选）
            library_name: 库名（可选）
            cell_name: 单元名（可选）
        """
        print("Listing simulation tasks...")
        print("Filters - Project: {}, Library: {}, Cell: {}".format(
            project_name or "All", 
            library_name or "All", 
            cell_name or "All"
        ))
        
        # TODO: 实现查询仿真任务状态的逻辑
        # 这里应该连接到后台服务查询仿真任务状态
        # 返回格式化后的任务列表
        print("Simulation task list:")
        print("  Task ID    | Status     | Project    | Library    | Cell")
        print("  -----------|------------|------------|------------|------------")
        print("  task-001   | Running    | ProjectA   | Lib1       | Cell1")
        print("  task-002   | Completed  | ProjectB   | Lib2       | Cell2")
        print("  task-003   | Failed     | ProjectC   | Lib3       | Cell3")
        
        print("\nNote: This is a placeholder implementation. Actual implementation should connect to backend service.")

    def run_simulation_task(self, config_file: str):
        """
        运行仿真任务（伪代码接口）
        
        Args:
            config_file: 仿真配置文件路径
        """
        print("Running simulation task...")
        print("Config file: {}".format(config_file))
        
        try:
            # 加载任务配置文件
            reader = config.ConfigReader(config_file)
            sim_config = reader.load_task_config(config_file)
            
            # TODO: 实现运行仿真的逻辑
            # 1. 生成仿真脚本
            # 2. 执行仿真
            # 3. 监控仿真状态
            print("\nSimulation started successfully!")
            print("Task ID: task-{}".format(hash(config_file) % 10000))
            print("\nNote: This is a placeholder implementation. Actual implementation should execute the simulation.")
        except Exception as e:
            print("Failed to run simulation task: {}".format(e))
            sys.exit(1)

    def create_testbench(self, name: str, config_file: str, description: Optional[str] = None):
        """
        创建testbench（伪代码接口）
        
        Args:
            name: Testbench名称
            config_file: 配置文件路径
            description: Testbench描述（可选）
        """
        print("Creating testbench...")
        print("Name: {}".format(name))
        print("Config file: {}".format(config_file))
        if description:
            print("Description: {}".format(description))
        
        # TODO: 实现创建testbench的逻辑
        # 1. 验证配置文件
        # 2. 创建testbench记录
        # 3. 保存配置
        print("\nTestbench created successfully!")
        print("\nNote: This is a placeholder implementation. Actual implementation should create a testbench record.")

    def delete_testbench(self, name: str):
        """
        删除testbench（伪代码接口）
        
        Args:
            name: Testbench名称
        """
        print("Deleting testbench...")
        print("Name: {}".format(name))
        
        # TODO: 实现删除testbench的逻辑
        # 1. 查找testbench记录
        # 2. 删除相关文件
        # 3. 更新数据库记录
        print("\nTestbench deleted successfully!")
        print("\nNote: This is a placeholder implementation. Actual implementation should delete a testbench record.")

    def update_testbench(self, name: str, config_file: Optional[str] = None, description: Optional[str] = None):
        """
        更新testbench（伪代码接口）
        
        Args:
            name: Testbench名称
            config_file: 新的配置文件路径（可选）
            description: 新的Testbench描述（可选）
        """
        print("Updating testbench...")
        print("Name: {}".format(name))
        if config_file:
            print("New config file: {}".format(config_file))
        if description:
            print("New description: {}".format(description))
        
        # TODO: 实现更新testbench的逻辑
        # 1. 查找testbench记录
        # 2. 更新配置文件
        # 3. 更新描述信息
        print("\nTestbench updated successfully!")
        print("\nNote: This is a placeholder implementation. Actual implementation should update a testbench record.")

    def list_testbenches(self):
        """
        列出所有testbench（伪代码接口）
        """
        print("Listing all testbenches...")
        
        # TODO: 实现列出testbench的逻辑
        # 1. 查询所有testbench记录
        # 2. 格式化输出
        print("Testbench list:")
        print("  Name       | Description")
        print("  -----------|------------")
        print("  tb1        | Testbench 1")
        print("  tb2        | Testbench 2")
        
        print("\nNote: This is a placeholder implementation. Actual implementation should list all testbench records.")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Analog Chip Simulation Automation Demo",
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # 添加仿真命令
    register_simulation_commands(subparsers)
    
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助信息
    if args.command is None:
        parser.print_help()
        return
    
    # 处理仿真命令
    if args.command == 'simulation':
        handle_simulation_command(args)


if __name__ == "__main__":
    main()