# 03 vRealize/Aria Automation（Cloud Assembly / Service Broker / Code Stream）

## 1. 目标（Objectives）

- 与 vSphere 打通端到端编排：蓝图 → 审批/策略 → 部署 → 证据归档
- 提供最小可复现实例（含 YAML 蓝图、API/CLI、策略与证据目录结构）
- 对接外部系统（ITSM/Webhook）与本仓库的调度与审计规范

## 2. 架构与组件（Architecture）

- Cloud Assembly：定义与维护蓝图（Blueprint）与云账户（Cloud Account）
- Service Broker：目录（Catalog）发布、审批与约束策略（Policy/Constraint）
- Code Stream（可选）：流水线与集成（Git/CI/变更门禁）
- 集成对象：vCenter、NSX、vSphere Tags、命名空间与网络/存储策略

## 3. 前置条件（Prerequisites）

- vCenter 可达；具备具有最小权限的自动化账号（仅部署所需）
- 已在 vCenter 侧准备 VM 模板或内容库（Content Library）
- 网络与存储策略已在 vSphere/NSX 中命名并可被标签/约束引用
- 证书与时间同步（NTP）一致；审计与 Syslog 策略就绪

## 4. 接入 vCenter（Cloud Account）

步骤要点：

- 在 Cloud Assembly 中创建 vCenter Cloud Account，绑定数据中心/集群/网络/存储范围
- 同步 vSphere Tags 以用于蓝图约束（如 `env=prod`、`tier=gold`）
- 为自动化账号赋权：最小权限集合（克隆、部署、读写标签、开关机等）

## 5. 最小蓝图示例（Single-VM + 网络/存储 约束）

示例蓝图（YAML 片段，可在 Cloud Assembly 粘贴使用）：

```yaml
formatVersion: 1
inputs:
  vm_name:
    type: string
    title: VM Name
  cpu:
    type: number
    default: 2
  memory:
    type: number
    default: 4096
resources:
  my_vm:
    type: Cloud.vSphere.Machine
    properties:
      name: "${input.vm_name}"
      image: "rhel8-template"
      flavor: "small"
      cpuCount: "${input.cpu}"
      totalMemoryMB: "${input.memory}"
      networks:
        - network: "net-prod-seg"
          assignment: static
      storage:
        constraints:
          - tag: "tier:gold"
      constraints:
        - tag: "env:prod"
```

要点：

- 使用 tag/constraint 与 vSphere/NSX 命名策略对齐；蓝图不写死底层资源 ID
- 输入参数允许在发布目录中由申请人自助填写并受策略限制

## 6. 发布与审批策略（Service Broker + Policies）

流程：

1) 将蓝图发布为 Catalog Item，并添加输入校验（最小/最大 CPU/内存）
2) 配置审批策略：
   - 按标签 `env=prod` 触发审批
   - 费用阈值或配额超限触发审批
3) 约束策略：限定可用网络/存储域、命名规范、生命周期操作（关机/删除）

## 7. API 与自动化（与本仓库对接）

- 认证：使用 Aria Automation API Token 或 OIDC
- 常用端点：
  - 列出/触发部署：`POST /deployment/api/deployments`、`GET /deployment/api/deployments/{id}`
  - 目录项执行：`POST /catalog/api/items/{id}/request`
- 与仓库对接：将请求与结果写入 `artifacts/` 目录并生成 manifest/哈希

PowerShell 触发示例（伪代码）：

```powershell
$token = "<api_token>"
$headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }
$body = @{ inputs = @{ vm_name = 'vm-prod-001'; cpu = 2; memory = 4096 } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://aria.example.com/catalog/api/items/<item_id>/request" -Headers $headers -Body $body |
  ConvertTo-Json | Out-File artifacts/(Get-Date -Format 'yyyy-MM-dd')/deployment-response.json
```

## 8. 证据与归档（Evidence & Artifacts）

目录结构（与 `05_工作流编排.md` 一致）：

```text
artifacts/
  YYYY-MM-DD/
    deployment-response.json
    request-params.json
    blueprint.yaml
    evidence.log
    manifest.json
    manifest.sha256
```

manifest（建议字段）：

- blueprint_name、blueprint_version、catalog_item_id、deployment_id
- requested_by、change_id（变更单号）、requested_at、completed_at
- hashes：关键文件及其 SHA256
- rollback：回滚步骤或回滚蓝图/快照引用

## 9. 回滚与生命周期（Rollback & Day-2）

- Day-2 操作：扩容、关机/开机、删除、打标签；对关键操作同样生成证据
- 回滚策略：
  - 基于蓝图的逆向操作（删除/还原）
  - 基于快照或模板重建
  - 与变更单关联，写入 `manifest.json` 与 `evidence.log`

## 10. 与外部系统集成（Integration）

- Webhook：部署完成/失败回调，推送到审计或工单系统
- ITSM：变更单创建/关闭、审批状态同步
- GitOps：蓝图 YAML 存放在 Git，使用 Code Stream 触发发布流水线

## 11. 故障与排障（Troubleshooting）

- 常见错误：凭据/权限不足、标签约束不匹配、内容库镜像不可达
- 建议：开启 API 请求与蓝图日志，记录请求/响应至 `artifacts/`，统一时间源

## 12. 参考与交叉链接（Cross-Links）

- `02_PowerCLI技术.md`（脚本与证据）
- `04_API集成开发.md`（REST 集成端点与认证）
- `05_工作流编排.md`（计划任务/cron、证据与哈希、manifest 模型）
