#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仿真执行器模块
负责执行生成的Ocean脚本和管理仿真流程
"""

import os
import subprocess
import time
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime

from config import SimulationConfig
from ocean_generator import OceanScriptGenerator
from shell_generator import ShellScriptGenerator


class SimulationExecutor:
    """仿真执行器"""
    
    def __init__(self, config: SimulationConfig, work_dir: Optional[str] = None):
        """
        初始化仿真执行器
        
        Args:
            config: 仿真配置对象
            work_dir: 工作目录，默认为当前目录
        """
        self.config = config
        self.work_dir = Path(work_dir) if work_dir else Path.cwd()
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self.logger = self._setup_logger()
        
        # 仿真状态
        self.simulation_status = "Not started"
        self.start_time = None
        self.end_time = None
        self.log_files = []
        
        # 生成的脚本路径
        self.ocean_script_path = None
        # 注释掉复杂的shell脚本路径字典，因为现在使用一步式生成
        # self.shell_script_paths = {}  # 新增：shell脚本路径字典
        
        # 仿真进程
        self.simulation_process = None
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"simulator_{self.config.project_name}")
        logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not logger.handlers:
            # 文件handler
            log_file = self.work_dir / f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式化
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            self.log_files.append(str(log_file))
        
        return logger
    
    def prepare_simulation(self) -> bool:
        """
        准备仿真环境
        
        Returns:
            准备是否成功
        """
        try:
            self.logger.info("Starting simulation environment preparation...")
            
            # 1. 验证配置
            self.logger.info("Validating simulation configuration...")
            from config import ConfigReader
            
            # 创建临时配置读取器进行验证
            temp_reader = ConfigReader.__new__(ConfigReader)
            errors = temp_reader.validate_config(self.config) if hasattr(temp_reader, 'validate_config') else []
            
            if errors:
                for error in errors:
                    self.logger.error(f"Configuration error: {error}")
                return False
            
            # 2. 创建工作目录结构
            self._create_work_directories()
            
            # 3. 生成Ocean脚本
            self.logger.info("Generating Ocean script...")
            self.ocean_script_path = self._generate_ocean_script()
            
            # 4. 检查仿真器环境
            self.logger.info("Checking simulator environment...")
            if not self._check_simulator_environment():
                self.logger.warning("Simulator environment check failed, manual environment variable setup may be required")
            
            self.logger.info("Simulation environment preparation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error preparing simulation environment: {e}")
            return False
    
    def _create_work_directories(self):
        """创建工作目录结构"""
        directories = [
            "scripts",      # 脚本目录
            "results",      # 结果目录
            "logs",         # 日志目录
            "temp"          # 临时文件目录
        ]
        
        for dir_name in directories:
            dir_path = self.work_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            self.logger.debug(f"Creating directory: {dir_path}")
    
    def _generate_ocean_script(self) -> str:
        """
        生成Ocean脚本
        
        Returns:
            生成的脚本文件路径
        """
        generator = OceanScriptGenerator(self.config)
        script_path = self.work_dir / "scripts" / f"{self.config.project_name}.ocn"
        
        saved_path = generator.save_script(str(script_path))
        self.logger.info(f"Ocean script generated: {saved_path}")
        
        return saved_path
    

    
    def _check_simulator_environment(self) -> bool:
        """
        检查仿真器环境
        
        Returns:
            环境是否正常
        """
        simulator = self.config.simulator.lower()
        
        # 检查常见的仿真器命令
        simulator_commands = {
            'spectre': ['spectre', 'spectreX'],
            'virtuoso': ['virtuoso'],
        }
        
        if simulator in simulator_commands:
            for cmd in simulator_commands[simulator]:
                if shutil.which(cmd):
                    self.logger.info(f"Found simulator command: {cmd}")
                    return True
        
        # 检查Cadence环境变量
        cadence_vars = ['CDS_ROOT', 'MMSIM_ROOT', 'CDS_INST_DIR']
        for var in cadence_vars:
            if os.environ.get(var):
                self.logger.info(f"Found Cadence environment variable: {var}={os.environ[var]}")
                return True
        
        return False

    def run_ocean_simulation(self, timeout: int = 3600) -> Tuple[bool, str]:
        """
        运行Ocean脚本仿真
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            (成功状态, 输出信息)
        """
        if not self.ocean_script_path:
            return False, "Ocean script not generated"
        
        try:
            self.simulation_status = "Running Ocean simulation"
            self.start_time = datetime.now()
            self.logger.info("Starting Ocean simulation...")
            
            # 准备命令
            simulator = self.config.simulator.lower()
            
            if simulator == 'spectre':
                cmd = ['ocean', '-nograph', '-replay', self.ocean_script_path]
            elif simulator == 'virtuoso':
                cmd = ['ocean', '-nograph', '-replay', self.ocean_script_path]
            else:
                # 通用命令
                cmd = ['ocean', '-nograph', '-replay', self.ocean_script_path]
            
            # 设置工作目录和环境
            work_env = os.environ.copy()
            cwd = self.work_dir / "temp"
            
            self.logger.info(f"Executing command: {' '.join(cmd)}")
            self.logger.info(f"Working directory: {cwd}")
            
            # 运行仿真
            self.simulation_process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=work_env
            )
            
            # 实时输出日志
            output_lines = []
            if self.simulation_process.stdout:
                while True:
                    output = self.simulation_process.stdout.readline()
                    if output == '' and self.simulation_process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        output_lines.append(line)
                        self.logger.info(f"Simulation output: {line}")
            
            # 等待完成
            return_code = self.simulation_process.wait(timeout=timeout)
            
            self.end_time = datetime.now()
            duration = self.end_time - self.start_time
            
            if return_code == 0:
                self.simulation_status = "Ocean simulation completed"
                self.logger.info(f"Ocean simulation completed successfully, elapsed time: {duration}")
                
                return True, '\n'.join(output_lines)
            else:
                self.simulation_status = "Ocean simulation failed"
                self.logger.error(f"Ocean simulation failed, return code: {return_code}")
                return False, '\n'.join(output_lines)
                
        except subprocess.TimeoutExpired:
            self.simulation_status = "Ocean simulation timeout"
            self.logger.error(f"Ocean simulation timeout ({timeout} seconds)")
            if self.simulation_process:
                self.simulation_process.terminate()
            return False, "Simulation timeout"
            
        except Exception as e:
            self.simulation_status = "Ocean simulation error"
            self.logger.error(f"Error running Ocean simulation: {e}")
            return False, str(e)
    

    
    def stop_simulation(self):
        """停止正在运行的仿真"""
        if self.simulation_process:
            self.logger.info("Stopping simulation...")
            self.simulation_process.terminate()
            try:
                self.simulation_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.simulation_process.kill()
            
            self.simulation_status = "Simulation stopped"
            self.logger.info("Simulation stopped")
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """
        获取仿真状态信息
        
        Returns:
            状态信息字典
        """
        status_info = {
            'status': self.simulation_status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': str(self.end_time - self.start_time) if self.start_time and self.end_time else None,
            'work_dir': str(self.work_dir),
            'ocean_script': self.ocean_script_path,
            'log_files': self.log_files,
            'results_dir': str(self.config.results_dir),
            'project_name': self.config.project_name
        }
        
        return status_info
    
    def collect_results(self) -> Dict[str, Any]:
        """
        收集仿真结果
        
        Returns:
            结果信息字典
        """
        results = {
            'status': self.simulation_status,
            'files': [],
            'plots': [],
            'data': [],
            'logs': self.log_files
        }
        
        # 搜索结果文件
        results_dir = Path(self.config.results_dir)
        if results_dir.exists():
            # 搜索常见的结果文件
            patterns = ['*.log', '*.out', '*.raw', '*.tr0', '*.ac0', '*.dc0', '*.png', '*.pdf']
            
            for pattern in patterns:
                for file_path in results_dir.rglob(pattern):
                    file_info = {
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    }
                    
                    if file_path.suffix.lower() in ['.png', '.pdf', '.jpg', '.jpeg']:
                        results['plots'].append(file_info)
                    elif file_path.suffix.lower() in ['.raw', '.tr0', '.ac0', '.dc0']:
                        results['data'].append(file_info)
                    else:
                        results['files'].append(file_info)
        
        return results
    
    def cleanup(self, keep_results: bool = True):
        """
        清理临时文件
        
        Args:
            keep_results: 是否保留结果文件
        """
        try:
            self.logger.info("Starting temporary file cleanup...")
            
            # 清理临时目录
            temp_dir = self.work_dir / "temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                self.logger.info("Temporary files cleaned")
            
            if not keep_results:
                # 清理结果目录
                results_dir = Path(self.config.results_dir)
                if results_dir.exists():
                    shutil.rmtree(results_dir)
                    self.logger.info("Result files cleaned")
                
                # 清理脚本目录
                scripts_dir = self.work_dir / "scripts"
                if scripts_dir.exists():
                    shutil.rmtree(scripts_dir)
                    self.logger.info("Script files cleaned")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up files: {e}")


def run_simulation(config: SimulationConfig, 
                  work_dir: Optional[str] = None,
                  timeout: int = 3600) -> Tuple[bool, Dict[str, Any]]:
    """
    便捷函数：运行仿真
    
    Args:
        config: 仿真配置对象
        work_dir: 工作目录
        timeout: 超时时间
        
    Returns:
        (成功状态, 仿真结果)
    """
    executor = SimulationExecutor(config, work_dir)
    
    try:
        # 准备仿真
        if not executor.prepare_simulation():
            return False, {"error": "Simulation preparation failed"}
        
        # 运行仿真
        success, output = executor.run_ocean_simulation(timeout)
        
        # 收集结果
        results = executor.collect_results()
        results['output'] = output
        results['status_info'] = executor.get_simulation_status()
        
        return success, results
        
    except Exception as e:
        return False, {"error": str(e)}
    
    finally:
        # 清理临时文件
        executor.cleanup(keep_results=True)


if __name__ == "__main__":
    # 测试仿真执行功能
    from config import SimulationConfig
    
    # 创建测试配置
    test_config = SimulationConfig(
        project_dir="/path/to/test",
        library_name="test_lib",
        cell_name="test_cell",
        simulation_path="/path/to/test/sim",
        simulator="spectre",
        analyses={"tran": {"stop": "1n"}},
        save_nodes=["/vout"],
        temperature=27.0
    )
    
    # 创建执行器
    executor = SimulationExecutor(test_config, "./test_work")
    
    # 准备仿真
    if executor.prepare_simulation():
        print("Simulation environment prepared successfully")
        print(f"Ocean script: {executor.ocean_script_path}")
        
        # 显示状态
        status = executor.get_simulation_status()
        print(f"Simulation status: {status}")
    else:
        print("Simulation environment preparation failed")