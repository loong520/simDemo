#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell脚本生成器模块
生成包含环境变量设置和EDA工具调用的shell脚本
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template
from config import SimulationConfig
from ocean_generator import OceanScriptGenerator


class ShellScriptGenerator:
    """基于模板的Shell脚本生成器"""
    
    def __init__(self, config: SimulationConfig):
        """
        初始化Shell脚本生成器
        
        Args:
            config: 仿真配置对象
        """
        self.config = config
        self.templates_dir = Path(__file__).parent / "templates" / "shell"
        
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def _load_template(self, template_name: str) -> Template:
        """
        加载模板文件
        
        Args:
            template_name: 模板文件名称
            
        Returns:
            Jinja2模板对象
        """
        try:
            return self.env.get_template(template_name)
        except Exception as e:
            raise FileNotFoundError(f"Template file not found: {template_name}, error: {e}")
        
    def generate_shell_script(self, 
                             script_type: str = "ocean",
                             target_script_path: Optional[str] = None,
                             output_dir: Optional[str] = None) -> str:
        """
        生成shell脚本
        
        Args:
            script_type: 脚本类型 ("ocean")
            target_script_path: 目标脚本路径（ocean脚本）
            output_dir: 输出目录
            
        Returns:
            生成的shell脚本路径
        """
        if not self.config.eda_tools:
            raise ValueError("No EDA tools configuration found")
        
        # 获取当前仿真器的工具配置
        tool_config = self.config.eda_tools.get_tool_config(self.config.simulator)
        if not tool_config:
            raise ValueError(f"No configuration found for simulator: {self.config.simulator}")
        
        # 准备输出路径
        if not output_dir:
            output_dir = "./scripts"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        shell_script_name = f"run_{self.config.project_name}_{script_type}.sh"
        shell_script_path = output_path / shell_script_name
        
        # 准备模板变量
        template_vars = self._prepare_template_variables(
            script_type, target_script_path, tool_config
        )
        
        # 加载并渲染模板
        template = self._load_template('main_script.sh')
        script_content = template.render(**template_vars)
        
        # 写入文件
        with open(shell_script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(shell_script_path, 0o755)
        
        return str(shell_script_path.absolute())
    def generate_netlist_script(self, output_dir: Optional[str] = None) -> str:
        """
        生成网表创建脚本
        
        Args:
            output_dir: 输出目录
            
        Returns:
            生成的网表脚本路径
        """
        if not self.config.eda_tools:
            raise ValueError("No EDA tools configuration found")
        
        # 获取当前仿真器的工具配置
        tool_config = self.config.eda_tools.get_tool_config(self.config.simulator)
        if not tool_config:
            raise ValueError(f"No configuration found for simulator: {self.config.simulator}")
        
        # 准备输出路径
        if not output_dir:
            output_dir = "./scripts"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        netlist_script_name = f"run_{self.config.project_name}_netlist.sh"
        netlist_script_path = output_path / netlist_script_name
        
        # 网表脚本路径
        netlist_ocn_path = f"{self.config.project_name}_netlist.ocn"
        
        # 准备模板变量
        template_vars = self._prepare_netlist_template_variables(tool_config, netlist_ocn_path)
        
        # 加载并渲染模板
        template = self._load_template('netlist_script.sh')
        script_content = template.render(**template_vars)
        
        # 写入文件
        with open(netlist_script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(netlist_script_path, 0o755)
        
        return str(netlist_script_path.absolute())
    
    def _prepare_netlist_template_variables(self, tool_config, netlist_script_path: str) -> Dict:
        """
        准备网表脚本模板变量
        
        Args:
            tool_config: 工具配置对象
            netlist_script_path: 网表脚本路径
            
        Returns:
            模板变量字典
        """
        # 获取source命令和export命令
        source_commands = tool_config.get_source_commands()
        export_commands = tool_config.get_export_commands()
        
        # 准备Ocean命令
        if self.config.simulator == 'spectre':
            ocean_cmd = "ocean"
        elif self.config.simulator == 'virtuoso':
            ocean_cmd = "ocean"  # Virtuoso也使用ocean命令
        else:
            ocean_cmd = self.config.simulator  # 使用仿真器名称作为默认命令
        
        launch_args = ' '.join(tool_config.launch_args) if tool_config.launch_args else ""
        
        return {
            'project_name': self.config.project_name,
            'simulator': self.config.simulator,
            'netlist_script_path': netlist_script_path,
            'design_path_dir': str(Path(self.config.design_path).parent) if self.config.design_path else ".",
            'source_commands': source_commands,
            'export_commands': export_commands,
            'ocean_cmd': ocean_cmd,
            'launch_args': launch_args
        }
    
    def generate_complete_simulation_package(self, 
                                           script_type: str = "ocean",
                                           output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        生成完整的仿真包（仿真脚本 + shell脚本）
        
        Args:
            script_type: 脚本类型 ("ocean" 或 "python")
            output_dir: 输出目录
            
        Returns:
            生成的所有脚本路径字典
        """
        if not self.config.eda_tools:
            raise ValueError("No EDA tools configuration found")
        
        # 准备输出目录
        if not output_dir:
            output_dir = "./scripts"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        result_paths = {}
        
        # 第一步：生成仿真脚本
        generator = OceanScriptGenerator(self.config)
        
        if script_type == "ocean":
            # 生成Ocean脚本
            ocean_script_path = output_path / f"{self.config.project_name}.ocn"
            ocean_path = generator.save_script(str(ocean_script_path))
            result_paths['simulation_script'] = ocean_path
            target_script_name = f"{self.config.project_name}.ocn"
        else:
            raise ValueError(f"Unsupported script type: {script_type}")
        
        # 第二步：生成Shell脚本（调用上面生成的仿真脚本）
        shell_script_path = self.generate_shell_script(
            script_type=script_type,
            target_script_path=target_script_name,
            output_dir=output_dir
        )
        result_paths['shell_script'] = shell_script_path
        
        return result_paths
    
    def generate_batch_script(self, output_dir: Optional[str] = None) -> str:
        """
        生成批量执行脚本
        
        Args:
            output_dir: 输出目录
            
        Returns:
            生成的批量脚本路径
        """
        if not output_dir:
            output_dir = "./scripts"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        batch_script_name = f"run_{self.config.project_name}_batch.sh"
        batch_script_path = output_path / batch_script_name
        
        # 准备模板变量
        template_vars = {
            'project_name': self.config.project_name
        }
        
        # 加载并渲染模板
        template = self._load_template('batch_script.sh')
        script_content = template.render(**template_vars)
        
        # 写入文件
        with open(batch_script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 设置执行权限
        os.chmod(batch_script_path, 0o755)
        
        return str(batch_script_path.absolute())
