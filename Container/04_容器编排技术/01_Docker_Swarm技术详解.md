# Docker Swarm技术详解

## 目录

- [Docker Swarm技术详解](#docker-swarm技术详解)
  - [目录](#目录)
  - [1. Docker Swarm概述](#1-docker-swarm概述)
  - [2. Swarm架构原理](#2-swarm架构原理)
  - [3. Swarm集群管理](#3-swarm集群管理)
  - [4. 服务管理](#4-服务管理)
  - [5. 网络管理](#5-网络管理)
  - [6. 存储管理](#6-存储管理)
  - [7. 安全机制](#7-安全机制)
  - [8. 监控与日志](#8-监控与日志)
  - [9. 故障诊断](#9-故障诊断)
  - [10. 最佳实践](#10-最佳实践)

## 1. Docker Swarm概述

### 1.1 什么是Docker Swarm

Docker Swarm是Docker原生的容器编排工具，提供集群管理和服务编排功能。
它是Docker Engine的内置功能，无需额外安装。

**核心特性**：

- **原生集成**：Docker Engine内置功能
- **简单易用**：与Docker CLI完全兼容
- **高可用性**：支持多节点集群
- **服务发现**：内置DNS服务发现
- **负载均衡**：内置负载均衡器
- **滚动更新**：支持零停机更新

### 1.2 Swarm vs Kubernetes

| 特性 | Docker Swarm | Kubernetes |
|------|-------------|------------|
| **复杂度** | 简单 | 复杂 |
| **学习曲线** | 平缓 | 陡峭 |
| **功能丰富度** | 基础 | 丰富 |
| **社区支持** | 中等 | 强大 |
| **企业采用** | 较少 | 广泛 |
| **适用场景** | 中小型项目 | 大型企业 |

### 1.3 适用场景

**适合使用Swarm的场景**：

- 中小型项目快速部署
- 团队Docker技能较强
- 需要简单的容器编排
- 资源有限的环境
- 快速原型开发

**不适合使用Swarm的场景**：

- 大型复杂应用
- 需要丰富的扩展功能
- 多云环境部署
- 需要强大的生态系统

## 2. Swarm架构原理

### 2.1 整体架构

```text
┌─────────────────────────────────────────────────────────────┐
│                    Swarm集群架构                            │
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Manager    │  │  Manager    │  │  Manager    │         │
│  │   Node      │  │   Node      │  │   Node      │         │
│  │  (Leader)   │  │ (Follower)  │  │ (Follower)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│           │               │               │                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Worker    │  │   Worker    │  │   Worker    │         │
│  │   Node      │  │   Node      │  │   Node      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

**Manager节点**：

- **Raft一致性算法**：保证集群状态一致性
- **调度器**：决定服务在哪个节点运行
- **API服务器**：处理集群管理请求
- **服务发现**：维护服务注册表

**Worker节点**：

- **容器运行时**：运行容器实例
- **代理**：与Manager节点通信
- **网络代理**：处理网络流量

### 2.3 服务模型

```yaml
    # 服务定义示例
version: '3.8'
services:
  web:
    image: nginx:alpine
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
    networks:
      - webnet
    ports:
      - "80:80"

networks:
  webnet:
    driver: overlay
```

## 3. Swarm集群管理

### 3.1 初始化集群

**创建Swarm集群**：

```bash
    # 初始化Swarm集群
docker swarm init --advertise-addr 192.168.1.100

    # 输出示例
Swarm initialized: current node (abc123) is now a manager.

To add a worker to this swarm, run the following command:
    docker swarm join --token SWMTKN-1-xxx 192.168.1.100:2377

To add a manager to this swarm, run the following command:
    docker swarm join-token manager
```

**加入集群**：

```bash
    # Worker节点加入
docker swarm join --token SWMTKN-1-xxx 192.168.1.100:2377

    # Manager节点加入
docker swarm join-token manager
docker swarm join --token SWMTKN-1-xxx 192.168.1.100:2377
```

### 3.2 集群管理命令

**查看集群信息**：

```bash
    # 查看节点信息
docker node ls

    # 查看集群详细信息
docker system info

    # 查看服务信息
docker service ls

    # 查看网络信息
docker network ls
```

**节点管理**：

```bash
    # 查看节点详细信息
docker node inspect <node-id>

    # 更新节点标签
docker node update --label-add env=production <node-id>

    # 排空节点（停止在该节点上运行新任务）
docker node update --availability drain <node-id>

    # 激活节点
docker node update --availability active <node-id>

    # 移除节点
docker node rm <node-id>
```

### 3.3 高可用配置

**多Manager节点配置**：

```bash
    # 在第一个Manager节点初始化
docker swarm init --advertise-addr 192.168.1.100

    # 在其他节点加入为Manager
docker swarm join-token manager
docker swarm join --token SWMTKN-1-xxx 192.168.1.101:2377
docker swarm join --token SWMTKN-1-xxx 192.168.1.102:2377

    # 查看Manager节点状态
docker node ls
```

**自动故障转移**：

```bash
    # 查看当前Leader
docker node ls

    # 模拟Leader节点故障
docker node update --availability drain <leader-node-id>

    # 查看新的Leader选举结果
docker node ls
```

## 4. 服务管理

### 4.1 服务创建与部署

**创建服务**：

```bash
    # 创建简单服务
docker service create --name web --replicas 3 nginx:alpine

    # 创建带端口映射的服务
docker service create \
  --name web \
  --replicas 3 \
  --publish 80:80 \
  nginx:alpine

    # 创建带环境变量的服务
docker service create \
  --name web \
  --replicas 3 \
  --env MYSQL_HOST=mysql \
  --env MYSQL_PORT=3306 \
  nginx:alpine
```

**使用Docker Compose部署**：

```yaml
    # docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx:alpine
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == worker
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
      restart_policy:
        condition: on-failure
    ports:
      - "80:80"
    networks:
      - webnet

  db:
    image: mysql:8.0
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.labels.db == true
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
    environment:
      MYSQL_ROOT_PASSWORD: secret
      MYSQL_DATABASE: app
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - webnet

networks:
  webnet:
    driver: overlay

volumes:
  db_data:
    driver: local
```

**部署服务栈**：

```bash
    # 部署服务栈
docker stack deploy -c docker-compose.yml myapp

    # 查看服务栈
docker stack ls
docker stack services myapp

    # 删除服务栈
docker stack rm myapp
```

### 4.2 服务更新与回滚

**滚动更新**：

```bash
    # 更新服务镜像
docker service update --image nginx:1.20 web

    # 更新服务配置
docker service update \
  --env-add DEBUG=true \
  --replicas 5 \
  web

    # 查看更新状态
docker service ps web
```

**更新配置**：

```yaml
    # 更新配置示例
version: '3.8'
services:
  web:
    image: nginx:1.20
    deploy:
      replicas: 5
      update_config:
        parallelism: 2
        delay: 10s
        failure_action: rollback
        monitor: 60s
        max_failure_ratio: 0.3
      rollback_config:
        parallelism: 1
        delay: 5s
        failure_action: pause
        monitor: 60s
```

**回滚操作**：

```bash
    # 回滚到上一个版本
docker service rollback web

    # 查看回滚状态
docker service ps web
```

### 4.3 服务扩展与收缩

**手动扩缩容**：

```bash
    # 扩展服务
docker service scale web=5

    # 收缩服务
docker service scale web=2

    # 查看服务状态
docker service ps web
```

**自动扩缩容**：

```bash
    # 创建带资源限制的服务
docker service create \
  --name web \
  --replicas 3 \
  --limit-cpu 0.5 \
  --limit-memory 512M \
  --reserve-cpu 0.25 \
  --reserve-memory 256M \
  nginx:alpine
```

## 5. 网络管理

### 5.1 Swarm网络架构

**网络类型**：

- **Overlay网络**：跨节点通信
- **Ingress网络**：外部访问
- **Bridge网络**：单节点通信

**网络创建**：

```bash
    # 创建Overlay网络
docker network create \
  --driver overlay \
  --subnet 10.0.0.0/24 \
  --attachable \
  webnet

    # 创建带加密的Overlay网络
docker network create \
  --driver overlay \
  --opt encrypted \
  webnet

    # 查看网络信息
docker network ls
docker network inspect webnet
```

### 5.2 服务发现

**DNS服务发现**：

```bash
    # 创建服务
docker service create --name web nginx:alpine
docker service create --name db mysql:8.0

    # 在服务中通过服务名访问
    # web服务可以通过 http://db:3306 访问数据库
```

**负载均衡**：

```bash
    # 创建带负载均衡的服务
docker service create \
  --name web \
  --replicas 3 \
  --publish 80:80 \
  nginx:alpine

    # 访问服务（自动负载均衡）
curl http://localhost
```

### 5.3 网络配置

**高级网络配置**：

```yaml
    # docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx:alpine
    networks:
      - frontend
      - backend
    deploy:
      replicas: 3

  db:
    image: mysql:8.0
    networks:
      - backend
    deploy:
      replicas: 1

networks:
  frontend:
    driver: overlay
    config:
      - subnet: 10.0.1.0/24
  backend:
    driver: overlay
    config:
      - subnet: 10.0.2.0/24
    driver_opts:
      encrypted: "true"
```

## 6. 存储管理

### 6.1 数据卷管理

**创建数据卷**：

```bash
    # 创建命名卷
docker volume create db_data

    # 创建带驱动的卷
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw \
  --opt device=:/path/to/nfs \
  nfs_data
```

**在服务中使用卷**：

```yaml
    # docker-compose.yml
version: '3.8'
services:
  db:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql
      - ./config:/etc/mysql/conf.d
    deploy:
      placement:
        constraints:
          - node.labels.storage == ssd

volumes:
  db_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/mysql-data
```

### 6.2 数据持久化策略

**数据备份**：

```bash
    # 备份数据卷
docker run --rm \
  -v db_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db_backup.tar.gz -C /data .

    # 恢复数据卷
docker run --rm \
  -v db_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/db_backup.tar.gz -C /data
```

**数据同步**：

```bash
    # 使用rsync同步数据
docker run --rm \
  -v db_data:/data \
  alpine sh -c "rsync -av /data/ user@backup-server:/backup/"
```

## 7. 安全机制

### 7.1 集群安全

**TLS加密**：

```bash
    # 初始化带TLS的集群
docker swarm init \
  --advertise-addr 192.168.1.100 \
  --cert-expiry 2160h

    # 查看证书信息
docker system info
```

**节点认证**：

```bash
    # 轮换加入令牌
docker swarm join-token --rotate worker
docker swarm join-token --rotate manager
```

### 7.2 服务安全

**网络隔离**：

```yaml
    # 网络隔离配置
version: '3.8'
services:
  web:
    image: nginx:alpine
    networks:
      - frontend
    deploy:
      replicas: 3

  db:
    image: mysql:8.0
    networks:
      - backend
    deploy:
      replicas: 1

networks:
  frontend:
    driver: overlay
  backend:
    driver: overlay
    internal: true  # 内部网络，不允许外部访问
```

**资源限制**：

```bash
    # 创建带资源限制的服务
docker service create \
  --name web \
  --limit-cpu 0.5 \
  --limit-memory 512M \
  --reserve-cpu 0.25 \
  --reserve-memory 256M \
  nginx:alpine
```

## 8. 监控与日志

### 8.1 服务监控

**查看服务状态**：

```bash
    # 查看服务详细信息
docker service inspect web

    # 查看服务任务
docker service ps web

    # 查看服务日志
docker service logs web

    # 实时查看日志
docker service logs -f web
```

**资源监控**：

```bash
    # 查看节点资源使用
docker node ls
docker system df

    # 查看服务资源使用
docker stats $(docker ps -q)
```

### 8.2 日志管理

**日志配置**：

```yaml
    # docker-compose.yml
version: '3.8'
services:
  web:
    image: nginx:alpine
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      replicas: 3
```

**集中化日志**：

```yaml
    # 使用ELK Stack收集日志
version: '3.8'
services:
  web:
    image: nginx:alpine
    logging:
      driver: "gelf"
      options:
        gelf-address: "udp://logstash:12201"
    deploy:
      replicas: 3

  logstash:
    image: logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "12201:12201/udp"
    deploy:
      replicas: 1
```

## 9. 故障诊断

### 9.1 常见问题

**服务无法启动**：

```bash
    # 检查服务状态
docker service ps web

    # 查看服务日志
docker service logs web

    # 检查节点状态
docker node ls

    # 检查资源使用
docker system df
```

**网络连接问题**：

```bash
    # 检查网络配置
docker network ls
docker network inspect webnet

    # 测试网络连接
docker exec -it <container-id> ping <service-name>

    # 检查DNS解析
docker exec -it <container-id> nslookup <service-name>
```

**存储问题**：

```bash
    # 检查数据卷
docker volume ls
docker volume inspect db_data

    # 检查挂载点
docker exec -it <container-id> df -h
```

### 9.2 故障处理流程

**故障诊断步骤**：

1. 检查集群状态
2. 检查节点状态
3. 检查服务状态
4. 查看服务日志
5. 检查网络配置
6. 检查存储配置

**故障处理脚本**：

```bash
#!/bin/bash
    # Swarm故障诊断脚本

echo "=== Swarm集群状态 ==="
docker node ls

echo "=== 服务状态 ==="
docker service ls

echo "=== 网络状态 ==="
docker network ls

echo "=== 存储状态 ==="
docker volume ls

echo "=== 系统资源 ==="
docker system df
```

## 10. 最佳实践

### 10.1 集群设计

**节点规划**：

- Manager节点：3个或5个（奇数）
- Worker节点：根据负载需求
- 节点标签：用于服务放置约束

**网络设计**：

- 使用Overlay网络进行跨节点通信
- 网络隔离：前端、后端、管理网络分离
- 启用网络加密

### 10.2 服务设计

**服务配置**：

```yaml
    # 最佳实践配置
version: '3.8'
services:
  web:
    image: nginx:alpine
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.role == worker
          - node.labels.env == production
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
        monitor: 60s
        max_failure_ratio: 0.3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - frontend
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 10.3 安全最佳实践

**安全配置**：

- 启用TLS加密
- 定期轮换加入令牌
- 使用网络隔离
- 实施资源限制
- 启用日志审计

**访问控制**：

- 限制Manager节点访问
- 使用防火墙规则
- 实施网络策略
- 定期安全审计

### 10.4 运维最佳实践

**监控告警**：

- 设置服务健康检查
- 监控资源使用情况
- 配置日志收集
- 实施告警机制

**备份恢复**：

- 定期备份数据卷
- 备份集群配置
- 测试恢复流程
- 文档化操作流程

**版本管理**：

- 使用版本标签
- 实施滚动更新
- 准备回滚方案
- 测试更新流程

## 总结

Docker Swarm作为Docker原生的容器编排工具，提供了简单易用的集群管理功能。虽然功能相对简单，但对于中小型项目来说是一个不错的选择。在实际使用中，需要根据具体需求选择合适的编排工具，并遵循最佳实践来确保系统的稳定性和安全性。
