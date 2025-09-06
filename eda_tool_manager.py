#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDA工具管理客户端
用于调用后台Java服务的REST API接口管理EDA工具
"""

import requests
import json
from typing import Dict, List, Optional
import argparse
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

import config
from service_request import ServiceRequest


class EDAToolManager(ServiceRequest):
    """EDA工具管理器"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化EDA工具管理器
        
        Args:
            base_url: 后台服务的基础URL
            api_key: API密钥（如果需要认证）
        """
        super().__init__(base_url, api_key)
    
    def create_tool(self, name: str, version: str, launch_command: str, vendor: str, environment_variables: List[str]) -> Dict:
        """
        创建EDA工具
        
        Args:
            name: 工具名称
            version: 工具版本
            launch_command: 启动命令
            vendor: 工具供应商
            environment_variables: 环境变量列表
            
        Returns:
            创建的工具信息
        """
        data = {
            "name": name,
            "version": version,
            "launchCommand": launch_command,
            "vendor": vendor,
            "environmentVariables": environment_variables
        }
        
        return self._make_request('POST', '/api/eda-tools', data)
    
    def get_tool(self, tool_id: str) -> Dict:
        """
        查询EDA工具信息
        
        Args:
            tool_id: 工具ID
            
        Returns:
            工具信息
        """
        return self._make_request('GET', f'/api/eda-tools/{tool_id}')
    
    def list_tools(self) -> List[Dict]:
        """
        列出所有EDA工具
        
        Returns:
            工具列表
        """
        result = self._make_request('GET', '/api/eda-tools')
        return result.get('tools', [])
    
    def delete_tool(self, tool_id: str) -> Dict:
        """
        删除EDA工具
        
        Args:
            tool_id: 工具ID
            
        Returns:
            删除结果
        """
        return self._make_request('DELETE', f'/api/eda-tools/{tool_id}')
    
    def update_tool(self, tool_id: str, name: Optional[str] = None, version: Optional[str] = None, 
                   launch_command: Optional[str] = None, vendor: Optional[str] = None, 
                   environment_variables: Optional[List[str]] = None) -> Dict:
        """
        更新EDA工具信息
        
        Args:
            tool_id: 工具ID
            name: 工具名称（可选）
            version: 工具版本（可选）
            launch_command: 启动命令（可选）
            vendor: 工具供应商（可选）
            environment_variables: 环境变量列表（可选）
            
        Returns:
            更新后的工具信息
        """
        data = {}
        if name is not None:
            data["name"] = name
        if version is not None:
            data["version"] = version
        if launch_command is not None:
            data["launchCommand"] = launch_command
        if vendor is not None:
            data["vendor"] = vendor
        if environment_variables is not None:
            data["environmentVariables"] = environment_variables
        
        return self._make_request('PUT', f'/api/eda-tools/{tool_id}', data)


def register_eda_tool_commands(subparsers):
    """添加EDA工具管理命令"""
    # EDA工具管理父命令
    eda_tool_parser = subparsers.add_parser('eda-tool', help='EDA Tool management')
    
    # 创建EDA工具管理子命令的子解析器
    eda_tool_subparsers = eda_tool_parser.add_subparsers(dest='eda_tool_action', help='EDA Tool management actions')
    
    # EDA工具创建命令
    create_parser = eda_tool_subparsers.add_parser('create', help='Create a new EDA tool')
    create_parser.add_argument('--name', required=True, help='Tool name')
    create_parser.add_argument('--version', required=True, help='Tool version')
    create_parser.add_argument('--launch-command', required=True, help='Tool launch command')
    create_parser.add_argument('--vendor', required=True, help='Tool vendor')
    create_parser.add_argument('--env-var', action='append', help='Environment variables (can be specified multiple times)')
    
    # EDA工具查询命令
    get_parser = eda_tool_subparsers.add_parser('get', help='Get EDA tool information')
    get_parser.add_argument('--tool-id', required=True, help='Tool ID')
    
    # EDA工具列表命令
    list_parser = eda_tool_subparsers.add_parser('list', help='List all EDA tools')
    
    # EDA工具删除命令
    delete_parser = eda_tool_subparsers.add_parser('delete', help='Delete an EDA tool')
    delete_parser.add_argument('--tool-id', required=True, help='Tool ID')
    
    # EDA工具更新命令
    update_parser = eda_tool_subparsers.add_parser('update', help='Update an EDA tool')
    update_parser.add_argument('--tool-id', required=True, help='Tool ID')
    update_parser.add_argument('--name', help='Tool name')
    update_parser.add_argument('--version', help='Tool version')
    update_parser.add_argument('--launch-command', help='Tool launch command')
    update_parser.add_argument('--vendor', help='Tool vendor')
    update_parser.add_argument('--env-var', action='append', help='Environment variables (can be specified multiple times)')


def handle_eda_tool_command(args):
    """处理EDA工具管理命令"""
    # 默认配置文件路径
    config_file = "simulation_config.yaml"
    
    try:
        # 检查配置文件是否存在
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"Error: Configuration file not found: {config_file}")
            sys.exit(1)
        
        # 从配置文件读取服务器配置
        config_obj = config.load_task_config(str(config_path))
        server_url = config_obj.server.url
        api_key = config_obj.server.api_key
        
        if not server_url:
            print("Error: Server URL not configured in config file")
            sys.exit(1)
        
        manager = EDAToolManager(server_url, api_key)
        print("Executing EDA tool management action: {}".format(args.eda_tool_action))
        
        # 根据不同的操作调用相应的函数
        if args.eda_tool_action == 'create':
            env_vars = args.env_var or []
            result = manager.create_tool(
                name=args.name,
                version=args.version,
                launch_command=args.launch_command,
                vendor=args.vendor,
                environment_variables=env_vars
            )
            print("Tool created successfully: {}".format(result))
        elif args.eda_tool_action == 'get':
            result = manager.get_tool(tool_id=args.tool_id)
            print("Tool information: {}".format(result))
        elif args.eda_tool_action == 'list':
            result = manager.list_tools()
            print("Tools list: {}".format(result))
        elif args.eda_tool_action == 'delete':
            result = manager.delete_tool(tool_id=args.tool_id)
            print("Tool deleted successfully: {}".format(result))
        elif args.eda_tool_action == 'update':
            env_vars = args.env_var or [] if args.env_var is not None else None
            result = manager.update_tool(
                tool_id=args.tool_id,
                name=args.name if args.name is not None else None,
                version=args.version if args.version is not None else None,
                launch_command=args.launch_command if args.launch_command is not None else None,
                vendor=args.vendor if args.vendor is not None else None,
                environment_variables=env_vars
            )
            print("Tool updated successfully: {}".format(result))
        
        return
    except Exception as e:
        print("EDA tool management failed: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    # 测试代码
    pass