#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDK管理客户端
用于调用后台Java服务的REST API接口管理PDK
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


class PDKManager(ServiceRequest):
    """PDK管理器"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化PDK管理器
        
        Args:
            base_url: 后台服务的基础URL
            api_key: API密钥（如果需要认证）
        """
        super().__init__(base_url, api_key)
    
    def create_pdk(self, name: str, version: str, process: str, vendor: str, root_path: str,
                   drc_path: str, lvs_path: str, xrc_path: str, 
                   spectre_path: str, hspice_path: str) -> Dict:
        """
        创建PDK
        
        Args:
            name: PDK名称
            version: PDK版本
            process: 工艺
            vendor: 供应商
            root_path: 根目录
            drc_path: DRC模型文件目录
            lvs_path: LVS模型文件目录
            xrc_path: XRC模型文件目录
            spectre_path: Spectre模型文件目录
            hspice_path: HSPICE模型文件目录
            
        Returns:
            创建的PDK信息
        """
        data = {
            "name": name,
            "version": version,
            "process": process,
            "vendor": vendor,
            "rootPath": root_path,
            "drcPath": drc_path,
            "lvsPath": lvs_path,
            "xrcPath": xrc_path,
            "spectrePath": spectre_path,
            "hspicePath": hspice_path
        }
        
        return self._make_request('POST', '/api/pdks', data)
    
    def get_pdk(self, pdk_id: str) -> Dict:
        """
        查询PDK信息
        
        Args:
            pdk_id: PDK ID
            
        Returns:
            PDK信息
        """
        return self._make_request('GET', f'/api/pdks/{pdk_id}')
    
    def list_pdks(self) -> List[Dict]:
        """
        列出所有PDK
        
        Returns:
            PDK列表
        """
        result = self._make_request('GET', '/api/pdks')
        return result.get('pdks', [])
    
    def delete_pdk(self, pdk_id: str) -> Dict:
        """
        删除PDK
        
        Args:
            pdk_id: PDK ID
            
        Returns:
            删除结果
        """
        return self._make_request('DELETE', f'/api/pdks/{pdk_id}')
    
    def update_pdk(self, pdk_id: str, name: Optional[str] = None, version: Optional[str] = None,
                   process: Optional[str] = None, vendor: Optional[str] = None, 
                   root_path: Optional[str] = None, drc_path: Optional[str] = None,
                   lvs_path: Optional[str] = None, xrc_path: Optional[str] = None,
                   spectre_path: Optional[str] = None, hspice_path: Optional[str] = None) -> Dict:
        """
        更新PDK信息
        
        Args:
            pdk_id: PDK ID
            name: PDK名称（可选）
            version: PDK版本（可选）
            process: 工艺（可选）
            vendor: 供应商（可选）
            root_path: 根目录（可选）
            drc_path: DRC模型文件目录（可选）
            lvs_path: LVS模型文件目录（可选）
            xrc_path: XRC模型文件目录（可选）
            spectre_path: Spectre模型文件目录（可选）
            hspice_path: HSPICE模型文件目录（可选）
            
        Returns:
            更新后的PDK信息
        """
        data = {}
        if name is not None:
            data["name"] = name
        if version is not None:
            data["version"] = version
        if process is not None:
            data["process"] = process
        if vendor is not None:
            data["vendor"] = vendor
        if root_path is not None:
            data["rootPath"] = root_path
        if drc_path is not None:
            data["drcPath"] = drc_path
        if lvs_path is not None:
            data["lvsPath"] = lvs_path
        if xrc_path is not None:
            data["xrcPath"] = xrc_path
        if spectre_path is not None:
            data["spectrePath"] = spectre_path
        if hspice_path is not None:
            data["hspicePath"] = hspice_path
        
        return self._make_request('PUT', f'/api/pdks/{pdk_id}', data)


