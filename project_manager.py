#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目管理客户端
用于调用后台Java服务的REST API接口
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


class ProjectManager(ServiceRequest):
    """项目管理器"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化项目管理器
        
        Args:
            base_url: 后台服务的基础URL
            api_key: API密钥（如果需要认证）
        """
        super().__init__(base_url, api_key)
    
    def create_project(self, name: str, description: str = "", owner: str = "") -> Dict:
        """
        创建项目
        
        Args:
            name: 项目名称
            description: 项目描述
            owner: 项目所有者（可选，默认为当前用户）
            
        Returns:
            创建的项目信息
        """
        data = {
            "name": name,
            "description": description
        }
        
        # 如果提供了owner，则添加到请求数据中
        if owner:
            data["owner"] = owner
        
        return self._make_request('POST', '/api/projects', data)
    
    def configure_project_members(self, project_id: str, members: List[Dict]) -> Dict:
        """
        配置项目成员角色
        
        Args:
            project_id: 项目ID
            members: 成员列表，每个成员包含userId和role
            
        Returns:
            配置结果
        """
        data = {
            "members": members
        }
        
        return self._make_request('PUT', f'/api/projects/{project_id}/members', data)
    
    def configure_project_directory(self, project_id: str, directory_path: str) -> Dict:
        """
        配置项目所在目录
        
        Args:
            project_id: 项目ID
            directory_path: 项目目录路径
            
        Returns:
            配置结果
        """
        data = {
            "directoryPath": directory_path
        }
        
        return self._make_request('PUT', f'/api/projects/{project_id}/directory', data)
    
    def configure_pdk_directory(self, project_id: str, pdk_path: str) -> Dict:
        """
        配置项目使用的PDK目录
        
        Args:
            project_id: 项目ID
            pdk_path: PDK目录路径
            
        Returns:
            配置结果
        """
        data = {
            "pdkPath": pdk_path
        }
        
        return self._make_request('PUT', f'/api/projects/{project_id}/pdk', data)
    
    def configure_libraries(self, project_id: str, libraries: List[Dict]) -> Dict:
        """
        配置项目中的库和单元
        
        Args:
            project_id: 项目ID
            libraries: 库列表，每个库包含name和cells
            
        Returns:
            配置结果
        """
        data = {
            "libraries": libraries
        }
        
        return self._make_request('PUT', f'/api/projects/{project_id}/libraries', data)
    
    def configure_eda_tools(self, project_id: str, eda_config: Dict) -> Dict:
        """
        配置项目各阶段的EDA工具
        
        Args:
            project_id: 项目ID
            eda_config: EDA工具配置，包含各个阶段的工具配置
            
        Returns:
            配置结果
        """
        return self._make_request('PUT', f'/api/projects/{project_id}/eda-tools', eda_config)
    
    def get_project(self, project_id: str) -> Dict:
        """
        获取项目信息
        
        Args:
            project_id: 项目ID
            
        Returns:
            项目信息
        """
        return self._make_request('GET', f'/api/projects/{project_id}')
    
    def list_projects(self) -> List[Dict]:
        """
        列出所有项目
        
        Returns:
            项目列表
        """
        result = self._make_request('GET', '/api/projects')
        return result.get('projects', [])
    
    def delete_project(self, project_id: str) -> Dict:
        """
        删除项目
        
        Args:
            project_id: 项目ID
        """
        return self._make_request('DELETE', f'/api/projects/{project_id}')


