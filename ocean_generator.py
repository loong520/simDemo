#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ocean脚本生成器模块
用于根据配置生成各种类型的Ocean脚本
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader
from config import SimulationConfig


class OceanScriptGenerator:
    """Ocean脚本生成器"""
    
    def __init__(self, config: SimulationConfig):
        """
        初始化Ocean脚本生成器
        
        Args:
            config: 仿真配置对象
        """
        self.config = config
        self.script_content = []
        
        # 设置模板环境
        self.template_dir = Path(__file__).parent / 'templates'
        self.ocean_template_dir = self.template_dir / 'ocean'
        self.python_template_dir = self.template_dir / 'python'
        
        # 创建Jinja2环境
        self.ocean_env = Environment(loader=FileSystemLoader(str(self.ocean_template_dir)))
        self.python_env = Environment(loader=FileSystemLoader(str(self.python_template_dir)))
    
    def _load_template(self, template_name: str, template_type: str = 'ocean'):
        """
        加载模板文件
        
        Args:
            template_name: 模板名称（不包含扩展名）
            template_type: 模板类型（'ocean' 或 'python'）
            
        Returns:
            Jinja2模板对象
        """
        if template_type == 'ocean':
            template_file = f'{template_name}.ocean'
            return self.ocean_env.get_template(template_file)
        elif template_type == 'python':
            template_file = f'{template_name}.py'
            return self.python_env.get_template(template_file)
        else:
            raise ValueError(f'Unknown template type: {template_type}')
    
    def generate_netlist_script(self) -> str:
        """
        Generate Ocean script for netlist creation
        
        Returns:
            Generated Ocean script content for netlist creation
        """
        template = self._load_template('netlist_generation')
        content = template.render(
            simulator=self.config.simulator,
            library_name=self.config.library_name,
            cell_name=self.config.cell_name,
            design_type=self.config.design_type
        )
        return content
    
    def save_netlist_script(self, output_file: str) -> str:
        """
        Generate and save netlist creation Ocean script to file
        
        Args:
            output_file: Output file path
            
        Returns:
            Saved file path
        """
        script_content = self.generate_netlist_script()
        
        # Ensure output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write script to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(output_path)
    
    def generate_script(self) -> str:
        """
        生成完整的Ocean脚本
        
        Returns:
            生成的Ocean脚本内容
        """
        self.script_content = []
        
        # 1. 添加头部注释
        self._add_header()
        
        # 2. 设置仿真器
        self._add_simulator()
        
        # 3. 设置设计路径
        self._add_design()
        
        # 4. 设置结果目录
        self._add_results_dir()
        
        # 5. 加载模型文件
        self._add_model_files()
        
        # 6. 加载激励文件
        self._add_stimulus_files()
        
        # 7. 设置设计变量
        self._add_design_variables()
        
        # 8. 配置分析类型
        self._add_analyses()
        
        # 9. 保存节点配置
        self._add_save_nodes()
        
        # 10. 初始条件设置
        self._add_initial_conditions()
        
        # 11. 环境配置
        self._add_environment()
        
        # 12. 运行仿真
        self._add_run()
        
        # 13. 后处理
        self._add_post_processing()
        
        return '\n'.join(self.script_content)
    
    def _add_header(self):
        """添加头部注释"""
        template = self._load_template('header')
        content = template.render(project_name=self.config.project_name)
        self.script_content.append(content)
    
    def _add_simulator(self):
        """添加仿真器配置"""
        template = self._load_template('simulator')
        content = template.render(simulator=self.config.simulator)
        self.script_content.append(content)
    
    def _add_design(self):
        """添加设计路径配置"""
        template = self._load_template('design')
        content = template.render(design_path=self.config.design_path)
        self.script_content.append(content)
    
    def _add_results_dir(self):
        """添加结果目录配置"""
        # 确保结果目录存在
        results_path = Path(self.config.results_dir)
        results_path.mkdir(parents=True, exist_ok=True)
        
        template = self._load_template('results_dir')
        content = template.render(results_dir=self.config.results_dir)
        self.script_content.append(content)
    
    def _add_model_files(self):
        """添加模型文件配置"""
        if self.config.model_files:
            template = self._load_template('model_file')
            content = template.render(model_files=self.config.model_files)
            self.script_content.append(content)
    
    def _add_stimulus_files(self):
        """添加激励文件配置"""
        if self.config.stimulus_files:
            template = self._load_template('stimulus')
            content = template.render(stimulus_files=self.config.stimulus_files)
            self.script_content.append(content)
    
    def _add_design_variables(self):
        """添加设计变量配置"""
        if self.config.design_variables:
            template = self._load_template('design_variables')
            content = template.render(design_variables=self.config.design_variables)
            self.script_content.append(content)
    
    def _add_analyses(self):
        """添加分析配置"""
        for analysis_type, analysis_params in self.config.analyses.items():
            try:
                # 尝试加载特定分析类型的模板
                template = self._load_template(f'analysis_{analysis_type}')
                content = template.render(analysis_params=analysis_params)
                self.script_content.append(content)
            except:
                # 如果没有找到特定模板，使用通用分析模板
                self._add_generic_analysis(analysis_type, analysis_params)
    
    def _add_generic_analysis(self, analysis_type: str, params: Dict[str, Any]):
        """添加通用分析配置"""
        analysis_content = f"; {analysis_type.upper()} analysis configuration\n"
        analysis_content += f"analysis('{analysis_type}\n"
        
        for param, value in params.items():
            if isinstance(value, str):
                analysis_content += f'         ?{param} "{value}"\n'
            else:
                analysis_content += f'         ?{param} {value}\n'
        
        analysis_content += ")\n"
        self.script_content.append(analysis_content)
    
    def _add_save_nodes(self):
        """添加保存节点配置"""
        if self.config.save_nodes:
            template = self._load_template('save_nodes')
            content = template.render(save_nodes=self.config.save_nodes)
            self.script_content.append(content)
    
    def _add_initial_conditions(self):
        """添加初始条件设置"""
        if self.config.initial_conditions:
            template = self._load_template('initial_conditions')
            content = template.render(initial_conditions=self.config.initial_conditions)
            self.script_content.append(content)
    
    def _add_environment(self):
        """添加环境配置"""
        template = self._load_template('environment')
        content = template.render(temperature=self.config.temperature)
        self.script_content.append(content)
    
    def _add_run(self):
        """添加运行命令"""
        template = self._load_template('run')
        content = template.render()
        self.script_content.append(content)
    
    def _add_post_processing(self):
        """添加后处理配置"""
        if self.config.post_processing:
            post_config = self.config.post_processing
            
            # 获取主要分析类型用于selectResult
            main_analysis = list(self.config.analyses.keys())[0] if self.config.analyses else 'tran'
            
            template = self._load_template('post_processing')
            content = template.render(
                analysis_type=main_analysis,
                plot_enabled=post_config.get('plot_enabled', False),
                plots=post_config.get('plots', []),
                save_data=post_config.get('save_data', False),
                save_items=post_config.get('save_items', [])
            )
            self.script_content.append(content)
    
    def save_script(self, output_file: str) -> str:
        """
        保存Ocean脚本到文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            实际保存的文件路径
        """
        script_content = self.generate_script()
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(output_path.absolute())
    



