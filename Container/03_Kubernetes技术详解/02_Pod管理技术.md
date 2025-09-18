# Pod管理技术

## 目录

- [Pod管理技术](#pod管理技术)
  - [目录](#目录)
  - [1. Pod 模型与生命周期](#1-pod-模型与生命周期)
  - [2. Probes 健康检查](#2-probes-健康检查)
  - [3. 资源与 QoS](#3-资源与-qos)
  - [4. 安全与隔离](#4-安全与隔离)
  - [5. 调度与亲和/反亲和](#5-调度与亲和反亲和)
  - [6. 实操与 FAQ](#6-实操与-faq)
  - [7. 故障清单与排查](#7-故障清单与排查)
  - [8. 示例 YAML 与 SOP](#8-示例-yaml-与-sop)

## 1. Pod 模型与生命周期

- Init/Sidecar/主容器；阶段与状态

## 2. Probes 健康检查

- liveness/readiness/startup 探针与回退策略

## 3. 资源与 QoS

- requests/limits 与 QoS 类别，驱逐策略

## 4. 安全与隔离

- Pod Security、SecurityContext、能力与 seccomp

## 5. 调度与亲和/反亲和

- nodeAffinity/podAffinity/taints & tolerations

## 6. 实操与 FAQ

- 常见 YAML 模板与排障路径

（待补充：示例与最佳实践）

## 7. 故障清单与排查

- Pod Pending：查看 `kubectl describe pod` 事件，检查调度约束/资源配额。
- CrashLoopBackOff：检查容器日志与探针、Init 容器依赖。
- OOMKilled：校对 requests/limits 与节点可用内存。

## 8. 示例 YAML 与 SOP

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  containers:
  - name: nginx
    image: nginx:1.27-alpine
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "500m"
        memory: "256Mi"
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 15
      periodSeconds: 20
```

SOP（排障简表）：

- 查看事件：`kubectl describe pod web | sed -n '1,120p'`
- 查看日志：`kubectl logs web -c nginx --tail=200`
- 进入容器：`kubectl exec -it web -c nginx -- sh`
