# vSphere 安全与合规管理（Security & Compliance）

## 目录

- [vSphere 安全与合规管理（Security \& Compliance）](#vsphere-安全与合规管理security--compliance)
  - [目录](#目录)
  - [目标与范围](#目标与范围)
  - [快速入口](#快速入口)
  - [学习路径（可执行）](#学习路径可执行)
  - [对标映射（References \& Mapping）](#对标映射references--mapping)
  - [产出物](#产出物)
  - [证据留存与完整性（新增）](#证据留存与完整性新增)
  - [可复现实例索引（新增）](#可复现实例索引新增)
  - [REST 报表示例入口（新增）](#rest-报表示例入口新增)
  - [变更与版本](#变更与版本)
  - [09 安全与合规管理](#09-安全与合规管理)
  - [导航](#导航)
  - [学习路径（建议）](#学习路径建议)
  - [快速Checklist](#快速checklist)
  - [状态与后续](#状态与后续)
  - [对标与参考](#对标与参考)

## 目标与范围

- 以 ISO/IEC 27001、NIST SP 800-53、CIS Benchmarks（vSphere/ESXi/NSX）为对标
- 输出可执行的基线 Checklist 与变更窗口 Runbook，形成可审计证据
- 覆盖身份与访问、配置与补丁、日志与审计、数据保护与灾备

## 快速入口

- 基线清单：`./Checklist_基线清单.md`
- 审计与运行手册（Runbook）：`./Runbook_审计与变更操作.md`
- 合规模板：`./Templates_证据与对标映射.md`（已提供模板与示例脚本）
- 深入解析：`./05_合规管理审计.md`
- 证据脚本入口：见合规模板内“证据生成脚本占位”PowerCLI 示例

## 学习路径（可执行）

1. 对标与范围认知：阅读 `formal_container/02_技术标准与规范/01_国际标准概览.md`
2. 配置最小基线：执行 `Checklist_基线清单.md` 的“最小可用”部分
3. 集中日志与证据：按 Runbook 完成 Syslog/事件/任务留存与导出
4. 合规评估：使用 PowerCLI 基线对照并出具合规状态报表

## 对标映射（References & Mapping）

- ISO/IEC 27001：A.8（资产）、A.12（运维安全/日志）、A.16（事件管理）
- NIST SP 800-53：AU（审计）、CM（配置）、SI（完整性/监测）
- CIS Benchmarks：vSphere/ESXi/NSX（服务、访问控制、日志）
- PCI DSS：Req.10（日志）、Req.11（测试）、Req.12（政策）

> 注：详细条款与控制项请参见 `formal_container` 相关章节。

## 产出物

- Checklist：可直接执行的检查与配置项，含命令与期望状态
- Runbook：变更窗口操作步骤、前置条件、回滚方案与证据存档位
- 模板：审计证据命名规范、导出字段定义、保留期与存档结构（新增：建议目录结构见 Runbook）

## 证据留存与完整性（新增）

- 命名与目录：遵循 `Templates_证据与对标映射.md` 的命名/目录规范
- 完整性：对 CSV/JSON 生成 SHA256 哈希并与 `manifest.json` 一并归档
- 保留策略：关键证据建议 WORM/不可变存储，保留 ≥ 90 天（按法规调整）
- 审批链路：证据需关联 TicketId（变更/事件），实现可追溯

## 可复现实例索引（新增）

- PowerCLI：NTP/Syslog/服务状态/基线合规检查 → 见 `Runbook_审计与变更操作.md`
- 报表导出：vCenter Events/Tasks → 见 `Runbook_审计与变更操作.md`（CSV 导出示例）
- 证据模板：命名、字段与 manifest 示例 → 见 `Templates_证据与对标映射.md`

## REST 报表示例入口（新增）

- vSphere REST（Automation API）：查询事件/任务/告警以生成合规报表
- 推荐在同一流水线中合并 PowerCLI 与 REST 输出，统一落盘与签名

## 变更与版本

- 本目录遵循仓库 `ai.md` 发布与版本化规范
- 重要更新包含：控制项新增/调整、脚本更新、对标版本同步说明

---

## 09 安全与合规管理

## 导航

- 01_安全架构设计.md
- 02_身份认证与访问控制.md
- 03_数据安全保护.md
- 04_网络安全防护.md
- 05_合规管理审计.md

## 学习路径（建议）

1) 威胁建模与安全域 → 2) 身份与访问控制 → 3) 数据保护与加密 → 4) 审计与日志 → 5) 合规映射

## 快速Checklist

- RBAC 与最小权限、双人复核关键操作
- 基础设施与租户隔离、凭据与密钥托管
- 审计日志集中与完整性校验（WORM/哈希）
- 合规控制矩阵：ISO 27001/NIST/CIS/PCI/GDPR 映射

## 状态与后续

- 已补充：`Checklist_基线清单.md` 的详细控制项与证据路径；`Runbook_审计与变更操作.md` 的归档结构与 FAQ；`Templates_证据与对标映射.md` 的命名规范、映射表与脚本示例
- 后续计划：新增更多控制项的证据脚本与 REST API 报表示例（如 vCenter Events 查询）

## 对标与参考

- 标准概览：`../../formal_container/02_技术标准与规范/01_国际标准概览.md`
- 审计与基线：`../../formal_container/02_技术标准与规范/02_容器技术标准详解.md`
