# Nonebot Plugin Pipe

基于 [NoneBot2](https://github.com/nonebot/nonebot2) 的 OneBot V12 会话转接插件

[![License](https://img.shields.io/github/license/nonepkg/nonebot-plugin-pipe?style=flat-square)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)
![NoneBot Version](https://img.shields.io/badge/nonebot-2.3.0+-red.svg?style=flat-square)
[![PyPI Version](https://img.shields.io/pypi/v/nonebot-plugin-pipe.svg?style=flat-square)](https://pypi.python.org/pypi/nonebot-plugin-pipe)

![截图](./docs/screenshot.jpg)

## 安装

<!--
### 从 PyPI 安装（推荐）

- 使用 nb-cli  

```sh
nb plugin install nonebot-plugin-pipe
```

- 使用 pdm

```sh
pdm add nonebot-plugin-pipe
```

-->
### 从 GitHub 安装（不推荐）

```sh
pdm add git+https://github.com/nonepkg/nonebot-plugin-pipe
```

## 使用

> [!NOTE]
> 本插件使用 [he0119/nonebot-plugin-user](https://github.com/he0119/nonebot-plugin-user) 用于多平台账号绑定与获取统一用户名。

### /pipe

目前可用的命令：new/delete, link/unlink, list, show

README 中截图所示，你需要先使用 new 命令创建管道，再使用 link 将当前会话连接到该管道，且连接会话时需要 SUPERUSER 在该会话内。

### /at

可使用 User 插件设置的用户名或 `{platform}-{id}` 格式来 @ 他人，方便 @ 其他平台的用户。
