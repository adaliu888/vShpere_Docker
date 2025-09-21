# 01 vSphere 基础架构

## 目录

- [01 vSphere 基础架构](#01-vsphere-基础架构)
  - [导航](#导航)
  - [学习路径（建议）](#学习路径建议)
  - [前置条件（最小可用）](#前置条件最小可用)
  - [快速Checklist](#快速checklist)
  - [可复现实例](#可复现实例)
- [连接 vCenter 并创建资源池与数据中心（示例）](#连接-vcenter-并创建资源池与数据中心示例)
  - [对标与参考](#对标与参考)



## 导航

- 01_vSphere架构概述.md
- 02_ESXi主机管理.md
- 03_vCenter Server管理.md
- 04_虚拟化基础概念.md
- 05_vSphere组件关系.md

## 学习路径（建议）

1) 概念与组件 → 2) ESXi 与 vCenter 基本操作 → 3) 组件关系与运行机制 → 4) 基础运维与常见问题

## 前置条件（最小可用）

- 1× vCenter + 1-2× ESXi（管理、vMotion、存储网络可用）
- DNS/NTP/证书配置完备；账户遵循最小权限（RBAC）
- 具备基础存储资源（本地或共享），便于创建测试 VM

## 快速Checklist

- 统一版本基线（ESXi/vCenter 兼容矩阵）
- 主机命名/IP/VLAN/时钟/NTP/证书规划
- vCenter RBAC 最小权限与审计开启
- 变更与备份策略纳入运行手册

## 可复现实例

```powershell
# 连接 vCenter 并创建资源池与数据中心（示例）
Connect-VIServer -Server vcenter.example.com
New-Datacenter -Name LabDC | Out-Null
New-Cluster -Name LabCluster -Location LabDC -DrsEnabled -HaEnabled | Out-Null
```

## 对标与参考

- 标准概览：`../../formal_container/02_技术标准与规范/01_国际标准概览.md`
- vSphere 架构深度：`../../formal_container/03_vSphere_VMware技术体系/01_vSphere架构深度解析.md`
- 能力与运行机制：`../../formal_container/07_执行流控制流数据流/01_系统运行机制深度分析.md`
