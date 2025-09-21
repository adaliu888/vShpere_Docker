## 目录

- [PowerCLI技术详解](#powercli技术详解)
  - [PowerCLI概述](#powercli概述)
    - [什么是PowerCLI](#什么是powercli)
    - [安装和配置](#安装和配置)
- [安装PowerCLI模块](#安装powercli模块)
- [导入模块](#导入模块)
- [查看已安装的模块](#查看已安装的模块)
- [配置PowerCLI设置](#配置powercli设置)
  - [连接管理](#连接管理)
    - [连接vCenter Server](#连接vcenter-server)
- [基本连接](#基本连接)
- [使用凭据连接](#使用凭据连接)
- [连接多个vCenter](#连接多个vcenter)
- [查看连接状态](#查看连接状态)
- [断开连接](#断开连接)
    - [会话管理](#会话管理)
- [保存会话](#保存会话)
- [恢复会话](#恢复会话)
- [会话超时设置](#会话超时设置)
  - [主机管理](#主机管理)
    - [ESXi主机操作](#esxi主机操作)
- [获取主机信息](#获取主机信息)
- [添加主机到vCenter](#添加主机到vcenter)
- [移除主机](#移除主机)
- [主机维护模式](#主机维护模式)
- [重启主机](#重启主机)
    - [主机配置](#主机配置)
- [配置NTP](#配置ntp)
- [配置Syslog](#配置syslog)
- [配置防火墙](#配置防火墙)
- [配置高级设置](#配置高级设置)
  - [虚拟机管理](#虚拟机管理)
    - [虚拟机操作](#虚拟机操作)
- [获取虚拟机信息](#获取虚拟机信息)
- [创建虚拟机](#创建虚拟机)
- [启动虚拟机](#启动虚拟机)
- [停止虚拟机](#停止虚拟机)
- [重启虚拟机](#重启虚拟机)
- [挂起虚拟机](#挂起虚拟机)
- [恢复虚拟机](#恢复虚拟机)
    - [虚拟机配置](#虚拟机配置)
- [修改虚拟机配置](#修改虚拟机配置)
- [添加硬盘](#添加硬盘)
- [添加网络适配器](#添加网络适配器)
- [配置CD/DVD](#配置cddvd)
- [配置快照](#配置快照)
    - [虚拟机克隆和模板](#虚拟机克隆和模板)
- [克隆虚拟机](#克隆虚拟机)
- [创建模板](#创建模板)
- [从模板部署](#从模板部署)
- [自定义规范](#自定义规范)
  - [集群管理](#集群管理)
    - [集群操作](#集群操作)
- [创建集群](#创建集群)
- [添加主机到集群](#添加主机到集群)
- [配置HA](#配置ha)
- [配置DRS](#配置drs)
- [配置EVC](#配置evc)
    - [资源池管理](#资源池管理)
- [创建资源池](#创建资源池)
- [配置资源池](#配置资源池)
- [移动虚拟机到资源池](#移动虚拟机到资源池)
  - [存储管理](#存储管理)
    - [数据存储操作](#数据存储操作)
- [获取数据存储信息](#获取数据存储信息)
- [创建数据存储](#创建数据存储)
- [移除数据存储](#移除数据存储)
- [扩展数据存储](#扩展数据存储)
    - [vSAN管理](#vsan管理)
- [启用vSAN](#启用vsan)
- [配置vSAN存储策略](#配置vsan存储策略)
- [应用存储策略](#应用存储策略)
  - [网络管理](#网络管理)
    - [虚拟交换机](#虚拟交换机)
- [获取虚拟交换机](#获取虚拟交换机)
- [创建标准交换机](#创建标准交换机)
- [创建端口组](#创建端口组)
- [配置端口组](#配置端口组)
    - [分布式交换机](#分布式交换机)
- [创建分布式交换机](#创建分布式交换机)
- [添加主机到分布式交换机](#添加主机到分布式交换机)
- [创建分布式端口组](#创建分布式端口组)
- [配置分布式端口组](#配置分布式端口组)
  - [性能监控](#性能监控)
    - [性能统计](#性能统计)
- [获取实时性能统计](#获取实时性能统计)
- [获取历史性能统计](#获取历史性能统计)
- [获取多个统计指标](#获取多个统计指标)
    - [性能分析](#性能分析)
- [性能分析脚本](#性能分析脚本)
  - [事件和任务管理](#事件和任务管理)
    - [事件管理](#事件管理)
- [获取事件](#获取事件)
- [获取特定类型的事件](#获取特定类型的事件)
- [获取虚拟机事件](#获取虚拟机事件)
    - [任务管理](#任务管理)
- [获取任务](#获取任务)
- [获取正在运行的任务](#获取正在运行的任务)
- [等待任务完成](#等待任务完成)
  - [高级功能](#高级功能)
    - [批量操作](#批量操作)
- [批量启动虚拟机](#批量启动虚拟机)
- [批量配置虚拟机](#批量配置虚拟机)
- [批量创建快照](#批量创建快照)
    - [自动化脚本](#自动化脚本)
- [自动化部署脚本](#自动化部署脚本)
- [使用示例](#使用示例)
    - [错误处理](#错误处理)
- [错误处理示例](#错误处理示例)
- [使用示例](#使用示例)
  - [最佳实践](#最佳实践)
    - [性能优化](#性能优化)
    - [错误处理1](#错误处理1)
    - [安全考虑](#安全考虑)

- [PowerCLI技术详解](#powercli技术详解)
  - [PowerCLI概述](#powercli概述)
    - [什么是PowerCLI](#什么是powercli)
    - [安装和配置](#安装和配置)
- [安装PowerCLI模块](#安装powercli模块)
- [导入模块](#导入模块)
- [查看已安装的模块](#查看已安装的模块)
- [配置PowerCLI设置](#配置powercli设置)
  - [连接管理](#连接管理)
    - [连接vCenter Server](#连接vcenter-server)
- [基本连接](#基本连接)
- [使用凭据连接](#使用凭据连接)
- [连接多个vCenter](#连接多个vcenter)
- [查看连接状态](#查看连接状态)
- [断开连接](#断开连接)
    - [会话管理](#会话管理)
- [保存会话](#保存会话)
- [恢复会话](#恢复会话)
- [会话超时设置](#会话超时设置)
  - [主机管理](#主机管理)
    - [ESXi主机操作](#esxi主机操作)
- [获取主机信息](#获取主机信息)
- [添加主机到vCenter](#添加主机到vcenter)
- [移除主机](#移除主机)
- [主机维护模式](#主机维护模式)
- [重启主机](#重启主机)
    - [主机配置](#主机配置)
- [配置NTP](#配置ntp)
- [配置Syslog](#配置syslog)
- [配置防火墙](#配置防火墙)
- [配置高级设置](#配置高级设置)
  - [虚拟机管理](#虚拟机管理)
    - [虚拟机操作](#虚拟机操作)
- [获取虚拟机信息](#获取虚拟机信息)
- [创建虚拟机](#创建虚拟机)
- [启动虚拟机](#启动虚拟机)
- [停止虚拟机](#停止虚拟机)
- [重启虚拟机](#重启虚拟机)
- [挂起虚拟机](#挂起虚拟机)
- [恢复虚拟机](#恢复虚拟机)
    - [虚拟机配置](#虚拟机配置)
- [修改虚拟机配置](#修改虚拟机配置)
- [添加硬盘](#添加硬盘)
- [添加网络适配器](#添加网络适配器)
- [配置CD/DVD](#配置cddvd)
- [配置快照](#配置快照)
    - [虚拟机克隆和模板](#虚拟机克隆和模板)
- [克隆虚拟机](#克隆虚拟机)
- [创建模板](#创建模板)
- [从模板部署](#从模板部署)
- [自定义规范](#自定义规范)
  - [集群管理](#集群管理)
    - [集群操作](#集群操作)
- [创建集群](#创建集群)
- [添加主机到集群](#添加主机到集群)
- [配置HA](#配置ha)
- [配置DRS](#配置drs)
- [配置EVC](#配置evc)
    - [资源池管理](#资源池管理)
- [创建资源池](#创建资源池)
- [配置资源池](#配置资源池)
- [移动虚拟机到资源池](#移动虚拟机到资源池)
  - [存储管理](#存储管理)
    - [数据存储操作](#数据存储操作)
- [获取数据存储信息](#获取数据存储信息)
- [创建数据存储](#创建数据存储)
- [移除数据存储](#移除数据存储)
- [扩展数据存储](#扩展数据存储)
    - [vSAN管理](#vsan管理)
- [启用vSAN](#启用vsan)
- [配置vSAN存储策略](#配置vsan存储策略)
- [应用存储策略](#应用存储策略)
  - [网络管理](#网络管理)
    - [虚拟交换机](#虚拟交换机)
- [获取虚拟交换机](#获取虚拟交换机)
- [创建标准交换机](#创建标准交换机)
- [创建端口组](#创建端口组)
- [配置端口组](#配置端口组)
    - [分布式交换机](#分布式交换机)
- [创建分布式交换机](#创建分布式交换机)
- [添加主机到分布式交换机](#添加主机到分布式交换机)
- [创建分布式端口组](#创建分布式端口组)
- [配置分布式端口组](#配置分布式端口组)
  - [性能监控](#性能监控)
    - [性能统计](#性能统计)
- [获取实时性能统计](#获取实时性能统计)
- [获取历史性能统计](#获取历史性能统计)
- [获取多个统计指标](#获取多个统计指标)
    - [性能分析](#性能分析)
- [性能分析脚本](#性能分析脚本)
  - [事件和任务管理](#事件和任务管理)
    - [事件管理](#事件管理)
- [获取事件](#获取事件)
- [获取特定类型的事件](#获取特定类型的事件)
- [获取虚拟机事件](#获取虚拟机事件)
    - [任务管理](#任务管理)
- [获取任务](#获取任务)
- [获取正在运行的任务](#获取正在运行的任务)
- [等待任务完成](#等待任务完成)
  - [高级功能](#高级功能)
    - [批量操作](#批量操作)
- [批量启动虚拟机](#批量启动虚拟机)
- [批量配置虚拟机](#批量配置虚拟机)
- [批量创建快照](#批量创建快照)
    - [自动化脚本](#自动化脚本)
- [自动化部署脚本](#自动化部署脚本)
- [使用示例](#使用示例)
    - [错误处理](#错误处理)
- [错误处理示例](#错误处理示例)
- [使用示例](#使用示例)
  - [最佳实践](#最佳实践)
    - [性能优化](#性能优化)
    - [错误处理1](#错误处理1)
    - [安全考虑](#安全考虑)


# PowerCLI技术详解

## PowerCLI概述

### 什么是PowerCLI

PowerCLI是VMware提供的PowerShell模块集合，用于自动化管理vSphere环境。它提供了丰富的cmdlet来管理ESXi主机、vCenter Server、虚拟机等资源。

### 安装和配置

```powershell
# 安装PowerCLI模块
Install-Module VMware.PowerCLI -Scope CurrentUser -Force

# 导入模块
Import-Module VMware.PowerCLI

# 查看已安装的模块
Get-Module VMware.PowerCLI -ListAvailable

# 配置PowerCLI设置
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
Set-PowerCLIConfiguration -DefaultVIServerMode Multiple -Confirm:$false
```

## 连接管理

### 连接vCenter Server

```powershell
# 基本连接
Connect-VIServer -Server vcenter.company.com

# 使用凭据连接
$credential = Get-Credential
Connect-VIServer -Server vcenter.company.com -Credential $credential

# 连接多个vCenter
Connect-VIServer -Server @("vcenter1.company.com", "vcenter2.company.com")

# 查看连接状态
Get-VIServer

# 断开连接
Disconnect-VIServer -Server vcenter.company.com -Confirm:$false
```

### 会话管理

```powershell
# 保存会话
Save-VIServer -Server vcenter.company.com -Path "C:\Scripts\session.xml"

# 恢复会话
Restore-VIServer -Path "C:\Scripts\session.xml"

# 会话超时设置
Set-PowerCLIConfiguration -WebOperationTimeoutSeconds 300 -Confirm:$false
```

## 主机管理

### ESXi主机操作

```powershell
# 获取主机信息
Get-VMHost | Select Name, Version, ConnectionState, PowerState

# 添加主机到vCenter
Add-VMHost -Name "esxi01.company.com" -Location (Get-Datacenter -Name "Datacenter1")

# 移除主机
Remove-VMHost -VMHost "esxi01.company.com" -Confirm:$false

# 主机维护模式
Set-VMHost -VMHost "esxi01.company.com" -State Maintenance
Set-VMHost -VMHost "esxi01.company.com" -State Connected

# 重启主机
Restart-VMHost -VMHost "esxi01.company.com" -Confirm:$false
```

### 主机配置

```powershell
# 配置NTP
Get-VMHost | Add-VMHostNtpServer -NtpServer "pool.ntp.org"
Get-VMHost | Get-VMHostService | Where-Object {$_.Key -eq 'ntpd'} | Set-VMHostService -Policy On -Running $true

# 配置Syslog
Get-VMHost | Set-VMHostSysLogServer -SysLogServer "udp://syslog.company.com:514"

# 配置防火墙
Get-VMHost | Get-VMHostFirewallSystem | Set-VMHostFirewallSystem -Enabled $true

# 配置高级设置
Get-VMHost | Get-AdvancedSetting -Name "Mem.MemEagerZero" | Set-AdvancedSetting -Value 1
```

## 虚拟机管理

### 虚拟机操作

```powershell
# 获取虚拟机信息
Get-VM | Select Name, PowerState, NumCpu, MemoryGB, Guest

# 创建虚拟机
New-VM -Name "TestVM" -Template "Windows2019Template" -Datastore "Datastore1" -Location "Cluster1"

# 启动虚拟机
Start-VM -VM "TestVM"

# 停止虚拟机
Stop-VM -VM "TestVM" -Confirm:$false

# 重启虚拟机
Restart-VM -VM "TestVM" -Confirm:$false

# 挂起虚拟机
Suspend-VM -VM "TestVM"

# 恢复虚拟机
Resume-VM -VM "TestVM"
```

### 虚拟机配置

```powershell
# 修改虚拟机配置
Set-VM -VM "TestVM" -NumCpu 4 -MemoryGB 8

# 添加硬盘
New-HardDisk -VM "TestVM" -CapacityGB 100 -StorageFormat "Thin"

# 添加网络适配器
New-NetworkAdapter -VM "TestVM" -NetworkName "VM Network" -Type "Vmxnet3"

# 配置CD/DVD
Set-CDDrive -CD "TestVM" -IsoPath "[Datastore1] ISO/Windows2019.iso" -Connected $true

# 配置快照
New-Snapshot -VM "TestVM" -Name "Before Update" -Description "快照描述"
Get-Snapshot -VM "TestVM" | Restore-Snapshot
Remove-Snapshot -Snapshot (Get-Snapshot -VM "TestVM" -Name "Before Update") -Confirm:$false
```

### 虚拟机克隆和模板

```powershell
# 克隆虚拟机
New-VM -Name "TestVM-Clone" -VM "TestVM" -Datastore "Datastore1"

# 创建模板
Set-Template -Template "Windows2019Template" -ToVM

# 从模板部署
New-VM -Name "NewVM" -Template "Windows2019Template" -Datastore "Datastore1"

# 自定义规范
New-OSCustomizationSpec -Name "Windows2019Spec" -OSType Windows -FullName "Administrator" -OrgName "Company"
Set-VM -VM "NewVM" -OSCustomizationSpec "Windows2019Spec"
```

## 集群管理

### 集群操作

```powershell
# 创建集群
New-Cluster -Name "Production" -Location (Get-Datacenter -Name "Datacenter1")

# 添加主机到集群
Add-VMHost -Name "esxi01.company.com" -Location (Get-Cluster -Name "Production")

# 配置HA
Set-Cluster -Cluster "Production" -HAEnabled $true
Set-Cluster -Cluster "Production" -HAAdmissionControlEnabled $true

# 配置DRS
Set-Cluster -Cluster "Production" -DRSEnabled $true
Set-Cluster -Cluster "Production" -DRSAutomationLevel "FullyAutomated"

# 配置EVC
Set-Cluster -Cluster "Production" -EVCMode "intel-broadwell"
```

### 资源池管理

```powershell
# 创建资源池
New-ResourcePool -Name "Development" -Location (Get-Cluster -Name "Production")

# 配置资源池
Set-ResourcePool -ResourcePool "Development" -CpuLimitMHz 8000 -MemLimitGB 16

# 移动虚拟机到资源池
Move-VM -VM "TestVM" -Destination (Get-ResourcePool -Name "Development")
```

## 存储管理

### 数据存储操作

```powershell
# 获取数据存储信息
Get-Datastore | Select Name, FreeSpaceGB, CapacityGB, Type

# 创建数据存储
New-Datastore -Name "NewDatastore" -VMHost "esxi01.company.com" -Path "/vmfs/volumes/datastore1"

# 移除数据存储
Remove-Datastore -Datastore "OldDatastore" -Confirm:$false

# 扩展数据存储
Get-Datastore -Name "Datastore1" | Set-Datastore -CapacityGB 2000
```

### vSAN管理

```powershell
# 启用vSAN
Enable-VsanCluster -Cluster "Production"

# 配置vSAN存储策略
New-SpbmStoragePolicy -Name "Gold-Tier" -Description "高性能存储策略" -Rules @(
    New-SpbmRule -Capability @{
        "VSAN.hostFailuresToTolerate" = "1"
        "VSAN.forceProvisioning" = "false"
        "VSAN.replicaPreference" = "RAID-1 (Mirroring)"
    }
)

# 应用存储策略
Set-SpbmEntityConfiguration -Configuration (Get-VM -Name "TestVM") -StoragePolicy "Gold-Tier"
```

## 网络管理

### 虚拟交换机

```powershell
# 获取虚拟交换机
Get-VirtualSwitch -VMHost "esxi01.company.com"

# 创建标准交换机
New-VirtualSwitch -VMHost "esxi01.company.com" -Name "vSwitch1"

# 创建端口组
New-VirtualPortGroup -VirtualSwitch "vSwitch1" -Name "VM Network"

# 配置端口组
Set-VirtualPortGroup -VirtualPortGroup "VM Network" -VlanId 100
```

### 分布式交换机

```powershell
# 创建分布式交换机
New-VDSwitch -Name "vDSwitch1" -Location (Get-Datacenter -Name "Datacenter1")

# 添加主机到分布式交换机
Add-VDSwitchVMHost -VDSwitch "vDSwitch1" -VMHost "esxi01.company.com"

# 创建分布式端口组
New-VDPortgroup -Name "Distributed-VM-Network" -VDSwitch "vDSwitch1"

# 配置分布式端口组
Set-VDPortgroup -VDPortgroup "Distributed-VM-Network" -VlanId 200
```

## 性能监控

### 性能统计

```powershell
# 获取实时性能统计
Get-Stat -Entity (Get-VMHost -Name "esxi01.company.com") -Stat cpu.usage.average -Realtime
Get-Stat -Entity (Get-VM -Name "TestVM") -Stat mem.usage.average -Realtime

# 获取历史性能统计
Get-Stat -Entity (Get-VMHost -Name "esxi01.company.com") -Stat cpu.usage.average -Start (Get-Date).AddHours(-24)

# 获取多个统计指标
Get-Stat -Entity (Get-VM -Name "TestVM") -Stat @("cpu.usage.average", "mem.usage.average", "disk.usage.average") -Realtime
```

### 性能分析

```powershell
# 性能分析脚本
function Get-VMPerformanceAnalysis {
    param([string]$VMName)
    
    $vm = Get-VM -Name $VMName
    $stats = Get-Stat -Entity $vm -Stat @("cpu.usage.average", "mem.usage.average", "disk.usage.average") -Realtime
    
    $analysis = @{
        VM = $VMName
        CPU = $stats | Where-Object {$_.MetricId -eq "cpu.usage.average"} | Select-Object -ExpandProperty Value
        Memory = $stats | Where-Object {$_.MetricId -eq "mem.usage.average"} | Select-Object -ExpandProperty Value
        Disk = $stats | Where-Object {$_.MetricId -eq "disk.usage.average"} | Select-Object -ExpandProperty Value
        Timestamp = Get-Date
    }
    
    return $analysis
}
```

## 事件和任务管理

### 事件管理

```powershell
# 获取事件
Get-VIEvent -Start (Get-Date).AddDays(-1)

# 获取特定类型的事件
Get-VIEvent -Start (Get-Date).AddDays(-1) | Where-Object {$_.GetType().Name -eq "VmPoweredOnEvent"}

# 获取虚拟机事件
Get-VIEvent -Entity (Get-VM -Name "TestVM") -Start (Get-Date).AddDays(-7)
```

### 任务管理

```powershell
# 获取任务
Get-Task -Start (Get-Date).AddDays(-1)

# 获取正在运行的任务
Get-Task | Where-Object {$_.State -eq "Running"}

# 等待任务完成
$task = Start-VM -VM "TestVM" -RunAsync
Wait-Task -Task $task
```

## 高级功能

### 批量操作

```powershell
# 批量启动虚拟机
Get-VM | Where-Object {$_.PowerState -eq "PoweredOff"} | Start-VM

# 批量配置虚拟机
Get-VM | Where-Object {$_.Name -like "Test*"} | Set-VM -NumCpu 2 -MemoryGB 4

# 批量创建快照
Get-VM | Where-Object {$_.PowerState -eq "PoweredOn"} | New-Snapshot -Name "Batch Snapshot"
```

### 自动化脚本

```powershell
# 自动化部署脚本
function Deploy-VMFromTemplate {
    param(
        [string]$VMName,
        [string]$TemplateName,
        [string]$DatastoreName,
        [string]$ClusterName
    )
    
    $template = Get-Template -Name $TemplateName
    $datastore = Get-Datastore -Name $DatastoreName
    $cluster = Get-Cluster -Name $ClusterName
    
    $vm = New-VM -Name $VMName -Template $template -Datastore $datastore -Location $cluster
    Start-VM -VM $vm
    
    return $vm
}

# 使用示例
$vm = Deploy-VMFromTemplate -VMName "NewVM" -TemplateName "Windows2019Template" -DatastoreName "Datastore1" -ClusterName "Production"
```

### 错误处理

```powershell
# 错误处理示例
function Safe-VMOperation {
    param(
        [string]$VMName,
        [scriptblock]$Operation
    )
    
    try {
        $vm = Get-VM -Name $VMName
        if ($vm) {
            & $Operation
            Write-Host "操作成功完成" -ForegroundColor Green
        }
        else {
            throw "虚拟机 $VMName 不存在"
        }
    }
    catch {
        Write-Error "操作失败: $($_.Exception.Message)"
        throw
    }
}

# 使用示例
Safe-VMOperation -VMName "TestVM" -Operation { Start-VM -VM "TestVM" }
```

## 最佳实践

### 性能优化

1. **批量操作**: 使用管道和批量操作减少API调用
2. **异步操作**: 使用-RunAsync参数进行异步操作
3. **缓存对象**: 缓存常用对象避免重复查询
4. **限制结果**: 使用Where-Object过滤结果

### 错误处理1

1. **Try-Catch**: 使用try-catch处理异常
2. **参数验证**: 验证输入参数的有效性
3. **日志记录**: 记录操作日志便于故障排除
4. **回滚机制**: 实现操作回滚机制

### 安全考虑

1. **凭据管理**: 安全存储和管理凭据
2. **权限控制**: 使用最小权限原则
3. **审计日志**: 记录所有操作日志
4. **网络安全**: 使用加密连接

---

*本指南提供了PowerCLI的全面使用方法和最佳实践，可根据实际需求进行扩展和定制。*
