# Ocean脚本模板系统

## 概述

这个目录包含了Ocean脚本生成器使用的Jinja2模板文件。模板被组织成不同的类别，以便于维护和扩展。

## 目录结构

```
templates/
├── ocean/          # Ocean脚本模板
│   ├── header.ocean              # 脚本头部注释
│   ├── simulator.ocean           # 仿真器配置
│   ├── design.ocean             # 设计文件配置
│   ├── results_dir.ocean        # 结果目录配置
│   ├── model_file.ocean         # 模型文件加载
│   ├── stimulus.ocean           # 激励文件加载
│   ├── design_variables.ocean   # 设计变量配置
│   ├── analysis_*.ocean         # 各类分析配置模板
│   ├── save_nodes.ocean         # 节点保存配置
│   ├── initial_conditions.ocean # 初始条件设置
│   ├── environment.ocean        # 环境配置
│   ├── run.ocean                # 运行命令
│   ├── post_processing.ocean    # 后处理脚本
│   └── netlist_generation.ocean # 网表生成脚本
└── shell/          # Shell脚本模板
    ├── main_script.sh           # 主要仿真执行脚本
    └── batch_script.sh          # 批量执行脚本
```

## 模板使用说明

### Ocean模板

每个Ocean模板文件对应Ocean脚本的一个功能模块：

- **header.ocean**: 生成脚本头部注释，包含项目信息
- **simulator.ocean**: 配置使用的仿真器（Spectre、HSPICE等）
- **design.ocean**: 设置设计网表路径
- **results_dir.ocean**: 设置仿真结果存储目录
- **model_file.ocean**: 加载工艺模型文件
- **stimulus.ocean**: 加载激励文件
- **design_variables.ocean**: 设置设计参数变量
- **analysis_*.ocean**: 不同分析类型的配置模板
  - `analysis_dc.ocean`: DC分析
  - `analysis_ac.ocean`: AC分析  
  - `analysis_tran.ocean`: 瞬态分析
  - `analysis_noise.ocean`: 噪声分析
- **save_nodes.ocean**: 配置需要保存的节点
- **initial_conditions.ocean**: 设置初始条件
- **environment.ocean**: 配置仿真环境（温度等）
- **run.ocean**: 执行仿真命令
- **post_processing.ocean**: 后处理和数据提取
- **netlist_generation.ocean**: 网表生成配置

### Shell模板

- **main_script.sh**: 生成主要的Shell执行脚本，包含环境变量设置和仿真执行
- **batch_script.sh**: 生成批量执行Shell脚本

## 模板变量

模板使用Jinja2语法，常用变量包括：

- `project_name`: 项目名称
- `simulator`: 仿真器名称
- `design_path`: 设计网表路径
- `results_dir`: 结果目录
- `model_files`: 模型文件列表
- `stimulus_files`: 激励文件列表
- `design_variables`: 设计变量字典
- `analyses`: 分析配置字典
- `save_nodes`: 保存节点列表
- `initial_conditions`: 初始条件字典
- `temperature`: 仿真温度

## 添加新模板

要添加新的模板文件：

1. 在相应目录下创建新的模板文件
2. 使用Jinja2语法编写模板内容
3. 在`OceanScriptGenerator`类中添加相应的加载和使用逻辑

## 模板示例

```jinja2
; 设置仿真器
simulator( '{{ simulator }} )
```

```jinja2
; 设置设计变量
{% for var_name, var_value in design_variables.items() %}
desVar( "{{ var_name }}" {{ var_value }} )
{% endfor %}
```

## 优势

使用独立的模板文件相比硬编码在代码中的优势：

1. **可维护性**: 模板和业务逻辑分离，更易维护
2. **可读性**: 模板文件更直观，易于理解和修改
3. **扩展性**: 添加新模板无需修改核心代码
4. **复用性**: 模板可以被多个生成器共享
5. **版本控制**: 模板变更可以独立跟踪