def generate_ocean_script(config: SimulationConfig, output_file: Optional[str] = None) -> str:
    """
    Convenient function: Generate Ocean script
    
    Args:
        config: Simulation configuration object
        output_file: Output file path, if None then do not save file
        
    Returns:
        Generated script content or saved file path
    """
    generator = OceanScriptGenerator(config)
    
    if output_file:
        return generator.save_script(output_file)
    else:
        return generator.generate_script()


def generate_netlist_script(config: SimulationConfig, output_file: Optional[str] = None) -> str:
    """
    Convenient function: Generate netlist creation Ocean script
    
    Args:
        config: Simulation configuration object
        output_file: Output file path, if None then return script content
        
    Returns:
        Generated script content or saved file path
    """
    generator = OceanScriptGenerator(config)
    
    if output_file:
        return generator.save_netlist_script(output_file)
    else:
        return generator.generate_netlist_script()


if __name__ == "__main__":
    # 测试脚本生成功能
    from config import SimulationConfig
    
    # 创建测试配置
    test_config = SimulationConfig(
        project_dir="/path/to/project",
        library_name="test_lib",
        cell_name="test_cell", 
        simulation_path="/path/to/simulation",
        design_type="schematic",
        simulator="spectre",
        model_files=[
            ["/path/to/models/design.scs", ""],
            ["/path/to/models/process.scs", "tt"]
        ],
        analyses={
            "tran": {"stop": "1n", "step": "1p"},
            "dc": {"saveOppoint": "t"}
        },
        design_variables={"vdd": 1.8, "temp_coeff": 1e-3},
        save_nodes=["/vout", "/vin", "/vdd"],
        initial_conditions={"/vin": 0.0},
        temperature=27.0
    )
    
    # 生成Ocean脚本
    generator = OceanScriptGenerator(test_config)
    script_content = generator.generate_script()
    print("Generated Ocean script:")
    print("=" * 50)
    print(script_content)