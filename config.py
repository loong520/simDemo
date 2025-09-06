#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
芯片仿真配置文件读取模块
支持YAML格式的配置文件
"""

import yaml
import os
from collections import defaultdict


class ServerConfig(object):
    """服务器配置数据类"""
    def __init__(self, url="", api_key=""):
        self.url = url      # 服务器URL
        self.api_key = api_key  # API密钥


class EDATool(object):
    """EDA工具配置数据类"""
    def __init__(self, executable="", launch_args=None, environment_variables=None, options=None):
        # 启动命令配置
        self.executable = executable
        self.launch_args = launch_args or []
        
        # 环境变量配置（每个成员是"export VAR=value"格式）
        self.environment_variables = environment_variables or []
        
        # 工具特定选项
        self.options = options or {}
    
    def get_environment_dict(self):
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
    
    def get_source_commands(self):
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
    
    def get_export_commands(self):
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
                env_line = "export " + env_line
                
            export_commands.append(env_line)
        
        return export_commands


class EDASToolsConfig(object):
    """EDA工具配置数据类"""
    def __init__(self):
        # 各个工具的配置
        self.spectre = EDATool()
        self.virtuoso = EDATool()
    
    def get_tool_config(self, tool_name):
        """
        获取指定工具的配置
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具配置对象
        """
        return getattr(self, tool_name, None)


class SimulationConfig(object):
    """仿真配置数据类"""
    def __init__(self):
        # 基本仿真配置
        self.simulator = "spectre"  # 仿真器类型 (spectre, virtuoso, etc.)
        self.project_dir = ""       # 项目目录路径
        self.library_name = ""      # 库名称
        self.cell_name = ""         # 单元名称
        self.simulation_path = ""   # 仿真路径
        self.design_type = "schematic"  # 设计类型 (schematic, layout, etc.)
        
        # EDA工具配置 (从系统配置文件加载)
        self.eda_tools = EDASToolsConfig()
        
        # 模型文件配置 (从testbench配置文件加载)
        self.model_files = []  # 模型文件路径和工艺角
        
        # 仿真分析配置 (从testbench配置文件加载)
        self.analyses = {}  # 分析类型和参数
        
        # 激励配置 (从testbench配置文件加载)
        self.stimulus_files = []    # 激励文件路径
        
        # 设计变量 (从testbench配置文件加载)
        self.design_variables = {}
        
        # 保存节点 (从testbench配置文件加载)
        self.save_nodes = []
        
        # 环境配置
        self.temperature = 27.0           # 仿真温度
        self.supply_voltage = 1.8         # 电源电压
        
        # 服务器配置 (从系统配置文件加载)
        self.server = ServerConfig()
        
        # 收敛配置 (从testbench配置文件加载)
        self.initial_conditions = {}
        
        # 后处理配置 (从testbench配置文件加载)
        self.post_processing = {}
    
    @property
    def project_name(self):
        """从project_dir自动获取项目名称"""
        if self.project_dir:
            return os.path.basename(self.project_dir)
        return "sim_project"
    
    @property
    def design_path(self):
        """自动计算design_path"""
        if not all([self.simulation_path, self.cell_name, self.simulator, self.design_type]):
            return ""
        return "{}/{}/{}/{}/netlist/netlist".format(
            self.simulation_path, self.cell_name, self.simulator, self.design_type)
    
    @property
    def results_dir(self):
        """自动计算results_dir"""
        if not all([self.simulation_path, self.cell_name, self.simulator, self.design_type]):
            return ""
        return "{}/{}/{}/{}".format(
            self.simulation_path, self.cell_name, self.simulator, self.design_type)


class ConfigReader(object):
    """配置文件读取器"""
    
    # 系统配置文件路径（全局变量）
    SYSTEM_CONFIG_FILE = "conf/system_config.yaml"
    
    def __init__(self, config_file=None):
        """
        初始化配置读取器
        
        Args:
            config_file: 仿真任务配置文件路径
        """
        self.config_file = config_file
        self.system_config_data = self._load_system_config()
        self.testbench_config_data = {}
        
        if self.config_file and os.path.exists(self.config_file):
            self.task_config_data = self._load_config(self.config_file)
            # 加载testbench配置
            testbench_path = self.task_config_data.get('testbench_config')
            if testbench_path:
                testbench_file = testbench_path
                if not os.path.exists(testbench_file):
                    # 尝试在相同目录下查找
                    task_config_dir = os.path.dirname(self.config_file)
                    testbench_file = os.path.join(task_config_dir, testbench_path)
                if os.path.exists(testbench_file):
                    self.testbench_config_data = self._load_config(testbench_file)
        else:
            self.task_config_data = {}
    
    def _load_system_config(self):
        """加载系统配置文件"""
        system_config_path = self.SYSTEM_CONFIG_FILE
        if not os.path.exists(system_config_path):
            raise IOError("System configuration file not found: {}".format(self.SYSTEM_CONFIG_FILE))
        return self._load_config(system_config_path)
    
    def _load_config(self, config_path):
        """加载配置文件"""
        file_ext = os.path.splitext(config_path)[1].lower()
        
        if file_ext in ['.yaml', '.yml']:
            return self._load_yaml(config_path)
        else:
            raise ValueError("Unsupported configuration file format: {}, only YAML format is supported".format(file_ext))
    
    def _load_yaml(self, config_path):
        """加载YAML配置文件"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError("YAML configuration file parsing error: {}".format(e))

    
    def get_simulation_config(self):
        """获取仿真配置对象"""
        try:
            # 创建仿真配置对象
            sim_config = SimulationConfig()
            
            # 从任务配置文件加载基本仿真配置
            basic_config = self.task_config_data.get('simulation', {})
            sim_config.simulator = basic_config.get('simulator', 'spectre')
            sim_config.project_dir = basic_config.get('project_dir', '')
            sim_config.library_name = basic_config.get('library_name', '')
            sim_config.cell_name = basic_config.get('cell_name', '')
            sim_config.simulation_path = basic_config.get('simulation_path', '')
            sim_config.design_type = basic_config.get('design_type', 'schematic')
            sim_config.temperature = float(basic_config.get('temperature', 27.0))
            sim_config.supply_voltage = float(basic_config.get('supply_voltage', 1.8))
            
            # 从系统配置文件加载EDA工具配置
            if 'eda_tools' in self.system_config_data:
                eda_config = self.system_config_data['eda_tools']
                
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
            
            # 从系统配置文件加载服务器配置
            if 'server' in self.system_config_data:
                server_config = self.system_config_data['server']
                sim_config.server = ServerConfig(
                    url=server_config.get('url', ''),
                    api_key=server_config.get('api_key', '')
                )
            
            # 从testbench配置文件加载模型文件配置
            if 'models' in self.testbench_config_data:
                model_config = self.testbench_config_data['models']
                sim_config.model_files = model_config.get('files', [])
            
            # 从testbench配置文件加载分析配置
            if 'analyses' in self.testbench_config_data:
                sim_config.analyses = self.testbench_config_data['analyses']
            
            # 从testbench配置文件加载激励文件
            if 'stimulus' in self.testbench_config_data:
                stimulus_config = self.testbench_config_data['stimulus']
                sim_config.stimulus_files = stimulus_config.get('files', [])
            
            # 从testbench配置文件加载设计变量
            if 'variables' in self.testbench_config_data:
                sim_config.design_variables = self.testbench_config_data['variables']
            
            # 从testbench配置文件加载保存节点
            if 'outputs' in self.testbench_config_data:
                output_config = self.testbench_config_data['outputs']
                sim_config.save_nodes = output_config.get('save_nodes', [])
            
            # 从testbench配置文件加载初始条件
            if 'initial_conditions' in self.testbench_config_data:
                sim_config.initial_conditions = self.testbench_config_data['initial_conditions']
            
            # 从testbench配置文件加载环境配置
            if 'environment' in self.testbench_config_data:
                env_config = self.testbench_config_data['environment']
                sim_config.temperature = float(env_config.get('temperature', 27.0))
                sim_config.supply_voltage = float(env_config.get('supply_voltage', 1.8))
            
            # 从testbench配置文件加载后处理配置
            if 'post_processing' in self.testbench_config_data:
                sim_config.post_processing = self.testbench_config_data['post_processing']
            
            return sim_config
            
        except Exception as e:
            raise ValueError("Configuration file parsing error: {}".format(e))
    
    def load_system_config(self):
        """
        便捷函数：加载系统配置文件并返回配置对象（用于HTTP接口）
        
        Returns:
            仿真配置对象（仅包含系统配置）
        """
        config = SimulationConfig()
        
        # 从系统配置文件加载EDA工具配置
        if 'eda_tools' in self.system_config_data:
            eda_config = self.system_config_data['eda_tools']
            
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
            
            config.eda_tools = tools_config
        
        # 从系统配置文件加载服务器配置
        if 'server' in self.system_config_data:
            server_config = self.system_config_data['server']
            config.server = ServerConfig(
                url=server_config.get('url', ''),
                api_key=server_config.get('api_key', '')
            )
        
        return config
    
    def load_task_config(self, config_file):
        """
        便捷函数：加载仿真任务配置文件并返回配置对象
        
        Args:
            config_file: 仿真任务配置文件路径
            
        Returns:
            仿真配置对象
        """
        reader = ConfigReader(config_file)
        config = reader.get_simulation_config()
        
        # 验证配置
        errors = reader.validate_config(config)
        if errors:
            error_msg = "Configuration file validation failed:\n" + "\n".join("- {}".format(error) for error in errors)
            raise ValueError(error_msg)
        
        return config
    
    def validate_config(self, config):
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
        elif not os.path.exists(config.project_dir):
            errors.append("Project directory does not exist: {}".format(config.project_dir))
        
        if not config.simulation_path:
            errors.append("Simulation path (simulation_path) cannot be empty")
            
        if not config.library_name:
            errors.append("Library name (library_name) cannot be empty")
            
        if not config.cell_name:
            errors.append("Cell name (cell_name) cannot be empty")
        
        # 检查计算出的design_path
        design_path = config.design_path
        if design_path and not os.path.exists(design_path):
            errors.append("Design file does not exist (computed path): {}".format(design_path))
        
        # 检查模型文件
        for model_file_info in config.model_files:
            if isinstance(model_file_info, list) and len(model_file_info) >= 1:
                model_path = model_file_info[0]
                if not os.path.exists(model_path):
                    errors.append("Model file does not exist: {}".format(model_path))
        
        # 检查激励文件
        for stimulus_file in config.stimulus_files:
            if not os.path.exists(stimulus_file):
                errors.append("Stimulus file does not exist: {}".format(stimulus_file))
        
        # 检查分析配置
        if not config.analyses:
            errors.append("At least one analysis type must be configured")
        
        # 检查仿真器支持
        supported_simulators = ['spectre', 'virtuoso']
        if config.simulator not in supported_simulators:
            errors.append("Unsupported simulator: {}".format(config.simulator))
        
        # 检查EDA工具配置
        if config.eda_tools:
            # 获取当前仿真器的工具配置
            tool_config = config.eda_tools.get_tool_config(config.simulator)
            if tool_config:
                # 检查可执行命令是否配置
                if not tool_config.executable:
                    errors.append("Executable command not configured for simulator: {}".format(config.simulator))
                
                # 检查关键环境变量（简化检查）
                env_vars = tool_config.environment_variables
                if not env_vars:
                    errors.append("No environment variables configured for simulator: {}".format(config.simulator))
            else:
                errors.append("No tool configuration found for simulator: {}".format(config.simulator))
        
        return errors


def load_system_config():
    """
    便捷函数：加载系统配置文件并返回配置对象（用于HTTP接口）
    
    Returns:
        仿真配置对象（仅包含系统配置）
    """
    reader = ConfigReader()
    return reader.load_system_config()


def load_task_config(config_file):
    """
    便捷函数：加载仿真任务配置文件并返回配置对象
    
    Args:
        config_file: 仿真任务配置文件路径
        
    Returns:
        仿真配置对象
    """
    reader = ConfigReader(config_file)
    return reader.load_task_config(config_file)


if __name__ == "__main__":
    # 测试配置读取功能
    try:
        # 测试系统配置加载
        system_config = load_system_config()
        print("System configuration loaded successfully!")
        print("Server URL: {}".format(system_config.server.url))
        
        # 测试任务配置加载
        task_config = load_task_config("simulation_task_config.yaml")
        print("Task configuration loaded successfully!")
        print("Simulator: {}".format(task_config.simulator))
        print("Design path: {}".format(task_config.design_path))
        print("Analysis types: {}".format(list(task_config.analyses.keys())))
    except Exception as e:
        print("Configuration loading failed: {}".format(e))