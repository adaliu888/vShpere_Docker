# Kubernetes编排技术详解

> 版本锚点与 Artifacts（新增）：本文涉及 Kubernetes/OCI 等版本请统一参考《2025年技术标准最终对齐报告.md》。与编排相关的基线/事件/策略等证据请在文末“Artifacts 索引”说明的结构中留存。

## 目录

- [Kubernetes编排技术详解](#kubernetes编排技术详解)
  - [目录](#目录)
  - [1. Kubernetes编排概述](#1-kubernetes编排概述)
    - [1.1 编排概念](#11-编排概念)
    - [1.2 编排层次](#12-编排层次)
    - [1.3 编排优势](#13-编排优势)
  - [2. 工作负载编排](#2-工作负载编排)
    - [2.1 Deployment编排](#21-deployment编排)
    - [2.2 StatefulSet编排](#22-statefulset编排)
    - [2.3 DaemonSet编排](#23-daemonset编排)
    - [2.4 Job和CronJob编排](#24-job和cronjob编排)
  - [3. 服务编排](#3-服务编排)
    - [3.1 Service编排](#31-service编排)
    - [3.2 Ingress编排](#32-ingress编排)
    - [3.3 Gateway API编排](#33-gateway-api编排)
  - [4. 配置编排](#4-配置编排)
    - [4.1 ConfigMap编排](#41-configmap编排)
    - [4.2 Secret编排](#42-secret编排)
    - [4.3 配置热更新](#43-配置热更新)
  - [5. 存储编排](#5-存储编排)
    - [5.1 PersistentVolume编排](#51-persistentvolume编排)
    - [5.2 PersistentVolumeClaim编排](#52-persistentvolumeclaim编排)
  - [6. 网络编排](#6-网络编排)
    - [6.1 NetworkPolicy编排](#61-networkpolicy编排)
    - [6.2 服务网格编排](#62-服务网格编排)
  - [7. 安全编排](#7-安全编排)
    - [7.1 PodSecurityPolicy编排](#71-podsecuritypolicy编排)
    - [7.2 RBAC编排](#72-rbac编排)
  - [8. 监控编排](#8-监控编排)
    - [8.1 Prometheus监控编排](#81-prometheus监控编排)
    - [8.2 日志收集编排](#82-日志收集编排)
  - [9. 自动化编排](#9-自动化编排)
    - [9.1 HPA自动扩缩容](#91-hpa自动扩缩容)
    - [9.2 VPA自动资源调整](#92-vpa自动资源调整)
    - [9.3 自动备份编排](#93-自动备份编排)
  - [10. 最佳实践](#10-最佳实践)
    - [10.1 编排设计原则](#101-编排设计原则)
    - [10.2 高可用编排](#102-高可用编排)
    - [10.3 安全编排](#103-安全编排)
    - [10.4 监控编排](#104-监控编排)
  - [总结](#总结)

## Artifacts 索引（新增）

- 目录建议：`artifacts/YYYY-MM-DD/` 下按领域分层：
  - cluster/（manifests、RBAC、Quota、PSA）
  - runtime/（policies、audit、events、admission 报告）
  - images/（sbom、signatures、attestations）
- 锚点：统一参见《2025年技术标准最终对齐报告.md》与 `vShpere_VMware/09_安全与合规管理/Artifacts_Index.md`。

## 1. Kubernetes编排概述

### 1.1 编排概念

Kubernetes编排是指通过声明式配置和自动化机制，管理容器化应用的部署、扩展、更新和维护过程。

**编排核心要素**：

- **声明式配置**：描述期望状态
- **自动化管理**：自动维护期望状态
- **服务发现**：自动发现和注册服务
- **负载均衡**：自动分发流量
- **健康检查**：自动监控和恢复
- **滚动更新**：零停机更新

### 1.2 编排层次

```text
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes编排层次                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   应用层    │  │   服务层    │  │   基础设施层 │         │
│  │  (Apps)     │  │ (Services)  │  │(Infrastructure)│      │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│           │               │               │                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   工作负载  │  │   网络编排  │  │   存储编排  │         │
│  │ (Workloads) │  │ (Networking)│  │ (Storage)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│           │               │               │                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   配置管理  │  │   安全编排  │  │   监控编排  │         │
│  │  (Config)   │  │ (Security)  │  │ (Monitoring)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 编排优势

**自动化管理**：

- 自动调度Pod到合适节点
- 自动扩展和收缩应用
- 自动故障检测和恢复
- 自动负载均衡

**声明式配置**：

- 描述期望状态而非操作步骤
- 系统自动维护期望状态
- 配置版本控制和回滚
- 基础设施即代码

## 2. 工作负载编排

### 2.1 Deployment编排

**基本Deployment**：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  labels:
    app: web
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
        image: nginx:1.20
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
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

**高级Deployment配置**：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
        version: v1.0
    spec:
      affinity:
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
        image: nginx:1.20
        ports:
        - containerPort: 80
        env:
        - name: ENV
          value: "production"
        - name: LOG_LEVEL
          value: "info"
        volumeMounts:
        - name: config
          mountPath: /etc/nginx/conf.d
        - name: logs
          mountPath: /var/log/nginx
      volumes:
      - name: config
        configMap:
          name: nginx-config
      - name: logs
        emptyDir: {}
```

### 2.2 StatefulSet编排

**有状态应用编排**：

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: root-password
        - name: MYSQL_DATABASE
          value: "app"
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
        - name: mysql-config
          mountPath: /etc/mysql/conf.d
        livenessProbe:
          exec:
            command:
            - mysqladmin
            - ping
            - -h
            - localhost
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - mysql
            - -h
            - localhost
            - -e
            - "SELECT 1"
          initialDelaySeconds: 5
          periodSeconds: 2
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
      storageClassName: fast-ssd
```

### 2.3 DaemonSet编排

**节点级服务编排**：

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  labels:
    app: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.logging.svc.cluster.local"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        - name: FLUENT_ELASTICSEARCH_SCHEME
          value: "http"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: fluentd-config
          mountPath: /fluentd/etc
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: fluentd-config
        configMap:
          name: fluentd-config
```

### 2.4 Job和CronJob编排

**批处理任务编排**：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-processing
spec:
  completions: 5
  parallelism: 2
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: processor
        image: data-processor:latest
        command:
        - /bin/sh
        - -c
        - |
          echo "Processing data batch $JOB_COMPLETION_INDEX"
          # 数据处理逻辑
          sleep 30
        env:
        - name: JOB_COMPLETION_INDEX
          valueFrom:
            fieldRef:
              fieldPath: metadata.annotations['batch.kubernetes.io/job-completion-index']
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

**定时任务编排**：

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点执行
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: backup-tool:latest
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting backup at $(date)"
              # 备份逻辑
              tar -czf /backup/data-$(date +%Y%m%d).tar.gz /data
              echo "Backup completed at $(date)"
            volumeMounts:
            - name: data
              mountPath: /data
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: data
            persistentVolumeClaim:
              claimName: data-pvc
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

## 3. 服务编排

### 3.1 Service编排

**基本Service配置**：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
  labels:
    app: web
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP
  type: ClusterIP
```

**高级Service配置**：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  selector:
    app: web
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  - name: https
    port: 443
    targetPort: 8443
    protocol: TCP
  type: LoadBalancer
  loadBalancerSourceRanges:
  - 10.0.0.0/8
  - 172.16.0.0/12
  - 192.168.0.0/16
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
```

### 3.2 Ingress编排

**基本Ingress配置**：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - web.example.com
    secretName: web-tls
  rules:
  - host: web.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

**高级Ingress配置**：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/auth-type: basic
    nginx.ingress.kubernetes.io/auth-secret: basic-auth
    nginx.ingress.kubernetes.io/auth-realm: 'Authentication Required'
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - web.example.com
    - api.example.com
    secretName: web-tls
  rules:
  - host: web.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
  - host: api.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      - path: /admin
        pathType: Prefix
        backend:
          service:
            name: admin-service
            port:
              number: 8080
```

### 3.3 Gateway API编排

**Gateway配置**：

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: Gateway
metadata:
  name: web-gateway
spec:
  gatewayClassName: nginx
  listeners:
  - name: http
    port: 80
    protocol: HTTP
    allowedRoutes:
      namespaces:
        from: Same
  - name: https
    port: 443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
      - name: web-tls
    allowedRoutes:
      namespaces:
        from: Same
```

**HTTPRoute配置**：

```yaml
apiVersion: gateway.networking.k8s.io/v1beta1
kind: HTTPRoute
metadata:
  name: web-route
spec:
  parentRefs:
  - name: web-gateway
  hostnames:
  - "web.example.com"
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /
    backendRefs:
    - name: web-service
      port: 80
  - matches:
    - path:
        type: PathPrefix
        value: /api
    backendRefs:
    - name: api-service
      port: 8080
```

## 4. 配置编排

### 4.1 ConfigMap编排

**基本ConfigMap**：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.properties: |
    server.port=8080
    logging.level=INFO
    database.url=jdbc:mysql://mysql:3306/app
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        location / {
            proxy_pass http://backend;
        }
    }
```

**使用ConfigMap**：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: web-app:latest
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: "production"
        envFrom:
        - configMapRef:
            name: app-config
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: config
        configMap:
          name: app-config
          items:
          - key: app.properties
            path: application.properties
      - name: nginx-config
        configMap:
          name: app-config
          items:
          - key: nginx.conf
            path: default.conf
```

### 4.2 Secret编排

**Secret创建**：

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  username: YWRtaW4=  # base64编码
  password: cGFzc3dvcmQ=  # base64编码
  database-url: amRiYzpteXNxbDovL215c3FsOjMzMDYvYXBw  # base64编码
```

**使用Secret**：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: web-app:latest
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: password
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        volumeMounts:
        - name: secrets
          mountPath: /app/secrets
          readOnly: true
      volumes:
      - name: secrets
        secret:
          secretName: app-secrets
          defaultMode: 0400
```

### 4.3 配置热更新

**配置更新策略**：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
      annotations:
        checksum/config: "sha256:abc123..."
    spec:
      containers:
      - name: web-app
        image: web-app:latest
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: secrets
          mountPath: /app/secrets
          readOnly: true
      volumes:
      - name: config
        configMap:
          name: app-config
      - name: secrets
        secret:
          secretName: app-secrets
```

## 5. 存储编排

### 5.1 PersistentVolume编排

**静态PV配置**：

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  hostPath:
    path: /data/mysql
```

**动态PV配置**：

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
  fsType: ext4
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
```

### 5.2 PersistentVolumeClaim编排

**PVC配置**：

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd
```

**使用PVC**：

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: root-password
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
      storageClassName: fast-ssd
```

## 6. 网络编排

### 6.1 NetworkPolicy编排

**基本网络策略**：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-network-policy
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
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 3306
```

**高级网络策略**：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-network-policy
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
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: load-balancer
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8443
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 3306
  - to:
    - namespaceSelector:
        matchLabels:
          name: cache
    ports:
    - protocol: TCP
      port: 6379
  - to: []  # 允许所有出站流量到DNS
    ports:
    - protocol: UDP
      port: 53
```

### 6.2 服务网格编排

**Istio配置**：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: web-vs
spec:
  hosts:
  - web-service
  http:
  - match:
    - headers:
        version:
          exact: v2
    route:
    - destination:
        host: web-service
        subset: v2
  - route:
    - destination:
        host: web-service
        subset: v1
      weight: 90
    - destination:
        host: web-service
        subset: v2
      weight: 10
```

**DestinationRule配置**：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: web-dr
spec:
  host: web-service
  trafficPolicy:
    loadBalancer:
      simple: LEAST_CONN
    connectionPool:
      tcp:
        maxConnections: 10
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 2
    circuitBreaker:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

## 7. 安全编排

### 7.1 PodSecurityPolicy编排

**PSP配置**：

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

**使用PSP**：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: psp-user
rules:
- apiGroups: ['policy']
  resources: ['podsecuritypolicies']
  verbs: ['use']
  resourceNames:
  - restricted-psp
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: psp-user-binding
roleRef:
  kind: ClusterRole
  name: psp-user
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: default
  namespace: default
```

### 7.2 RBAC编排

**Role配置**：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
```

**RoleBinding配置**：

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
- kind: ServiceAccount
  name: default
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## 8. 监控编排

### 8.1 Prometheus监控编排

**ServiceMonitor配置**：

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: web-monitor
  labels:
    app: web
spec:
  selector:
    matchLabels:
      app: web
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

**PrometheusRule配置**：

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: web-alerts
spec:
  groups:
  - name: web.rules
    rules:
    - alert: WebHighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value }}"
    - alert: WebHighResponseTime
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High response time detected"
        description: "95th percentile response time is {{ $value }}s"
```

### 8.2 日志收集编排

**Fluentd配置**：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
    </source>
    
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name app-logs
    </match>
```

## 9. 自动化编排

### 9.1 HPA自动扩缩容

**HPA配置**：

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

### 9.2 VPA自动资源调整

**VPA配置**：

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-deployment
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: web
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 1
        memory: 1Gi
      controlledResources: ["cpu", "memory"]
```

### 9.3 自动备份编排

**备份CronJob**：

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: backup-tool:latest
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting backup at $(date)"
              # 备份数据库
              mysqldump -h mysql -u root -p$MYSQL_ROOT_PASSWORD app > /backup/db-$(date +%Y%m%d).sql
              # 备份配置文件
              tar -czf /backup/config-$(date +%Y%m%d).tar.gz /app/config
              # 上传到云存储
              aws s3 cp /backup/ s3://backup-bucket/$(date +%Y%m%d)/ --recursive
              echo "Backup completed at $(date)"
            env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secret
                  key: root-password
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

## 10. 最佳实践

### 10.1 编排设计原则

**声明式配置**：

- 使用YAML文件描述期望状态
- 避免使用命令式操作
- 版本控制所有配置文件
- 使用模板化配置

**资源管理**：

- 设置合理的资源请求和限制
- 使用HPA和VPA自动扩缩容
- 监控资源使用情况
- 优化资源配置

### 10.2 高可用编排

**多副本部署**：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      affinity:
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
        image: nginx:1.20
        ports:
        - containerPort: 80
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

### 10.3 安全编排

**安全配置**：

- 使用非root用户运行容器
- 启用PodSecurityPolicy
- 配置NetworkPolicy
- 使用Secret管理敏感信息
- 启用RBAC权限控制

### 10.4 监控编排

**全面监控**：

- 应用指标监控
- 基础设施监控
- 日志收集和分析
- 告警配置
- 性能监控

## 总结

Kubernetes编排技术提供了强大的容器化应用管理能力，通过声明式配置和自动化机制，可以实现应用的自动化部署、扩展、更新和维护。在实际使用中，需要根据具体需求选择合适的编排策略，并遵循最佳实践来确保系统的稳定性和安全性。
