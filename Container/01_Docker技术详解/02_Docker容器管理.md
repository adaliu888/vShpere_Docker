# Docker容器管理技术详解

## 目录

- [Docker容器管理技术详解](#docker容器管理技术详解)
  - [目录](#目录)
  - [1. 容器生命周期管理](#1-容器生命周期管理)
    - [1.1 容器创建与启动](#11-容器创建与启动)
    - [1.2 容器运行状态管理](#12-容器运行状态管理)
    - [1.3 容器停止与删除](#13-容器停止与删除)
    - [1.4 容器重启与恢复](#14-容器重启与恢复)
  - [2. 容器配置与资源管理](#2-容器配置与资源管理)
    - [2.1 资源限制与配额](#21-资源限制与配额)
    - [2.2 环境变量与配置](#22-环境变量与配置)
    - [2.3 端口映射与网络配置](#23-端口映射与网络配置)
    - [2.4 存储卷挂载](#24-存储卷挂载)
  - [3. 容器健康检查](#3-容器健康检查)
    - [3.1 健康检查机制](#31-健康检查机制)
    - [3.2 健康检查配置](#32-健康检查配置)
    - [3.3 健康检查最佳实践](#33-健康检查最佳实践)
  - [4. Docker Compose V2](#4-docker-compose-v2)
    - [4.1 Compose文件格式](#41-compose文件格式)
    - [4.2 服务编排与管理](#42-服务编排与管理)
    - [4.3 网络与存储管理](#43-网络与存储管理)
    - [4.4 环境变量与配置管理](#44-环境变量与配置管理)
  - [5. 容器监控与日志](#5-容器监控与日志)
    - [5.1 容器状态监控](#51-容器状态监控)
    - [5.2 日志收集与管理](#52-日志收集与管理)
    - [5.3 性能指标收集](#53-性能指标收集)
  - [6. 容器安全与隔离](#6-容器安全与隔离)
    - [6.1 用户权限管理](#61-用户权限管理)
    - [6.2 安全策略配置](#62-安全策略配置)
    - [6.3 容器间隔离](#63-容器间隔离)
  - [7. 故障诊断与排错](#7-故障诊断与排错)
    - [7.1 常见问题诊断](#71-常见问题诊断)
    - [7.2 日志分析技巧](#72-日志分析技巧)
    - [7.3 性能问题排查](#73-性能问题排查)
  - [8. 最佳实践与优化](#8-最佳实践与优化)
    - [8.1 容器设计原则](#81-容器设计原则)
    - [8.2 资源优化策略](#82-资源优化策略)
    - [8.3 运维自动化](#83-运维自动化)
  - [9. 快速上手指南](#9-快速上手指南)
  - [10. 命令速查表](#10-命令速查表)
  - [11. 故障排除FAQ](#11-故障排除faq)

## 1. 容器生命周期管理

### 1.1 容器创建与启动

#### 基本容器创建

```bash
# 创建并启动容器
docker run -d --name my-container nginx:latest

# 创建容器但不启动
docker create --name my-container nginx:latest

# 启动已创建的容器
docker start my-container
```

#### 高级创建选项

```bash
# 带资源限制的容器
docker run -d \
  --name web-server \
  --memory=512m \
  --cpus=1.0 \
  --restart=unless-stopped \
  -p 80:80 \
  nginx:latest

# 带环境变量的容器
docker run -d \
  --name app \
  -e DATABASE_URL=postgresql://user:pass@db:5432/mydb \
  -e DEBUG=true \
  myapp:latest
```

### 1.2 容器运行状态管理

#### 状态查看

```bash
# 查看容器状态
docker ps                    # 运行中的容器
docker ps -a                 # 所有容器
docker ps -q                 # 只显示容器ID
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 查看容器详细信息
docker inspect my-container
docker inspect --format='{{.State.Status}}' my-container
```

#### 状态管理

```bash
# 暂停/恢复容器
docker pause my-container
docker unpause my-container

# 重启容器
docker restart my-container

# 停止容器
docker stop my-container
docker kill my-container     # 强制停止
```

### 1.3 容器停止与删除

```bash
# 停止容器
docker stop my-container

# 删除容器
docker rm my-container

# 强制删除运行中的容器
docker rm -f my-container

# 清理所有停止的容器
docker container prune
```

### 1.4 容器重启与恢复

#### 重启策略

```bash
# 设置重启策略
docker run -d --restart=no nginx:latest           # 不自动重启
docker run -d --restart=always nginx:latest       # 总是重启
docker run -d --restart=unless-stopped nginx:latest # 除非手动停止
docker run -d --restart=on-failure nginx:latest   # 失败时重启
```

## 2. 容器配置与资源管理

### 2.1 资源限制与配额

#### CPU限制

```bash
# CPU限制
docker run -d --cpus="1.5" nginx:latest
docker run -d --cpu-shares=512 nginx:latest
docker run -d --cpuset-cpus="0,1" nginx:latest
```

#### 内存限制

```bash
# 内存限制
docker run -d --memory=512m nginx:latest
docker run -d --memory-swap=1g nginx:latest
docker run -d --oom-kill-disable nginx:latest
```

#### 存储限制

```bash
# 存储限制
docker run -d --storage-opt size=10G nginx:latest
```

### 2.2 环境变量与配置

```bash
# 设置环境变量
docker run -d -e NODE_ENV=production nginx:latest

# 从文件加载环境变量
docker run -d --env-file .env nginx:latest

# 传递主机环境变量
docker run -d -e HOME nginx:latest
```

### 2.3 端口映射与网络配置

```bash
# 端口映射
docker run -d -p 8080:80 nginx:latest
docker run -d -p 127.0.0.1:8080:80 nginx:latest
docker run -d -P nginx:latest  # 随机端口

# 网络配置
docker run -d --network=bridge nginx:latest
docker run -d --network=host nginx:latest
docker run -d --network=none nginx:latest
```

### 2.4 存储卷挂载

```bash
# 绑定挂载
docker run -d -v /host/path:/container/path nginx:latest

# 命名卷
docker run -d -v my-volume:/data nginx:latest

# 只读挂载
docker run -d -v /host/path:/container/path:ro nginx:latest

# tmpfs挂载
docker run -d --tmpfs /tmp nginx:latest
```

## 3. 容器健康检查

### 3.1 健康检查机制

Docker提供内置的健康检查机制，通过定期执行检查命令来监控容器健康状态。

#### 健康检查状态

- `starting`: 容器启动中
- `healthy`: 健康检查通过
- `unhealthy`: 健康检查失败
- `none`: 未配置健康检查

### 3.2 健康检查配置

#### Dockerfile中配置

```dockerfile
FROM nginx:latest

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1
```

#### 运行时配置

```bash
# 运行时添加健康检查
docker run -d \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  --health-timeout=3s \
  --health-start-period=5s \
  --health-retries=3 \
  nginx:latest
```

### 3.3 健康检查最佳实践

1. **检查命令选择**: 使用轻量级、快速的检查命令
2. **超时设置**: 合理设置超时时间，避免误报
3. **重试机制**: 配置适当的重试次数
4. **启动延迟**: 给应用足够的启动时间

## 4. Docker Compose V2

### 4.1 Compose文件格式

#### 基本结构

```yaml
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

### 4.2 服务编排与管理

#### 服务管理命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 重启服务
docker compose restart

# 查看服务状态
docker compose ps

# 查看服务日志
docker compose logs -f web
```

#### 服务扩展

```bash
# 扩展服务实例
docker compose up -d --scale web=3

# 更新服务
docker compose up -d --force-recreate web
```

### 4.3 网络与存储管理

#### 网络配置

```yaml
services:
  web:
    networks:
      - frontend
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

#### 存储配置

```yaml
services:
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backup:/backup:ro

volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/postgres_data
```

### 4.4 环境变量与配置管理

#### 环境文件

```bash
# .env文件
DATABASE_URL=postgresql://user:pass@db:5432/mydb
REDIS_URL=redis://redis:6379
DEBUG=false
```

#### Compose配置

```yaml
services:
  web:
    env_file:
      - .env
      - .env.production
    environment:
      - NODE_ENV=${NODE_ENV:-production}
```

## 5. 容器监控与日志

### 5.1 容器状态监控

#### 实时监控

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats my-container

# 持续监控
docker stats --no-stream
```

#### 详细信息

```bash
# 查看容器详细信息
docker inspect my-container

# 查看容器进程
docker top my-container

# 查看容器资源使用历史
docker system df
```

### 5.2 日志收集与管理

#### 日志查看

```bash
# 查看容器日志
docker logs my-container

# 实时查看日志
docker logs -f my-container

# 查看最近日志
docker logs --tail=100 my-container

# 带时间戳的日志
docker logs -t my-container
```

#### 日志驱动配置

```bash
# 配置日志驱动
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx:latest
```

### 5.3 性能指标收集

#### 系统指标

```bash
# 查看系统信息
docker system info

# 查看磁盘使用
docker system df

# 查看事件
docker events
```

## 6. 容器安全与隔离

### 6.1 用户权限管理

#### 用户配置

```bash
# 指定用户运行
docker run -d --user=1000:1000 nginx:latest

# 只读根文件系统
docker run -d --read-only nginx:latest

# 禁用特权模式
docker run -d --privileged=false nginx:latest
```

### 6.2 安全策略配置

#### 安全选项

```bash
# 禁用网络
docker run -d --network=none nginx:latest

# 禁用进程间通信
docker run -d --ipc=none nginx:latest

# 禁用用户命名空间
docker run -d --userns=none nginx:latest
```

### 6.3 容器间隔离

#### 资源隔离

```bash
# CPU隔离
docker run -d --cpuset-cpus="0" nginx:latest

# 内存隔离
docker run -d --memory=512m nginx:latest

# 存储隔离
docker run -d --storage-opt size=10G nginx:latest
```

## 7. 故障诊断与排错

### 7.1 常见问题诊断

#### 容器启动失败

```bash
# 查看容器日志
docker logs my-container

# 检查容器配置
docker inspect my-container

# 测试镜像
docker run --rm -it nginx:latest /bin/bash
```

#### 性能问题

```bash
# 查看资源使用
docker stats my-container

# 查看系统资源
docker system df

# 分析容器进程
docker top my-container
```

### 7.2 日志分析技巧

#### 日志过滤

```bash
# 过滤错误日志
docker logs my-container 2>&1 | grep -i error

# 按时间过滤
docker logs --since="2023-01-01T00:00:00" my-container

# 多容器日志
docker compose logs -f --tail=100
```

### 7.3 性能问题排查

#### 资源瓶颈识别

```bash
# CPU使用率
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}"

# 内存使用率
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}"

# 网络I/O
docker stats --no-stream --format "table {{.Container}}\t{{.NetIO}}"
```

## 8. 最佳实践与优化

### 8.1 容器设计原则

1. **单一职责**: 每个容器只运行一个进程
2. **无状态设计**: 避免在容器中存储状态数据
3. **最小化镜像**: 使用多阶段构建减少镜像大小
4. **健康检查**: 配置适当的健康检查机制

### 8.2 资源优化策略

#### 资源限制

```bash
# 合理设置资源限制
docker run -d \
  --memory=512m \
  --cpus=1.0 \
  --restart=unless-stopped \
  nginx:latest
```

#### 存储优化

```bash
# 使用命名卷
docker run -d -v app-data:/data nginx:latest

# 清理未使用的资源
docker system prune -a
```

### 8.3 运维自动化

#### 自动化脚本

```bash
#!/bin/bash
# 容器健康检查脚本

check_container_health() {
    local container_name=$1
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' $container_name)
    
    if [ "$health_status" != "healthy" ]; then
        echo "Container $container_name is unhealthy: $health_status"
        docker logs --tail=50 $container_name
        return 1
    fi
    
    echo "Container $container_name is healthy"
    return 0
}
```

## 9. 快速上手指南

### 9.1 基础操作流程

1. **拉取镜像**: `docker pull nginx:latest`
2. **创建容器**: `docker run -d --name web nginx:latest`
3. **查看状态**: `docker ps`
4. **查看日志**: `docker logs web`
5. **停止容器**: `docker stop web`
6. **删除容器**: `docker rm web`

### 9.2 常用场景

#### Web应用部署

```bash
# 部署Web应用
docker run -d \
  --name web-app \
  -p 80:80 \
  -v /opt/html:/usr/share/nginx/html \
  --restart=unless-stopped \
  nginx:latest
```

#### 数据库部署

```bash
# 部署数据库
docker run -d \
  --name mysql-db \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=password \
  -v mysql-data:/var/lib/mysql \
  --restart=unless-stopped \
  mysql:8.0
```

## 10. 命令速查表

### 10.1 容器管理命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `docker run` | 创建并运行容器 | `docker run -d nginx:latest` |
| `docker create` | 创建容器 | `docker create --name my-container nginx:latest` |
| `docker start` | 启动容器 | `docker start my-container` |
| `docker stop` | 停止容器 | `docker stop my-container` |
| `docker restart` | 重启容器 | `docker restart my-container` |
| `docker pause` | 暂停容器 | `docker pause my-container` |
| `docker unpause` | 恢复容器 | `docker unpause my-container` |
| `docker kill` | 强制停止容器 | `docker kill my-container` |
| `docker rm` | 删除容器 | `docker rm my-container` |

### 10.2 容器查看命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `docker ps` | 查看运行中的容器 | `docker ps -a` |
| `docker inspect` | 查看容器详细信息 | `docker inspect my-container` |
| `docker logs` | 查看容器日志 | `docker logs -f my-container` |
| `docker stats` | 查看容器资源使用 | `docker stats` |
| `docker top` | 查看容器进程 | `docker top my-container` |

### 10.3 Compose命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `docker compose up` | 启动服务 | `docker compose up -d` |
| `docker compose down` | 停止服务 | `docker compose down` |
| `docker compose ps` | 查看服务状态 | `docker compose ps` |
| `docker compose logs` | 查看服务日志 | `docker compose logs -f` |
| `docker compose restart` | 重启服务 | `docker compose restart` |

## 11. 故障排除FAQ

### 11.1 常见问题

**Q: 容器启动失败怎么办？**
A:

1. 检查镜像是否存在: `docker images`
2. 查看容器日志: `docker logs container-name`
3. 检查端口是否被占用: `netstat -tlnp | grep :port`
4. 验证命令和参数是否正确

**Q: 容器内存使用过高怎么办？**
A:

1. 检查应用是否有内存泄漏
2. 调整内存限制: `--memory=1g`
3. 监控内存使用: `docker stats`
4. 优化应用代码和配置

**Q: 容器网络不通怎么办？**
A:

1. 检查端口映射: `docker port container-name`
2. 验证网络配置: `docker network ls`
3. 检查防火墙设置
4. 测试网络连通性: `docker exec container-name ping host`

**Q: 容器存储空间不足怎么办？**
A:

1. 清理未使用的镜像: `docker image prune`
2. 清理未使用的容器: `docker container prune`
3. 清理未使用的卷: `docker volume prune`
4. 扩展存储空间或使用外部存储

### 11.2 性能优化

**Q: 如何提高容器启动速度？**
A:

1. 使用较小的基础镜像
2. 优化Dockerfile层数
3. 使用多阶段构建
4. 预拉取常用镜像

**Q: 如何减少容器资源消耗？**
A:

1. 合理设置资源限制
2. 使用轻量级基础镜像
3. 优化应用配置
4. 定期清理无用资源

### 11.3 安全加固

**Q: 如何提高容器安全性？**
A:

1. 使用非root用户运行
2. 启用只读根文件系统
3. 限制容器权限
4. 定期更新基础镜像
5. 扫描镜像漏洞

---

## 版本差异说明

- **Docker 20.10+**: 支持BuildKit，Compose V2
- **Docker 19.03+**: 支持GPU支持，多阶段构建优化
- **Docker 18.09+**: 支持BuildKit，健康检查改进

## 参考资源

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [容器最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [OCI运行时规范](https://github.com/opencontainers/runtime-spec)
