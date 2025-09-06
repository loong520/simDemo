# 芯片仿真自动化 Demo

一个基于 Python 的芯片模拟仿真自动化工具，支持从配置文件读取仿真参数，自动生成 Ocean 脚本和 Python 脚本，并执行 Cadence Spectre 等仿真器进行芯片电路仿真。

## 功能特性

- 📋 **配置文件驱动**: 支持 YAML 格式的配置文件
- 🔧 **多仿真器支持**: 支持 Spectre、HSPICE 等主流仿真器
- 📜 **自动脚本生成**: 生成标准 Ocean 脚本
- 🚀 **一键执行**: 命令行和交互式界面支持
- 📊 **结果管理**: 自动收集和整理仿真结果
- 🔍 **状态监控**: 实时监控仿真进度和状态
- 🛠️ **灵活扩展**: 模块化设计，易于扩展新功能

## 项目结构

```
simDemo/
├── main.py                      # 主程序入口
├── config.py                    # 配置文件读取模块
├── ocean_generator.py           # Ocean脚本生成器
├── shell_generator.py           # Shell脚本生成器
├── simulator.py                 # 仿真执行器
├── simulation_manager.py         # 仿真任务管理器
├── project_manager.py           # 项目管理器
├── eda_tool_manager.py          # EDA工具管理器
├── pdk_manager.py               # PDK管理器
├── service_request.py           # 服务请求基类
├── demo.py                      # 功能演示脚本
├── install.py                   # 安装脚本
├── requirements.txt             # Python依赖包
├── simulation_config.yaml       # 系统配置文件示例
├── simulation_task_config.yaml  # 仿真任务配置文件示例
├── system_config.yaml           # 系统配置文件示例
├── README.md                    # 项目说明文档
├── conf/                        # 配置文件目录
├── templates/                   # 模板文件目录
├── testbenches/                # Testbench配置文件目录
└── tests/                      # 测试文件目录
```

## 安装依赖

首先确保您的系统已安装 Python 3.7+，然后安装必要的依赖包：

```bash
pip install -r requirements.txt
```

主要依赖包：

- `pyyaml`: YAML 配置文件解析
- `jinja2`: 模板引擎，用于生成脚本
- `numpy`: 数值计算
- `pandas`: 数据处理
- `matplotlib`: 绘图

## 快速开始

### 1. 准备配置文件

复制并修改示例配置文件：

```bash
cp simulation_task_config.yaml my_task.yaml
```

编辑配置文件，修改以下关键参数：

- `simulation.project_dir`: 您的项目目录路径
- `simulation.library_name`: 库名称
- `simulation.cell_name`: 单元模块名称
- `testbench_config`: testbench 配置文件路径

### 2. 运行仿真

#### 命令行模式

```bash
# 查看所有可用命令
python main.py -h

# 运行仿真任务
python main.py simulation run-task -c my_task.yaml

# 创建testbench
python main.py simulation create-testbench --name my_testbench --config-file testbenches/testbench_config.yaml --description "My testbench"

# 列出所有testbench
python main.py simulation list-testbench

# 查询所有仿真任务运行状态
python main.py simulation show-task

# EDA工具管理命令
python main.py eda-tool -h

# PDK管理命令
python main.py pdk -h

# 项目管理命令
python main.py project -h
```

#### 交互式模式

```bash
python main.py -i
```

然后按照提示选择操作。

### 3. 查看结果

仿真完成后，结果将保存在配置文件中指定的目录中。

## 配置文件说明

### 仿真任务配置文件 (simulation_task_config.yaml)

```yaml
# 基本仿真配置
simulation:
  project_dir: "/home/IC/EDA/Test" # 项目目录路径
  library_name: "test" # 库名称
  cell_name: "inv" # 单元模块名称
  design_type: "schematic" # 设计类型 (schematic, layout)
  simulator: "spectre" # 仿真器类型 (spectre, virtuoso)
  simulation_path: "/home/IC/simulation" # 仿真根路径

# Testbench配置文件路径
testbench_config: "testbenches/testbench_config.yaml"
```

### Testbench 配置文件 (testbench_config.yaml)

```yaml
# 模型文件配置
models:
  files:
    - ["/path/to/model1.scs", "tt"] # [模型文件路径, 工艺角]
    - ["/path/to/model2.scs", ""]

# 分析配置
analyses:
  # 瞬态分析
  tran:
    start: "0"
    stop: "10u" # 仿真停止时间
    step: "10n" # 仿真步长
    errpreset: "conservative" # 高精度

# 环境配置
environment:
  temperature: 27.0 # 仿真温度 (摄氏度)
  supply_voltage: 1.8 # 电源电压 (V)

# 设计变量
variables:
  vdd: 1.8 # 电源电压

# 输出配置
outputs:
  save_nodes: # 需要保存的节点
    - "/vout" # 输出电压
    - "/vin" # 输入电压

# 初始条件
initial_conditions:
  "/vout": 0.9 # 输出节点初始电压
```

## 命令行接口

### 仿真管理命令

```bash
# 运行仿真任务
python main.py simulation run-task -c <config_file>

# 创建testbench
python main.py simulation create-testbench --name <name> --config-file <config_file> [--description <description>]

# 删除testbench
python main.py simulation delete-testbench --name <name>

# 更新testbench
python main.py simulation update-testbench --name <name> [--config-file <config_file>] [--description <description>]

# 列出所有testbench
python main.py simulation list-testbench

# 查询所有仿真任务运行状态
python main.py simulation show-task [--project-name <project>] [--library-name <library>] [--cell-name <cell>]
```

