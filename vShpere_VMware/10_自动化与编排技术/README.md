# 10 自动化与编排技术

## 目录

- [10 自动化与编排技术](#10-自动化与编排技术)
  - [导航](#导航)
  - [学习路径（建议）](#学习路径建议)
  - [前置条件（最小可用）](#前置条件最小可用)
    - [平台兼容与路径](#平台兼容与路径)
    - [离线安装 PowerCLI（新增）](#离线安装-powercli新增)
  - [快速Checklist](#快速checklist)
  - [故障排查（Troubleshooting）](#故障排查troubleshooting)
  - [证据与输出规范](#证据与输出规范)
  - [调度与任务编排（新增）](#调度与任务编排新增)
    - [Windows 计划任务（PowerShell）](#windows-计划任务powershell)
    - [Linux 定时任务（cron）](#linux-定时任务cron)
- [每日 02:00 执行](#每日-0200-执行)
    - [示例脚本 `daily_audit.ps1`（占位）](#示例脚本-daily_auditps1占位)
  - [对标与参考](#对标与参考)
  - [任务蓝图（示例）](#任务蓝图示例)
  - [可复现实例（最小可用）](#可复现实例最小可用)
    - [PowerCLI 基础连接与资产导出](#powercli-基础连接与资产导出)
- [安装模块（离线场景跳过）](#安装模块离线场景跳过)
- [Install-Module VMware.PowerCLI -Scope CurrentUser -Force](#install-module-vmwarepowercli-scope-currentuser-force)
- [连接 vCenter（建议使用只读或最小必要权限）](#连接-vcenter建议使用只读或最小必要权限)
- [导出主机/虚拟机清单（资产基线）](#导出主机虚拟机清单资产基线)
    - [调度与编排（示例）](#调度与编排示例)
- [例：按标签迁移低优先级 VM 至成本更低集群（窗口执行）](#例按标签迁移低优先级-vm-至成本更低集群窗口执行)
    - [作业输出归档（新增）](#作业输出归档新增)
    - [API 集成（REST 示例占位）](#api-集成rest-示例占位)
- [获取 vCenter Session（示例，替换为实际 token 获取流程）](#获取-vcenter-session示例替换为实际-token-获取流程)
    - [批量基线核查（示例）](#批量基线核查示例)
- [例：核查 ESXi 是否启用 Lockdown 模式与SSH状态](#例核查-esxi-是否启用-lockdown-模式与ssh状态)
    - [凭据安全与审计留痕（示例）](#凭据安全与审计留痕示例)
- [使用 Windows 凭据管理器/安全存储，避免明文凭据](#使用-windows-凭据管理器安全存储避免明文凭据)
  - [参考脚本与延伸](#参考脚本与延伸)
  - [GitOps 与合规流水线（建议）](#gitops-与合规流水线建议)
  - [变更审批与认证流程（新增）](#变更审批与认证流程新增)



## 导航

- 01_自动化基础.md（若未创建，请补充）
- 02_PowerCLI技术.md（若未创建，请补充）
- 03_vRealize Automation.md（或 Aria Automation）
- 04_API集成开发.md
- 05_工作流编排.md

## 学习路径（建议）

1) 自动化方法论 → 2) PowerCLI 资产与脚本库 → 3) API/SDK 集成 → 4) vRA/Aria 编排 → 5) GitOps 与合规流水线

## 前置条件（最小可用）

- 管理端安装 PowerShell 7+，建议安装 VMware.PowerCLI 模块
- 拥有只读或最小必要权限的 vCenter 账户（建议基于 RBAC）
- 已配置 NTP 与证书；vCenter/ESXi Syslog 已转发至集中日志

### 平台兼容与路径

- PowerShell 7+ 跨平台可用；Windows/ Linux/ macOS 均可运行 PowerCLI
- 模块搜索路径 `$env:PSModulePath` 示例：
  - Windows（当前用户）：`$HOME\Documents\PowerShell\Modules`
  - Windows（所有用户）：`C:\Program Files\PowerShell\7\Modules`
  - Linux：`~/.local/share/powershell/Modules`

### 离线安装 PowerCLI（新增）

- 在线环境：`Install-Module VMware.PowerCLI -Scope CurrentUser -Force`
- 离线环境：在可联网机器执行 `Save-Module VMware.PowerCLI -Path <share>`，将模块目录拷贝到目标机的 `$env:PSModulePath` 路径后 `Import-Module VMware.PowerCLI`

> 若需要企业内部镜像源，可在离线仓库维护 `VMware.PowerCLI` 版本目录结构，并通过文件共享分发。

## 快速Checklist

- 变更自动化与审批流、代码评审与版本化
- 机密与凭据托管（Secrets）、审计追踪与回滚机制
- IaC 模板复用、参数化与环境差异管理
- 与 CMDB/ITSM 集成、闭环度量与报表

## 故障排查（Troubleshooting）

- 证书与 TLS：如遇 `The underlying connection was closed`，临时启用 `Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false`（仅在实验环境）
- 模块冲突：`Get-Module -ListAvailable VMware.*` 检查重复版本，移除旧版本后重启 PowerShell
- API 权限：403/401 多为权限不足或 SSO 会话失效，确认最小权限与 Token 有效期

## 证据与输出规范

- 导出资产/配置/事件到 CSV/JSON 并入库（工件保留90天+）
- 变更脚本与审批记录关联，保留执行日志与回滚脚本

## 调度与任务编排（新增）

### Windows 计划任务（PowerShell）

```powershell
$action = New-ScheduledTaskAction -Execute 'pwsh.exe' -Argument '-File .\\daily_audit.ps1'
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00
Register-ScheduledTask -TaskName 'vSphereDailyAudit' -Action $action -Trigger $trigger -RunLevel Highest
```

### Linux 定时任务（cron）

```bash
crontab -e
# 每日 02:00 执行
0 2 * * * /usr/bin/pwsh -File /opt/vsphere/daily_audit.ps1 >> /opt/vsphere/automation.log 2>&1
```

### 示例脚本 `daily_audit.ps1`（占位）

```powershell
Connect-VIServer vcenter.example.com
Get-VMHost | Select Name, Version, Build | Export-Csv hosts.csv -NoTypeInformation
Get-Task -Start (Get-Date).AddDays(-1) | Export-Csv tasks-yesterday.csv -NoTypeInformation
```

## 对标与参考

- 自动化与编排路线：`../../ai.md`、`../../formal_container/07_执行流控制流数据流/01_系统运行机制深度分析.md`

## 任务蓝图（示例）

- 批量基线核查：脚本巡检 ESXi/vCenter 基线，生成差异报告
- 定时迁移与能耗优化：按标签迁移至低成本集群，窗口执行
- 证据流水线：每日导出资产与事件，推送到合规模块存档

## 可复现实例（最小可用）

### PowerCLI 基础连接与资产导出

```powershell
# 安装模块（离线场景跳过）
# Install-Module VMware.PowerCLI -Scope CurrentUser -Force

# 连接 vCenter（建议使用只读或最小必要权限）
Connect-VIServer -Server vcenter.example.com

# 导出主机/虚拟机清单（资产基线）
Get-VMHost | Select-Object Name, Version, Build | Export-Csv hosts.csv -NoTypeInformation
Get-VM    | Select-Object Name, PowerState, NumCpu, MemoryMB | Export-Csv vms.csv -NoTypeInformation
```

### 调度与编排（示例）

```powershell
# 例：按标签迁移低优先级 VM 至成本更低集群（窗口执行）
$targetCluster = Get-Cluster -Name "Cost-Optimized"
Get-VM -Tag "low-priority" |
  Where-Object {$_.PowerState -eq 'PoweredOn'} |
  Move-VM -Destination $targetCluster -Confirm:$false
```

### 作业输出归档（新增）

```powershell
$date = Get-Date -Format 'yyyy-MM-dd'
New-Item -ItemType Directory -Force -Path "artifacts/$date" | Out-Null
Get-FileHash hosts.csv | Select Hash | Set-Content "artifacts/$date/hosts.csv.sha256"
Move-Item hosts.csv "artifacts/$date/"
Move-Item tasks-yesterday.csv "artifacts/$date/"
```

> 证据要求：保留 CSV/JSON、日志与 `.sha256` 校验文件；同时生成 `manifest.json` 以便审计。

### API 集成（REST 示例占位）

```bash
# 获取 vCenter Session（示例，替换为实际 token 获取流程）
curl -k -X POST https://vcenter.example.com/api/session
```

### 批量基线核查（示例）

```powershell
# 例：核查 ESXi 是否启用 Lockdown 模式与SSH状态
Get-VMHost | Select Name,
  @{N='LockdownMode';E={(Get-VMHostService -VMHost $_ | Where-Object {$_.Key -eq 'TSM-SSH'}).Policy}},
  @{N='SSHRunning';E={(Get-VMHostService -VMHost $_ | Where-Object {$_.Key -eq 'TSM-SSH'}).Running}} |
  Export-Csv esxi_baseline.csv -NoTypeInformation
```

### 凭据安全与审计留痕（示例）

```powershell
# 使用 Windows 凭据管理器/安全存储，避免明文凭据
$cred = Get-Credential  # 或从企业密码库检索
Start-Transcript -Path automation_run.log -Append
try {
  Connect-VIServer -Server vcenter.example.com -Credential $cred | Out-Null
  # 变更操作前生成变更单号
  $ticket = "CHG-2025-0918-001"
  # 示例：创建/修改标签并记录证据
  New-TagCategory -Name "Cost" -Cardinality Single -EntityType VirtualMachine -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
  New-Tag -Name "low-priority" -Category "Cost" -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
  Get-VM -Name "DemoVM" | New-TagAssignment -Tag "low-priority" -Confirm:$false | Out-Null
  # 导出证据（含变更单号）
  Get-TagAssignment -Entity (Get-VM -Name "DemoVM") |
    Select @{N='TicketId';E={$ticket}}, Entity, Tag, @{N='Timestamp';E={(Get-Date).ToString('s')}} |
    Export-Csv evidence_tag_assignment.csv -NoTypeInformation
}
finally {
  Stop-Transcript | Out-Null
}
```

## 参考脚本与延伸

- `01_自动化基础.md`：最小闭环与 `manifest.json` 生成
- 后续页面：`02_PowerCLI技术.md`、`04_API集成开发.md`、`05_工作流编排.md`

## GitOps 与合规流水线（建议）

- 脚本版本化与代码评审；变更单关联与审批流自动化
- 机密托管（例如：Windows 凭据管理器/企业密码库）避免明文凭据
- 运行输出（CSV/JSON）作为流水线工件，供审计与回滚参考

## 变更审批与认证流程（新增）

- 流程要求：需求 → 代码评审 → 安全评审 → 预生产演练 → 变更窗口执行 → 证据归档 → 复盘
- 审批要点：
  - 最小权限与影响面评估（含回滚方案与RPO/RTO）
  - 风险等级与执行窗口（含黑名单时间段）
  - 证据产出列表（CSV/JSON/日志/截图）与保留期
- 运行清单：
  - 变更单号、代码版本（Git commit/Tag）、脚本清单、依赖版本
  - 执行人/复核人、演练记录、回滚验证结果
- 认证对接（占位）：
  - 与 VMware 认证内容映射（例如：VCP-DCV 管理与自动化场景）
  - 输出能力矩阵：PowerCLI、API、vRA 编排、合规与审计