def register_pdk_commands(subparsers):
    """添加PDK管理命令"""
    # PDK管理父命令
    pdk_parser = subparsers.add_parser('pdk', help='PDK management')
    
    # 创建PDK管理子命令的子解析器
    pdk_subparsers = pdk_parser.add_subparsers(dest='pdk_action', help='PDK management actions')
    
    # PDK创建命令
    create_parser = pdk_subparsers.add_parser('create', help='Create a new PDK')
    create_parser.add_argument('--name', required=True, help='PDK name')
    create_parser.add_argument('--version', required=True, help='PDK version')
    create_parser.add_argument('--process', required=True, help='Process technology')
    create_parser.add_argument('--vendor', required=True, help='PDK vendor')
    create_parser.add_argument('--root-path', required=True, help='PDK root directory')
    create_parser.add_argument('--drc-path', required=True, help='DRC model directory')
    create_parser.add_argument('--lvs-path', required=True, help='LVS model directory')
    create_parser.add_argument('--xrc-path', required=True, help='XRC model directory')
    create_parser.add_argument('--spectre-path', required=True, help='Spectre model directory')
    create_parser.add_argument('--hspice-path', required=True, help='HSPICE model directory')
    
    # PDK查询命令
    get_parser = pdk_subparsers.add_parser('get', help='Get PDK information')
    get_parser.add_argument('--pdk-id', required=True, help='PDK ID')
    
    # PDK列表命令
    list_parser = pdk_subparsers.add_parser('list', help='List all PDKs')
    
    # PDK删除命令
    delete_parser = pdk_subparsers.add_parser('delete', help='Delete a PDK')
    delete_parser.add_argument('--pdk-id', required=True, help='PDK ID')
    
    # PDK更新命令
    update_parser = pdk_subparsers.add_parser('update', help='Update a PDK')
    update_parser.add_argument('--pdk-id', required=True, help='PDK ID')
    update_parser.add_argument('--name', help='PDK name')
    update_parser.add_argument('--version', help='PDK version')
    update_parser.add_argument('--process', help='Process technology')
    update_parser.add_argument('--vendor', help='PDK vendor')
    update_parser.add_argument('--root-path', help='PDK root directory')
    update_parser.add_argument('--drc-path', help='DRC model directory')
    update_parser.add_argument('--lvs-path', help='LVS model directory')
    update_parser.add_argument('--xrc-path', help='XRC model directory')
    update_parser.add_argument('--spectre-path', help='Spectre model directory')
    update_parser.add_argument('--hspice-path', help='HSPICE model directory')


def handle_pdk_command(args):
    """处理PDK管理命令"""
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
        
        manager = PDKManager(server_url, api_key)
        print("Executing PDK management action: {}".format(args.pdk_action))
        
        # 根据不同的操作调用相应的函数
        if args.pdk_action == 'create':
            result = manager.create_pdk(
                name=args.name,
                version=args.version,
                process=args.process,
                vendor=args.vendor,
                root_path=args.root_path,
                drc_path=args.drc_path,
                lvs_path=args.lvs_path,
                xrc_path=args.xrc_path,
                spectre_path=args.spectre_path,
                hspice_path=args.hspice_path
            )
            print("PDK created successfully: {}".format(result))
        elif args.pdk_action == 'get':
            result = manager.get_pdk(pdk_id=args.pdk_id)
            print("PDK information: {}".format(result))
        elif args.pdk_action == 'list':
            result = manager.list_pdks()
            print("PDKs list: {}".format(result))
        elif args.pdk_action == 'delete':
            result = manager.delete_pdk(pdk_id=args.pdk_id)
            print("PDK deleted successfully: {}".format(result))
        elif args.pdk_action == 'update':
            result = manager.update_pdk(
                pdk_id=args.pdk_id,
                name=args.name if args.name is not None else None,
                version=args.version if args.version is not None else None,
                process=args.process if args.process is not None else None,
                vendor=args.vendor if args.vendor is not None else None,
                root_path=args.root_path if args.root_path is not None else None,
                drc_path=args.drc_path if args.drc_path is not None else None,
                lvs_path=args.lvs_path if args.lvs_path is not None else None,
                xrc_path=args.xrc_path if args.xrc_path is not None else None,
                spectre_path=args.spectre_path if args.spectre_path is not None else None,
                hspice_path=args.hspice_path if args.hspice_path is not None else None
            )
            print("PDK updated successfully: {}".format(result))
        
        return
    except Exception as e:
        print("PDK management failed: {}".format(e))
        sys.exit(1)


if __name__ == "__main__":
    # 测试代码
    pass