#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片仿真配置文件读取模块
支持YAML格式的配置文件
"""

import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EDATool:
    """EDA工具配置数据类"""
    # 启动命令配置
    executable: str = ""
    launch_args: List[str] = field(default_factory=list)
    
    # 环境变量配置（每个成员是"export VAR=value"格式）
    environment_variables: List[str] = field(default_factory=list)
    
    # 工具特定选项
    options: Dict[str, Any] = field(default_factory=dict)
    
    def get_environment_dict(self) -> Dict[str, str]:
        """
        获取完整的环境变量字典，用于设置进程环境
        注意：此方法只处理export格式的环境变量，不处理source命令
        
        Returns:
            环境变量字典
        """
        import os
        env_dict = os.environ.copy()
        
        # 解析环境变量列表，将"export VAR=value"格式转换为字典
        for env_line in self.environment_variables:
            env_line = env_line.strip()
            
            # 跳过source命令，只处理export命令
            if env_line.startswith('source '):
                continue
                
            # 移除"export "前缀（如果有）
            if env_line.startswith('export '):
                env_line = env_line[7:]  # 移除"export "
            
            # 解析VAR=value格式
            if '=' in env_line:
                var_name, var_value = env_line.split('=', 1)
                # 移除引号（如果有）
                var_value = var_value.strip('"\'')
                env_dict[var_name] = var_value
        
        return env_dict
    
    def get_source_commands(self) -> List[str]:
        """
        获取source命令列表
        
        Returns:
            source命令列表
        """
        source_commands = []
        
        for env_line in self.environment_variables:
            env_line = env_line.strip()
            if env_line.startswith('source '):
                source_commands.append(env_line)
        
        return source_commands
    
    def get_export_commands(self) -> List[str]:
        """
        获取export命令列表
        
        Returns:
            export命令列表
        """
        export_commands = []
        
        for env_line in self.environment_variables:
            env_line = env_line.strip()
            
            # 跳过source命令
            if env_line.startswith('source '):
                continue
                
            # 确保以export开头
            if not env_line.startswith('export '):
                env_line = f"export {env_line}"
                
            export_commands.append(env_line)
        
        return export_commands


@dataclass
class EDASToolsConfig:
    """EDA工具配置数据类"""
    # 各个工具的配置
    spectre: EDATool = field(default_factory=EDATool)
    virtuoso: EDATool = field(default_factory=EDATool)
    
    def get_tool_config(self, tool_name: str) -> Optional[EDATool]:
        """
        获取指定工具的配置
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具配置对象
        """
        return getattr(self, tool_name, None)


@dataclass
class SimulationConfig:
    """仿真配置数据类"""
    # 基本仿真配置
    simulator: str = "spectre"  # 仿真器类型 (spectre, virtuoso, etc.)
    project_dir: str = ""       # 项目目录路径
    library_name: str = ""      # 库名称
    cell_name: str = ""         # 单元名称
    simulation_path: str = ""   # 仿真路径
    design_type: str = "schematic"  # 设计类型 (schematic, layout, etc.)
    
    # EDA工具配置
    eda_tools: EDASToolsConfig = field(default_factory=EDASToolsConfig)
    
    # 模型文件配置
    model_files: List[List[str]] = field(default_factory=list)  # 模型文件路径和工艺角
    
    # 仿真分析配置
    analyses: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # 分析类型和参数
    
    # 激励配置
    stimulus_files: List[str] = field(default_factory=list)    # 激励文件路径
    
    # 设计变量
    design_variables: Dict[str, Any] = field(default_factory=dict)
    
    # 保存节点
    save_nodes: List[str] = field(default_factory=list)
    
    # 环境配置
    temperature: float = 27.0           # 仿真温度
    supply_voltage: float = 1.8         # 电源电压
    
    
    # 收敛配置
    initial_conditions: Dict[str, float] = field(default_factory=dict)
    
    # 后处理配置
    post_processing: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def project_name(self) -> str:
        """从project_dir自动获取项目名称"""
        if self.project_dir:
            return Path(self.project_dir).name
        return "sim_project"
    
    @property
    def design_path(self) -> str:
        """自动计算design_path"""
        if not all([self.simulation_path, self.cell_name, self.simulator, self.design_type]):
            return ""
        return f"{self.simulation_path}/{self.cell_name}/{self.simulator}/{self.design_type}/netlist/netlist"
    
    @property
    def results_dir(self) -> str:
        """自动计算results_dir"""
        if not all([self.simulation_path, self.cell_name, self.simulator, self.design_type]):
            return ""
        return f"{self.simulation_path}/{self.cell_name}/{self.simulator}/{self.design_type}"




class ConfigReader:
    """配置文件读取器"""
    
    def __init__(self, config_file: str):
        """
        初始化配置读取器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        file_ext = self.config_file.suffix.lower()
        
        if file_ext in ['.yaml', '.yml']:
            return self._load_yaml()
        else:
            raise ValueError(f"Unsupported configuration file format: {file_ext}, only YAML format is supported")
    
    def _load_yaml(self) -> Dict[str, Any]:
        """加载YAML配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML configuration file parsing error: {e}")

    
    def get_simulation_config(self) -> SimulationConfig:
        """获取仿真配置对象"""
        try:
            # 基本配置
            basic_config = self.config_data.get('simulation', {})
            
            # 创建仿真配置对象
            sim_config = SimulationConfig(
                simulator=basic_config.get('simulator', 'spectre'),
                project_dir=basic_config.get('project_dir', ''),
                library_name=basic_config.get('library_name', ''),
                cell_name=basic_config.get('cell_name', ''),
                simulation_path=basic_config.get('simulation_path', ''),
                design_type=basic_config.get('design_type', 'schematic'),
                temperature=float(basic_config.get('temperature', 27.0)),
                supply_voltage=float(basic_config.get('supply_voltage', 1.8))
            )
            
            # EDA工具配置
            if 'eda_tools' in self.config_data:
                eda_config = self.config_data['eda_tools']
                
                # 创建EDA工具配置对象
                tools_config = EDASToolsConfig()
                
                # 解析各个工具的配置
                for tool_name in ['spectre', 'virtuoso']:
                    if tool_name in eda_config:
                        tool_config_data = eda_config[tool_name]
                        tool_config = EDATool(
                            executable=tool_config_data.get('executable', ''),
                            launch_args=tool_config_data.get('launch_args', []),
                            environment_variables=tool_config_data.get('environment_variables', []),
                            options=tool_config_data.get('options', {})
                        )
                        setattr(tools_config, tool_name, tool_config)
                
                sim_config.eda_tools = tools_config
            
            # 模型文件配置
            if 'models' in self.config_data:
                model_config = self.config_data['models']
                sim_config.model_files = model_config.get('files', [])
            
            # 分析配置
            if 'analyses' in self.config_data:
                sim_config.analyses = self.config_data['analyses']
            
            # 激励文件
            if 'stimulus' in self.config_data:
                stimulus_config = self.config_data['stimulus']
                sim_config.stimulus_files = stimulus_config.get('files', [])
            
            # 设计变量
            if 'variables' in self.config_data:
                sim_config.design_variables = self.config_data['variables']
            
            # 保存节点
            if 'outputs' in self.config_data:
                output_config = self.config_data['outputs']
                sim_config.save_nodes = output_config.get('save_nodes', [])
            
            # 初始条件
            if 'initial_conditions' in self.config_data:
                sim_config.initial_conditions = self.config_data['initial_conditions']
            
            # 后处理配置
            if 'post_processing' in self.config_data:
                sim_config.post_processing = self.config_data['post_processing']
            
            return sim_config
            
        except Exception as e:
            raise ValueError(f"Configuration file parsing error: {e}")
    
    def validate_config(self, config: SimulationConfig) -> List[str]:
        """
        验证配置文件的有效性
        
        Args:
            config: 仿真配置对象
            
        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []
        
        # 检查必要的路径和配置
        if not config.project_dir:
            errors.append("Project directory (project_dir) cannot be empty")
        elif not Path(config.project_dir).exists():
            errors.append(f"Project directory does not exist: {config.project_dir}")
        
        if not config.simulation_path:
            errors.append("Simulation path (simulation_path) cannot be empty")
            
        if not config.library_name:
            errors.append("Library name (library_name) cannot be empty")
            
        if not config.cell_name:
            errors.append("Cell name (cell_name) cannot be empty")
        
        # 检查计算出的design_path
        design_path = config.design_path
        if design_path and not Path(design_path).exists():
            errors.append(f"Design file does not exist (computed path): {design_path}")
        
        # 检查模型文件
        for model_file_info in config.model_files:
            if isinstance(model_file_info, list) and len(model_file_info) >= 1:
                model_path = model_file_info[0]
                if not Path(model_path).exists():
                    errors.append(f"Model file does not exist: {model_path}")
        
        # 检查激励文件
        for stimulus_file in config.stimulus_files:
            if not Path(stimulus_file).exists():
                errors.append(f"Stimulus file does not exist: {stimulus_file}")
        
        # 检查分析配置
        if not config.analyses:
            errors.append("At least one analysis type must be configured")
        
        # 检查仿真器支持
        supported_simulators = ['spectre', 'virtuoso']
        if config.simulator not in supported_simulators:
            errors.append(f"Unsupported simulator: {config.simulator}")
        
        # 检查EDA工具配置
        if config.eda_tools:
            # 获取当前仿真器的工具配置
            tool_config = config.eda_tools.get_tool_config(config.simulator)
            if tool_config:
                # 检查可执行命令是否配置
                if not tool_config.executable:
                    errors.append(f"Executable command not configured for simulator: {config.simulator}")
                
                # 检查关键环境变量（简化检查）
                env_vars = tool_config.environment_variables
                if not env_vars:
                    errors.append(f"No environment variables configured for simulator: {config.simulator}")
            else:
                errors.append(f"No tool configuration found for simulator: {config.simulator}")
        
        return errors


def load_config(config_file: str) -> SimulationConfig:
    """
    便捷函数：加载配置文件并返回配置对象
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        仿真配置对象
    """
    reader = ConfigReader(config_file)
    config = reader.get_simulation_config()
    
    # 验证配置
    errors = reader.validate_config(config)
    if errors:
        error_msg = "Configuration file validation failed:\n" + "\n".join(f"- {error}" for error in errors)
        raise ValueError(error_msg)
    
    return config


if __name__ == "__main__":
    # 测试配置读取功能
    try:
        config = load_config("simulation_config.yaml")
        print("Configuration loaded successfully!")
        print(f"Simulator: {config.simulator}")
        print(f"Design path: {config.design_path}")
        print(f"Analysis types: {list(config.analyses.keys())}")
    except Exception as e:
        print(f"Configuration loading failed: {e}")