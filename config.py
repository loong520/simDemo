"""
芯片仿真配置文件读取模块
支持YAML格式的配置文件
"""

import yaml
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SimulationConfig:
    """仿真配置数据类"""
    # 基本仿真配置
    simulator: str = "spectre"  # 仿真器类型 (spectre, hspice, etc.)
    design_path: str = ""       # 原理图netlist路径
    results_dir: str = ""       # 仿真结果输出目录
    project_name: str = "sim_project"  # 项目名称
    
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
                design_path=basic_config.get('design_path', ''),
                results_dir=basic_config.get('results_dir', './results'),
                project_name=basic_config.get('project_name', 'sim_project'),
                temperature=float(basic_config.get('temperature', 27.0)),
                supply_voltage=float(basic_config.get('supply_voltage', 1.8))
            )
            
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
        
        # 检查必要的路径
        if not config.design_path:
            errors.append("Design path (design_path) cannot be empty")
        elif not Path(config.design_path).exists():
            errors.append(f"Design file does not exist: {config.design_path}")
        
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
        supported_simulators = ['spectre', 'hspice', 'eldo']
        if config.simulator not in supported_simulators:
            errors.append(f"Unsupported simulator: {config.simulator}")
        
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