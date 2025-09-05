# EDA工具管理功能使用说明

## 功能概述

本工具集成了EDA工具管理功能，可以通过命令行调用后台Java服务的REST API接口，实现EDA工具的全生命周期管理。

## 可用的EDA工具管理命令

1. **工具创建** - create
2. **工具查询** - get
3. **工具列表** - list
4. **工具删除** - delete
5. **工具更新** - update

## 配置文件设置

服务器的URL配置在仿真配置文件中，无需在命令行中手动指定。工具会自动使用当前目录下的`simulation_config.yaml`文件。

在配置文件中添加以下配置：

```yaml
# 服务器配置
server:
  url: "http://localhost:8080" # 服务器URL
  api_key: "" # API密钥（可选）
```

## 使用方法

### 1. EDA工具创建

```bash
python main.py eda-tool create --name "Spectre" --version "19.1" --launch-command "/tools/spectre/bin/spectre" --vendor "Cadence" --env-var "PATH=/tools/spectre/bin" --env-var "LM_LICENSE_FILE=27000@license.server"
```

### 2. EDA工具查询

```bash
python main.py eda-tool get --tool-id "tool-12345"
```

### 3. EDA工具列表

```bash
python main.py eda-tool list
```

### 4. EDA工具删除

```bash
python main.py eda-tool delete --tool-id "tool-12345"
```

### 5. EDA工具更新

```bash
python main.py eda-tool update --tool-id "tool-12345" --version "20.1" --env-var "PATH=/tools/spectre/bin" --env-var "LM_LICENSE_FILE=27000@new-license.server"
```

## 注意事项

1. EDA工具管理功能需要后台Java服务支持相应的REST API接口
2. 工具会自动使用当前目录下的`simulation_config.yaml`配置文件
3. 服务器URL必须在配置文件中正确配置
4. 某些操作可能需要认证，可以通过配置文件提供API密钥
5. EDA工具管理功能与项目管理、仿真功能可以独立使用，互不影响

## API接口要求

后台Java服务需要提供以下REST API接口：

- `POST /api/eda-tools` - 创建EDA工具
- `GET /api/eda-tools` - 列出所有EDA工具
- `GET /api/eda-tools/{toolId}` - 获取EDA工具信息
- `PUT /api/eda-tools/{toolId}` - 更新EDA工具信息
- `DELETE /api/eda-tools/{toolId}` - 删除EDA工具