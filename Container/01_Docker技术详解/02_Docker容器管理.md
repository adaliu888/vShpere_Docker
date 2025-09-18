# Docker容器管理

## 目录

- [Docker容器管理](#docker容器管理)
  - [目录](#目录)
  - [1. 基本操作与生命周期](#1-基本操作与生命周期)
  - [2. 健康检查与重启策略](#2-健康检查与重启策略)
  - [3. 资源限制与隔离](#3-资源限制与隔离)
  - [4. 日志与调试](#4-日志与调试)
  - [5. 与 Compose V2 协同](#5-与-compose-v2-协同)
  - [6. 实践清单与 FAQ](#6-实践清单与-faq)

## 1. 基本操作与生命周期

- run/start/stop/restart/rm/pause/unpause/exec/cp
- 状态机：created → running → paused → exited → dead

## 2. 健康检查与重启策略

- HEALTHCHECK 指令与 `--health-*` 参数
- `--restart` 策略：no/always/on-failure/unless-stopped

## 3. 资源限制与隔离

- CPU/内存/IO/PIDs/ulimits；cgroups v2 注意事项
- 用户/能力（capabilities）与 seccomp

## 4. 日志与调试

- `docker logs/-f`、`inspect`、`events`、进入容器排障
- 日志驱动与收集建议（与 监控/日志 章节互引）

## 5. 与 Compose V2 协同

- `docker compose up -d` 基础；依赖、健康检查、扩缩容
- 环境分层与多文件合并

## 6. 实践清单与 FAQ

- 最小可用运行参数模板
- 常见问题：时区/编码/权限/时钟漂移/容器退出码

（待补充：实验示例与命令速查表）
