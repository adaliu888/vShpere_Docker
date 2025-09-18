# 02 PowerCLI 技术

## 目标

- 提供可直接复用的 PowerCLI 最小可复现实例与最佳实践
- 覆盖连接、查询、变更、导出证据与回滚的基础闭环

## 前置条件

- PowerShell 7+ 或 Windows PowerShell 5.1+
- 安装 VMware.PowerCLI 模块（离线导入可参考目录 README）
- vCenter 可达且具备最小必要权限账号

## 基础配置

```powershell
# 可选：在实验环境忽略自签证书（生产不建议）
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Scope Session -Confirm:$false | Out-Null

# 导入模块（如已自动加载可省略）
Import-Module VMware.PowerCLI -ErrorAction SilentlyContinue
```

## 连接与断开

```powershell
$cred = Get-Credential  # 建议使用凭据管理器或企业密码库
Connect-VIServer -Server vcenter.example.com -Credential $cred

# 结束后断开
Disconnect-VIServer -Server vcenter.example.com -Confirm:$false
```

## 资产导出（可审计）

```powershell
Connect-VIServer vcenter.example.com

$date = Get-Date -Format 'yyyy-MM-dd'
New-Item -ItemType Directory -Force -Path "artifacts/$date" | Out-Null

Get-VMHost | Select Name, Version, Build |
  Export-Csv hosts.csv -NoTypeInformation
Get-VM | Select Name, PowerState, NumCpu, MemoryMB, Folder |
  Export-Csv vms.csv -NoTypeInformation

Get-FileHash -Algorithm SHA256 hosts.csv | Select Hash | Set-Content "artifacts/$date/hosts.csv.sha256"
Get-FileHash -Algorithm SHA256 vms.csv   | Select Hash | Set-Content "artifacts/$date/vms.csv.sha256"
Move-Item hosts.csv "artifacts/$date/"
Move-Item vms.csv   "artifacts/$date/"
```

## 查询与筛选示例

```powershell
# 查询近24小时失败任务
Get-Task -Start (Get-Date).AddDays(-1) | Where-Object {$_.State -eq 'Error'}

# 查询打特定标签的 VM
Get-VM -Tag 'low-priority' | Select Name, PowerState
```

## 变更与回滚示例（含证据）

```powershell
Start-Transcript -Path automation_run.log -Append
try {
  $ticket = 'CHG-2025-0918-002'
  Connect-VIServer vcenter.example.com | Out-Null

  # 例：为指定 VM 调整 CPU 核数
  $vmName = 'DemoVM'
  $old = Get-VM -Name $vmName | Select-Object Name, NumCpu
  Set-VM -VM $vmName -NumCpu 4 -Confirm:$false | Out-Null
  $new = Get-VM -Name $vmName | Select-Object Name, NumCpu

  # 证据输出
  $evidence = [pscustomobject]@{
    TicketId  = $ticket
    Name      = $vmName
    OldNumCpu = $old.NumCpu
    NewNumCpu = $new.NumCpu
    Timestamp = (Get-Date).ToString('s')
  }
  $date = Get-Date -Format 'yyyy-MM-dd'
  New-Item -ItemType Directory -Force -Path "artifacts/$date" | Out-Null
  $evidence | Export-Csv "artifacts/$date/cpu_change.csv" -NoTypeInformation
  Get-FileHash "artifacts/$date/cpu_change.csv" | Select Hash |
    Set-Content "artifacts/$date/cpu_change.csv.sha256"
}
catch {
  Write-Error $_
}
finally {
  Stop-Transcript | Out-Null
}
```

回滚建议：在变更前导出原配置（如 CPU/内存/网络/存储），回滚时按清单恢复。

## 批量基线核查

```powershell
Connect-VIServer vcenter.example.com
Get-VMHost | Select Name,
  @{N='Lockdown';E={(Get-VMHost | Get-View).Config.LockdownMode}},
  @{N='SSHRunning';E={(Get-VMHostService -VMHost $_ | Where-Object {$_.Key -eq 'TSM-SSH'}).Running}} |
  Export-Csv esxi_baseline.csv -NoTypeInformation
```

## 常见问题排查

