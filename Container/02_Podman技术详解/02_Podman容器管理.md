# Podman容器管理技术详解

## 目录

- [Podman容器管理技术详解](#podman容器管理技术详解)
  - [1. 容器与Pod生命周期管理](#1-容器与pod生命周期管理)
    - [1.1 容器生命周期](#11-容器生命周期)
      - [基本容器操作](#基本容器操作)
- [创建并运行容器](#创建并运行容器)
- [创建容器但不启动](#创建容器但不启动)
- [启动已创建的容器](#启动已创建的容器)
- [停止容器](#停止容器)
- [重启容器](#重启容器)
- [删除容器](#删除容器)
      - [高级容器操作](#高级容器操作)
- [带资源限制的容器](#带资源限制的容器)
- [带环境变量的容器](#带环境变量的容器)
      - [容器状态管理](#容器状态管理)
- [查看容器状态](#查看容器状态)
- [查看容器详细信息](#查看容器详细信息)
- [查看容器日志](#查看容器日志)
    - [1.2 Pod生命周期](#12-pod生命周期)
      - [Pod基本操作](#pod基本操作)
- [创建Pod](#创建pod)
- [查看Pod列表](#查看pod列表)
- [查看Pod详细信息](#查看pod详细信息)
- [启动Pod](#启动pod)
- [停止Pod](#停止pod)
- [删除Pod](#删除pod)
      - [在Pod中运行容器](#在pod中运行容器)
- [在Pod中运行容器](#在pod中运行容器)
- [查看Pod中的容器](#查看pod中的容器)
- [查看Pod中容器的详细信息](#查看pod中容器的详细信息)
      - [Pod高级配置](#pod高级配置)
- [创建带资源限制的Pod](#创建带资源限制的pod)
- [在Pod中运行多个容器](#在pod中运行多个容器)
    - [1.3 容器与Pod关系](#13-容器与pod关系)
      - [Pod架构理解](#pod架构理解)
      - [容器间通信](#容器间通信)
- [在Pod中，容器可以通过localhost通信](#在pod中容器可以通过localhost通信)
- [容器间通信示例](#容器间通信示例)
  - [2. 健康检查与重启策略](#2-健康检查与重启策略)
    - [2.1 健康检查机制](#21-健康检查机制)
      - [健康检查配置](#健康检查配置)
- [运行时配置健康检查](#运行时配置健康检查)
      - [健康检查状态](#健康检查状态)
- [查看健康检查状态](#查看健康检查状态)
- [查看健康检查历史](#查看健康检查历史)
      - [自定义健康检查](#自定义健康检查)
- [创建健康检查脚本](#创建健康检查脚本)
- [使用自定义健康检查](#使用自定义健康检查)
    - [2.2 重启策略](#22-重启策略)
      - [重启策略类型](#重启策略类型)
- [不自动重启](#不自动重启)
- [总是重启](#总是重启)
- [除非手动停止](#除非手动停止)
- [失败时重启](#失败时重启)
      - [重启策略验证](#重启策略验证)
- [查看重启策略](#查看重启策略)
- [测试重启策略](#测试重启策略)
    - [2.3 systemd集成](#23-systemd集成)
      - [生成systemd服务](#生成systemd服务)
- [为容器生成systemd服务](#为容器生成systemd服务)
- [为Pod生成systemd服务](#为pod生成systemd服务)
- [安装systemd服务](#安装systemd服务)
      - [systemd服务配置](#systemd服务配置)
- [查看生成的systemd服务文件](#查看生成的systemd服务文件)
- [自定义systemd服务](#自定义systemd服务)
  - [3. 资源限制与隔离](#3-资源限制与隔离)
    - [3.1 资源限制](#31-资源限制)
      - [CPU限制](#cpu限制)
- [CPU限制](#cpu限制)
      - [内存限制](#内存限制)
- [内存限制](#内存限制)
      - [存储限制](#存储限制)
- [存储限制](#存储限制)
    - [3.2 隔离机制](#32-隔离机制)
      - [命名空间隔离](#命名空间隔离)
- [使用特定命名空间](#使用特定命名空间)
- [禁用用户命名空间](#禁用用户命名空间)
      - [能力控制](#能力控制)
- [添加能力](#添加能力)
- [删除能力](#删除能力)
- [查看能力](#查看能力)
    - [3.3 安全配置](#33-安全配置)
      - [安全选项](#安全选项)
- [只读根文件系统](#只读根文件系统)
- [禁用特权模式](#禁用特权模式)
- [指定用户](#指定用户)
      - [SELinux配置](#selinux配置)
- [使用SELinux标签](#使用selinux标签)
- [禁用SELinux](#禁用selinux)
  - [4. 日志与调试](#4-日志与调试)
    - [4.1 日志管理](#41-日志管理)
      - [日志查看](#日志查看)
- [查看容器日志](#查看容器日志)
- [实时查看日志](#实时查看日志)
- [查看最近日志](#查看最近日志)
- [带时间戳的日志](#带时间戳的日志)
      - [日志配置](#日志配置)
- [配置日志驱动](#配置日志驱动)
    - [4.2 调试技巧](#42-调试技巧)
      - [容器调试](#容器调试)
- [进入容器](#进入容器)
- [查看容器进程](#查看容器进程)
- [查看容器统计信息](#查看容器统计信息)
      - [系统调试](#系统调试)
- [查看容器事件](#查看容器事件)
- [查看系统信息](#查看系统信息)
- [查看容器详细信息](#查看容器详细信息)
    - [4.3 故障排查](#43-故障排查)
      - [常见问题排查](#常见问题排查)
- [容器启动失败](#容器启动失败)
- [网络问题](#网络问题)
- [存储问题](#存储问题)
      - [性能问题排查](#性能问题排查)
- [查看资源使用](#查看资源使用)
- [查看系统资源](#查看系统资源)
- [分析容器性能](#分析容器性能)
  - [5. 与systemd集成](#5-与systemd集成)
    - [5.1 systemd服务生成](#51-systemd服务生成)
      - [基本服务生成](#基本服务生成)
- [为容器生成systemd服务](#为容器生成systemd服务)
- [为Pod生成systemd服务](#为pod生成systemd服务)
- [生成新的服务（每次重启创建新容器）](#生成新的服务每次重启创建新容器)
      - [高级服务配置](#高级服务配置)
- [生成带环境变量的服务](#生成带环境变量的服务)
- [生成带依赖的服务](#生成带依赖的服务)
    - [5.2 用户服务管理](#52-用户服务管理)
      - [用户服务配置](#用户服务配置)
- [启用用户服务](#启用用户服务)
- [生成用户服务](#生成用户服务)
- [安装用户服务](#安装用户服务)
      - [用户服务管理](#用户服务管理)
- [查看用户服务状态](#查看用户服务状态)
- [重启用户服务](#重启用户服务)
- [停止用户服务](#停止用户服务)
    - [5.3 服务配置优化](#53-服务配置优化)
      - [服务优化配置](#服务优化配置)
- [生成优化的systemd服务](#生成优化的systemd服务)
- [自定义服务配置](#自定义服务配置)
  - [6. 与Compose/Play协同](#6-与composeplay协同)
    - [6.1 Podman Compose](#61-podman-compose)
      - [Compose文件配置](#compose文件配置)
- [docker-compose.yml](#docker-composeyml)
      - [Compose操作](#compose操作)
- [启动服务](#启动服务)
- [停止服务](#停止服务)
- [查看服务状态](#查看服务状态)
- [查看服务日志](#查看服务日志)
    - [6.2 Podman Play](#62-podman-play)
      - [Kubernetes YAML配置](#kubernetes-yaml配置)
- [app.yaml](#appyaml)
      - [Play操作](#play操作)
- [运行Kubernetes YAML](#运行kubernetes-yaml)
- [停止Pod](#停止pod)
- [查看Pod状态](#查看pod状态)
    - [6.3 使用场景对比](#63-使用场景对比)
      - [场景选择](#场景选择)
  - [7. 最佳实践与FAQ](#7-最佳实践与faq)
    - [7.1 最佳实践](#71-最佳实践)
      - [容器设计原则](#容器设计原则)
      - [Pod设计原则](#pod设计原则)
    - [7.2 常见问题](#72-常见问题)
      - [Q: 容器无法启动怎么办？](#q-容器无法启动怎么办)
      - [Q: Pod中的容器无法通信怎么办？](#q-pod中的容器无法通信怎么办)
      - [Q: systemd服务无法启动怎么办？](#q-systemd服务无法启动怎么办)
    - [7.3 性能优化](#73-性能优化)
      - [容器性能优化](#容器性能优化)
- [使用轻量级基础镜像](#使用轻量级基础镜像)
- [合理设置资源限制](#合理设置资源限制)
- [使用只读文件系统](#使用只读文件系统)
      - [Pod性能优化](#pod性能优化)
- [合理设置Pod资源限制](#合理设置pod资源限制)
- [优化容器启动顺序](#优化容器启动顺序)
  - [版本差异说明](#版本差异说明)
  - [参考资源](#参考资源)

- [Podman容器管理技术详解](#podman容器管理技术详解)
  - [1. 容器与Pod生命周期管理](#1-容器与pod生命周期管理)
    - [1.1 容器生命周期](#11-容器生命周期)
      - [基本容器操作](#基本容器操作)
- [创建并运行容器](#创建并运行容器)
- [创建容器但不启动](#创建容器但不启动)
- [启动已创建的容器](#启动已创建的容器)
- [停止容器](#停止容器)
- [重启容器](#重启容器)
- [删除容器](#删除容器)
      - [高级容器操作](#高级容器操作)
- [带资源限制的容器](#带资源限制的容器)
- [带环境变量的容器](#带环境变量的容器)
      - [容器状态管理](#容器状态管理)
- [查看容器状态](#查看容器状态)
- [查看容器详细信息](#查看容器详细信息)
- [查看容器日志](#查看容器日志)
    - [1.2 Pod生命周期](#12-pod生命周期)
      - [Pod基本操作](#pod基本操作)
- [创建Pod](#创建pod)
- [查看Pod列表](#查看pod列表)
- [查看Pod详细信息](#查看pod详细信息)
- [启动Pod](#启动pod)
- [停止Pod](#停止pod)
- [删除Pod](#删除pod)
      - [在Pod中运行容器](#在pod中运行容器)
- [在Pod中运行容器](#在pod中运行容器)
- [查看Pod中的容器](#查看pod中的容器)
- [查看Pod中容器的详细信息](#查看pod中容器的详细信息)
      - [Pod高级配置](#pod高级配置)
- [创建带资源限制的Pod](#创建带资源限制的pod)
- [在Pod中运行多个容器](#在pod中运行多个容器)
    - [1.3 容器与Pod关系](#13-容器与pod关系)
      - [Pod架构理解](#pod架构理解)
      - [容器间通信](#容器间通信)
- [在Pod中，容器可以通过localhost通信](#在pod中容器可以通过localhost通信)
- [容器间通信示例](#容器间通信示例)
  - [2. 健康检查与重启策略](#2-健康检查与重启策略)
    - [2.1 健康检查机制](#21-健康检查机制)
      - [健康检查配置](#健康检查配置)
- [运行时配置健康检查](#运行时配置健康检查)
      - [健康检查状态](#健康检查状态)
- [查看健康检查状态](#查看健康检查状态)
- [查看健康检查历史](#查看健康检查历史)
      - [自定义健康检查](#自定义健康检查)
- [创建健康检查脚本](#创建健康检查脚本)
- [使用自定义健康检查](#使用自定义健康检查)
    - [2.2 重启策略](#22-重启策略)
      - [重启策略类型](#重启策略类型)
- [不自动重启](#不自动重启)
- [总是重启](#总是重启)
- [除非手动停止](#除非手动停止)
- [失败时重启](#失败时重启)
      - [重启策略验证](#重启策略验证)
- [查看重启策略](#查看重启策略)
- [测试重启策略](#测试重启策略)
    - [2.3 systemd集成](#23-systemd集成)
      - [生成systemd服务](#生成systemd服务)
- [为容器生成systemd服务](#为容器生成systemd服务)
- [为Pod生成systemd服务](#为pod生成systemd服务)
- [安装systemd服务](#安装systemd服务)
      - [systemd服务配置](#systemd服务配置)
- [查看生成的systemd服务文件](#查看生成的systemd服务文件)
- [自定义systemd服务](#自定义systemd服务)
  - [3. 资源限制与隔离](#3-资源限制与隔离)
    - [3.1 资源限制](#31-资源限制)
      - [CPU限制](#cpu限制)
- [CPU限制](#cpu限制)
      - [内存限制](#内存限制)
- [内存限制](#内存限制)
      - [存储限制](#存储限制)
- [存储限制](#存储限制)
    - [3.2 隔离机制](#32-隔离机制)
      - [命名空间隔离](#命名空间隔离)
- [使用特定命名空间](#使用特定命名空间)
- [禁用用户命名空间](#禁用用户命名空间)
      - [能力控制](#能力控制)
- [添加能力](#添加能力)
- [删除能力](#删除能力)
- [查看能力](#查看能力)
    - [3.3 安全配置](#33-安全配置)
      - [安全选项](#安全选项)
- [只读根文件系统](#只读根文件系统)
- [禁用特权模式](#禁用特权模式)
- [指定用户](#指定用户)
      - [SELinux配置](#selinux配置)
- [使用SELinux标签](#使用selinux标签)
- [禁用SELinux](#禁用selinux)
  - [4. 日志与调试](#4-日志与调试)
    - [4.1 日志管理](#41-日志管理)
      - [日志查看](#日志查看)
- [查看容器日志](#查看容器日志)
- [实时查看日志](#实时查看日志)
- [查看最近日志](#查看最近日志)
- [带时间戳的日志](#带时间戳的日志)
      - [日志配置](#日志配置)
- [配置日志驱动](#配置日志驱动)
    - [4.2 调试技巧](#42-调试技巧)
      - [容器调试](#容器调试)
- [进入容器](#进入容器)
- [查看容器进程](#查看容器进程)
- [查看容器统计信息](#查看容器统计信息)
      - [系统调试](#系统调试)
- [查看容器事件](#查看容器事件)
- [查看系统信息](#查看系统信息)
- [查看容器详细信息](#查看容器详细信息)
    - [4.3 故障排查](#43-故障排查)
      - [常见问题排查](#常见问题排查)
- [容器启动失败](#容器启动失败)
- [网络问题](#网络问题)
- [存储问题](#存储问题)
      - [性能问题排查](#性能问题排查)
- [查看资源使用](#查看资源使用)
- [查看系统资源](#查看系统资源)
- [分析容器性能](#分析容器性能)
  - [5. 与systemd集成](#5-与systemd集成)
    - [5.1 systemd服务生成](#51-systemd服务生成)
      - [基本服务生成](#基本服务生成)
- [为容器生成systemd服务](#为容器生成systemd服务)
- [为Pod生成systemd服务](#为pod生成systemd服务)
- [生成新的服务（每次重启创建新容器）](#生成新的服务每次重启创建新容器)
      - [高级服务配置](#高级服务配置)
- [生成带环境变量的服务](#生成带环境变量的服务)
- [生成带依赖的服务](#生成带依赖的服务)
    - [5.2 用户服务管理](#52-用户服务管理)
      - [用户服务配置](#用户服务配置)
- [启用用户服务](#启用用户服务)
- [生成用户服务](#生成用户服务)
- [安装用户服务](#安装用户服务)
      - [用户服务管理](#用户服务管理)
- [查看用户服务状态](#查看用户服务状态)
- [重启用户服务](#重启用户服务)
- [停止用户服务](#停止用户服务)
    - [5.3 服务配置优化](#53-服务配置优化)
      - [服务优化配置](#服务优化配置)
- [生成优化的systemd服务](#生成优化的systemd服务)
- [自定义服务配置](#自定义服务配置)
  - [6. 与Compose/Play协同](#6-与composeplay协同)
    - [6.1 Podman Compose](#61-podman-compose)
      - [Compose文件配置](#compose文件配置)
- [docker-compose.yml](#docker-composeyml)
      - [Compose操作](#compose操作)
- [启动服务](#启动服务)
- [停止服务](#停止服务)
- [查看服务状态](#查看服务状态)
- [查看服务日志](#查看服务日志)
    - [6.2 Podman Play](#62-podman-play)
      - [Kubernetes YAML配置](#kubernetes-yaml配置)
- [app.yaml](#appyaml)
      - [Play操作](#play操作)
- [运行Kubernetes YAML](#运行kubernetes-yaml)
- [停止Pod](#停止pod)
- [查看Pod状态](#查看pod状态)
    - [6.3 使用场景对比](#63-使用场景对比)
      - [场景选择](#场景选择)
  - [7. 最佳实践与FAQ](#7-最佳实践与faq)
    - [7.1 最佳实践](#71-最佳实践)
      - [容器设计原则](#容器设计原则)
      - [Pod设计原则](#pod设计原则)
    - [7.2 常见问题](#72-常见问题)
      - [Q: 容器无法启动怎么办？](#q-容器无法启动怎么办)
      - [Q: Pod中的容器无法通信怎么办？](#q-pod中的容器无法通信怎么办)
      - [Q: systemd服务无法启动怎么办？](#q-systemd服务无法启动怎么办)
    - [7.3 性能优化](#73-性能优化)
      - [容器性能优化](#容器性能优化)
- [使用轻量级基础镜像](#使用轻量级基础镜像)
- [合理设置资源限制](#合理设置资源限制)
- [使用只读文件系统](#使用只读文件系统)
      - [Pod性能优化](#pod性能优化)
- [合理设置Pod资源限制](#合理设置pod资源限制)
- [优化容器启动顺序](#优化容器启动顺序)
  - [版本差异说明](#版本差异说明)
  - [参考资源](#参考资源)

- [Podman容器管理技术详解](#podman容器管理技术详解)
  - [目录](#目录)
  - [1. 容器与Pod生命周期管理](#1-容器与pod生命周期管理)
    - [1.1 容器生命周期](#11-容器生命周期)
    - [1.2 Pod生命周期](#12-pod生命周期)
    - [1.3 容器与Pod关系](#13-容器与pod关系)
  - [2. 健康检查与重启策略](#2-健康检查与重启策略)
    - [2.1 健康检查机制](#21-健康检查机制)
    - [2.2 重启策略](#22-重启策略)
    - [2.3 systemd集成](#23-systemd集成)
  - [3. 资源限制与隔离](#3-资源限制与隔离)
    - [3.1 资源限制](#31-资源限制)
    - [3.2 隔离机制](#32-隔离机制)
    - [3.3 安全配置](#33-安全配置)
  - [4. 日志与调试](#4-日志与调试)
    - [4.1 日志管理](#41-日志管理)
    - [4.2 调试技巧](#42-调试技巧)
    - [4.3 故障排查](#43-故障排查)
  - [5. 与systemd集成](#5-与systemd集成)
    - [5.1 systemd服务生成](#51-systemd服务生成)
    - [5.2 用户服务管理](#52-用户服务管理)
    - [5.3 服务配置优化](#53-服务配置优化)
  - [6. 与Compose/Play协同](#6-与composeplay协同)
    - [6.1 Podman Compose](#61-podman-compose)
    - [6.2 Podman Play](#62-podman-play)
    - [6.3 使用场景对比](#63-使用场景对比)
  - [7. 最佳实践与FAQ](#7-最佳实践与faq)
    - [7.1 最佳实践](#71-最佳实践)
    - [7.2 常见问题](#72-常见问题)
    - [7.3 性能优化](#73-性能优化)

## 1. 容器与Pod生命周期管理

### 1.1 容器生命周期

#### 基本容器操作

```bash
# 创建并运行容器
podman run -d --name my-container nginx:latest

# 创建容器但不启动
podman create --name my-container nginx:latest

# 启动已创建的容器
podman start my-container

# 停止容器
podman stop my-container

# 重启容器
podman restart my-container

# 删除容器
podman rm my-container
```

#### 高级容器操作

```bash
# 带资源限制的容器
podman run -d \
  --name web-server \
  --memory=512m \
  --cpus=1.0 \
  --restart=unless-stopped \
  -p 80:80 \
  nginx:latest

# 带环境变量的容器
podman run -d \
  --name app \
  -e DATABASE_URL=postgresql://user:pass@db:5432/mydb \
  -e DEBUG=true \
  myapp:latest
```

#### 容器状态管理

```bash
# 查看容器状态
podman ps                    # 运行中的容器
podman ps -a                 # 所有容器
podman ps -q                 # 只显示容器ID

# 查看容器详细信息
podman inspect my-container

# 查看容器日志
podman logs my-container
podman logs -f my-container  # 实时查看日志
```

### 1.2 Pod生命周期

#### Pod基本操作

```bash
# 创建Pod
podman pod create --name web-pod -p 8080:80

# 查看Pod列表
podman pod ls

# 查看Pod详细信息
podman pod inspect web-pod

# 启动Pod
podman pod start web-pod

# 停止Pod
podman pod stop web-pod

# 删除Pod
podman pod rm web-pod
```

#### 在Pod中运行容器

```bash
# 在Pod中运行容器
podman run -d --pod web-pod --name web nginx:latest
podman run -d --pod web-pod --name db postgres:13

# 查看Pod中的容器
podman pod ps web-pod

# 查看Pod中容器的详细信息
podman pod inspect web-pod
```

#### Pod高级配置

```bash
# 创建带资源限制的Pod
podman pod create \
  --name app-pod \
  --memory=1g \
  --cpus=2.0 \
  -p 8080:80 \
  -p 5432:5432

# 在Pod中运行多个容器
podman run -d --pod app-pod --name frontend nginx:latest
podman run -d --pod app-pod --name backend node:18
podman run -d --pod app-pod --name database postgres:13
```

### 1.3 容器与Pod关系

#### Pod架构理解

```text
┌─────────────────────────────────────┐
│                Pod                  │
│  ┌─────────────┐  ┌─────────────┐   │
│  │  Container  │  │  Container  │   │
│  │   (web)     │  │   (db)      │   │
│  └─────────────┘  └─────────────┘   │
│  ┌─────────────────────────────────┐ │
│  │        Shared Network           │ │
│  │        (localhost)              │ │
│  └─────────────────────────────────┘ │
│  ┌─────────────────────────────────┐ │
│  │        Shared Storage           │ │
│  │        (volumes)                │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

#### 容器间通信

```bash
# 在Pod中，容器可以通过localhost通信
podman run -d --pod web-pod --name web nginx:latest
podman run -d --pod web-pod --name api node:18

# 容器间通信示例
podman exec web curl http://localhost:3000/api
```

## 2. 健康检查与重启策略

### 2.1 健康检查机制

#### 健康检查配置

```bash
# 运行时配置健康检查
podman run -d \
  --name web \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-start-period=5s \
  --health-retries=3 \
  nginx:latest
```

#### 健康检查状态

```bash
# 查看健康检查状态
podman inspect web --format='{{.State.Health.Status}}'

# 查看健康检查历史
podman inspect web --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

#### 自定义健康检查

```bash
# 创建健康检查脚本
cat > healthcheck.sh << 'EOF'
#!/bin/bash
if curl -f http://localhost/health; then
    exit 0
else
    exit 1
fi
EOF

chmod +x healthcheck.sh

# 使用自定义健康检查
podman run -d \
  --name app \
  -v $(pwd)/healthcheck.sh:/healthcheck.sh \
  --health-cmd="/healthcheck.sh" \
  myapp:latest
```

### 2.2 重启策略

#### 重启策略类型

```bash
# 不自动重启
podman run -d --restart=no nginx:latest

# 总是重启
podman run -d --restart=always nginx:latest

# 除非手动停止
podman run -d --restart=unless-stopped nginx:latest

# 失败时重启
podman run -d --restart=on-failure nginx:latest
```

#### 重启策略验证

```bash
# 查看重启策略
podman inspect container_name --format='{{.HostConfig.RestartPolicy.Name}}'

# 测试重启策略
podman stop container_name
podman start container_name
```

### 2.3 systemd集成

#### 生成systemd服务

```bash
# 为容器生成systemd服务
podman generate systemd --name web --files

# 为Pod生成systemd服务
podman generate systemd --name web-pod --files

# 安装systemd服务
sudo cp container-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable container-web.service
sudo systemctl start container-web.service
```

#### systemd服务配置

```bash
# 查看生成的systemd服务文件
cat container-web.service

# 自定义systemd服务
podman generate systemd --name web --new > /etc/systemd/system/container-web.service
```

## 3. 资源限制与隔离

### 3.1 资源限制

#### CPU限制

```bash
# CPU限制
podman run -d --cpus="1.5" nginx:latest
podman run -d --cpu-shares=512 nginx:latest
podman run -d --cpuset-cpus="0,1" nginx:latest
```

#### 内存限制

```bash
# 内存限制
podman run -d --memory=512m nginx:latest
podman run -d --memory-swap=1g nginx:latest
podman run -d --oom-kill-disable nginx:latest
```

#### 存储限制

```bash
# 存储限制
podman run -d --storage-opt size=10G nginx:latest
```

### 3.2 隔离机制

#### 命名空间隔离

```bash
# 使用特定命名空间
podman run -d --pid=host nginx:latest
podman run -d --network=host nginx:latest
podman run -d --uts=host nginx:latest

# 禁用用户命名空间
podman run -d --userns=host nginx:latest
```

#### 能力控制

```bash
# 添加能力
podman run -d --cap-add=NET_ADMIN nginx:latest

# 删除能力
podman run -d --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx:latest

# 查看能力
podman inspect container_name --format='{{.HostConfig.CapAdd}}'
```

### 3.3 安全配置

#### 安全选项

```bash
# 只读根文件系统
podman run -d --read-only --tmpfs /tmp nginx:latest

# 禁用特权模式
podman run -d --privileged=false nginx:latest

# 指定用户
podman run -d --user=1000:1000 nginx:latest
```

#### SELinux配置

```bash
# 使用SELinux标签
podman run -d --security-opt label=type:container_t nginx:latest

# 禁用SELinux
podman run -d --security-opt label=disable nginx:latest
```

## 4. 日志与调试

### 4.1 日志管理

#### 日志查看

```bash
# 查看容器日志
podman logs container_name

# 实时查看日志
podman logs -f container_name

# 查看最近日志
podman logs --tail=100 container_name

# 带时间戳的日志
podman logs -t container_name
```

#### 日志配置

```bash
# 配置日志驱动
podman run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx:latest
```

### 4.2 调试技巧

#### 容器调试

```bash
# 进入容器
podman exec -it container_name /bin/bash

# 查看容器进程
podman top container_name

# 查看容器统计信息
podman stats container_name
```

#### 系统调试

```bash
# 查看容器事件
podman events

# 查看系统信息
podman info

# 查看容器详细信息
podman inspect container_name
```

### 4.3 故障排查

#### 常见问题排查

```bash
# 容器启动失败
podman logs container_name
podman inspect container_name

# 网络问题
podman network ls
podman network inspect bridge

# 存储问题
podman volume ls
podman volume inspect volume_name
```

#### 性能问题排查

```bash
# 查看资源使用
podman stats

# 查看系统资源
podman system df

# 分析容器性能
podman exec container_name top
```

## 5. 与systemd集成

### 5.1 systemd服务生成

#### 基本服务生成

```bash
# 为容器生成systemd服务
podman generate systemd --name web --files

# 为Pod生成systemd服务
podman generate systemd --name web-pod --files

# 生成新的服务（每次重启创建新容器）
podman generate systemd --name web --new --files
```

#### 高级服务配置

```bash
# 生成带环境变量的服务
podman generate systemd --name web --env-file .env --files

# 生成带依赖的服务
podman generate systemd --name web --requires=network.target --files
```

### 5.2 用户服务管理

#### 用户服务配置

```bash
# 启用用户服务
loginctl enable-linger $USER

# 生成用户服务
podman generate systemd --name web --files --new

# 安装用户服务
mkdir -p ~/.config/systemd/user
cp container-web.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable container-web.service
systemctl --user start container-web.service
```

#### 用户服务管理

```bash
# 查看用户服务状态
systemctl --user status container-web.service

# 重启用户服务
systemctl --user restart container-web.service

# 停止用户服务
systemctl --user stop container-web.service
```

### 5.3 服务配置优化

#### 服务优化配置

```bash
# 生成优化的systemd服务
podman generate systemd --name web --new --restart-policy=always --files

# 自定义服务配置
cat > /etc/systemd/system/container-web.service << EOF
[Unit]
Description=Container web
After=network.target

[Service]
Type=forking
ExecStart=/usr/bin/podman start web
ExecStop=/usr/bin/podman stop web
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

## 6. 与Compose/Play协同

### 6.1 Podman Compose

#### Compose文件配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    volumes:
      - ./html:/usr/share/nginx/html
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Compose操作

```bash
# 启动服务
podman-compose up -d

# 停止服务
podman-compose down

# 查看服务状态
podman-compose ps

# 查看服务日志
podman-compose logs -f web
```

### 6.2 Podman Play

#### Kubernetes YAML配置

```yaml
# app.yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    ports:
    - containerPort: 80
  - name: api
    image: node:18
    ports:
    - containerPort: 3000
```

#### Play操作

```bash
# 运行Kubernetes YAML
podman play kube app.yaml

# 停止Pod
podman play kube --down app.yaml

# 查看Pod状态
podman pod ls
```

### 6.3 使用场景对比

#### 场景选择

| 场景 | 推荐工具 | 原因 |
|------|----------|------|
| 开发环境 | Podman Compose | 简单易用，Docker兼容 |
| 测试环境 | Podman Play | 支持Kubernetes YAML |
| 生产环境 | systemd服务 | 更好的系统集成 |
| 学习K8s | Podman Play | 本地运行K8s应用 |

## 7. 最佳实践与FAQ

### 7.1 最佳实践

#### 容器设计原则

1. **单一职责**: 每个容器只运行一个进程
2. **无状态设计**: 避免在容器中存储状态数据
3. **最小化镜像**: 使用最小化的基础镜像
4. **健康检查**: 配置适当的健康检查机制

#### Pod设计原则

1. **相关容器**: 将相关的容器放在同一个Pod中
2. **共享资源**: 利用Pod的共享网络和存储
3. **生命周期**: 确保Pod中容器的生命周期一致
4. **资源管理**: 合理设置Pod的资源限制

### 7.2 常见问题

#### Q: 容器无法启动怎么办？

A:

1. 检查镜像是否存在: `podman images`
2. 查看容器日志: `podman logs container_name`
3. 检查端口是否被占用: `netstat -tlnp | grep :port`
4. 验证命令和参数是否正确

#### Q: Pod中的容器无法通信怎么办？

A:

1. 检查Pod网络配置: `podman pod inspect pod_name`
2. 验证容器是否在同一个Pod中
3. 检查容器端口配置
4. 使用localhost进行通信

#### Q: systemd服务无法启动怎么办？

A:

1. 检查服务文件: `systemctl status service_name`
2. 查看服务日志: `journalctl -u service_name`
3. 验证Podman命令路径
4. 检查权限配置

### 7.3 性能优化

#### 容器性能优化

```bash
# 使用轻量级基础镜像
podman run -d alpine:latest

# 合理设置资源限制
podman run -d --memory=512m --cpus=1.0 nginx:latest

# 使用只读文件系统
podman run -d --read-only --tmpfs /tmp nginx:latest
```

#### Pod性能优化

```bash
# 合理设置Pod资源限制
podman pod create --name app-pod --memory=1g --cpus=2.0

# 优化容器启动顺序
podman run -d --pod app-pod --name db postgres:13
podman run -d --pod app-pod --name api node:18
podman run -d --pod app-pod --name web nginx:latest
```

---

## 版本差异说明

- **Podman 4.7+**: 支持netavark网络，性能提升
- **Podman 4.5+**: 支持Pod资源限制
- **Podman 4.3+**: 支持systemd服务生成优化

## 参考资源

- [Podman官方文档](https://docs.podman.io/)
- [Podman Compose文档](https://github.com/containers/podman-compose)
- [systemd集成指南](https://docs.podman.io/en/latest/markdown/podman-generate-systemd.1.html)
- [Podman Play文档](https://docs.podman.io/en/latest/markdown/podman-play-kube.1.html)
