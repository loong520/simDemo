# 芯片仿真自动化Demo

一个基于Python的芯片模拟仿真自动化工具，支持从配置文件读取仿真参数，自动生成Ocean脚本和Python脚本，并执行Cadence Spectre等仿真器进行芯片电路仿真。

## 功能特性

- 📋 **配置文件驱动**: 支持YAML格式的配置文件
- 🔧 **多仿真器支持**: 支持Spectre、HSPICE、Eldo等主流仿真器
- 📜 **自动脚本生成**: 生成标准Ocean脚本和Python skillbridge脚本
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
├── simulator.py                 # 仿真执行器
├── test_demo.py                 # 功能测试脚本
├── requirements.txt             # Python依赖包
├── simulation_config.yaml       # YAML配置文件示例
└── README.md                    # 项目说明文档
```

## 安装依赖

首先确保您的系统已安装Python 3.7+，然后安装必要的依赖包：

```bash
pip install -r requirements.txt
```

主要依赖包：
- `pyyaml`: YAML配置文件解析
- `jinja2`: 模板引擎，用于生成脚本
- `numpy`: 数值计算
- `pandas`: 数据处理
- `matplotlib`: 绘图

## 快速开始

### 1. 准备配置文件

复制并修改示例配置文件：

```bash
cp simulation_config.yaml my_simulation.yaml
```

编辑配置文件，修改以下关键参数：
- `design_path`: 您的电路设计netlist路径
- `model_files`: 工艺模型文件路径
- `analyses`: 需要运行的分析类型
- `save_nodes`: 需要保存的信号节点

### 2. 运行仿真

#### 命令行模式

```bash
# 交互式模式
python main.py -c my_simulation.yaml

# 仅生成脚本
python main.py -c my_simulation.yaml -g

# 运行Ocean仿真
python main.py -c my_simulation.yaml -r ocean
```

#### 交互式模式

```bash
python main.py -i
```

然后按照提示选择操作。

### 3. 查看结果

仿真完成后，结果将保存在配置文件中指定的`results_dir`目录中。

## 配置文件说明

### YAML格式配置文件

```yaml
# 基本仿真配置
simulation:
  project_name: "my_project"           # 项目名称
  simulator: "spectre"                 # 仿真器类型
  design_path: "/path/to/netlist"      # 设计文件路径
  results_dir: "./results"             # 结果目录
  temperature: 27.0                    # 仿真温度
  supply_voltage: 1.8                  # 电源电压

# 模型文件
models:
  files:
    - ["/path/to/model1.scs", ""]      # [文件路径, 工艺角]
    - ["/path/to/model2.scs", "tt"]

# 分析类型
analyses:
  tran:                                # 瞬态分析
    stop: "10n"                        # 停止时间
    step: "1p"                         # 时间步长
  dc:                                  # DC分析
    saveOppoint: "t"                   # 保存工作点

# 设计变量
variables:
  vdd: 1.8
  temp_coeff: 1e-3

# 保存节点
outputs:
  save_nodes:
    - "/vout"
    - "/vin"

# 初始条件
initial_conditions:
  "/vout": 0.9
```

## 高级功能

### 1. 自定义仿真流程

```python
from config import load_config
from simulator import SimulationExecutor

# 加载配置
config = load_config("my_config.yaml")

# 创建执行器
executor = SimulationExecutor(config, "./my_work_dir")

# 准备仿真
executor.prepare_simulation()

# 运行Ocean仿真
success, output = executor.run_ocean_simulation()

# 收集结果
results = executor.collect_results()
```

### 2. 批量仿真

```python
from pathlib import Path
from main import SimulationManager

# 批量处理多个配置文件
config_files = Path("./configs").glob("*.yaml")

for config_file in config_files:
    manager = SimulationManager(str(config_file))
    manager.run_simulation("ocean")
```

### 3. 脚本生成和自定义

```python
from config import SimulationConfig
from ocean_generator import OceanScriptGenerator

# 创建配置
config = SimulationConfig(
    project_name="custom_sim",
    simulator="spectre",
    # ... 其他参数
)

# 生成脚本
generator = OceanScriptGenerator(config)
ocean_script = generator.generate_script()

# 保存脚本
generator.save_script("my_simulation.ocn")
```

## 支持的仿真器

- **Cadence Spectre**: 默认支持，推荐使用
- **Synopsys HSPICE**: 基本支持
- **Mentor Eldo**: 基本支持

## 支持的分析类型

- **瞬态分析 (tran)**: 时域仿真
- **DC分析 (dc)**: 直流工作点和扫描
- **AC分析 (ac)**: 交流小信号分析
- **噪声分析 (noise)**: 噪声分析
- **参数扫描**: 支持多参数扫描

## 故障排除

### 常见问题

1. **配置文件加载失败**
   - 检查文件路径是否正确
   - 确认文件格式符合YAML规范
   - 检查必要字段是否存在

2. **仿真器环境问题**
   - 确保仿真器已正确安装并设置环境变量
   - 检查LICENSE服务器是否正常
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

欢迎提交Issue和Pull Request来改进此项目。

## 联系方式

如果您有任何问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件到项目维护者

---

**注意**: 使用本工具前请确保您有合法的EDA工具License，并且熟悉相关仿真器的使用方法。