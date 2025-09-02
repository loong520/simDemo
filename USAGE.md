# 芯片仿真自动化Demo - 使用指南

## 快速开始

### 1. 环境设置
```bash
# 检查和安装依赖
python install.py

# 运行功能演示
python demo.py

# 运行功能测试
python test_demo.py
```

### 2. 基本使用

#### 交互式模式（推荐新手）
```bash
python main.py -i
```

#### 命令行模式
```bash
# 使用示例配置运行Ocean仿真
python main.py -c simulation_config.yaml -r ocean

# 使用示例配置运行Python仿真
python main.py -c simulation_config.yaml -r python

# 仅生成脚本不运行
python main.py -c simulation_config.yaml -g
```

## 配置文件详解

### YAML格式示例
```yaml
simulation:
  project_name: "my_amplifier"
  simulator: "spectre"
  design_path: "/path/to/your/netlist.scs"
  results_dir: "./sim_results"
  temperature: 27.0

models:
  files:
    - ["/path/to/models/design.scs", ""]
    - ["/path/to/models/process.scs", "tt"]

analyses:
  tran:
    stop: "10n"
    step: "1p"
  dc:
    saveOppoint: "t"

variables:
  vdd: 1.8
  load_cap: 100e-15

outputs:
  save_nodes:
    - "/vout"
    - "/vin"
```

### 关键配置项说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `design_path` | 电路设计netlist文件路径 | `/path/to/circuit.scs` |
| `simulator` | 仿真器类型 | `spectre`, `hspice`, `eldo` |
| `analyses` | 分析类型和参数 | `tran`, `dc`, `ac`, `noise` |
| `model_files` | 工艺模型文件 | `[文件路径, 工艺角]` |
| `save_nodes` | 需要保存的信号节点 | `/vout`, `/vin` |

## 输出文件说明

运行仿真后会生成以下文件：

```
sim_work/
├── scripts/
│   ├── project_name.ocn           # 生成的Ocean脚本
│   └── project_name_skillbridge.py # 生成的Python脚本
├── results/
│   ├── *.log                      # 仿真日志
│   ├── *.raw                      # 原始数据文件
│   └── *.png                      # 生成的波形图
└── logs/
    └── simulation_*.log           # 系统日志
```

## 高级功能

### 1. 批量仿真
```python
from pathlib import Path
from main import SimulationManager

# 处理多个配置文件
for config_file in Path("configs").glob("*.yaml"):
    manager = SimulationManager(str(config_file))
    manager.run_simulation("ocean")
```

### 2. 自定义脚本生成
```python
from config import SimulationConfig
from ocean_generator import OceanScriptGenerator

config = SimulationConfig(
    project_name="custom_sim",
    simulator="spectre",
    # ... 其他参数
)

generator = OceanScriptGenerator(config)
script = generator.generate_script()
```

### 3. Python API使用
```python
from config import load_config
from simulator import run_simulation

# 加载配置并运行仿真
config = load_config("my_config.yaml")
success, results = run_simulation(config, "ocean")

if success:
    print("仿真成功！")
    print(f"结果文件: {results['files']}")
```

## 故障排除

### 常见错误及解决方案

1. **模块导入错误**
   ```
   ModuleNotFoundError: No module named 'yaml'
   ```
   解决: `python install.py` 或 `pip install pyyaml`

2. **配置文件格式错误**
   ```
   配置文件解析错误: ...
   ```
   解决: 检查YAML语法，确保缩进正确

3. **设计文件路径错误**
   ```
   设计文件不存在: /path/to/design
   ```
   解决: 检查配置文件中的路径是否正确

4. **仿真器环境问题**
   ```
   仿真器环境检查失败
   ```
   解决: 确保Cadence等仿真工具已正确安装并设置环境变量

### 调试技巧

1. **查看详细日志**
   ```bash
   # 日志文件位置
   ./sim_work/logs/simulation_*.log
   ```

2. **测试配置文件**
   ```bash
   python -c "from config import load_config; print(load_config('your_config.yaml'))"
   ```

3. **单独测试脚本生成**
   ```bash
   python main.py -c your_config.yaml -g
   ```

## 扩展开发

### 添加新仿真器支持

1. 在 `simulator.py` 中添加新仿真器命令：
```python
if simulator == 'your_simulator':
    cmd = ['your_simulator', '-args', self.ocean_script_path]
```

2. 在 `ocean_generator.py` 中添加对应模板

### 自定义分析类型

1. 在配置文件中定义新分析：
```yaml
analyses:
  custom_analysis:
    param1: value1
    param2: value2
```

2. 在 `ocean_generator.py` 中添加对应模板

### 后处理扩展

可以在 `post_processing` 配置中定义：
- 自定义绘图参数
- 数据导出格式
- 结果文件处理逻辑

## 最佳实践

1. **配置管理**
   - 为不同的项目创建单独的配置文件
   - 使用版本控制管理配置文件
   - 定期备份重要的仿真配置

2. **性能优化**
   - 合理设置时间步长
   - 选择适当的仿真精度
   - 使用快速模型进行初步验证

3. **结果管理**
   - 定期清理临时文件
   - 归档重要的仿真结果
   - 使用描述性的项目名称

4. **脚本维护**
   - 定期更新模型文件路径
   - 验证生成的脚本语法
   - 记录重要的仿真参数变更

## 技术支持

遇到问题时可以：

1. 运行 `python test_demo.py` 检查系统状态
2. 运行 `python demo.py` 查看功能演示
3. 查看日志文件了解详细错误信息
4. 检查配置文件格式和参数设置

---

**注意**: 本工具需要合法的EDA工具许可证才能进行实际仿真。