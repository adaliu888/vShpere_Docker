# 02 ESXi 技术详解

## 目录

- [02 ESXi 技术详解](#02-esxi-技术详解)
  - [导航](#导航)
  - [学习路径（建议）](#学习路径建议)
  - [前置条件（最小可用）](#前置条件最小可用)
  - [快速Checklist](#快速checklist)
  - [可复现实例](#可复现实例)
- [安装后基础配置（ESXi Shell 示例，按需开启维护窗口）](#安装后基础配置esxi-shell-示例按需开启维护窗口)
- [PowerCLI：批量收集主机版本与补丁基线](#powercli批量收集主机版本与补丁基线)
  - [对标与参考](#对标与参考)



## 导航

- 01_ESXi架构原理.md
- 02_ESXi安装配置.md
- 03_ESXi性能优化.md
- 04_ESXi安全管理.md
- 05_ESXi故障诊断.md

## 学习路径（建议）

1) 架构与原理 → 2) 标准化安装与配置 → 3) 性能（NUMA/调度/存储/网络） → 4) 安全基线 → 5) 故障诊断流程

## 前置条件（最小可用）

- 受支持的服务器或实验机，启用 VT-x/AMD-V，关闭超频
- 一致的 BIOS/固件版本；已规划管理/vMotion/vSAN 网络
- vCenter 可用，具备最小必要权限账号；集中 Syslog 就绪

## 快速Checklist

- 锁定模式/SSH 与 Shell 管控、仅允必要防火墙端口
- Account Lockout/密码策略与日志远转（Syslog）
- VMkernel 适配（vMotion/vSAN/Management）与 NIC 绑核/多队列
- BIOS/固件一致性、超频关闭、节能策略固定

## 可复现实例

```shell
# 安装后基础配置（ESXi Shell 示例，按需开启维护窗口）
esxcli system ntp set -s pool.ntp.org
esxcli system ntp set -e true
esxcli network firewall ruleset set -e true -r syslog
esxcli system syslog config set --loghost='udp://log.example.com:514'
esxcli system syslog reload
```

```powershell
# PowerCLI：批量收集主机版本与补丁基线
Connect-VIServer -Server vcenter.example.com
Get-VMHost | Select Name, Version, Build | Export-Csv esxi_hosts.csv -NoTypeInformation
```

## 对标与参考

- ESXi 管理与优化：`../../formal_container/03_vSphere_VMware技术体系/02_ESXi管理与优化.md`
- CIS Benchmarks（参考）：`../../formal_container/02_技术标准与规范/02_容器技术标准详解.md`
