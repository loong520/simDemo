# PDK管理功能使用说明

## 功能概述

本工具集成了PDK管理功能，可以通过命令行调用后台Java服务的REST API接口，实现PDK的全生命周期管理。

## 可用的PDK管理命令

1. **PDK创建** - create
2. **PDK查询** - get
3. **PDK列表** - list
4. **PDK删除** - delete
5. **PDK更新** - update

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

### 1. PDK创建

```bash
python3 main.py pdk create --name "TSMC_N16" --version "1.0" --process "N16" --vendor "TSMC" --root-path "/pdk/tsmc/N16" --drc-path "/pdk/tsmc/N16/drc" --lvs-path "/pdk/tsmc/N16/lvs" --xrc-path "/pdk/tsmc/N16/xrc" --spectre-path "/pdk/tsmc/N16/spectre" --hspice-path "/pdk/tsmc/N16/hspice"
```

### 2. PDK查询

```bash
python3 main.py pdk get --pdk-id "pdk-12345"
```

### 3. PDK列表

```bash
python3 main.py pdk list
```

### 4. PDK删除

```bash
python3 main.py pdk delete --pdk-id "pdk-12345"
```

### 5. PDK更新

```bash
python3 main.py pdk update --pdk-id "pdk-12345" --version "2.0" --drc-path "/pdk/tsmc/N16/drc_v2"
```

## 注意事项

1. PDK管理功能需要后台Java服务支持相应的REST API接口
2. 工具会自动使用当前目录下的`simulation_config.yaml`配置文件
3. 服务器URL必须在配置文件中正确配置
4. 某些操作可能需要认证，可以通过配置文件提供API密钥
5. PDK管理功能与项目管理、仿真功能可以独立使用，互不影响

## API接口要求

后台Java服务需要提供以下REST API接口：

- `POST /api/pdks` - 创建PDK
- `GET /api/pdks` - 列出所有PDK
- `GET /api/pdks/{pdkId}` - 获取PDK信息
- `PUT /api/pdks/{pdkId}` - 更新PDK信息
- `DELETE /api/pdks/{pdkId}` - 删除PDK