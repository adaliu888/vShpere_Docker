    # Kubernetes Pod管理技术详解

## 目录

- [Kubernetes Pod管理技术详解](#kubernetes-pod管理技术详解)
  - [目录](#目录)
  - [1. Pod基础概念](#1-pod基础概念)
    - [1.1 Pod定义与特性](#11-pod定义与特性)
    - [1.2 Pod生命周期](#12-pod生命周期)
    - [1.3 Pod与容器的关系](#13-pod与容器的关系)
  - [2. Pod创建与管理](#2-pod创建与管理)
    - [2.1 Pod创建方式](#21-pod创建方式)
    - [2.2 Pod配置管理](#22-pod配置管理)
    - [2.3 Pod更新与删除](#23-pod更新与删除)
  - [3. Pod资源管理](#3-pod资源管理)
    - [3.1 资源请求与限制](#31-资源请求与限制)
    - [3.2 资源配额管理](#32-资源配额管理)
    - [3.3 资源监控与调优](#33-资源监控与调优)
  - [4. Pod健康检查](#4-pod健康检查)
    - [4.1 探针类型](#41-探针类型)
    - [4.2 探针配置](#42-探针配置)
    - [4.3 健康检查最佳实践](#43-健康检查最佳实践)
  - [5. Pod安全策略](#5-pod安全策略)
    - [5.1 Pod安全标准](#51-pod安全标准)
    - [5.2 安全上下文配置](#52-安全上下文配置)
    - [5.3 网络策略](#53-网络策略)
  - [6. Pod调度与亲和性](#6-pod调度与亲和性)
    - [6.1 节点选择器](#61-节点选择器)
    - [6.2 亲和性与反亲和性](#62-亲和性与反亲和性)
    - [6.3 污点与容忍](#63-污点与容忍)
  - [7. Pod存储管理](#7-pod存储管理)
    - [7.1 卷类型](#71-卷类型)
    - [7.2 持久化存储](#72-持久化存储)
    - [7.3 存储类管理](#73-存储类管理)
  - [8. Pod网络管理](#8-pod网络管理)
    - [8.1 网络模型](#81-网络模型)
    - [8.2 服务发现](#82-服务发现)
    - [8.3 网络策略](#83-网络策略)
  - [9. Pod监控与日志](#9-pod监控与日志)
    - [9.1 指标收集](#91-指标收集)
    - [9.2 日志管理](#92-日志管理)
    - [9.3 事件监控](#93-事件监控)
  - [10. 故障诊断与排错](#10-故障诊断与排错)
    - [10.1 常见问题诊断](#101-常见问题诊断)
    - [10.2 调试技巧](#102-调试技巧)
    - [10.3 性能问题排查](#103-性能问题排查)
  - [11. 最佳实践与优化](#11-最佳实践与优化)
    - [11.1 Pod设计原则](#111-pod设计原则)
    - [11.2 性能优化策略](#112-性能优化策略)
    - [11.3 运维自动化](#113-运维自动化)
  - [12. 快速上手指南](#12-快速上手指南)
  - [13. 命令速查表](#13-命令速查表)
  - [14. 故障排除FAQ](#14-故障排除faq)

## 1. Pod基础概念

### 1.1 Pod定义与特性

Pod是Kubernetes中最小的部署单元，包含一个或多个紧密耦合的容器。

#### Pod特性

- **共享网络**: Pod内所有容器共享同一个IP地址和端口空间
- **共享存储**: Pod内所有容器可以共享存储卷
- **生命周期一致**: Pod内所有容器同时启动和停止
- **调度单元**: Kubernetes以Pod为单位进行调度

#### Pod YAML示例

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: web
    version: v1
spec:
  containers:
  - name: web-container
    image: nginx:latest
    ports:
    - containerPort: 80
  - name: sidecar-container
    image: busybox:latest
    command: ['sh', '-c', 'while true; do echo "sidecar running"; sleep 30; done']
```

### 1.2 Pod生命周期

#### 生命周期阶段

1. **Pending**: Pod已被Kubernetes接受，但容器尚未创建
2. **Running**: Pod已绑定到节点，所有容器已创建
3. **Succeeded**: Pod中所有容器成功终止
4. **Failed**: Pod中至少有一个容器以失败状态终止
5. **Unknown**: 无法获取Pod状态

#### 生命周期管理

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: lifecycle-pod
spec:
  containers:
  - name: main-container
    image: nginx:latest
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c", "echo 'Container started'"]
      preStop:
        exec:
          command: ["/bin/sh", "-c", "echo 'Container stopping'"]
```

### 1.3 Pod与容器的关系

#### 单容器Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: single-container-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    ports:
    - containerPort: 80
```

#### 多容器Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    ports:
    - containerPort: 80
  - name: log-collector
    image: fluentd:latest
    volumeMounts:
    - name: logs
      mountPath: /var/log
  volumes:
  - name: logs
    emptyDir: {}
```

## 2. Pod创建与管理

### 2.1 Pod创建方式

#### 直接创建Pod

```bash
    # 使用kubectl创建
kubectl create -f pod.yaml

    # 使用kubectl apply
kubectl apply -f pod.yaml

    # 直接运行Pod
kubectl run my-pod --image=nginx:latest --port=80
```

#### 通过控制器创建

```yaml
    # Deployment创建Pod
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:latest
        ports:
        - containerPort: 80
```

### 2.2 Pod配置管理

#### 环境变量配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    env:
    - name: NODE_ENV
      value: "production"
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: url
```

#### 配置映射

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    envFrom:
    - configMapRef:
        name: app-config
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

### 2.3 Pod更新与删除

#### Pod更新

```bash
    # 更新Pod配置
kubectl apply -f updated-pod.yaml

    # 编辑Pod配置
kubectl edit pod my-pod

    # 替换Pod
kubectl replace -f pod.yaml
```

#### Pod删除

```bash
    # 删除Pod
kubectl delete pod my-pod

    # 强制删除Pod
kubectl delete pod my-pod --force --grace-period=0

    # 删除所有Pod
kubectl delete pods --all
```

## 3. Pod资源管理

### 3.1 资源请求与限制

#### 资源配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

#### 资源类型

- **CPU**: 以millicores为单位，1000m = 1 CPU核心
- **内存**: 以字节为单位，支持Mi、Gi等单位
- **存储**: 临时存储和持久化存储
- **扩展资源**: GPU、FPGA等

### 3.2 资源配额管理

#### 命名空间资源配额

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: production
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "10"
```

#### 限制范围

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: mem-limit-range
  namespace: production
spec:
  limits:
  - default:
      memory: "512Mi"
      cpu: "500m"
    defaultRequest:
      memory: "256Mi"
      cpu: "250m"
    type: Container
```

### 3.3 资源监控与调优

#### 资源使用监控

```bash
    # 查看Pod资源使用
kubectl top pods

    # 查看节点资源使用
kubectl top nodes

    # 查看Pod详细信息
kubectl describe pod my-pod
```

#### 资源调优

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: optimized-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
    # 启用资源监控
    env:
    - name: ENABLE_METRICS
      value: "true"
```

## 4. Pod健康检查

### 4.1 探针类型

#### 存活探针 (Liveness Probe)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
```

#### 就绪探针 (Readiness Probe)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readiness-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    readinessProbe:
      httpGet:
        path: /health
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 1
      failureThreshold: 3
```

#### 启动探针 (Startup Probe)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: startup-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    startupProbe:
      httpGet:
        path: /
        port: 80
      failureThreshold: 30
      periodSeconds: 10
```

### 4.2 探针配置

#### HTTP探针

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
    scheme: HTTPS
    httpHeaders:
    - name: Custom-Header
      value: Awesome
```

#### TCP探针

```yaml
livenessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
```

#### 命令探针

```yaml
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

### 4.3 健康检查最佳实践

1. **探针选择**: 根据应用特性选择合适的探针类型
2. **超时设置**: 合理设置超时时间，避免误报
3. **重试机制**: 配置适当的重试次数和间隔
4. **启动延迟**: 给应用足够的启动时间

## 5. Pod安全策略

### 5.1 Pod安全标准

#### Pod安全上下文

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: web
    image: nginx:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

### 5.2 安全上下文配置

#### 用户和组配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: user-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 1000
    runAsNonRoot: true
  containers:
  - name: web
    image: nginx:latest
    securityContext:
      runAsUser: 1000
      runAsGroup: 1000
```

#### 权限控制

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: capability-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    securityContext:
      capabilities:
        add:
        - NET_BIND_SERVICE
        drop:
        - ALL
      privileged: false
      readOnlyRootFilesystem: true
```

### 5.3 网络策略

#### 网络策略配置

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-netpol
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: frontend
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: backend
    ports:
    - protocol: TCP
      port: 5432
```

## 6. Pod调度与亲和性

### 6.1 节点选择器

#### 节点选择器配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-selector-pod
spec:
  nodeSelector:
    disktype: ssd
    zone: us-west-1a
  containers:
  - name: web
    image: nginx:latest
```

### 6.2 亲和性与反亲和性

#### Pod亲和性

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: affinity-pod
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - web
        topologyKey: kubernetes.io/hostname
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: app
              operator: In
              values:
              - web
          topologyKey: kubernetes.io/hostname
  containers:
  - name: web
    image: nginx:latest
```

#### 节点亲和性

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: node-affinity-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/arch
            operator: In
            values:
            - amd64
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
  containers:
  - name: web
    image: nginx:latest
```

### 6.3 污点与容忍

#### 污点配置

```bash
    # 给节点添加污点
kubectl taint nodes node1 key1=value1:NoSchedule

    # 查看节点污点
kubectl describe node node1
```

#### 容忍配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: toleration-pod
spec:
  tolerations:
  - key: "key1"
    operator: "Equal"
    value: "value1"
    effect: "NoSchedule"
  - key: "key2"
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 3600
  containers:
  - name: web
    image: nginx:latest
```

## 7. Pod存储管理

### 7.1 卷类型

#### 临时卷

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: volume-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    volumeMounts:
    - name: temp-storage
      mountPath: /tmp
  volumes:
  - name: temp-storage
    emptyDir:
      sizeLimit: 1Gi
```

#### 配置映射卷

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: configmap-volume-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

### 7.2 持久化存储

#### 持久化卷声明

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    volumeMounts:
    - name: persistent-storage
      mountPath: /data
  volumes:
  - name: persistent-storage
    persistentVolumeClaim:
      claimName: my-pvc
```

### 7.3 存储类管理

#### 存储类配置

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

## 8. Pod网络管理

### 8.1 网络模型

#### Pod网络配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: network-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    ports:
    - containerPort: 80
      protocol: TCP
    - containerPort: 443
      protocol: TCP
```

### 8.2 服务发现

#### 服务配置

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

### 8.3 网络策略

#### 8.3.1 网络策略配置

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-netpol
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

## 9. Pod监控与日志

### 9.1 指标收集

#### 资源指标

```bash
    # 查看Pod资源使用
kubectl top pods

    # 查看Pod详细信息
kubectl describe pod my-pod

    # 查看Pod事件
kubectl get events --field-selector involvedObject.name=my-pod
```

### 9.2 日志管理

#### 日志查看

```bash
    # 查看Pod日志
kubectl logs my-pod

    # 查看多容器Pod日志
kubectl logs my-pod -c container-name

    # 实时查看日志
kubectl logs -f my-pod

    # 查看最近日志
kubectl logs --tail=100 my-pod
```

#### 日志配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: logging-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    # 日志轮转配置
    resources:
      limits:
        ephemeral-storage: "1Gi"
```

### 9.3 事件监控

#### 事件查看

```bash
    # 查看所有事件
kubectl get events

    # 查看特定Pod事件
kubectl get events --field-selector involvedObject.name=my-pod

    # 按时间排序
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 10. 故障诊断与排错

### 10.1 常见问题诊断

#### Pod启动失败

```bash
    # 查看Pod状态
kubectl get pods

    # 查看Pod详细信息
kubectl describe pod my-pod

    # 查看Pod日志
kubectl logs my-pod

    # 查看事件
kubectl get events --field-selector involvedObject.name=my-pod
```

#### 资源不足

```bash
    # 查看节点资源
kubectl top nodes

    # 查看Pod资源使用
kubectl top pods

    # 查看资源配额
kubectl describe quota
```

### 10.2 调试技巧

#### 进入Pod调试

```bash
    # 进入Pod容器
kubectl exec -it my-pod -- /bin/bash

    # 进入特定容器
kubectl exec -it my-pod -c container-name -- /bin/bash

    # 执行命令
kubectl exec my-pod -- ps aux
```

#### 端口转发

```bash
    # 端口转发
kubectl port-forward pod/my-pod 8080:80

    # 访问本地端口
curl http://localhost:8080
```

### 10.3 性能问题排查

#### 性能分析

```bash
    # 查看Pod资源使用
kubectl top pods

    # 查看节点资源
kubectl top nodes

    # 查看Pod详细信息
kubectl describe pod my-pod
```

## 11. 最佳实践与优化

### 11.1 Pod设计原则

1. **单一职责**: 每个Pod只运行一个主要应用
2. **无状态设计**: 避免在Pod中存储状态数据
3. **资源限制**: 合理设置资源请求和限制
4. **健康检查**: 配置适当的探针

### 11.2 性能优化策略

#### 资源优化

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: optimized-pod
spec:
  containers:
  - name: web
    image: nginx:latest
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
    # 启用资源监控
    env:
    - name: ENABLE_METRICS
      value: "true"
```

### 11.3 运维自动化

#### 自动化脚本

```bash
#!/bin/bash
    # Pod健康检查脚本

check_pod_health() {
    local pod_name=$1
    local namespace=${2:-default}
    
    # 检查Pod状态
    local status=$(kubectl get pod $pod_name -n $namespace -o jsonpath='{.status.phase}')
    
    if [ "$status" != "Running" ]; then
        echo "Pod $pod_name is not running: $status"
        kubectl describe pod $pod_name -n $namespace
        return 1
    fi
    
    # 检查健康探针
    local ready=$(kubectl get pod $pod_name -n $namespace -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    
    if [ "$ready" != "True" ]; then
        echo "Pod $pod_name is not ready"
        kubectl logs $pod_name -n $namespace --tail=50
        return 1
    fi
    
    echo "Pod $pod_name is healthy"
    return 0
}
```

## 12. 快速上手指南

### 12.1 基础操作流程

1. **创建Pod**: `kubectl apply -f pod.yaml`
2. **查看状态**: `kubectl get pods`
3. **查看日志**: `kubectl logs my-pod`
4. **进入Pod**: `kubectl exec -it my-pod -- /bin/bash`
5. **删除Pod**: `kubectl delete pod my-pod`

### 12.2 常用场景

#### Web应用部署

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-app
  labels:
    app: web
spec:
  containers:
  - name: web
    image: nginx:latest
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

## 13. 命令速查表

### 13.1 Pod管理命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `kubectl get pods` | 查看Pod列表 | `kubectl get pods -o wide` |
| `kubectl describe pod` | 查看Pod详细信息 | `kubectl describe pod my-pod` |
| `kubectl create -f` | 创建Pod | `kubectl create -f pod.yaml` |
| `kubectl apply -f` | 应用Pod配置 | `kubectl apply -f pod.yaml` |
| `kubectl delete pod` | 删除Pod | `kubectl delete pod my-pod` |
| `kubectl edit pod` | 编辑Pod配置 | `kubectl edit pod my-pod` |
| `kubectl replace -f` | 替换Pod配置 | `kubectl replace -f pod.yaml` |

### 13.2 Pod调试命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `kubectl logs` | 查看Pod日志 | `kubectl logs -f my-pod` |
| `kubectl exec` | 进入Pod容器 | `kubectl exec -it my-pod -- /bin/bash` |
| `kubectl port-forward` | 端口转发 | `kubectl port-forward pod/my-pod 8080:80` |
| `kubectl top pods` | 查看Pod资源使用 | `kubectl top pods` |
| `kubectl get events` | 查看事件 | `kubectl get events` |

### 13.3 资源管理命令

| 命令 | 功能 | 示例 |
|------|------|------|
| `kubectl describe quota` | 查看资源配额 | `kubectl describe quota` |
| `kubectl describe limitrange` | 查看限制范围 | `kubectl describe limitrange` |
| `kubectl top nodes` | 查看节点资源 | `kubectl top nodes` |
| `kubectl top pods` | 查看Pod资源 | `kubectl top pods` |

## 14. 故障排除FAQ

### 14.1 常见问题

**Q: Pod一直处于Pending状态怎么办？**
A:

1. 检查节点资源是否充足: `kubectl describe nodes`
2. 检查调度器日志: `kubectl logs -n kube-system deployment/kube-scheduler`
3. 检查污点和容忍配置
4. 检查资源配额和限制

**Q: Pod启动失败怎么办？**
A:

1. 查看Pod事件: `kubectl get events --field-selector involvedObject.name=my-pod`
2. 查看Pod日志: `kubectl logs my-pod`
3. 检查镜像是否存在和可访问
4. 验证配置和权限

**Q: Pod内存使用过高怎么办？**
A:

1. 检查应用是否有内存泄漏
2. 调整内存限制: `resources.limits.memory`
3. 监控内存使用: `kubectl top pods`
4. 优化应用代码和配置

**Q: Pod网络不通怎么办？**
A:

1. 检查网络策略配置
2. 验证服务配置: `kubectl get svc`
3. 检查DNS解析: `kubectl exec my-pod -- nslookup kubernetes.default`
4. 测试网络连通性: `kubectl exec my-pod -- ping target-host`

### 14.2 性能优化

**Q: 如何提高Pod启动速度？**
A:

1. 使用较小的基础镜像
2. 优化镜像层数
3. 预拉取常用镜像
4. 使用本地镜像仓库

**Q: 如何减少Pod资源消耗？**
A:

1. 合理设置资源请求和限制
2. 使用轻量级基础镜像
3. 优化应用配置
4. 定期清理无用资源

### 14.3 安全加固

**Q: 如何提高Pod安全性？**
A:

1. 使用非root用户运行
2. 启用只读根文件系统
3. 限制容器权限
4. 配置网络策略
5. 定期更新基础镜像

---

## 版本差异说明

- **Kubernetes 1.28+**: 支持Pod安全标准，启动探针改进
- **Kubernetes 1.25+**: 支持Pod安全标准，移除PodSecurityPolicy
- **Kubernetes 1.20+**: 支持启动探针，资源指标改进

## 参考资源

- [Kubernetes官方文档](https://kubernetes.io/docs/)
- [Pod安全标准](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [资源管理](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [网络策略](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
