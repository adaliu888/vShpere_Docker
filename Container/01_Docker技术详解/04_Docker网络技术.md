# Docker网络技术深度解析

## 目录

- [Docker网络技术深度解析](#docker网络技术深度解析)
  - [目录](#目录)
  - [1. 网络模式与适用场景](#1-网络模式与适用场景)
    - [1.1 网络模式概述](#11-网络模式概述)
      - [网络模式类型](#网络模式类型)
    - [1.2 网络模式对比](#12-网络模式对比)
    - [1.3 选型建议](#13-选型建议)
      - [单机环境](#单机环境)
      - [多机环境](#多机环境)
  - [2. Bridge/Host/None 细节](#2-bridgehostnone-细节)
    - [2.1 Bridge网络详解](#21-bridge网络详解)
      - [Bridge网络架构](#bridge网络架构)
      - [Bridge网络配置](#bridge网络配置)
      - [Bridge网络特性](#bridge网络特性)
    - [2.2 Host网络详解](#22-host网络详解)
      - [Host网络架构](#host网络架构)
      - [Host网络使用](#host网络使用)
      - [Host网络特性](#host网络特性)
    - [2.3 None网络详解](#23-none网络详解)
      - [None网络架构](#none网络架构)
      - [None网络使用](#none网络使用)
      - [None网络特性](#none网络特性)
    - [2.4 端口映射与NAT](#24-端口映射与nat)
      - [端口映射配置](#端口映射配置)
      - [NAT规则查看](#nat规则查看)
  - [3. Overlay 与跨主机互联](#3-overlay-与跨主机互联)
    - [3.1 Overlay网络原理](#31-overlay网络原理)
      - [Overlay网络架构](#overlay网络架构)
      - [Overlay网络创建](#overlay网络创建)
    - [3.2 VXLAN技术](#32-vxlan技术)
      - [VXLAN配置](#vxlan配置)
      - [VXLAN特性](#vxlan特性)
    - [3.3 跨主机通信](#33-跨主机通信)
      - [服务发现](#服务发现)
      - [负载均衡](#负载均衡)
    - [3.4 网络加密](#34-网络加密)
      - [启用网络加密](#启用网络加密)
      - [加密特性](#加密特性)
  - [4. IPv6 与策略控制](#4-ipv6-与策略控制)
    - [4.1 IPv6支持](#41-ipv6支持)
      - [IPv6网络配置](#ipv6网络配置)
      - [IPv6特性](#ipv6特性)
    - [4.2 地址规划](#42-地址规划)
      - [IPv6地址规划](#ipv6地址规划)
      - [地址管理](#地址管理)
    - [4.3 网络策略](#43-网络策略)
      - [网络策略配置](#网络策略配置)
      - [策略类型](#策略类型)
    - [4.4 安全控制](#44-安全控制)
      - [网络安全配置](#网络安全配置)
      - [安全特性](#安全特性)
  - [5. 故障诊断与调优](#5-故障诊断与调优)
    - [5.1 网络诊断工具](#51-网络诊断工具)
      - [基础诊断命令](#基础诊断命令)
      - [高级诊断工具](#高级诊断工具)
    - [5.2 常见问题排查](#52-常见问题排查)
      - [网络连通性问题](#网络连通性问题)
      - [性能问题排查](#性能问题排查)
    - [5.3 性能调优](#53-性能调优)
      - [网络性能优化](#网络性能优化)
      - [容器网络优化](#容器网络优化)
    - [5.4 监控与日志](#54-监控与日志)
      - [网络监控](#网络监控)
      - [日志分析](#日志分析)
  - [6. 与K8s/CNI对接](#6-与k8scni对接)
    - [6.1 CNI插件集成](#61-cni插件集成)
      - [CNI插件配置](#cni插件配置)
      - [与Kubernetes集成](#与kubernetes集成)
    - [6.2 网络策略对接](#62-网络策略对接)
      - [6.2.1 网络策略配置](#621-网络策略配置)
    - [6.3 服务发现](#63-服务发现)
      - [服务配置](#服务配置)
  - [7. 最佳实践与FAQ](#7-最佳实践与faq)
    - [7.1 最佳实践](#71-最佳实践)
      - [网络设计原则](#网络设计原则)
      - [安全最佳实践](#安全最佳实践)
    - [7.2 常见问题](#72-常见问题)
      - [Q: 容器无法访问外网怎么办？](#q-容器无法访问外网怎么办)
      - [Q: 容器间无法通信怎么办？](#q-容器间无法通信怎么办)
      - [Q: 网络性能差怎么办？](#q-网络性能差怎么办)
    - [7.3 性能优化](#73-性能优化)
      - [7.3.1 网络性能优化](#731-网络性能优化)
  - [版本差异说明](#版本差异说明)
  - [参考资源](#参考资源)

## 1. 网络模式与适用场景

### 1.1 网络模式概述

Docker提供多种网络模式，每种模式都有其特定的使用场景和特点：

#### 网络模式类型

- **Bridge**: 默认网络模式，通过网桥连接
- **Host**: 直接使用宿主机网络
- **None**: 无网络接口
- **Overlay**: 跨主机网络通信
- **Macvlan**: 物理网络接口直连
- **IPvlan**: 共享物理接口的虚拟网络

### 1.2 网络模式对比

| 网络模式 | 隔离性 | 性能 | 复杂度 | 适用场景 |
|---------|--------|------|--------|----------|
| Bridge | 中等 | 中等 | 低 | 单机容器通信 |
| Host | 无 | 高 | 低 | 高性能应用 |
| None | 完全 | N/A | 低 | 特殊安全要求 |
| Overlay | 高 | 中等 | 高 | 跨主机通信 |
| Macvlan | 高 | 高 | 中等 | 物理网络集成 |
| IPvlan | 高 | 高 | 中等 | 网络虚拟化 |

### 1.3 选型建议

#### 单机环境

- **开发测试**: Bridge模式
- **高性能应用**: Host模式
- **安全隔离**: None模式

#### 多机环境

- **容器编排**: Overlay模式
- **物理网络**: Macvlan/IPvlan模式
- **混合部署**: 多种模式组合

## 2. Bridge/Host/None 细节

### 2.1 Bridge网络详解

#### Bridge网络架构

```text
┌─────────────────────────────────────────┐
│              Host System                │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Container │    │   Container │    │
│  │      A      │    │      B      │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         └─────────┬─────────┘          │
│                   │                    │
│            ┌─────────────┐             │
│            │   Bridge    │             │
│            │   docker0   │             │
│            └─────────────┘             │
│                   │                    │
│            ┌─────────────┐             │
│            │   Host NIC  │             │
│            └─────────────┘             │
└─────────────────────────────────────────┘
```

#### Bridge网络配置

```bash
    # 创建自定义bridge网络
docker network create \
  --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  --gateway=172.20.0.1 \
  my-bridge-network

    # 查看网络配置
docker network inspect my-bridge-network

    # 连接容器到网络
docker run -d --network my-bridge-network --name web nginx:latest
```

#### Bridge网络特性

- **自动DNS解析**: 容器间可通过名称通信
- **端口映射**: 支持端口转发
- **网络隔离**: 不同bridge网络间隔离
- **动态配置**: 支持运行时网络配置

### 2.2 Host网络详解

#### Host网络架构

```text
┌─────────────────────────────────────────┐
│              Host System                │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Container │    │   Container │    │
│  │      A      │    │      B      │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         └─────────┬─────────┘          │
│                   │                    │
│            ┌─────────────┐             │
│            │   Host NIC  │             │
│            └─────────────┘             │
└─────────────────────────────────────────┘
```

#### Host网络使用

```bash
    # 使用host网络
docker run -d --network host nginx:latest

    # 查看网络配置
docker run --network host --rm alpine ip addr show
```

#### Host网络特性

- **性能最优**: 无网络虚拟化开销
- **端口冲突**: 需要避免端口冲突
- **安全风险**: 容器直接暴露在主机网络
- **简单配置**: 无需额外网络配置

### 2.3 None网络详解

#### None网络架构

```text
┌─────────────────────────────────────────┐
│              Host System                │
│  ┌─────────────┐    ┌─────────────┐    │
│  │   Container │    │   Container │    │
│  │      A      │    │      B      │    │
│  └─────────────┘    └─────────────┘    │
│         │                   │          │
│         └─────────┬─────────┘          │
│                   │                    │
│            ┌─────────────┐             │
│            │   Host NIC  │             │
│            └─────────────┘             │
└─────────────────────────────────────────┘
```

#### None网络使用

```bash
    # 使用none网络
docker run -d --network none --name isolated alpine:latest sleep 3600

    # 手动配置网络
docker exec isolated ip addr add 192.168.1.100/24 dev eth0
docker exec isolated ip link set eth0 up
```

#### None网络特性

- **完全隔离**: 无网络接口
- **手动配置**: 需要手动配置网络
- **安全最高**: 完全网络隔离
- **特殊用途**: 用于特殊安全场景

### 2.4 端口映射与NAT

#### 端口映射配置

```bash
    # 基本端口映射
docker run -d -p 8080:80 nginx:latest

    # 指定IP的端口映射
docker run -d -p 127.0.0.1:8080:80 nginx:latest

    # 随机端口映射
docker run -d -P nginx:latest

    # 查看端口映射
docker port container_name
```

#### NAT规则查看

```bash
    # 查看NAT规则
iptables -t nat -L -n

    # 查看Docker相关规则
iptables -t nat -L DOCKER

    # 查看端口转发规则
iptables -t nat -L PREROUTING
```

## 3. Overlay 与跨主机互联

### 3.1 Overlay网络原理

#### Overlay网络架构

```text
┌─────────────────┐    ┌─────────────────┐
│   Host Node 1   │    │   Host Node 2   │
│  ┌───────────┐  │    │  ┌───────────┐  │
│  │ Container │  │    │  │ Container │  │
│  │     A     │  │    │  │     B     │  │
│  └───────────┘  │    │  └───────────┘  │
│        │        │    │        │        │
│  ┌───────────┐  │    │  ┌───────────┐  │
│  │  VXLAN    │  │◄──►│  │  VXLAN    │  │
│  │  Tunnel   │  │    │  │  Tunnel   │  │
│  └───────────┘  │    │  └───────────┘  │
│        │        │    │        │        │
│  ┌───────────┐  │    │  ┌───────────┐  │
│  │   Host    │  │    │  │   Host    │  │
│  │    NIC    │  │    │  │    NIC    │  │
│  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘
```

#### Overlay网络创建

```bash
    # 初始化Swarm集群
docker swarm init

    # 创建overlay网络
docker network create \
  --driver overlay \
  --subnet=10.0.0.0/24 \
  --attachable \
  my-overlay-network

    # 在overlay网络中运行服务
docker service create \
  --name web \
  --network my-overlay-network \
  --replicas 3 \
  nginx:latest
```

### 3.2 VXLAN技术

#### VXLAN配置

```bash
    # 查看VXLAN接口
ip link show type vxlan

    # 查看VXLAN配置
docker network inspect my-overlay-network

    # 手动创建VXLAN接口
ip link add vxlan0 type vxlan id 100 local 192.168.1.100 dstport 4789
```

#### VXLAN特性

- **封装协议**: UDP封装
- **VNI标识**: 24位VNI标识网络
- **MTU处理**: 需要考虑封装开销
- **负载均衡**: 支持ECMP负载均衡

### 3.3 跨主机通信

#### 服务发现

```bash
    # 创建服务
docker service create \
  --name web \
  --network my-overlay-network \
  --replicas 3 \
  nginx:latest

    # 创建客户端服务
docker service create \
  --name client \
  --network my-overlay-network \
  --replicas 1 \
  alpine:latest ping web
```

#### 负载均衡

```bash
    # 查看服务端点
docker service ps web

    # 查看服务网络
docker service inspect web --format '{{.Endpoint.VirtualIPs}}'
```

### 3.4 网络加密

#### 启用网络加密

```bash
    # 创建加密overlay网络
docker network create \
  --driver overlay \
  --opt encrypted \
  --subnet=10.0.0.0/24 \
  encrypted-network

    # 查看加密配置
docker network inspect encrypted-network
```

#### 加密特性

- **IPSec加密**: 使用IPSec保护数据
- **密钥管理**: 自动密钥轮换
- **性能影响**: 加密会带来性能开销
- **安全增强**: 保护跨主机通信

## 4. IPv6 与策略控制

### 4.1 IPv6支持

#### IPv6网络配置

```bash
    # 创建IPv6网络
docker network create \
  --driver bridge \
  --ipv6 \
  --subnet=2001:db8::/64 \
  --ip-range=2001:db8::/80 \
  ipv6-network

    # 使用IPv6网络
docker run -d --network ipv6-network --name ipv6-app nginx:latest
```

#### IPv6特性

- **双栈支持**: 同时支持IPv4和IPv6
- **地址分配**: 自动IPv6地址分配
- **DNS解析**: 支持IPv6 DNS解析
- **路由配置**: 自动IPv6路由配置

### 4.2 地址规划

#### IPv6地址规划

```bash
    # 查看IPv6地址
docker network inspect ipv6-network

    # 手动分配IPv6地址
docker run -d \
  --network ipv6-network \
  --ip6 2001:db8::100 \
  --name ipv6-app \
  nginx:latest
```

#### 地址管理

- **子网规划**: 合理规划IPv6子网
- **地址分配**: 自动或手动地址分配
- **路由配置**: IPv6路由表配置
- **DNS配置**: IPv6 DNS记录

### 4.3 网络策略

#### 网络策略配置

```bash
    # 创建网络策略
docker network create \
  --driver bridge \
  --opt com.docker.network.bridge.enable_icc=false \
  --opt com.docker.network.bridge.enable_ip_masquerade=false \
  isolated-network

    # 应用网络策略
docker run -d --network isolated-network --name isolated-app nginx:latest
```

#### 策略类型

- **访问控制**: 控制容器间访问
- **流量过滤**: 过滤网络流量
- **端口限制**: 限制端口访问
- **协议控制**: 控制协议类型

### 4.4 安全控制

#### 网络安全配置

```bash
    # 禁用容器间通信
docker network create \
  --driver bridge \
  --opt com.docker.network.bridge.enable_icc=false \
  secure-network

    # 启用IP伪装
docker network create \
  --driver bridge \
  --opt com.docker.network.bridge.enable_ip_masquerade=true \
  masquerade-network
```

#### 安全特性

- **网络隔离**: 容器间网络隔离
- **流量控制**: 网络流量控制
- **访问限制**: 访问权限限制
- **监控审计**: 网络活动监控

## 5. 故障诊断与调优

### 5.1 网络诊断工具

#### 基础诊断命令

```bash
    # 查看网络配置
docker network ls
docker network inspect bridge

    # 查看容器网络
docker exec container_name ip addr show
docker exec container_name ip route show

    # 测试网络连通性
docker exec container_name ping 8.8.8.8
docker exec container_name nslookup google.com
```

#### 高级诊断工具

```bash
    # 网络抓包
docker exec container_name tcpdump -i eth0

    # 网络统计
docker exec container_name netstat -tuln
docker exec container_name ss -tuln

    # 网络性能测试
docker exec container_name iperf3 -c target_host
```

### 5.2 常见问题排查

#### 网络连通性问题

```bash
    # 检查网络配置
docker network inspect network_name

    # 检查端口映射
docker port container_name

    # 检查防火墙规则
iptables -L -n
iptables -t nat -L -n

    # 检查路由表
ip route show
```

#### 性能问题排查

```bash
    # 检查网络延迟
docker exec container_name ping -c 10 target_host

    # 检查带宽
docker exec container_name iperf3 -c target_host

    # 检查丢包率
docker exec container_name ping -c 100 target_host
```

### 5.3 性能调优

#### 网络性能优化

```bash
    # 调整网络缓冲区
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf

    # 调整TCP参数
echo 'net.ipv4.tcp_rmem = 4096 87380 16777216' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 16777216' >> /etc/sysctl.conf

    # 应用配置
sysctl -p
```

#### 容器网络优化

```bash
    # 使用host网络模式
docker run -d --network host nginx:latest

    # 调整MTU大小
docker network create --opt com.docker.network.driver.mtu=9000 large-mtu-network

    # 启用网络加速
docker run -d --network bridge --cap-add=NET_ADMIN nginx:latest
```

### 5.4 监控与日志

#### 网络监控

```bash
    # 监控网络流量
docker stats --format "table {{.Container}}\t{{.NetIO}}"

    # 监控网络连接
docker exec container_name netstat -an | grep ESTABLISHED

    # 监控网络错误
docker logs container_name 2>&1 | grep -i network
```

#### 日志分析

```bash
    # 查看Docker网络日志
journalctl -u docker.service | grep network

    # 查看系统网络日志
dmesg | grep -i network

    # 查看网络错误日志
tail -f /var/log/messages | grep -i network
```

## 6. 与K8s/CNI对接

### 6.1 CNI插件集成

#### CNI插件配置

```json
{
  "cniVersion": "0.3.1",
  "name": "docker-bridge",
  "type": "bridge",
  "bridge": "docker0",
  "isGateway": true,
  "ipMasq": true,
  "ipam": {
    "type": "host-local",
    "subnet": "172.17.0.0/16"
  }
}
```

#### 与Kubernetes集成

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
  hostNetwork: false
```

### 6.2 网络策略对接

#### 6.2.1 网络策略配置

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nginx-policy
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: client
    ports:
    - protocol: TCP
      port: 80
```

### 6.3 服务发现

#### 服务配置

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

## 7. 最佳实践与FAQ

### 7.1 最佳实践

#### 网络设计原则

1. **网络隔离**: 合理使用网络隔离
2. **性能优化**: 根据需求选择网络模式
3. **安全加固**: 实施网络安全策略
4. **监控告警**: 建立网络监控体系

#### 安全最佳实践

```bash
    # 使用网络策略
docker network create \
  --driver bridge \
  --opt com.docker.network.bridge.enable_icc=false \
  secure-network

    # 限制端口暴露
docker run -d -p 127.0.0.1:8080:80 nginx:latest

    # 使用TLS加密
docker run -d --network encrypted-network nginx:latest
```

### 7.2 常见问题

#### Q: 容器无法访问外网怎么办？

A:

1. 检查DNS配置: `docker exec container_name nslookup google.com`
2. 检查路由表: `docker exec container_name ip route show`
3. 检查防火墙: `iptables -L -n`
4. 检查网络模式: `docker network inspect network_name`

#### Q: 容器间无法通信怎么办？

A:

1. 检查网络配置: `docker network inspect network_name`
2. 检查容器网络: `docker exec container_name ip addr show`
3. 检查网络策略: `iptables -L -n`
4. 检查服务发现: `docker exec container_name nslookup service_name`

#### Q: 网络性能差怎么办？

A:

1. 使用host网络模式
2. 调整网络参数
3. 优化MTU大小
4. 使用网络加速

### 7.3 性能优化

#### 7.3.1 网络性能优化

```bash
    # 使用host网络
docker run -d --network host nginx:latest

    # 调整网络参数
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
sysctl -p

    # 使用网络加速
docker run -d --cap-add=NET_ADMIN nginx:latest
```

---

## 版本差异说明

- **Docker 20.10+**: 支持IPv6，网络策略增强
- **Docker 19.03+**: 支持Macvlan/IPvlan
- **Docker 18.09+**: 支持Overlay网络加密

## 参考资源

- [Docker网络文档](https://docs.docker.com/network/)
- [CNI规范](https://github.com/containernetworking/cni)
- [VXLAN规范](https://tools.ietf.org/html/rfc7348)
- [IPv6配置指南](https://docs.docker.com/network/ipv6/)