### EDA 工具管理命令

```bash
# 创建EDA工具
python main.py eda-tool create --name <name> --version <version> --launch-command <command> --vendor <vendor> [--env-var <var>]

# 查询EDA工具信息
python main.py eda-tool get --tool-id <id>

# 列出所有EDA工具
python main.py eda-tool list

# 删除EDA工具
python main.py eda-tool delete --tool-id <id>

# 更新EDA工具
python main.py eda-tool update --tool-id <id> [--name <name>] [--version <version>] [--launch-command <command>] [--vendor <vendor>] [--env-var <var>]
```

### PDK 管理命令

```bash
# 创建PDK
python main.py pdk create --name <name> --version <version> --process <process> --vendor <vendor> --root-path <path> --drc-path <path> --lvs-path <path> --xrc-path <path> --spectre-path <path> --hspice-path <path>

# 查询PDK信息
python main.py pdk get --pdk-id <id>

# 列出所有PDK
python main.py pdk list

# 删除PDK
python main.py pdk delete --pdk-id <id>

# 更新PDK
python main.py pdk update --pdk-id <id> [--name <name>] [--version <version>] [--process <process>] [--vendor <vendor>] [--root-path <path>] [--drc-path <path>] [--lvs-path <path>] [--xrc-path <path>] [--spectre-path <path>] [--hspice-path <path>]
```

### 项目管理命令

```bash
# 创建项目
python main.py project create --name <name> [--description <description>]

# 配置项目成员
python main.py project members --project-id <id> --members <members_json>

# 配置项目目录
python main.py project directory --project-id <id> --path <path>

# 配置项目PDK目录
python main.py project pdk --project-id <id> --path <path>

# 配置项目库和单元
python main.py project libraries --project-id <id> --libraries <libraries_json>
```

## 高级功能

### 1. 自定义仿真流程

```python
from config import ConfigReader
from simulation_manager import SimulationManager

# 加载配置
reader = ConfigReader("my_task.yaml")
config = reader.load_task_config("my_task.yaml")

# 创建仿真管理器
manager = SimulationManager()
manager.load_simulation_configuration("my_task.yaml")

# 运行仿真任务
manager.run_simulation_task("my_task.yaml")
```

### 2. 批量仿真

```python
from pathlib import Path
from simulation_manager import SimulationManager

# 批量处理多个配置文件
config_files = Path("./tasks").glob("*.yaml")

for config_file in config_files:
    manager = SimulationManager()
    manager.load_simulation_configuration(str(config_file))
    manager.run_simulation_task(str(config_file))
```

### 3. 脚本生成和自定义

```python
from config import ConfigReader
from ocean_generator import OceanScriptGenerator

# 创建配置读取器
reader = ConfigReader("my_task.yaml")
config = reader.load_task_config("my_task.yaml")

# 生成脚本
generator = OceanScriptGenerator(config)
ocean_script = generator.generate_script()

# 保存脚本
generator.save_script("my_simulation.ocn")
```

## 支持的仿真器

- **Cadence Spectre**: 默认支持，推荐使用
- **Synopsys HSPICE**: 基本支持

## 支持的分析类型

- **瞬态分析 (tran)**: 时域仿真
- **DC 分析 (dc)**: 直流工作点和扫描
- **AC 分析 (ac)**: 交流小信号分析
- **噪声分析 (noise)**: 噪声分析
- **参数扫描**: 支持多参数扫描

## 故障排除

### 常见问题

1. **配置文件加载失败**

   - 检查文件路径是否正确
   - 确认文件格式符合 YAML 规范
   - 检查必要字段是否存在

2. **仿真器环境问题**

   - 确保仿真器已正确安装并设置环境变量
   - 检查 LICENSE 服务器是否正常
   - 验证设计文件和模型文件路径

3. **脚本生成错误**

   - 检查配置文件中的参数是否正确
   - 确认模板语法没有错误

4. **仿真执行失败**
   - 查看仿真日志文件了解详细错误信息
   - 检查设计文件语法是否正确
   - 确认仿真参数设置合理

### 调试模式

运行测试脚本检查各模块功能：

```bash
python test_demo.py
```

### 日志分析

仿真日志保存在工作目录的`logs`文件夹中，包含详细的执行信息和错误诊断。

## 扩展开发

### 添加新的仿真器支持

1. 在`simulator.py`中添加新仿真器的命令生成逻辑
2. 在`ocean_generator.py`中添加对应的脚本模板
3. 更新配置验证逻辑

### 添加新的分析类型

1. 在`ocean_generator.py`中添加新的分析模板
2. 更新配置文件格式说明
3. 添加相应的测试用例

### 自定义后处理

可以通过修改`post_processing`配置来自定义结果处理逻辑，支持：

- 自定义绘图
- 数据格式转换
- 结果文件整理

## 性能优化

- 使用适当的时间步长设置
- 合理设置仿真精度参数
- 并行运行多个仿真任务
- 使用快速模型进行初步验证

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进此项目。

## 联系方式

如果您有任何问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件到项目维护者

---

**注意**: 使用本工具前请确保您有合法的 EDA 工具 License，并且熟悉相关仿真器的使用方法。
