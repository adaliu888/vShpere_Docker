## 目录

- [Templates：证据与对标映射（模板）](#templates证据与对标映射模板)
  - [1. 命名规范（Evidence Naming）](#1-命名规范evidence-naming)
  - [2. 字段模板（CSV/JSON）](#2-字段模板csvjson)
  - [3. 对标映射表（示例）](#3-对标映射表示例)
  - [4. 证据生成脚本占位](#4-证据生成脚本占位)
- [vCenter/ESXi Syslog 配置与状态导出（示例）](#vcenteresxi-syslog-配置与状态导出示例)
  - [5. 审核与留存流程](#5-审核与留存流程)
  - [6. manifest 模式（新增）](#6-manifest-模式新增)
  - [7. 留存与归档建议（新增）](#7-留存与归档建议新增)
  - [8. 变更记录](#8-变更记录)
  - [9. 证据完整性校验与留存示例（扩展）](#9-证据完整性校验与留存示例扩展)

- [Templates：证据与对标映射（模板）](#templates证据与对标映射模板)
  - [1. 命名规范（Evidence Naming）](#1-命名规范evidence-naming)
  - [2. 字段模板（CSV/JSON）](#2-字段模板csvjson)
  - [3. 对标映射表（示例）](#3-对标映射表示例)
  - [4. 证据生成脚本占位](#4-证据生成脚本占位)
- [vCenter/ESXi Syslog 配置与状态导出（示例）](#vcenteresxi-syslog-配置与状态导出示例)
  - [5. 审核与留存流程](#5-审核与留存流程)
  - [6. manifest 模式（新增）](#6-manifest-模式新增)
  - [7. 留存与归档建议（新增）](#7-留存与归档建议新增)
  - [8. 变更记录](#8-变更记录)
  - [9. 证据完整性校验与留存示例（扩展）](#9-证据完整性校验与留存示例扩展)


# Templates：证据与对标映射（模板）

> 目的：将标准条款 → 控制项 → 执行证据 建立一一映射，确保审计可追溯、变更可验证。

## 1. 命名规范（Evidence Naming）

- 文件命名：`日期_系统_域_控制项_环境_版本.扩展名`
  - 示例：`2025-09-18_vSphere_Audit_SyslogForwarding_Prod_v1.csv`
- 目录结构：
  - `evidence/YYMM/域/系统/控制项/环境/`
  - 示例：`evidence/2509/SEC/vSphere/SyslogForwarding/Prod/`
- 元数据清单（manifest.json）：
  - `controlId`、`standard`、`owner`、`generatedBy`、`hash`、`retentionDays`

## 2. 字段模板（CSV/JSON）

- 最小字段：`Timestamp, Source, Object, ControlId, Expected, Actual, Result, Operator, TicketId`
- 建议增加：`Version, Tool, Command, EvidenceHash, Reviewer`

## 3. 对标映射表（示例）

| Standard | Clause/ID | Control（控制项） | Expected（期望） | Evidence（证据样例） | 生成方式 |
|---|---|---|---|---|---|
| ISO/IEC 27001 | A.12.4 | 集中日志与监控 | vCenter/ESXi Syslog 远转启用 | `syslog_targets.csv`、`esxi_syslog_status.json` | PowerCLI/ESXCLI 导出 |
| NIST SP 800-53 | AU-6 | 审计审查与报告 | 每日生成审计事件报表 | `vc_audit_events_YYYYMMDD.csv` | REST API 导出/SQL 报表 |
| CIS vSphere | 1.1.1 | 禁用未用服务 | SSH 设为手动且非运行 | `esxi_services_ssh.csv` | PowerCLI `Get-VMHostService` |
| CIS ESXi | 3.2 | 账户锁定策略 | 锁定阈值与时间符合基线 | `esxi_account_lockout.csv` | ESXCLI/PowerCLI |
| PCI DSS | 10.x | 审计与保留 | 保留≥90天，可检索 | `log_retention_manifest.json` | 日志平台导出 |

## 4. 证据生成脚本占位

```powershell
# vCenter/ESXi Syslog 配置与状态导出（示例）
Connect-VIServer -Server vcenter.example.com
Get-VMHost | Select Name, @{N='SyslogHost';E={(Get-AdvancedSetting -Entity $_ -Name Syslog.global.logHost).Value}} |
  Export-Csv syslog_targets.csv -NoTypeInformation

Get-VMHost | ForEach-Object {
  $ssh = Get-VMHostService -VMHost $_ | Where-Object {$_.Key -eq 'TSM-SSH'}
  [PSCustomObject]@{
    Host = $_.Name
    Service = 'TSM-SSH'
    Policy = $ssh.Policy
    Running = $ssh.Running
    ControlId = 'CIS-ESXi-SSH-01'
  }
} | Export-Csv esxi_services_ssh.csv -NoTypeInformation
```

```json
{
  "controlId": "ISO27001-A.12.4",
  "standard": "ISO/IEC 27001:2022",
  "owner": "secops",
  "generatedBy": "PowerCLI 13",
  "hash": "<sha256>",
  "retentionDays": 180,
  "artifacts": [
    "syslog_targets.csv",
    "esxi_services_ssh.csv"
  ]
}
```

## 5. 审核与留存流程

- 生成：脚本/流水线每日定时运行，失败自动告警
- 复核：双人复核（Operator/Reviewer），签名并归档 manifest
- 留存：冷存 ≥90 天，关键证据启用 WORM/不可篡改存储
- 追溯：TicketId 关联变更单/问题单，形成闭环

## 6. manifest 模式（新增）

```json
{
  "ticketId": "CHG-2025-0918-001",
  "generatedAt": "2025-09-18T10:00:00Z",
  "generatedBy": "PowerCLI 13",
  "retentionDays": 180,
  "storageClass": "WORM",
  "artifacts": [
    {"name": "syslog_targets.csv", "sha256": "<hash>", "standard": "ISO27001-A.12.4", "controlId": "LOG-SYSLOG-001"},
    {"name": "esxi_services_ssh.csv", "sha256": "<hash>", "standard": "CIS-ESXi", "controlId": "CIS-SSH-001"},
    {"name": "vc_events.json", "sha256": "<hash>", "standard": "NIST-AU", "controlId": "AU-6-Events"}
  ]
}
```

## 7. 留存与归档建议（新增）

- 目录：`artifacts/YYYY-MM/<域>/<系统>/<控制项>/<环境>/`
- 清单：每个目录包含 `manifest.json` 与所有 `.sha256` 文件
- 不可变：对象存储 WORM 或文件系统只读快照，记录到期处理流程

## 8. 变更记录

- 2025-09-18：创建初版模板与示例脚本/清单结构

## 9. 证据完整性校验与留存示例（扩展）

- 生成哈希（Windows PowerShell）：

```powershell
Get-FileHash -Algorithm SHA256 syslog_targets.csv | Select-Object Hash | Set-Content syslog_targets.csv.sha256
Get-FileHash -Algorithm SHA256 esxi_services_ssh.csv | Select-Object Hash | Set-Content esxi_services_ssh.csv.sha256
```

- 生成哈希（Linux/WSL）：

```bash
sha256sum syslog_targets.csv > syslog_targets.csv.sha256
sha256sum esxi_services_ssh.csv > esxi_services_ssh.csv.sha256
```

- 更新 manifest（字段扩展建议）：

```json
{
  "artifacts": [
    {"name": "syslog_targets.csv", "sha256": "<hash>", "signed": false},
    {"name": "esxi_services_ssh.csv", "sha256": "<hash>", "signed": false}
  ],
  "retentionDays": 180,
  "storageClass": "WORM",
  "location": "artifacts/2025-09/SEC/vSphere/SyslogForwarding/Prod/"
}
```

- 不可变/WORM 留存建议：
  - 对关键证据使用对象存储的不可变策略或文件系统的快照只读策略
  - 记录保留策略与到期处理流程，避免违规删除
