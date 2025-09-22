# Docker安全机制深度解析

> 版本锚点与证据落盘（新增）：本文涉及 Docker/OCI/运行时版本请统一参考《2025年技术标准最终对齐报告.md》。与安全相关的扫描/签名/审计输出建议按照 `vShpere_VMware/09_安全与合规管理/Artifacts_Index.md` 的目录结构归档到 `artifacts/`，并生成 `manifest.json` 与 `*.sha256`。

## 目录

- [Docker安全机制深度解析](#docker安全机制深度解析)
  - [目录](#目录)
  - [1. 隔离与权限模型](#1-隔离与权限模型)
    - [1.1 命名空间隔离](#11-命名空间隔离)
    - [1.2 控制组限制](#12-控制组限制)
    - [1.3 能力控制](#13-能力控制)
    - [1.4 系统调用过滤](#14-系统调用过滤)
    - [1.5 强制访问控制](#15-强制访问控制)
  - [2. 镜像与供应链安全](#2-镜像与供应链安全)
    - [2.1 镜像签名验证](#21-镜像签名验证)
    - [2.2 供应链安全](#22-供应链安全)
    - [2.3 漏洞扫描](#23-漏洞扫描)
    - [2.4 安全策略](#24-安全策略)
  - [3. 运行时与网络安全](#3-运行时与网络安全)
    - [3.1 运行时安全](#31-运行时安全)
    - [3.2 网络安全](#32-网络安全)
    - [3.3 资源限制](#33-资源限制)
    - [3.4 监控审计](#34-监控审计)
  - [4. Rootless 与沙箱运行时](#4-rootless-与沙箱运行时)
    - [4.1 Rootless模式](#41-rootless模式)
    - [4.2 沙箱运行时](#42-沙箱运行时)
    - [4.3 安全边界](#43-安全边界)
    - [4.4 性能权衡](#44-性能权衡)
  - [5. 安全基线与合规](#5-安全基线与合规)
    - [5.1 安全基线](#51-安全基线)
    - [5.2 合规要求](#52-合规要求)
    - [5.3 审计日志](#53-审计日志)
    - [5.4 密钥管理](#54-密钥管理)
  - [6. 故障与应急响应](#6-故障与应急响应)
    - [6.1 安全事件检测](#61-安全事件检测)
    - [6.2 应急响应流程](#62-应急响应流程)
    - [6.3 证据保全](#63-证据保全)
    - [6.4 恢复策略](#64-恢复策略)
  - [7. 最佳实践与工具](#7-最佳实践与工具)
    - [7.1 安全最佳实践](#71-安全最佳实践)
    - [7.2 安全工具](#72-安全工具)
    - [7.3 加固脚本](#73-加固脚本)
    - [7.4 监控告警](#74-监控告警)

## 1. 隔离与权限模型

### 1.1 命名空间隔离

#### 命名空间类型

Docker使用Linux命名空间提供容器隔离：

- **PID Namespace**: 进程ID隔离
- **Network Namespace**: 网络隔离
- **Mount Namespace**: 文件系统隔离
- **UTS Namespace**: 主机名隔离
- **IPC Namespace**: 进程间通信隔离
- **User Namespace**: 用户ID隔离

#### 命名空间配置

```bash
    # 查看容器命名空间
docker inspect container_name | grep -A 10 "Namespaces"

    # 使用特定命名空间
docker run -d \
  --pid=host \
  --network=host \
  --uts=host \
  nginx:latest

    # 禁用用户命名空间
docker run -d --userns=host nginx:latest
```

#### 命名空间安全

```bash
    # 检查命名空间配置
docker run --rm --privileged alpine:latest nsenter -t 1 -m -u -i -n -p ps aux

    # 验证隔离效果
docker run --rm alpine:latest ps aux
```

### 1.2 控制组限制

#### cgroups配置

```bash
    # 设置CPU限制
docker run -d --cpus="1.5" nginx:latest

    # 设置内存限制
docker run -d --memory=512m nginx:latest

    # 设置I/O限制
docker run -d \
  --device-read-bps /dev/sda:1mb \
  --device-write-bps /dev/sda:1mb \
  nginx:latest
```

#### cgroups安全

```bash
    # 查看cgroups配置
docker inspect container_name | grep -A 10 "Cgroup"

    # 验证资源限制
docker stats container_name
```

### 1.3 能力控制

#### 能力管理

```bash
    # 添加能力
docker run -d --cap-add=NET_ADMIN nginx:latest

    # 删除能力
docker run -d --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx:latest

    # 查看能力
docker inspect container_name | grep -A 5 "CapAdd\|CapDrop"
```

#### 安全能力配置

```bash
    # 最小能力配置
docker run -d \
  --cap-drop=ALL \
  --cap-add=CHOWN \
  --cap-add=SETGID \
  --cap-add=SETUID \
  nginx:latest
```

### 1.4 系统调用过滤

#### seccomp配置

```bash
    # 使用默认seccomp配置
docker run -d --security-opt seccomp=default nginx:latest

    # 禁用seccomp
docker run -d --security-opt seccomp=unconfined nginx:latest

    # 使用自定义seccomp配置
docker run -d --security-opt seccomp=seccomp-profile.json nginx:latest
```

#### 自定义seccomp配置

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_X32"
  ],
  "syscalls": [
    {
      "names": [
        "accept",
        "accept4",
        "access",
        "alarm",
        "bind",
        "brk",
        "capget",
        "capset",
        "chdir",
        "chmod",
        "chown",
        "chroot",
        "clock_getres",
        "clock_gettime",
        "clock_nanosleep",
        "close",
        "connect",
        "copy_file_range",
        "creat",
        "dup",
        "dup2",
        "dup3",
        "epoll_create",
        "epoll_create1",
        "epoll_ctl",
        "epoll_pwait",
        "epoll_wait",
        "eventfd",
        "eventfd2",
        "execve",
        "execveat",
        "exit",
        "exit_group",
        "faccessat",
        "fadvise64",
        "fallocate",
        "fanotify_mark",
        "fchdir",
        "fchmod",
        "fchmodat",
        "fchown",
        "fchownat",
        "fcntl",
        "fcntl64",
        "fdatasync",
        "fgetxattr",
        "flistxattr",
        "flock",
        "fork",
        "fremovexattr",
        "fsetxattr",
        "fstat",
        "fstat64",
        "fstatat64",
        "fstatfs",
        "fstatfs64",
        "fsync",
        "ftruncate",
        "ftruncate64",
        "futex",
        "futimesat",
        "getcpu",
        "getcwd",
        "getdents",
        "getdents64",
        "getegid",
        "getegid32",
        "geteuid",
        "geteuid32",
        "getgid",
        "getgid32",
        "getgroups",
        "getgroups32",
        "getpeername",
        "getpgid",
        "getpgrp",
        "getpid",
        "getppid",
        "getpriority",
        "getrandom",
        "getresgid",
        "getresgid32",
        "getresuid",
        "getresuid32",
        "getrlimit",
        "get_robust_list",
        "getrusage",
        "getsid",
        "getsockname",
        "getsockopt",
        "get_thread_area",
        "gettid",
        "gettimeofday",
        "getuid",
        "getuid32",
        "getxattr",
        "getxgid",
        "getxpid",
        "getxuid",
        "inotify_add_watch",
        "inotify_init",
        "inotify_init1",
        "inotify_rm_watch",
        "io_cancel",
        "ioctl",
        "io_destroy",
        "io_getevents",
        "ioprio_get",
        "ioprio_set",
        "io_setup",
        "io_submit",
        "ipc",
        "kill",
        "lchown",
        "lchown32",
        "lgetxattr",
        "link",
        "linkat",
        "listen",
        "listxattr",
        "llistxattr",
        "lremovexattr",
        "lseek",
        "lsetxattr",
        "lstat",
        "lstat64",
        "madvise",
        "mincore",
        "mkdir",
        "mkdirat",
        "mknod",
        "mknodat",
        "mlock",
        "mlockall",
        "mmap",
        "mmap2",
        "mprotect",
        "mq_getsetattr",
        "mq_notify",
        "mq_open",
        "mq_timedreceive",
        "mq_timedsend",
        "mq_unlink",
        "mremap",
        "msgctl",
        "msgget",
        "msgrcv",
        "msgsnd",
        "msync",
        "munlock",
        "munlockall",
        "munmap",
        "nanosleep",
        "newfstatat",
        "_newselect",
        "open",
        "openat",
        "pause",
        "pipe",
        "pipe2",
        "poll",
        "ppoll",
        "prctl",
        "pread64",
        "preadv",
        "prlimit64",
        "pselect6",
        "ptrace",
        "pwrite64",
        "pwritev",
        "read",
        "readahead",
        "readlink",
        "readlinkat",
        "readv",
        "recv",
        "recvfrom",
        "recvmmsg",
        "recvmsg",
        "remap_file_pages",
        "removexattr",
        "rename",
        "renameat",
        "renameat2",
        "restart_syscall",
        "rmdir",
        "rt_sigaction",
        "rt_sigpending",
        "rt_sigprocmask",
        "rt_sigqueueinfo",
        "rt_sigreturn",
        "rt_sigsuspend",
        "rt_sigtimedwait",
        "rt_tgsigqueueinfo",
        "sched_get_priority_max",
        "sched_get_priority_min",
        "sched_getaffinity",
        "sched_getparam",
        "sched_getscheduler",
        "sched_rr_get_interval",
        "sched_setaffinity",
        "sched_setparam",
        "sched_setscheduler",
        "sched_yield",
        "seccomp",
        "select",
        "sendfile",
        "sendfile64",
        "sendmmsg",
        "sendmsg",
        "sendto",
        "setfsgid",
        "setfsgid32",
        "setfsuid",
        "setfsuid32",
        "setgid",
        "setgid32",
        "setgroups",
        "setgroups32",
        "setitimer",
        "setpgid",
        "setpriority",
        "setregid",
        "setregid32",
        "setresgid",
        "setresgid32",
        "setresuid",
        "setresuid32",
        "setreuid",
        "setreuid32",
        "setrlimit",
        "set_robust_list",
        "setsid",
        "setsockopt",
        "set_thread_area",
        "set_tid_address",
        "setuid",
        "setuid32",
        "setxattr",
        "sigaction",
        "sigaltstack",
        "signal",
        "signalfd",
        "signalfd4",
        "sigpending",
        "sigprocmask",
        "sigreturn",
        "sigsuspend",
        "sigtimedwait",
        "sigwait",
        "sigwaitinfo",
        "socket",
        "socketcall",
        "socketpair",
        "splice",
        "stat",
        "stat64",
        "statfs",
        "statfs64",
        "symlink",
        "symlinkat",
        "sync",
        "sync_file_range",
        "syncfs",
        "sysinfo",
        "syslog",
        "tee",
        "tgkill",
        "time",
        "timer_create",
        "timer_delete",
        "timer_getoverrun",
        "timer_gettime",
        "timer_settime",
        "timerfd_create",
        "timerfd_gettime",
        "timerfd_settime",
        "times",
        "tkill",
        "truncate",
        "truncate64",
        "ugetrlimit",
        "umask",
        "uname",
        "unlink",
        "unlinkat",
        "utime",
        "utimensat",
        "utimes",
        "vfork",
        "vmsplice",
        "wait4",
        "waitid",
        "waitpid",
        "write",
        "writev"
      ],
      "action": "SCMP_ACT_ALLOW",
      "args": [],
      "comment": "",
      "includes": {},
      "excludes": {}
    }
  ]
}
```

### 1.5 强制访问控制

#### SELinux配置

```bash
    # 启用SELinux
setenforce 1

    # 查看SELinux状态
sestatus

    # 使用SELinux标签
docker run -d \
  --security-opt label:type:container_t \
  nginx:latest
```

#### AppArmor配置

```bash
    # 查看AppArmor状态
aa-status

    # 使用AppArmor配置
docker run -d \
  --security-opt apparmor=docker-default \
  nginx:latest
```

#### 自定义AppArmor配置

```bash
    # 创建AppArmor配置文件
cat > /etc/apparmor.d/docker-web << EOF
#include <tunables/global>

profile docker-web flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  
  # 允许访问网络
  network,
  
  # 允许访问文件系统
  /var/www/html/** rw,
  
  # 拒绝其他访问
  deny /etc/passwd r,
  deny /etc/shadow r,
  deny /etc/group r,
}
EOF

    # 加载AppArmor配置
apparmor_parser -r /etc/apparmor.d/docker-web

    # 使用自定义配置
docker run -d \
  --security-opt apparmor=docker-web \
  nginx:latest
```

## 2. 镜像与供应链安全

### 2.1 镜像签名验证

#### Docker Content Trust

```bash
    # 启用内容信任
export DOCKER_CONTENT_TRUST=1

    # 推送签名镜像
docker push myregistry/myapp:latest

    # 拉取签名镜像
docker pull myregistry/myapp:latest
```

#### 镜像签名配置

```bash
    # 配置Notary服务器
export DOCKER_CONTENT_TRUST_SERVER=https://notary.docker.io

    # 初始化Notary
notary init myregistry/myapp

    # 添加签名
notary add myregistry/myapp latest myapp.tar

    # 发布签名
notary publish myregistry/myapp
```

### 2.2 供应链安全

#### SBOM生成

```bash
    # 使用syft生成SBOM
syft myapp:latest -o spdx-json > sbom.json

    # 使用trivy扫描
trivy image --format json myapp:latest > scan.json
```

#### 供应链验证

```bash
    # 验证镜像完整性
docker trust inspect myregistry/myapp:latest

    # 检查镜像历史
docker history myapp:latest

    # 验证镜像签名
docker trust verify myregistry/myapp:latest
```

### 2.3 漏洞扫描

#### 集成扫描工具

```bash
    # 使用Trivy扫描
trivy image --severity HIGH,CRITICAL myapp:latest

    # 使用Clair扫描
clair-scanner --ip 192.168.1.100 myapp:latest

    # 使用Anchore扫描
anchore-cli image add myapp:latest
anchore-cli image vuln myapp:latest all
```

#### CI/CD集成

```yaml
    # GitHub Actions示例
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'myapp:latest'
    format: 'sarif'
    output: 'trivy-results.sarif'
```

### 2.4 安全策略

#### 镜像安全策略

```yaml
    # 安全策略示例
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-policy
data:
  policy.yaml: |
    rules:
    - name: "no-root"
      description: "禁止以root用户运行"
      match:
        - "USER root"
    - name: "no-privileged"
      description: "禁止特权模式"
      match:
        - "privileged: true"
    - name: "no-insecure-registries"
      description: "禁止使用不安全仓库"
      match:
        - "registry: http://"
```

## 3. 运行时与网络安全

### 3.1 运行时安全

#### 只读根文件系统

```bash
    # 使用只读根文件系统
docker run -d \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /var/run \
  nginx:latest
```

#### 用户权限控制

```bash
    # 使用非root用户
docker run -d \
  --user 1000:1000 \
  nginx:latest

    # 创建专用用户
docker run -d \
  --user $(id -u):$(id -g) \
  nginx:latest
```

#### 资源限制

```bash
    # 设置资源限制
docker run -d \
  --memory=512m \
  --cpus=1.0 \
  --pids-limit=100 \
  nginx:latest
```

### 3.2 网络安全

#### 网络隔离

```bash
    # 使用自定义网络
docker network create --driver bridge secure-network

    # 运行容器
docker run -d \
  --network secure-network \
  nginx:latest
```

#### 端口限制

```bash
    # 限制端口暴露
docker run -d \
  -p 127.0.0.1:8080:80 \
  nginx:latest

    # 使用随机端口
docker run -d -P nginx:latest
```

#### 网络策略

```bash
    # 禁用容器间通信
docker network create \
  --driver bridge \
  --opt com.docker.network.bridge.enable_icc=false \
  secure-network
```

### 3.3 资源限制

#### 内存限制

```bash
    # 设置内存限制
docker run -d \
  --memory=512m \
  --memory-swap=1g \
  nginx:latest

    # 设置内存预留
docker run -d \
  --memory-reservation=256m \
  nginx:latest
```

#### CPU限制

```bash
    # 设置CPU限制
docker run -d \
  --cpus="1.5" \
  --cpu-shares=512 \
  nginx:latest

    # 设置CPU亲和性
docker run -d \
  --cpuset-cpus="0,1" \
  nginx:latest
```

### 3.4 监控审计

#### 审计日志

```bash
    # 启用审计日志
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  nginx:latest
```

#### 监控配置

```bash
    # 配置监控
docker run -d \
  --restart=unless-stopped \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  nginx:latest
```

## 4. Rootless 与沙箱运行时

### 4.1 Rootless模式

#### Rootless配置

```bash
    # 安装Rootless Docker
dockerd-rootless-setuptool.sh install

    # 设置环境变量
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock

    # 验证Rootless模式
docker info | grep -i rootless
```

#### Rootless特性

- **无特权运行**: 不需要root权限
- **用户隔离**: 每个用户独立的Docker实例
- **安全增强**: 减少攻击面
- **性能影响**: 网络性能可能下降

### 4.2 沙箱运行时

#### Kata Containers

```bash
    # 安装Kata Containers
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

    # 配置Kata运行时
cat > /etc/docker/daemon.json << EOF
{
  "runtimes": {
    "kata": {
      "path": "/usr/bin/kata-runtime"
    }
  }
}
EOF
```

#### gVisor

```bash
    # 安装gVisor
curl -fsSL https://gvisor.dev/archive.key | sudo apt-key add -
echo "deb https://storage.googleapis.com/gvisor/releases release main" | sudo tee /etc/apt/sources.list.d/gvisor.list
sudo apt-get update && sudo apt-get install -y runsc

    # 配置gVisor运行时
cat > /etc/docker/daemon.json << EOF
{
  "runtimes": {
    "runsc": {
      "path": "/usr/bin/runsc"
    }
  }
}
EOF
```

### 4.3 安全边界

#### 隔离级别对比

| 运行时 | 隔离级别 | 性能 | 兼容性 | 安全 |
|--------|----------|------|--------|------|
| runc | 中等 | 高 | 高 | 中等 |
| Kata | 高 | 中等 | 高 | 高 |
| gVisor | 高 | 中等 | 中等 | 高 |

### 4.4 性能权衡

#### 性能测试

```bash
    # 测试不同运行时性能
docker run --rm --runtime=runc alpine:latest time dd if=/dev/zero of=/tmp/test bs=1M count=1000
docker run --rm --runtime=kata alpine:latest time dd if=/dev/zero of=/tmp/test bs=1M count=1000
docker run --rm --runtime=runsc alpine:latest time dd if=/dev/zero of=/tmp/test bs=1M count=1000
```

## 5. 安全基线与合规

### 5.1 安全基线

#### 基础安全配置

```bash
    # 配置Docker安全选项
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
EOF
```

#### 系统安全配置

```bash
    # 配置系统安全参数
echo 'net.ipv4.ip_forward = 0' >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.send_redirects = 0' >> /etc/sysctl.conf
echo 'net.ipv4.conf.default.send_redirects = 0' >> /etc/sysctl.conf
echo 'net.ipv4.conf.all.accept_redirects = 0' >> /etc/sysctl.conf
echo 'net.ipv4.conf.default.accept_redirects = 0' >> /etc/sysctl.conf
sysctl -p
```

### 5.2 合规要求

#### CIS Docker基准

```bash
    # 安装CIS基准检查工具
pip install docker-bench-security

    # 运行CIS基准检查
docker-bench-security
```

#### 合规检查脚本

```bash
#!/bin/bash
    # 合规检查脚本

echo "=== Docker安全合规检查 ==="

    # 检查Docker版本
echo "Docker版本:"
docker version

    # 检查Docker配置
echo "Docker配置:"
docker info | grep -E "(Storage Driver|Logging Driver|Cgroup Driver)"

    # 检查容器配置
echo "容器安全配置:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    # 检查镜像安全
echo "镜像安全:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### 5.3 审计日志

#### 日志配置

```bash
    # 配置审计日志
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "labels": "service,environment"
  }
}
EOF
```

#### 日志分析

```bash
    # 分析Docker日志
docker logs container_name 2>&1 | grep -E "(ERROR|WARN|CRITICAL)"

    # 分析系统日志
journalctl -u docker.service | grep -E "(ERROR|WARN|CRITICAL)"
```

### 5.4 密钥管理

#### 密钥存储

```bash
    # 使用Docker Secrets
echo "mysecret" | docker secret create my_secret -

    # 使用密钥
docker service create \
  --secret my_secret \
  --name web \
  nginx:latest
```

#### 密钥轮换

```bash
    # 创建新密钥
echo "newsecret" | docker secret create my_secret_v2 -

    # 更新服务
docker service update \
  --secret-rm my_secret \
  --secret-add my_secret_v2 \
  web
```

## 6. 故障与应急响应

### 6.1 安全事件检测

#### 异常检测

```bash
#!/bin/bash
    # 安全事件检测脚本

    # 检查异常容器
echo "检查异常容器:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -v "Up"

    # 检查异常网络连接
echo "检查异常网络连接:"
docker exec container_name netstat -an | grep ESTABLISHED

    # 检查异常进程
echo "检查异常进程:"
docker exec container_name ps aux | grep -v "PID"
```

#### 入侵检测

```bash
    # 检查文件完整性
docker exec container_name find / -type f -newer /tmp/baseline -exec ls -la {} \;

    # 检查网络异常
docker exec container_name netstat -an | grep -E "(LISTEN|ESTABLISHED)"

    # 检查系统调用
docker exec container_name strace -p 1
```

### 6.2 应急响应流程

#### 响应步骤

1. **隔离**: 立即隔离受影响的容器
2. **分析**: 分析攻击向量和影响范围
3. **遏制**: 阻止攻击扩散
4. **恢复**: 恢复系统正常运行
5. **总结**: 总结经验教训

#### 应急脚本

```bash
#!/bin/bash
    # 应急响应脚本

CONTAINER_NAME=$1

if [ -z "$CONTAINER_NAME" ]; then
    echo "Usage: $0 <container_name>"
    exit 1
fi

echo "=== 应急响应开始 ==="

    # 1. 隔离容器
echo "1. 隔离容器:"
docker stop $CONTAINER_NAME
docker network disconnect bridge $CONTAINER_NAME

    # 2. 保存证据
echo "2. 保存证据:"
docker export $CONTAINER_NAME > ${CONTAINER_NAME}_evidence.tar
docker logs $CONTAINER_NAME > ${CONTAINER_NAME}_logs.txt

    # 3. 分析容器
echo "3. 分析容器:"
docker inspect $CONTAINER_NAME > ${CONTAINER_NAME}_inspect.json

echo "=== 应急响应完成 ==="
```

### 6.3 证据保全

#### 证据收集

```bash
    # 收集容器证据
docker export container_name > container_evidence.tar
docker logs container_name > container_logs.txt
docker inspect container_name > container_inspect.json

    # 收集系统证据
dmesg > system_dmesg.txt
journalctl -u docker.service > docker_service_logs.txt
```

#### 证据分析

```bash
    # 分析容器文件系统
tar -tf container_evidence.tar | grep -E "(bin|sbin|usr|etc)"

    # 分析日志
grep -E "(ERROR|WARN|CRITICAL)" container_logs.txt

    # 分析网络连接
grep -E "(ESTABLISHED|LISTEN)" container_logs.txt
```

### 6.4 恢复策略

#### 系统恢复

```bash
    # 停止所有容器
docker stop $(docker ps -q)

    # 清理受感染的容器
docker rm $(docker ps -aq)

    # 重新部署
docker-compose up -d
```

#### 数据恢复

```bash
    # 从备份恢复数据
docker run --rm \
  -v my-volume:/data \
  -v /backup:/backup \
  alpine:latest \
  tar xzf /backup/volume-backup.tar.gz -C /data
```

## 7. 最佳实践与工具

### 7.1 安全最佳实践

#### 容器安全原则

1. **最小权限**: 使用最小权限运行容器
2. **最小镜像**: 使用最小化的基础镜像
3. **定期更新**: 定期更新基础镜像和依赖
4. **监控审计**: 建立完善的监控审计体系

#### 安全配置模板

```dockerfile
    # 安全Dockerfile模板
FROM alpine:latest

    # 创建非root用户
RUN adduser -D -s /bin/sh appuser

    # 设置工作目录
WORKDIR /app

    # 复制应用文件
COPY --chown=appuser:appuser . /app

    # 切换到非root用户
USER appuser

    # 设置健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

    # 启动应用
CMD ["/app/myapp"]
```

### 7.2 安全工具

#### 安全扫描工具

```bash
    # 安装Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

    # 扫描镜像
trivy image nginx:latest

    # 扫描文件系统
trivy fs /path/to/directory
```

#### 安全监控工具

```bash
    # 安装Falco
curl -s https://falco.org/repo/falcosecurity-3672BA8F.asc | apt-key add -
echo "deb https://download.falco.org/packages/deb stable main" | tee -a /etc/apt/sources.list.d/falcosecurity.list
apt-get update && apt-get install -y falco

    # 启动Falco
systemctl start falco
```

### 7.3 加固脚本

#### 系统加固脚本

```bash
#!/bin/bash
    # Docker系统加固脚本

echo "=== Docker系统加固开始 ==="

    # 1. 配置Docker安全选项
cat > /etc/docker/daemon.json << EOF
{
  "storage-driver": "overlay2",
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
EOF

    # 2. 配置系统安全参数
cat >> /etc/sysctl.conf << EOF
    # Docker安全参数
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
EOF

    # 3. 应用配置
sysctl -p
systemctl restart docker

echo "=== Docker系统加固完成 ==="
```

### 7.4 监控告警

#### 安全监控脚本

```bash
#!/bin/bash
    # 安全监控脚本

    # 检查异常容器
ABNORMAL_CONTAINERS=$(docker ps --format "{{.Names}}" | grep -v "Up")
if [ ! -z "$ABNORMAL_CONTAINERS" ]; then
    echo "发现异常容器: $ABNORMAL_CONTAINERS"
    # 发送告警
fi

    # 检查异常网络连接
ABNORMAL_CONNECTIONS=$(docker exec container_name netstat -an | grep -E "(ESTABLISHED|LISTEN)" | wc -l)
if [ $ABNORMAL_CONNECTIONS -gt 100 ]; then
    echo "发现异常网络连接: $ABNORMAL_CONNECTIONS"
    # 发送告警
fi

    # 检查异常进程
ABNORMAL_PROCESSES=$(docker exec container_name ps aux | grep -v "PID" | wc -l)
if [ $ABNORMAL_PROCESSES -gt 50 ]; then
    echo "发现异常进程: $ABNORMAL_PROCESSES"
    # 发送告警
fi
```

---

## 版本差异说明

- **Docker 20.10+**: 支持Rootless模式，安全增强
- **Docker 19.03+**: 支持用户命名空间，安全隔离改进
- **Docker 18.09+**: 支持seccomp配置，安全策略增强

## 参考资源

- [Docker安全文档](https://docs.docker.com/engine/security/)
- [CIS Docker基准](https://www.cisecurity.org/benchmark/docker)
- [Trivy安全扫描](https://github.com/aquasecurity/trivy)
- [Falco运行时安全](https://falco.org/)
