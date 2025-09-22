# Docker架构原理深度解析

## 目录

- [Docker架构原理深度解析](#docker架构原理深度解析)
  - [1. Docker技术概述](#1-docker技术概述)
    - [1.1 Docker定义与特性](#11-docker定义与特性)
      - [1.1.1 核心特性](#111-核心特性)
    - [1.2 Docker技术优势](#12-docker技术优势)
      - [1.2.1 与传统虚拟化对比](#121-与传统虚拟化对比)
      - [1.2.2 与物理机对比](#122-与物理机对比)
  - [2. Docker架构设计](#2-docker架构设计)
    - [2.1 整体架构](#21-整体架构)
    - [2.2 核心组件](#22-核心组件)
      - [2.2.1 Docker Client](#221-docker-client)
      - [2.2.2 Docker Daemon](#222-docker-daemon)
      - [2.2.3 Docker Registry](#223-docker-registry)
  - [3. Docker核心技术](#3-docker核心技术)
    - [3.1 Linux容器技术](#31-linux容器技术)
      - [3.1.1 Namespaces（命名空间）](#311-namespaces命名空间)
      - [3.1.2 Control Groups（cgroups）](#312-control-groupscgroups)
      - [3.1.3 Union File System（联合文件系统）](#313-union-file-system联合文件系统)
    - [3.2 Docker镜像技术](#32-docker镜像技术)
      - [3.2.1 镜像结构](#321-镜像结构)
      - [3.2.2 镜像构建](#322-镜像构建)
    - [3.3 Docker容器技术](#33-docker容器技术)
      - [3.3.1 容器生命周期](#331-容器生命周期)
      - [3.3.2 容器状态管理](#332-容器状态管理)
  - [4. Docker网络架构](#4-docker网络架构)
    - [4.1 网络模式](#41-网络模式)
      - [4.1.1 Bridge网络（默认）](#411-bridge网络默认)
      - [4.1.2 Host网络](#412-host网络)
      - [4.1.3 None网络](#413-none网络)
      - [4.1.4 Overlay网络](#414-overlay网络)
    - [4.2 网络组件](#42-网络组件)
      - [4.2.1 Docker网桥](#421-docker网桥)
      - [4.2.2 端口映射](#422-端口映射)
  - [5. Docker存储架构](#5-docker存储架构)
    - [5.1 存储驱动](#51-存储驱动)
      - [5.1.1 Overlay2（推荐）](#511-overlay2推荐)
      - [5.1.2 Device Mapper](#512-device-mapper)
      - [5.1.3 Btrfs](#513-btrfs)
    - [5.2 数据卷管理](#52-数据卷管理)
      - [5.2.1 数据卷（Volume）](#521-数据卷volume)
      - [5.2.2 绑定挂载（Bind Mount）](#522-绑定挂载bind-mount)
      - [5.2.3 tmpfs挂载](#523-tmpfs挂载)
  - [6. Docker安全架构](#6-docker安全架构)
    - [6.1 安全机制](#61-安全机制)
      - [6.1.1 容器隔离](#611-容器隔离)
      - [6.1.2 权限控制](#612-权限控制)
      - [6.1.3 镜像安全](#613-镜像安全)
    - [6.2 安全最佳实践](#62-安全最佳实践)
      - [6.2.1 镜像安全](#621-镜像安全)
      - [6.2.2 运行时安全](#622-运行时安全)
      - [6.2.3 网络安全](#623-网络安全)
  - [7. Docker性能优化](#7-docker性能优化)
    - [7.1 资源优化](#71-资源优化)
      - [7.1.1 CPU优化](#711-cpu优化)
      - [7.1.2 内存优化](#712-内存优化)
      - [7.1.3 I/O优化](#713-io优化)
    - [7.2 网络优化](#72-网络优化)
      - [7.2.1 网络性能](#721-网络性能)
      - [7.2.2 网络安全](#722-网络安全)
  - [8. Docker监控与日志](#8-docker监控与日志)
    - [8.1 监控技术](#81-监控技术)
      - [8.1.1 容器监控](#811-容器监控)
      - [8.1.2 监控工具](#812-监控工具)
    - [8.2 日志管理](#82-日志管理)
      - [8.2.1 日志类型](#821-日志类型)
      - [8.2.2 日志处理](#822-日志处理)
  - [9. Docker快速上手](#9-docker快速上手)
    - [9.1 安装与环境](#91-安装与环境)
    - [9.2 第一个容器](#92-第一个容器)
    - [9.3 镜像与数据卷](#93-镜像与数据卷)
  - [10. Docker命令速查](#10-docker命令速查)
    - [10.1 容器管理](#101-容器管理)
    - [10.2 镜像管理](#102-镜像管理)
    - [10.3 网络与存储](#103-网络与存储)
  - [11. Rootless 实操](#11-rootless-实操)
    - [11.1 前置条件](#111-前置条件)
    - [11.2 启用与验证](#112-启用与验证)
    - [11.3 常见问题](#113-常见问题)
  - [12. 故障诊断指南](#12-故障诊断指南)
    - [12.1 常见症状与排查路径](#121-常见症状与排查路径)
    - [12.2 网络问题定位](#122-网络问题定位)
    - [12.3 存储与权限问题](#123-存储与权限问题)
  - [13. FAQ](#13-faq)
  - [14. Docker发展趋势](#14-docker发展趋势)
    - [9.1 技术发展趋势](#91-技术发展趋势)
      - [9.1.1 容器技术演进](#911-容器技术演进)
      - [9.1.2 生态系统发展](#912-生态系统发展)
    - [9.2 应用场景扩展](#92-应用场景扩展)
      - [9.2.1 传统应用容器化](#921-传统应用容器化)
      - [9.2.2 新兴应用场景](#922-新兴应用场景)
  - [15. 总结](#15-总结)
  - [16. 版本差异与兼容说明（对齐至 2025）](#16-版本差异与兼容说明对齐至-2025)
  - [17. 安全基线与 Rootless 实践要点](#17-安全基线与-rootless-实践要点)
  - [18. BuildKit 与镜像构建优化](#18-buildkit-与镜像构建优化)
  - [19. 与 containerd/CRI 的关系与选型](#19-与-containerdcri-的关系与选型)
  - [20. 参考资料与链接](#20-参考资料与链接)

## 1. Docker技术概述

### 1.1 Docker定义与特性

Docker是一个开源的容器化平台，基于Linux容器（LXC）技术，通过操作系统级虚拟化实现应用程序的打包、分发和运行。

#### 1.1.1 核心特性

- **轻量级**: 基于操作系统级虚拟化，资源开销小
- **可移植性**: 一次构建，到处运行
- **一致性**: 开发、测试、生产环境完全一致
- **可扩展性**: 支持水平扩展和垂直扩展
- **隔离性**: 容器间相互隔离，互不影响

### 1.2 Docker技术优势

#### 1.2.1 与传统虚拟化对比

| 特性 | 传统虚拟化 | Docker容器化 |
|------|------------|--------------|
| 资源开销 | 高（每个VM需要完整OS） | 低（共享宿主机OS） |
| 启动时间 | 分钟级 | 秒级 |
| 资源利用率 | 低 | 高 |
| 隔离性 | 强 | 中等 |
| 可移植性 | 差 | 优秀 |

#### 1.2.2 与物理机对比

| 特性 | 物理机 | Docker容器 |
|------|--------|------------|
| 资源隔离 | 无 | 有 |
| 部署效率 | 低 | 高 |
| 资源利用率 | 低 | 高 |
| 管理复杂度 | 高 | 低 |
| 成本 | 高 | 低 |

## 2. Docker架构设计

### 2.1 整体架构

```text
┌─────────────────────────────────────────────────────────────┐
│                    Docker Client                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Docker    │  │   Docker    │  │   Docker    │         │
│  │   CLI       │  │   API       │  │   Compose   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Docker Daemon                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Registry  │  │   Images    │  │  Containers │         │
│  │   Service   │  │   Manager   │  │   Manager   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Network   │  │   Volume    │  │   Security  │         │
│  │   Manager   │  │   Manager   │  │   Manager   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ System Calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Host Operating System                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Linux     │  │   cgroups   │  │   namespaces│         │
│  │   Kernel    │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 Docker Client

- **功能**: 用户与Docker交互的接口
- **实现**: Docker CLI命令行工具
- **通信**: 通过REST API与Docker Daemon通信

#### 2.2.2 Docker Daemon

- **功能**: Docker的核心服务，管理容器生命周期
- **组件**:
  - Registry Service: 镜像仓库服务
  - Images Manager: 镜像管理器
  - Containers Manager: 容器管理器
  - Network Manager: 网络管理器
  - Volume Manager: 存储卷管理器
  - Security Manager: 安全管理器

#### 2.2.3 Docker Registry

- **功能**: 存储和分发Docker镜像
- **类型**:
  - Docker Hub: 官方公共仓库
  - 私有仓库: 企业内部仓库
  - 第三方仓库: 其他云服务商仓库

## 3. Docker核心技术

### 3.1 Linux容器技术

#### 3.1.1 Namespaces（命名空间）

提供进程隔离，每个容器拥有独立的命名空间：

- **PID Namespace**: 进程ID隔离
- **Network Namespace**: 网络隔离
- **Mount Namespace**: 文件系统隔离
- **UTS Namespace**: 主机名隔离
- **IPC Namespace**: 进程间通信隔离
- **User Namespace**: 用户ID隔离

#### 3.1.2 Control Groups（cgroups）

提供资源限制和统计：

- **CPU限制**: 限制CPU使用率
- **内存限制**: 限制内存使用量
- **I/O限制**: 限制磁盘I/O
- **网络限制**: 限制网络带宽

#### 3.1.3 Union File System（联合文件系统）

实现镜像的分层存储：

- **分层结构**: 镜像由多个只读层组成
- **写时复制**: 容器层可写，底层只读
- **存储效率**: 多个容器共享基础层

### 3.2 Docker镜像技术

#### 3.2.1 镜像结构

```text
┌─────────────────────────────────────┐
│            Container Layer          │ ← 可写层
├─────────────────────────────────────┤
│            Application Layer        │ ← 应用层
├─────────────────────────────────────┤
│            Runtime Layer            │ ← 运行时层
├─────────────────────────────────────┤
│            OS Layer                 │ ← 操作系统层
└─────────────────────────────────────┘
```

#### 3.2.2 镜像构建

- **Dockerfile**: 镜像构建脚本
- **构建上下文**: 构建时的文件系统
- **构建缓存**: 提高构建效率
- **多阶段构建**: 优化镜像大小

### 3.3 Docker容器技术

#### 3.3.1 容器生命周期

```text
创建 → 启动 → 运行 → 停止 → 删除
  ↑      ↑      ↑      ↑      ↑
  │      │      │      │      │
  │      │      │      │      └─ docker rm
  │      │      │      └─ docker stop
  │      │      └─ docker start
  │      └─ docker run
  └─ docker create
```

#### 3.3.2 容器状态管理

- **Created**: 容器已创建但未启动
- **Running**: 容器正在运行
- **Paused**: 容器已暂停
- **Restarting**: 容器正在重启
- **Removing**: 容器正在删除
- **Exited**: 容器已退出
- **Dead**: 容器已死亡

## 4. Docker网络架构

### 4.1 网络模式

#### 4.1.1 Bridge网络（默认）

- **特点**: 容器通过网桥与宿主机通信
- **适用场景**: 单机容器通信
- **网络隔离**: 容器间相互隔离

#### 4.1.2 Host网络

- **特点**: 容器直接使用宿主机网络
- **适用场景**: 高性能网络应用
- **网络隔离**: 无网络隔离

#### 4.1.3 None网络

- **特点**: 容器无网络接口
- **适用场景**: 特殊安全要求
- **网络隔离**: 完全网络隔离

#### 4.1.4 Overlay网络

- **特点**: 跨主机容器通信
- **适用场景**: 分布式应用
- **网络隔离**: 基于VXLAN技术

### 4.2 网络组件

#### 4.2.1 Docker网桥

- **功能**: 连接容器与宿主机网络
- **实现**: Linux bridge
- **配置**: 可自定义网段和网关

#### 4.2.2 端口映射

- **功能**: 将容器端口映射到宿主机端口
- **实现**: iptables规则
- **配置**: -p参数指定端口映射

## 5. Docker存储架构

### 5.1 存储驱动

#### 5.1.1 Overlay2（推荐）

- **特点**: 性能优秀，支持多级目录
- **适用场景**: 生产环境
- **限制**: 需要Linux 4.0+内核

#### 5.1.2 Device Mapper

- **特点**: 基于块设备
- **适用场景**: 企业级存储
- **限制**: 需要LVM支持

#### 5.1.3 Btrfs

- **特点**: 支持快照和压缩
- **适用场景**: 开发环境
- **限制**: 需要Btrfs文件系统

### 5.2 数据卷管理

#### 5.2.1 数据卷（Volume）

- **特点**: 由Docker管理
- **优势**: 可备份、可迁移
- **使用**: docker volume create

#### 5.2.2 绑定挂载（Bind Mount）

- **特点**: 直接挂载宿主机目录
- **优势**: 性能好，易于访问
- **使用**: -v /host/path:/container/path

#### 5.2.3 tmpfs挂载

- **特点**: 内存文件系统
- **优势**: 高性能，临时存储
- **使用**: --tmpfs参数

## 6. Docker安全架构

### 6.1 安全机制

#### 6.1.1 容器隔离

- **进程隔离**: Namespaces提供进程隔离
- **资源隔离**: cgroups提供资源隔离
- **文件系统隔离**: 联合文件系统提供文件隔离

#### 6.1.2 权限控制

- **用户权限**: 支持非root用户运行
- **能力控制**: 限制容器系统调用
- **SELinux/AppArmor**: 强制访问控制

#### 6.1.3 镜像安全

- **镜像签名**: 验证镜像完整性
- **漏洞扫描**: 检测镜像安全漏洞
- **最小化镜像**: 减少攻击面

### 6.2 安全最佳实践

#### 6.2.1 镜像安全

- 使用官方基础镜像
- 定期更新镜像
- 扫描镜像漏洞
- 使用最小化镜像

#### 6.2.2 运行时安全

- 以非root用户运行
- 限制容器权限
- 使用只读文件系统
- 启用安全策略

#### 6.2.3 网络安全

- 使用网络隔离
- 限制端口暴露
- 使用TLS加密
- 实施网络策略

## 7. Docker性能优化

### 7.1 资源优化

#### 7.1.1 CPU优化

- 合理设置CPU限制
- 使用CPU亲和性
- 优化应用代码
- 使用多核处理

#### 7.1.2 内存优化

- 合理设置内存限制
- 使用内存压缩
- 优化应用内存使用
- 监控内存泄漏

#### 7.1.3 I/O优化

- 使用SSD存储
- 优化存储驱动
- 使用数据卷
- 减少磁盘I/O

### 7.2 网络优化

#### 7.2.1 网络性能

- 使用host网络模式
- 优化网络配置
- 使用高速网络
- 减少网络延迟

#### 7.2.2 网络安全

- 使用网络隔离
- 实施访问控制
- 使用加密通信
- 监控网络流量

## 8. Docker监控与日志

### 8.1 监控技术

#### 8.1.1 容器监控

- **资源监控**: CPU、内存、磁盘、网络
- **性能监控**: 响应时间、吞吐量
- **健康检查**: 容器健康状态
- **告警机制**: 异常情况告警

#### 8.1.2 监控工具

- **Docker Stats**: 内置监控命令
- **Prometheus**: 开源监控系统
- **Grafana**: 监控数据可视化
- **ELK Stack**: 日志分析平台

### 8.2 日志管理

#### 8.2.1 日志类型

- **应用日志**: 应用程序输出
- **系统日志**: 操作系统日志
- **访问日志**: 网络访问日志
- **错误日志**: 错误和异常日志

#### 8.2.2 日志处理

- **日志收集**: 集中收集日志
- **日志存储**: 持久化存储
- **日志分析**: 日志内容分析
- **日志告警**: 异常日志告警

## 9. Docker快速上手

### 9.1 安装与环境

- Linux: 使用发行版包管理器或 `get.docker.com` 脚本安装；建议启用 `docker compose` 插件与 Buildx。
- Windows: Docker Desktop（WSL2 后端优先）；启用 Linux 容器。
- macOS: Docker Desktop；注意与原生网络/文件系统语义差异。

最小验证:

```bash
#!/bin/bash
# Docker环境验证脚本

echo "=== Docker版本信息 ==="
docker --version
docker-compose --version

echo "=== Docker服务状态 ==="
docker info | head -20

echo "=== Docker镜像列表 ==="
docker images

echo "=== Docker容器状态 ==="
docker ps -a

echo "=== 测试容器运行 ==="
docker run --rm hello-world
```

### 9.2 第一个容器

```bash
docker run --rm -p 8080:80 nginx:alpine
# 访问: http://localhost:8080
```

### 9.3 镜像与数据卷

```bash
docker pull alpine:3.20
docker volume create app-data
docker run --rm -it -v app-data:/data alpine:3.20 sh -lc 'echo ok > /data/health && cat /data/health'
```

## 10. Docker命令速查

### 10.1 容器管理

```bash
docker ps -a
docker run -d --name web -p 80:80 nginx:alpine
docker logs -f web
docker exec -it web sh
docker stop web && docker rm web
```

### 10.2 镜像管理

```bash
docker images
docker build -t demo:latest .
docker tag demo:latest registry.local/demo:1.0
docker push registry.local/demo:1.0
```

### 10.3 网络与存储

```bash
docker network ls
docker network create --driver bridge app-net
docker volume ls
```

## 11. Rootless 实操

### 11.1 前置条件

- cgroups v2、`newuidmap/newgidmap`、`subuid/subgid` 配置完成。
- 用户可无密码使用 `slirp4netns`/`pasta`（视发行版）。

### 11.2 启用与验证

```bash
dockerd-rootless-setuptool.sh install
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock
docker info | grep -i rootless
```

### 11.3 常见问题

- 端口 <1024 无法监听：使用 >=1024 端口或反向代理。
- 网络性能下降：调优 `slirp4netns` MTU/Offload；或改用 `pasta`。
- systemd 管理：使用 `loginctl enable-linger $USER` 保持用户服务常驻。

## 12. 故障诊断指南

### 12.1 常见症状与排查路径

- 容器启动失败 → `docker logs <id>` → `docker inspect <id>` → 资源/权限/镜像校验。
- 镜像拉取慢/失败 → 私库证书/代理配置 → `~/.docker/config.json` 与 `daemon.json`。
- CPU/内存飙升 → `docker stats` → cgroups 限额与应用 Profiling。

### 12.2 网络问题定位

```bash
docker network inspect bridge | sed -n '1,80p'
iptables -t nat -S | grep -i docker | head -n 20
```

要点：确认宿主机防火墙/NAT 规则、端口冲突与多网卡路由策略。

### 12.3 存储与权限问题

- Overlay2 报错：检查内核、`dmesg`、挂载参数；避免跨文件系统绑定。
- 权限拒绝：校验 `USER`、`capabilities`、SELinux/AppArmor 策略与挂载选项 `:z/:Z`。

## 13. FAQ

- 如何缩小镜像体积？使用多阶段构建、`--mount=type=cache`、distroless；清理包管理缓存。
- Docker 与 containerd 有何关系？现代 Docker 以 containerd 为核心执行容器生命周期。
- Compose V1 与 V2 区别？V2 为 `docker compose` 子命令，推荐使用。

## 14. Docker发展趋势

### 9.1 技术发展趋势

#### 9.1.1 容器技术演进

- **轻量化**: 更小的镜像和运行时
- **安全性**: 更强的安全机制
- **性能**: 更高的运行性能
- **易用性**: 更简单的使用方式

#### 9.1.2 生态系统发展

- **编排技术**: Kubernetes等编排工具
- **服务网格**: Istio等服务网格技术
- **云原生**: 云原生应用开发
- **边缘计算**: 边缘容器部署

### 9.2 应用场景扩展

#### 9.2.1 传统应用容器化

- **遗留系统**: 传统应用容器化改造
- **微服务**: 微服务架构实施
- **DevOps**: CI/CD流水线集成
- **混合云**: 多云环境部署

#### 9.2.2 新兴应用场景

- **AI/ML**: 机器学习模型部署
- **IoT**: 物联网应用容器化
- **边缘计算**: 边缘节点部署
- **区块链**: 区块链应用容器化

## 15. 总结

Docker作为容器化技术的代表，通过其创新的架构设计和技术实现，为应用程序的打包、分发和运行提供了革命性的解决方案。其核心优势在于：

1. **轻量级**: 基于操作系统级虚拟化，资源开销小
2. **可移植性**: 一次构建，到处运行
3. **一致性**: 开发、测试、生产环境完全一致
4. **可扩展性**: 支持水平扩展和垂直扩展
5. **隔离性**: 容器间相互隔离，互不影响

随着容器技术的不断发展和完善，Docker将继续在云计算、微服务、DevOps等领域发挥重要作用，推动软件开发和部署方式的变革。

## 16. 版本差异与兼容说明（对齐至 2025）

- Docker Engine 与 Moby/BuildKit:
  - 2020+ 默认启用 BuildKit 构建（DOCKER_BUILDKIT=1）；多阶段构建、缓存导入导出更完善。
  - 镜像清理、Manifest 列表与多架构（multi-arch）支持增强（buildx）。
- 运行时与 containerd:
  - 现代 Docker Engine 以 containerd 为核心（dockerd → containerd → runc/crun）。
  - Snapshotter 可选 overlayfs2、btrfs、zfs；性能与内核版本强相关。
- cgroups v2:
  - 新版发行版默认 cgroups v2；资源限制参数与层级有所区别，注意与老版本脚本兼容。
- Rootless 模式:
  - 更完善的 user namespace、无特权端口映射（>=1024）限制；需结合 slirp4netns 或 VPNKit（macOS/Windows）。
- Windows/macOS 桌面:
  - 通过轻量虚拟化（Hyper-V、WSL2、HyperKit）提供 Linux 容器能力；网络/挂载语义与 Linux 略有差异。

最小兼容建议:

- Linux 内核: 5.4+（overlayfs2/ebpf 生态更成熟）。
- Docker Engine: 24+；Buildx >= 0.11；Compose V2。
- containerd: 1.7+；runc: 1.1+；crun: 1.8+。

## 17. 安全基线与 Rootless 实践要点

基线目标: 最小权限、最小镜像、最小攻击面。

- 账户与权限:
  - 默认以非 root 用户运行容器进程（USER 指令）。
  - 限制 Linux capabilities（例如 drop NET_RAW、SYS_ADMIN 等高危）。
  - 文件系统尽量只读（--read-only）并通过 tmpfs 暂存可写目录。
- 供应链与镜像:
  - 仅使用受信任的基础镜像；启用镜像签名与策略（Notary/Sigstore）。
  - 在 CI 中执行 SCA/漏洞扫描（Trivy/Grype），阻断高危。
  - 多阶段构建分离构建依赖与运行时，选择 distroless/alpine 等最小基镜。
- 运行与网络:
  - 默认 Bridge 网络并限制端口暴露；对外开放端口走反向代理/网关。
  - 使用 seccomp、AppArmor/SELinux 策略；生产开启 auditing。
  - 限制资源（CPU/内存/IO/进程数），防止资源争用与逃逸利用。
- Rootless 注意:
  - 网络性能与端口限制需评估；结合 slirp4netns 参数优化（例如启用 mtu、offload 调整）。
  - 与 systemd 集成时，确保 cgroups v2、subuid/subgid 正确配置。

## 18. BuildKit 与镜像构建优化

- 并行与缓存:
  - 启用 BuildKit 与 buildx；使用 --cache-from/--cache-to 导入导出缓存，加速 CI。
  - 合理拆分层：高频变更置于靠后层，降低无效缓存失效。
- 多架构:
  - 使用 buildx bake/build 打包 multi-arch（linux/amd64, linux/arm64），推送 manifest 列表。
- 可复现构建:
  - 固定依赖版本与校验（sha256 校验/锁文件），避免“漂移”。
  - 记录构建元数据（labels: org.opencontainers.image.*）。

示例（多阶段 + 缓存）:

```Dockerfile
# syntax=docker/dockerfile:1.7
FROM --platform=$BUILDPLATFORM golang:1.22-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build -o /out/app ./cmd/app

FROM gcr.io/distroless/base-debian12
COPY --from=builder /out/app /usr/local/bin/app
USER nonroot
ENTRYPOINT ["/usr/local/bin/app"]
```

## 19. 与 containerd/CRI 的关系与选型

- 架构关系:
  - Docker Engine 将容器生命周期委托给 containerd，后者通过 runc/crun 执行 OCI 容器。
  - Kubernetes 集群通常通过 CRI（containerd/CRI-O）对接运行时；生产编排建议直接使用 containerd。
- 选型建议:
  - 单机/开发：Docker Engine 体验最佳，生态丰富。
  - 编排/生产：Kubernetes + containerd（或 CRI-O）；减少中间层，控制面一致。
  - 高安全隔离：考虑 Kata/gVisor 等沙箱运行时，结合策略与合规要求。

## 20. 参考资料与链接

- OCI 规范：Image/Runtime/Distribution（`https://opencontainers.org`）。
- Docker 文档与 Moby/BuildKit 项目（`https://docs.docker.com`，`https://github.com/moby/buildkit`）。
- containerd 与 runc（`https://containerd.io`，`https://github.com/opencontainers/runc`）。
- Rootless 容器与 cgroups v2 指南（Red Hat/containers 文档）。
