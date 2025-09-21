## 目录

- [Tanzu 容器桥接与证据一致性（最小可用）](#tanzu-容器桥接与证据一致性最小可用)
  - [1. 目标](#1-目标)
  - [2. 身份与访问](#2-身份与访问)
    - [2.1 RBAC 样例](#21-rbac-样例)
  - [3. 网络与安全](#3-网络与安全)
    - [3.1 NetworkPolicy 样例](#31-networkpolicy-样例)
  - [4. 证据与 artifacts](#4-证据与-artifacts)
  - [7. Gatekeeper/OPA 策略（示例）](#7-gatekeeperopa-策略示例)
- [生成策略快照（作为证据）](#生成策略快照作为证据)
  - [5. 跨域变更与回滚](#5-跨域变更与回滚)
  - [6. 交叉链接](#6-交叉链接)
  - [8. 前置条件与版本兼容（新增）](#8-前置条件与版本兼容新增)
  - [9. 常见陷阱与案例（新增）](#9-常见陷阱与案例新增)

- [Tanzu 容器桥接与证据一致性（最小可用）](#tanzu-容器桥接与证据一致性最小可用)
  - [1. 目标](#1-目标)
  - [2. 身份与访问](#2-身份与访问)
    - [2.1 RBAC 样例](#21-rbac-样例)
  - [3. 网络与安全](#3-网络与安全)
    - [3.1 NetworkPolicy 样例](#31-networkpolicy-样例)
  - [4. 证据与 artifacts](#4-证据与-artifacts)
  - [7. Gatekeeper/OPA 策略（示例）](#7-gatekeeperopa-策略示例)
- [生成策略快照（作为证据）](#生成策略快照作为证据)
  - [5. 跨域变更与回滚](#5-跨域变更与回滚)
  - [6. 交叉链接](#6-交叉链接)
  - [8. 前置条件与版本兼容（新增）](#8-前置条件与版本兼容新增)
  - [9. 常见陷阱与案例（新增）](#9-常见陷阱与案例新增)


# Tanzu 容器桥接与证据一致性（最小可用）

## 1. 目标

- 统一 vSphere ↔ 容器（Tanzu/K8s）在身份、策略与证据归档上的一致性

## 2. 身份与访问

- vSphere SSO ↔ Kubernetes RBAC 映射（最小权限）
- 审计：vCenter 事件/任务 vs. K8s Audit Log（集中留存与哈希）

### 2.1 RBAC 样例

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: readonly-ops
  namespace: prod
rules:
- apiGroups: [""]
  resources: ["pods","services","endpoints"]
  verbs: ["get","list","watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: readonly-ops-binding
  namespace: prod
subjects:
- kind: User
  name: corp\\ops.readonly  # 对齐 vSphere/SSO 映射
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: readonly-ops
```

## 3. 网络与安全

- NSX 与 CNI 策略一致性：命名/标签/命题（env/tier/app）一致
- Ingress/Egress 控制与微隔离策略对齐

### 3.1 NetworkPolicy 样例

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-app
  namespace: prod
spec:
  podSelector:
    matchLabels:
      tier: app
  policyTypes: ["Ingress"]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: web
    ports:
    - protocol: TCP
      port: 8080
```

## 4. 证据与 artifacts

```text
artifacts/
  YYYY-MM-DD/
    tanzu-cluster-inventory.json
    k8s-audit-YYYYMMDD.json
    policy-snapshot.yaml
    manifest.json
    manifest.sha256
```

## 7. Gatekeeper/OPA 策略（示例）

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: ns-requires-env-tier
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Namespace"]
  parameters:
    labels: ["env","tier"]
```

```yaml
# 生成策略快照（作为证据）
apiVersion: v1
kind: ConfigMap
metadata:
  name: policy-snapshot
  namespace: gatekeeper-system
data:
  exportedAt: "2025-09-18T10:00:00Z"
  policies: |
    - K8sRequiredLabels: ns-requires-env-tier
```

## 5. 跨域变更与回滚

- 变更单统一：TicketId 贯穿 vSphere 与 K8s
- 回滚策略：工作负载与基础设施分别定义，证据保持一致结构

## 6. 交叉链接

- `../10_自动化与编排技术/03_vRealize Automation.md`
- `../06_网络虚拟化技术/04_网络安全管理.md`

## 8. 前置条件与版本兼容（新增）

- vSphere + Tanzu 版本与 CNI/NSX 兼容矩阵确认
- OIDC/SSO 对接与 K8s 审计已开启
- 统一标签与命名：env/tier/app 与 vSphere/NSX 保持一致

## 9. 常见陷阱与案例（新增）

- RBAC 与 SSO 映射不一致：导致越权或拒绝；需建立映射表并定期复核
- NetworkPolicy 未覆盖 DNS/身份流量：默认拒绝引发隐性故障
- 策略变更无证据：缺少快照与 manifest，审计无法追溯