def register_project_commands(subparsers):
    """添加项目管理命令"""
    # 项目管理父命令
    project_parser = subparsers.add_parser('project', help='Project management')
    
    # 创建项目管理子命令的子解析器
    project_subparsers = project_parser.add_subparsers(dest='project_action', help='Project management actions')
    
    # 项目创建命令
    create_parser = project_subparsers.add_parser('create', help='Create a new project')
    create_parser.add_argument('--name', required=True, help='Project name')
    create_parser.add_argument('--description', help='Project description')
    
    # 项目成员配置命令
    members_parser = project_subparsers.add_parser('members', help='Configure project members')
    members_parser.add_argument('--project-id', required=True, help='Project ID')
    members_parser.add_argument('--members', required=True, help='Members configuration (JSON format)')
    
    # 项目目录配置命令
    directory_parser = project_subparsers.add_parser('directory', help='Configure project directory')
    directory_parser.add_argument('--project-id', required=True, help='Project ID')
    directory_parser.add_argument('--path', required=True, help='Project directory path')
    
    # 项目PDK目录配置命令
    pdk_parser = project_subparsers.add_parser('pdk', help='Configure PDK directory')
    pdk_parser.add_argument('--project-id', required=True, help='Project ID')
    pdk_parser.add_argument('--path', required=True, help='PDK directory path')
    
    # 项目库和单元配置命令
    libraries_parser = project_subparsers.add_parser('libraries', help='Configure libraries and cells')
    libraries_parser.add_argument('--project-id', required=True, help='Project ID')
    libraries_parser.add_argument('--libraries', required=True, help='Libraries configuration (JSON format)')
    
    # 项目EDA工具配置命令
    eda_parser = project_subparsers.add_parser('eda', help='Configure EDA tools')
    eda_parser.add_argument('--project-id', required=True, help='Project ID')
    eda_parser.add_argument('--config', required=True, help='EDA tools configuration (JSON format)')
    
    # 查询项目信息命令
    get_parser = project_subparsers.add_parser('get', help='Get project information')
    get_parser.add_argument('--project-id', required=True, help='Project ID')
    
    # 列出所有项目命令
    list_parser = project_subparsers.add_parser('list', help='List all projects')
    
    # 删除项目命令
    delete_parser = project_subparsers.add_parser('delete', help='Delete a project')
    delete_parser.add_argument('--project-id', required=True, help='Project ID')


def handle_project_command(args):
    """处理项目管理命令"""
    try:
        # 从系统配置文件读取服务器配置
        reader = config.ConfigReader()
        config_obj = reader.load_system_config()
        server_url = config_obj.server.url
        api_key = config_obj.server.api_key
        
        if not server_url:
            print("Error: Server URL not configured in system config file")
            sys.exit(1)
        
        manager = ProjectManager(server_url, api_key)
        print("Executing project management action: {}".format(args.project_action))
        
        # 根据不同的操作调用相应的函数
        if args.project_action == 'create':
            # 不再传递owner参数，让服务端自动设置创建者为owner
            result = manager.create_project(
                name=args.name,
                description=args.description or ""
            )
            print("Project created successfully: {}".format(result))
        elif args.project_action == 'members':
            members = json.loads(args.members)
            result = manager.configure_project_members(args.project_id, members)
            print("Project members configured successfully: {}".format(result))
        elif args.project_action == 'directory':
            result = manager.configure_project_directory(args.project_id, args.path)
            print("Project directory configured successfully: {}".format(result))
        elif args.project_action == 'pdk':
            result = manager.configure_pdk_directory(args.project_id, args.path)
            print("PDK directory configured successfully: {}".format(result))
        elif args.project_action == 'libraries':
            libraries = json.loads(args.libraries)
            result = manager.configure_libraries(args.project_id, libraries)
            print("Libraries configured successfully: {}".format(result))
        elif args.project_action == 'eda':
            eda_config = json.loads(args.config)
            result = manager.configure_eda_tools(args.project_id, eda_config)
            print("EDA tools configured successfully: {}".format(result))
        elif args.project_action == 'get':
            result = manager.get_project(args.project_id)
            print("Project information: {}".format(result))
        elif args.project_action == 'list':
            result = manager.list_projects()
            print("Projects list: {}".format(result))
        elif args.project_action == 'delete':
            result = manager.delete_project(args.project_id)
            print("Project deleted successfully: {}".format(result))
        
        return
    except Exception as e:
        print("Project management failed: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    # 测试代码
    pass