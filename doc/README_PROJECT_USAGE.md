# 项目管理功能使用说明

## 功能概述

本工具集成了项目管理功能，可以通过命令行调用后台Java服务的REST API接口，实现芯片设计项目的全生命周期管理。

## 可用的项目管理命令

1. **项目创建** - create
2. **项目成员角色配置** - members
3. **项目所在目录配置** - directory
4. **项目使用的PDK目录配置** - pdk
5. **项目中Library和Cell配置** - libraries
6. **项目各阶段EDA工具配置** - eda
7. **查询项目信息** - get
8. **列出所有项目** - list
9. **删除项目** - delete

## 配置文件设置

服务器的URL现在配置在仿真配置文件中，无需在命令行中手动指定。工具会自动使用当前目录下的`simulation_config.yaml`文件。

在配置文件中添加以下配置：

```yaml
# 服务器配置
server:
  url: "http://localhost:8080" # 服务器URL
  api_key: "" # API密钥（可选）
```

## 使用方法

### 1. 项目创建

```bash
python main.py project create --name "MyProject" --description "My project description" --owner "user1"
```

### 2. 项目成员角色配置

```bash
python main.py project members --project-id "project-12345" --members '[{"userId": "user1", "role": "admin"}, {"userId": "user2", "role": "member"}]'
```

### 3. 项目所在目录配置

```bash
python main.py project directory --project-id "project-12345" --path "/path/to/project/directory"
```

### 4. 项目使用的PDK目录配置

```bash
python main.py project pdk --project-id "project-12345" --path "/path/to/pdk/directory"
```

### 5. 项目中Library和Cell配置

```bash
python main.py project libraries --project-id "project-12345" --libraries '[{"name": "lib1", "cells": ["cell1", "cell2"]}, {"name": "lib2", "cells": ["cell3"]}]'
```

### 6. 项目各阶段EDA工具配置

```bash
python main.py project eda --project-id "project-12345" --config '{"circuitDesign": "tool1", "preSim": "tool2", "layout": "tool3", "physicalVerification": "tool4", "extraction": "tool5", "postSim": "tool6"}'
```

### 7. 查询项目信息

```bash
python main.py project get --project-id "project-12345"
```

### 8. 列出所有项目

```bash
python main.py project list
```

### 9. 删除项目

```bash
python main.py project delete --project-id "project-12345"
```

## 注意事项

1. 项目管理功能需要后台Java服务支持相应的REST API接口
2. 工具会自动使用当前目录下的`simulation_config.yaml`配置文件
3. 服务器URL必须在配置文件中正确配置
4. 某些操作可能需要认证，可以通过配置文件提供API密钥
5. 项目管理功能与仿真功能可以独立使用，互不影响

## API接口要求

后台Java服务需要提供以下REST API接口：

- `POST /api/projects` - 创建项目
- `GET /api/projects` - 列出所有项目
- `GET /api/projects/{projectId}` - 获取项目信息
- `DELETE /api/projects/{projectId}` - 删除项目
- `PUT /api/projects/{projectId}/members` - 配置项目成员
- `PUT /api/projects/{projectId}/directory` - 配置项目目录
- `PUT /api/projects/{projectId}/pdk` - 配置PDK目录
- `PUT /api/projects/{projectId}/libraries` - 配置库和单元
- `PUT /api/projects/{projectId}/eda-tools` - 配置EDA工具