# Runbook：vSphere 审计与变更操作

## 目录

- [Runbook：vSphere 审计与变更操作](#runbookvsphere-审计与变更操作)
  - [目录](#目录)
  - [前置条件](#前置条件)
  - [步骤一：时间与日志](#步骤一时间与日志)
  - [步骤二：访问与服务](#步骤二访问与服务)
  - [步骤三：补丁与基线](#步骤三补丁与基线)
  - [步骤四：证据导出与归档](#步骤四证据导出与归档)
    - [REST 报表导出（新增）](#rest-报表导出新增)
    - [配置快照导出（新增）](#配置快照导出新增)
    - [归档结构建议](#归档结构建议)
    - [清单与留存（新增）](#清单与留存新增)
  - [回滚说明](#回滚说明)
  - [记录与验收](#记录与验收)
  - [附：常见问题（FAQ）](#附常见问题faq)

> 目的：在维护窗口内完成合规相关的关键配置与证据留存，支持审计追溯。

## 前置条件

- 变更单已审批，通过窗口时间已确定
- vCenter/ESXi 备份点可用（配置快照或平台快照）
- PowerCLI 已连接并具备必要权限

## 步骤一：时间与日志

1. 校验/配置 NTP

```powershell
Get-VMHost | Get-VMHostNtpServer
Get-VMHost | Add-VMHostNtpServer -NtpServer "time.example.com"
Get-VMHost | Get-VMHostService | Where-Object {$_.Key -eq 'ntpd'} | Set-VMHostService -Policy On -Running $true
```

1. 配置 ESXi Syslog

```powershell
Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logHost
Get-VMHost | Set-VMHostSysLogServer -SysLogServer "udp://syslog.example.com:514"
Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDirUnique | Set-AdvancedSetting -Value $true
```

1. 设置 vCenter 事件/任务保留期

```powershell
Get-AdvancedSetting -Entity (Get-VCenterServer) -Name "VirtualCenter.EventsMaxAge"
Get-AdvancedSetting -Entity (Get-VCenterServer) -Name "VirtualCenter.TasksMaxAge"
```

## 步骤二：访问与服务

1. 关闭 DCUI/ESXi Shell/SSH（如非必需）

```powershell
Get-VMHost | Get-VMHostService | Where-Object {$_.Key -in 'DCUI','TSM','TSM-SSH'} | Set-VMHostService -Policy Off -Running:$false
```

1. 锁定模式状态核查

```powershell
Get-VMHost | Get-View | Select-Object Name, @{N='LockdownMode';E={$_.Config.LockdownMode}}
```

## 步骤三：补丁与基线

```powershell
$cluster = Get-Cluster -Name "Production-Cluster"
$baseline = Get-Baseline -Name "ESXi Security Patches"
Attach-Baseline -Entity $cluster -Baseline $baseline
Get-Compliance -Entity $cluster | Format-Table Entity, Status
```

## 步骤四：证据导出与归档

```powershell
$entity = Get-Cluster -Name "Production-Cluster"
$start  = (Get-Date).AddDays(-7)
Get-VIEvent -Entity $entity -Start $start |
  Where-Object {$_.FullFormattedMessage -match 'login|permission|profile|baseline'} |
  Export-Csv -Path "events-audit.csv" -NoTypeInformation

Get-Task | Select-Object Name, State, StartTime, FinishTime |
  Export-Csv -Path "tasks-archive.csv" -NoTypeInformation
```

### REST 报表导出（新增）

```powershell
# 通过 REST API 导出 vCenter Events（示例，需替换为实际 URL/Token）
$vc = "https://vcenter.example.com"
$token = "<BearerToken>"  # 建议运行前通过安全存储检索
$headers = @{ Authorization = "Bearer $token" }

# 示例：查询最近7天事件（分页/过滤按需扩展）
$since = (Get-Date).AddDays(-7).ToString('o')
$uri = "$vc/api/vcenter/evtmgr/events?start_time=$([uri]::EscapeDataString($since))"
$resp = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers -SkipCertificateCheck
$resp | ConvertTo-Json -Depth 5 | Set-Content vc_events.json

# 统一证据清单与哈希
Get-FileHash -Algorithm SHA256 events-audit.csv | Select-Object Hash | Set-Content events-audit.csv.sha256
Get-FileHash -Algorithm SHA256 tasks-archive.csv | Select-Object Hash | Set-Content tasks-archive.csv.sha256
Get-FileHash -Algorithm SHA256 vc_events.json | Select-Object Hash | Set-Content vc_events.json.sha256
```

### 配置快照导出（新增）

```powershell
# 导出主机关键配置（Syslog/服务/锁定模式）为 JSON
$date = Get-Date -Format 'yyyyMMdd'
$out  = Join-Path -Path "configs-$date" -ChildPath "cluster-Production-Cluster"
New-Item -ItemType Directory -Force -Path $out | Out-Null

Get-VMHost | ForEach-Object {
  $host = $_
  $syslog = Get-AdvancedSetting -Entity $host -Name Syslog.global.logHost
  $unique = Get-AdvancedSetting -Entity $host -Name Syslog.global.logDirUnique
  $svc    = Get-VMHostService -VMHost $host
  $view   = Get-View -ViewType HostSystem -Filter @{ Name = $host.Name }
  $obj = [PSCustomObject]@{
    Host            = $host.Name
    SyslogHost      = $syslog.Value
    SyslogUniqueDir = [bool]$unique.Value
    Services        = $svc | Select-Object Key, Policy, Running
    LockdownMode    = $view.Config.LockdownMode
  }
  $obj | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $out "host-$($host.Name).json")
}
```

### 归档结构建议

```text
artifacts/
├─ events/
│  └─ events-audit-YYYYMMDD.csv
├─ tasks/
│  └─ tasks-archive-YYYYMM.csv
├─ configs/
│  └─ cluster-<name>/host-<name>/*.json
└─ reports/
   └─ compliance-report-YYYYMM.pdf
```

### 清单与留存（新增）

- 生成 `manifest.json`，包含 artifacts 列表、SHA256、TicketId、retentionDays、storageClass（WORM）
- 将 CSV/JSON 与 `.sha256` 文件与 manifest 一并归档至 `artifacts/` 对应日期目录

## 回滚说明

- 如 NTP/Syslog 变更导致异常，恢复至变更前记录的配置值
- 如服务关闭影响运维，按审批在窗口内临时启用并记录理由

## 记录与验收

- 附件：CSV 导出、配置快照、合规状态截图
- 验收：对照 `Checklist_基线清单.md` 勾检并签署

## 附：常见问题（FAQ）

- 事件导出过慢：增加 `-MaxSamples` 限制或按实体分批导出
- Syslog 未生效：检查主机到日志服务器连通性与端口（udp/514 或 tcp/6514）
- 锁定模式异常：优先用 Host Profile 管控，避免逐台手工改动
