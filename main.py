#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片仿真自动化Demo - 主程序
提供命令行接口和图形界面来运行仿真
"""

import argparse
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

import config
import simulation_manager
import project_manager
import eda_tool_manager
import pdk_manager
from simulation_manager import SimulationManager


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Analog Chip Simulation Automation Demo",
    )
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # EDA工具管理命令
    eda_tool_manager.add_eda_tool_commands(subparsers)
    
    # PDK管理命令
    pdk_manager.add_pdk_commands(subparsers)
    
    # 项目管理命令
    project_manager.add_project_commands(subparsers)
    
    # 仿真命令
    simulation_manager.add_simulation_arguments(subparsers)
    
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助信息
    if args.command is None:
        parser.print_help()
        return
    
    # 处理EDA工具管理命令
    if args.command == 'eda-tool':
        eda_tool_manager.handle_eda_tool_command(args)
    
    # 处理PDK管理命令
    elif args.command == 'pdk':
        pdk_manager.handle_pdk_command(args)
    
    # 处理项目管理命令
    elif args.command == 'project':
        project_manager.handle_project_command(args)
    
    # 处理仿真命令
    elif args.command == 'simulation':
        simulation_manager.handle_simulation_command(args)


if __name__ == "__main__":
    main()