- TLS/证书问题：临时使用 `-InvalidCertificateAction Ignore`，生产改为可信证书
- 性能与超时：对大规模清单使用 `-PipelineVariable`、`Get-View` 批量化
- 权限不足：采用最小权限角色并按需授予 API 操作权限

## 参考

- `01_自动化基础.md`
- `README.md`

## 02 PowerCLI 技术（安装、连接、资产/合规导出）

## 目标1

- 提供可复现的 PowerCLI 安装方式（在线/离线）与连接范式
- 形成资产、配置、事件的标准导出与证据留存

## 安装

### 在线安装

```powershell
Install-Module VMware.PowerCLI -Scope CurrentUser -Force
Import-Module VMware.PowerCLI
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
```

### 离线安装

```powershell
# 在可联网机器
Save-Module VMware.PowerCLI -Path \\share\psmodules
# 在目标机器（拷贝后）
Copy-Item \\share\psmodules\VMware* -Destination $env:PSModulePath -Recurse
Import-Module VMware.PowerCLI
```

## 连接 vCenter（最小范式）

```powershell
$server = 'vcenter.example.com'
Connect-VIServer -Server $server  # 建议使用凭据管理器/企业密码库
```

可选：

```powershell
$cred = Get-Credential
Connect-VIServer -Server $server -Credential $cred
```

## 资产导出（CSV）

```powershell
Get-VMHost | Select-Object Name, Version, Build |
  Export-Csv hosts.csv -NoTypeInformation
Get-VM | Select-Object Name, PowerState, NumCpu, MemoryMB |
  Export-Csv vms.csv -NoTypeInformation
```

## 合规基线核查（示例）

```powershell
# SSH 服务策略与运行状态
Get-VMHost | ForEach-Object {
  $svc = Get-VMHostService -VMHost $_ | Where-Object {$_.Key -eq 'TSM-SSH'}
  [pscustomobject]@{
    Host    = $_.Name
    Service = 'TSM-SSH'
    Policy  = $svc.Policy
    Running = $svc.Running
  }
} | Export-Csv esxi_services_ssh.csv -NoTypeInformation

# Lockdown 模式
Get-VMHost | Get-View |
  Select-Object Name, @{N='LockdownMode';E={$_.Config.LockdownMode}} |
  Export-Csv esxi_lockdown.csv -NoTypeInformation
```

## 事件与任务导出（证据）

```powershell
$start = (Get-Date).AddDays(-7)
Get-VIEvent -Start $start |
  Where-Object { $_.FullFormattedMessage -match 'login|permission|profile|baseline' } |
  Export-Csv events-audit.csv -NoTypeInformation

Get-Task -Start $start |
  Select-Object Name, State, StartTime, FinishTime |
  Export-Csv tasks-archive.csv -NoTypeInformation
```

## 证据留存与完整性

```powershell
$date = Get-Date -Format 'yyyy-MM-dd'
New-Item -ItemType Directory -Force -Path "artifacts/$date" | Out-Null
foreach ($f in 'hosts.csv','vms.csv','esxi_services_ssh.csv','esxi_lockdown.csv','events-audit.csv','tasks-archive.csv') {
  if (Test-Path $f) {
    Get-FileHash -Algorithm SHA256 $f | Select Hash | Set-Content "artifacts/$date/$f.sha256"
    Move-Item $f "artifacts/$date/"
  }
}

$manifest = [pscustomobject]@{
  ticketId      = 'CHG-<id>'
  generatedAt   = (Get-Date).ToString('s')
  generatedBy   = 'PowerCLI'
  retentionDays = 180
  artifacts     = Get-ChildItem "artifacts/$date" -Filter *.csv | ForEach-Object {
    [pscustomobject]@{ name=$_.Name; sha256=(Get-Content ("artifacts/$date/"+$_.Name+".sha256")).Trim() }
  }
} | ConvertTo-Json -Depth 4
$manifest | Set-Content "artifacts/$date/manifest.json"
```

## 参考1

- `../09_安全与合规管理/Checklist_基线清单.md`
- `../09_安全与合规管理/Runbook_审计与变更操作.md`
- `../09_安全与合规管理/Templates_证据与对标映射.md`
