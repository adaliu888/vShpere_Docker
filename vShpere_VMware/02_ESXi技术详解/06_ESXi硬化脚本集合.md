## 目录

- [ESXi 硬化脚本集合（可执行）](#esxi-硬化脚本集合可执行)
  - [1. 目标](#1-目标)
  - [2. 检查与配置（示例）](#2-检查与配置示例)
- [连接](#连接)
- [禁用未用服务（SSH/ESXi Shell）](#禁用未用服务sshesxi-shell)
- [Syslog 唯一目录](#syslog-唯一目录)
- [锁定模式检查](#锁定模式检查)
- [证据导出](#证据导出)
- [ESXCLI（SSH 临时启用时执行）](#esxclissh-临时启用时执行)
  - [2.1 一键硬化与回滚（示例片段）](#21-一键硬化与回滚示例片段)
  - [3. 归档与清单](#3-归档与清单)
  - [4. 交叉链接](#4-交叉链接)

- [ESXi 硬化脚本集合（可执行）](#esxi-硬化脚本集合可执行)
  - [1. 目标](#1-目标)
  - [2. 检查与配置（示例）](#2-检查与配置示例)
- [连接](#连接)
- [禁用未用服务（SSH/ESXi Shell）](#禁用未用服务sshesxi-shell)
- [Syslog 唯一目录](#syslog-唯一目录)
- [锁定模式检查](#锁定模式检查)
- [证据导出](#证据导出)
- [ESXCLI（SSH 临时启用时执行）](#esxclissh-临时启用时执行)
  - [2.1 一键硬化与回滚（示例片段）](#21-一键硬化与回滚示例片段)
- [回滚示例：按需恢复服务策略](#回滚示例按需恢复服务策略)
  - [3. 归档与清单](#3-归档与清单)
  - [4. 交叉链接](#4-交叉链接)


# ESXi 硬化脚本集合（可执行）

## 1. 目标

- 提供可直接执行的 PowerCLI/ESXCLI 片段以对齐硬化基线，并生成证据

## 2. 检查与配置（示例）

```powershell
# 连接
Connect-VIServer vcenter.example.com

# 禁用未用服务（SSH/ESXi Shell）
Get-VMHost | Get-VMHostService | Where-Object {$_.Key -in 'TSM','TSM-SSH'} |
  Set-VMHostService -Policy Off -Running:$false

# Syslog 唯一目录
Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDirUnique |
  Set-AdvancedSetting -Value $true -Confirm:$false

# 锁定模式检查
Get-VMHost | Get-View | Select-Object Name, @{N='LockdownMode';E={$_.Config.LockdownMode}}

# 证据导出
Get-VMHost | Select Name, @{N='SSH';E={(Get-VMHostService -VMHost $_ | Where-Object {$_.Key -eq 'TSM-SSH'}).Running}} |
  Export-Csv esxi_hardening_services.csv -NoTypeInformation
Get-FileHash -Algorithm SHA256 esxi_hardening_services.csv | Select Hash | Set-Content esxi_hardening_services.csv.sha256
```

```bash
# ESXCLI（SSH 临时启用时执行）
esxcli system settings advanced set -o /Syslog/global/logDirUnique -i 1
esxcli network firewall ruleset list | grep -v false > esxi_firewall_enabled.txt
sha256sum esxi_firewall_enabled.txt > esxi_firewall_enabled.txt.sha256
```

## 2.1 一键硬化与回滚（示例片段）

```powershell
param(
  [switch]$Rollback
)

Start-Transcript -Path hardening.log -Append
try {
  if (-not $Rollback) {
    Get-VMHost | Get-VMHostService | Where-Object {$_.Key -in 'TSM','TSM-SSH'} | Set-VMHostService -Policy Off -Running:$false
    Get-VMHost | Get-AdvancedSetting -Name Syslog.global.logDirUnique | Set-AdvancedSetting -Value $true -Confirm:$false
  } else {
    # 回滚示例：按需恢复服务策略
    Get-VMHost | Get-VMHostService | Where-Object {$_.Key -eq 'TSM'} | Set-VMHostService -Policy On -Running:$false
  }
} finally {
  Stop-Transcript | Out-Null
}
```

## 3. 归档与清单

```text
artifacts/
  YYYY-MM-DD/
    esxi_hardening_services.csv
    esxi_hardening_services.csv.sha256
    esxi_firewall_enabled.txt
    esxi_firewall_enabled.txt.sha256
    manifest.json
```

## 4. 交叉链接

- `../09_安全与合规管理/Checklist_基线清单.md`
- `../09_安全与合规管理/Runbook_审计与变更操作.md`
