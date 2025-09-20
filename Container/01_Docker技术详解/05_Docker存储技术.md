# Docker存储技术深度解析

## 目录

- [Docker存储技术深度解析](#docker存储技术深度解析)
  - [目录](#目录)
  - [1. 存储驱动与特性](#1-存储驱动与特性)
    - [1.1 存储驱动概述](#11-存储驱动概述)
    - [1.2 Overlay2驱动](#12-overlay2驱动)
    - [1.3 其他存储驱动](#13-其他存储驱动)
    - [1.4 驱动选型建议](#14-驱动选型建议)
  - [2. 数据卷与绑定挂载](#2-数据卷与绑定挂载)
    - [2.1 数据卷管理](#21-数据卷管理)
    - [2.2 绑定挂载](#22-绑定挂载)
    - [2.3 tmpfs挂载](#23-tmpfs挂载)
    - [2.4 挂载选项与安全](#24-挂载选项与安全)
  - [3. 性能与一致性](#3-性能与一致性)
    - [3.1 性能优化](#31-性能优化)
    - [3.2 一致性保证](#32-一致性保证)
    - [3.3 监控指标](#33-监控指标)
    - [3.4 调优策略](#34-调优策略)
  - [4. 备份与迁移](#4-备份与迁移)
    - [4.1 数据备份](#41-数据备份)
    - [4.2 镜像迁移](#42-镜像迁移)
    - [4.3 数据迁移](#43-数据迁移)
    - [4.4 灾难恢复](#44-灾难恢复)
  - [5. 故障与恢复](#5-故障与恢复)
    - [5.1 常见故障](#51-常见故障)
    - [5.2 故障诊断](#52-故障诊断)
    - [5.3 恢复策略](#53-恢复策略)
    - [5.4 预防措施](#54-预防措施)
  - [6. 最佳实践与基线](#6-最佳实践与基线)
    - [6.1 最佳实践](#61-最佳实践)
    - [6.2 安全基线](#62-安全基线)
    - [6.3 性能基线](#63-性能基线)
    - [6.4 运维基线](#64-运维基线)

## 1. 存储驱动与特性

### 1.1 存储驱动概述

Docker存储驱动负责管理容器和镜像的数据存储，不同的驱动有不同的特性和适用场景：

#### 存储驱动类型

- **Overlay2**: 推荐驱动，性能优秀
- **Device Mapper**: 企业级存储
- **Btrfs**: 支持快照和压缩
- **ZFS**: 高级文件系统特性
- **AUFS**: 传统联合文件系统

### 1.2 Overlay2驱动

#### Overlay2架构

```text
┌─────────────────────────────────────────┐
│              Container Layer            │ ← 可写层
├─────────────────────────────────────────┤
│              Upper Layer                │ ← 上层目录
├─────────────────────────────────────────┤
│              Lower Layer                │ ← 下层目录
├─────────────────────────────────────────┤
│              Base Layer                 │ ← 基础层
└─────────────────────────────────────────┘
```

#### Overlay2配置

```bash
# 查看当前存储驱动
docker info | grep "Storage Driver"

# 配置Overlay2驱动
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
EOF

# 重启Docker服务
systemctl restart docker
```

#### Overlay2特性

- **性能优秀**: 基于内核原生支持
- **存储效率**: 支持硬链接和共享层
- **兼容性好**: 支持所有Linux发行版
- **功能完整**: 支持所有Docker特性

### 1.3 其他存储驱动

#### Device Mapper驱动

```bash
# 配置Device Mapper
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "devicemapper",
  "storage-opts": [
    "dm.thinpooldev=/dev/mapper/docker-thinpool",
    "dm.use_deferred_removal=true",
    "dm.use_deferred_deletion=true"
  ]
}
EOF
```

#### Btrfs驱动

```bash
# 配置Btrfs
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "btrfs"
}
EOF
```

#### 驱动对比

| 驱动 | 性能 | 稳定性 | 功能 | 推荐场景 |
|------|------|--------|------|----------|
| Overlay2 | 高 | 高 | 完整 | 生产环境 |
| Device Mapper | 中等 | 高 | 完整 | 企业存储 |
| Btrfs | 中等 | 中等 | 丰富 | 开发环境 |
| ZFS | 高 | 高 | 丰富 | 高级用户 |

### 1.4 驱动选型建议

#### 生产环境推荐

1. **Overlay2**: 默认选择，性能优秀
2. **Device Mapper**: 需要企业级存储特性
3. **ZFS**: 需要高级文件系统特性

#### 开发环境推荐

1. **Overlay2**: 简单易用
2. **Btrfs**: 需要快照功能

## 2. 数据卷与绑定挂载

### 2.1 数据卷管理

#### 数据卷创建

```bash
# 创建数据卷
docker volume create my-volume

# 创建带标签的数据卷
docker volume create \
  --label "env=production" \
  --label "app=web" \
  web-data

# 查看数据卷
docker volume ls
docker volume inspect my-volume
```

#### 数据卷使用

```bash
# 使用数据卷
docker run -d \
  --name web \
  -v my-volume:/var/www/html \
  nginx:latest

# 使用只读数据卷
docker run -d \
  --name web \
  -v my-volume:/var/www/html:ro \
  nginx:latest
```

#### 数据卷管理

```bash
# 备份数据卷
docker run --rm \
  -v my-volume:/data \
  -v $(pwd):/backup \
  alpine:latest \
  tar czf /backup/volume-backup.tar.gz -C /data .

# 恢复数据卷
docker run --rm \
  -v my-volume:/data \
  -v $(pwd):/backup \
  alpine:latest \
  tar xzf /backup/volume-backup.tar.gz -C /data

# 删除数据卷
docker volume rm my-volume
```

### 2.2 绑定挂载

#### 绑定挂载使用

```bash
# 基本绑定挂载
docker run -d \
  --name web \
  -v /host/path:/container/path \
  nginx:latest

# 只读绑定挂载
docker run -d \
  --name web \
  -v /host/path:/container/path:ro \
  nginx:latest

# 指定用户和权限
docker run -d \
  --name web \
  -v /host/path:/container/path:ro,Z \
  nginx:latest
```

#### 绑定挂载选项

- **ro**: 只读挂载
- **rw**: 读写挂载（默认）
- **Z**: SELinux共享标签
- **z**: SELinux私有标签

### 2.3 tmpfs挂载

#### tmpfs挂载使用

```bash
# 基本tmpfs挂载
docker run -d \
  --name web \
  --tmpfs /tmp \
  nginx:latest

# 指定tmpfs选项
docker run -d \
  --name web \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  nginx:latest
```

#### tmpfs选项

- **rw**: 读写权限
- **ro**: 只读权限
- **noexec**: 禁止执行
- **nosuid**: 禁止setuid
- **size**: 指定大小

### 2.4 挂载选项与安全

#### SELinux标签

```bash
# 使用SELinux标签
docker run -d \
  --name web \
  -v /host/path:/container/path:Z \
  nginx:latest

# 查看SELinux上下文
ls -Z /host/path
```

#### AppArmor配置

```bash
# 创建AppArmor配置文件
cat > /etc/apparmor.d/docker-web << EOF
#include <tunables/global>

profile docker-web flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  
  # 允许访问挂载点
  /host/path/** rw,
  
  # 拒绝其他访问
  deny /host/other/** rw,
}
EOF

# 加载AppArmor配置
apparmor_parser -r /etc/apparmor.d/docker-web
```

## 3. 性能与一致性

### 3.1 性能优化

#### 存储性能优化

```bash
# 调整I/O调度器
echo mq-deadline > /sys/block/sda/queue/scheduler

# 调整I/O队列深度
echo 128 > /sys/block/sda/queue/nr_requests

# 启用I/O合并
echo 1 > /sys/block/sda/queue/nomerges
```

#### 文件系统优化

```bash
# 调整ext4参数
tune2fs -o journal_data_writeback /dev/sda1

# 调整XFS参数
xfs_admin -c lazy-count=1 /dev/sda1

# 调整Btrfs参数
btrfs filesystem defragment -r /
```

### 3.2 一致性保证

#### 数据一致性

```bash
# 强制同步
docker run --rm \
  -v my-volume:/data \
  alpine:latest \
  sync

# 检查文件系统
docker run --rm \
  -v my-volume:/data \
  alpine:latest \
  fsck /data
```

#### 事务性操作

```bash
# 使用事务性操作
docker run --rm \
  -v my-volume:/data \
  alpine:latest \
  sh -c 'echo "data" > /data/file && sync'
```

### 3.3 监控指标

#### 存储监控

```bash
# 查看存储使用情况
docker system df

# 查看详细存储信息
docker system df -v

# 监控I/O性能
iostat -x 1

# 监控磁盘使用
df -h
```

#### 性能指标

```bash
# 查看I/O统计
docker stats --no-stream

# 查看容器I/O
docker exec container_name iostat -x 1

# 查看系统I/O
iostat -x 1
```

### 3.4 调优策略

#### 存储调优

```bash
# 调整Docker存储参数
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true",
    "overlay2.size=20G"
  ]
}
EOF
```

#### 系统调优

```bash
# 调整内核参数
echo 'vm.dirty_ratio = 15' >> /etc/sysctl.conf
echo 'vm.dirty_background_ratio = 5' >> /etc/sysctl.conf
echo 'vm.dirty_expire_centisecs = 3000' >> /etc/sysctl.conf
sysctl -p
```

## 4. 备份与迁移

### 4.1 数据备份

#### 数据卷备份

```bash
#!/bin/bash
# 数据卷备份脚本

VOLUME_NAME="my-volume"
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据卷
docker run --rm \
  -v $VOLUME_NAME:/data \
  -v $BACKUP_DIR:/backup \
  alpine:latest \
  tar czf /backup/${VOLUME_NAME}_${DATE}.tar.gz -C /data .

echo "Backup completed: ${VOLUME_NAME}_${DATE}.tar.gz"
```

#### 增量备份

```bash
#!/bin/bash
# 增量备份脚本

VOLUME_NAME="my-volume"
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建增量备份
docker run --rm \
  -v $VOLUME_NAME:/data \
  -v $BACKUP_DIR:/backup \
  alpine:latest \
  tar czf /backup/${VOLUME_NAME}_incremental_${DATE}.tar.gz \
  --newer-mtime="1 day ago" -C /data .

echo "Incremental backup completed: ${VOLUME_NAME}_incremental_${DATE}.tar.gz"
```

### 4.2 镜像迁移

#### 镜像导出

```bash
# 导出镜像
docker save -o nginx.tar nginx:latest

# 导出多个镜像
docker save -o images.tar nginx:latest alpine:latest

# 压缩导出
docker save nginx:latest | gzip > nginx.tar.gz
```

#### 镜像导入

```bash
# 导入镜像
docker load -i nginx.tar

# 从压缩文件导入
gunzip -c nginx.tar.gz | docker load
```

### 4.3 数据迁移

#### 容器迁移

```bash
# 导出容器
docker export container_name > container.tar

# 导入容器
docker import container.tar new_image:tag

# 运行新容器
docker run -d --name new_container new_image:tag
```

#### 数据迁移

```bash
# 迁移数据卷
docker run --rm \
  -v old-volume:/old \
  -v new-volume:/new \
  alpine:latest \
  cp -a /old/. /new/
```

### 4.4 灾难恢复

#### 恢复策略

```bash
#!/bin/bash
# 灾难恢复脚本

BACKUP_DIR="/backup"
VOLUME_NAME="my-volume"

# 停止相关容器
docker stop $(docker ps -q --filter "volume=$VOLUME_NAME")

# 恢复数据卷
docker run --rm \
  -v $VOLUME_NAME:/data \
  -v $BACKUP_DIR:/backup \
  alpine:latest \
  tar xzf /backup/${VOLUME_NAME}_latest.tar.gz -C /data

# 重启容器
docker start $(docker ps -aq --filter "volume=$VOLUME_NAME")

echo "Recovery completed"
```

## 5. 故障与恢复

### 5.1 常见故障

#### 存储空间不足

```bash
# 检查存储使用
docker system df

# 清理未使用的资源
docker system prune -a

# 清理特定资源
docker volume prune
docker image prune
docker container prune
```

#### 存储驱动问题

```bash
# 检查存储驱动状态
docker info | grep "Storage Driver"

# 检查存储驱动日志
journalctl -u docker.service | grep storage

# 重启存储服务
systemctl restart docker
```

### 5.2 故障诊断

#### 存储诊断

```bash
# 检查文件系统
df -h
lsblk

# 检查I/O状态
iostat -x 1
iotop

# 检查存储驱动
docker info | grep -A 10 "Storage Driver"
```

#### 数据完整性检查

```bash
# 检查数据卷完整性
docker run --rm \
  -v my-volume:/data \
  alpine:latest \
  find /data -type f -exec md5sum {} \;

# 检查文件系统
docker run --rm \
  -v my-volume:/data \
  alpine:latest \
  fsck /data
```

### 5.3 恢复策略

#### 数据恢复

```bash
# 从备份恢复
docker run --rm \
  -v my-volume:/data \
  -v /backup:/backup \
  alpine:latest \
  tar xzf /backup/volume-backup.tar.gz -C /data

# 验证恢复
docker run --rm \
  -v my-volume:/data \
  alpine:latest \
  ls -la /data
```

#### 系统恢复

```bash
# 重建存储驱动
systemctl stop docker
rm -rf /var/lib/docker
systemctl start docker

# 重新拉取镜像
docker pull nginx:latest
```

### 5.4 预防措施

#### 监控告警

```bash
#!/bin/bash
# 存储监控脚本

THRESHOLD=80
USAGE=$(df /var/lib/docker | awk 'NR==2 {print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
    echo "Storage usage is ${USAGE}%, exceeding threshold ${THRESHOLD}%"
    # 发送告警
    mail -s "Docker Storage Alert" admin@example.com << EOF
Docker storage usage is ${USAGE}%, exceeding threshold ${THRESHOLD}%
Please check and clean up unused resources.
EOF
fi
```

#### 定期维护

```bash
#!/bin/bash
# 定期维护脚本

# 清理未使用的资源
docker system prune -f

# 备份重要数据
docker run --rm \
  -v my-volume:/data \
  -v /backup:/backup \
  alpine:latest \
  tar czf /backup/daily-backup-$(date +%Y%m%d).tar.gz -C /data .

# 检查存储健康
docker system df
```

## 6. 最佳实践与基线

### 6.1 最佳实践

#### 存储设计原则

1. **分离存储**: 数据和系统分离
2. **备份策略**: 定期备份重要数据
3. **监控告警**: 建立存储监控体系
4. **性能优化**: 根据需求优化存储性能

#### 安全最佳实践

```bash
# 使用SELinux标签
docker run -d \
  --name web \
  -v /host/path:/container/path:Z \
  nginx:latest

# 限制挂载权限
docker run -d \
  --name web \
  -v /host/path:/container/path:ro \
  nginx:latest
```

### 6.2 安全基线

#### 存储安全配置

```bash
# 配置存储驱动
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "userns-remap": "default"
}
EOF
```

#### 权限控制

```bash
# 创建专用用户
useradd -r -s /bin/false docker-user

# 配置用户映射
echo "docker-user:100000:65536" >> /etc/subuid
echo "docker-user:100000:65536" >> /etc/subgid
```

### 6.3 性能基线

#### 性能配置

```bash
# 调整内核参数
cat >> /etc/sysctl.conf << EOF
# Docker存储优化
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.dirty_expire_centisecs = 3000
vm.dirty_writeback_centisecs = 500
EOF

sysctl -p
```

#### 存储优化

```bash
# 调整I/O调度器
echo mq-deadline > /sys/block/sda/queue/scheduler

# 调整队列深度
echo 128 > /sys/block/sda/queue/nr_requests
```

### 6.4 运维基线

#### 监控配置

```bash
# 配置存储监控
cat > /etc/docker/daemon.json << EOF
{
  "metrics-addr": "0.0.0.0:9323",
  "experimental": true
}
EOF
```

#### 日志配置

```bash
# 配置日志驱动
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
```

---

## 版本差异说明

- **Docker 20.10+**: 支持Overlay2优化，存储性能提升
- **Docker 19.03+**: 支持用户命名空间，存储安全增强
- **Docker 18.09+**: 支持存储驱动优化，性能改进

## 参考资源

- [Docker存储驱动文档](https://docs.docker.com/storage/storagedriver/)
- [Overlay2驱动文档](https://docs.docker.com/storage/storagedriver/overlayfs-driver/)
- [数据卷管理文档](https://docs.docker.com/storage/volumes/)
- [存储最佳实践](https://docs.docker.com/storage/)
