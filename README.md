# vShpere_Docker

## 目录

- [vShpere\_Docker](#vshpere_docker)
  - [目录](#目录)
  - [仓库结构](#仓库结构)
  - [快速开始](#快速开始)
    - [重点入口（新增）](#重点入口新增)
    - [本轮新增（Highlights）](#本轮新增highlights)
  - [内容规范](#内容规范)
  - [对标与参考](#对标与参考)
  - [贡献指南](#贡献指南)
    - [版本化与发布流程](#版本化与发布流程)
  - [路线图（Rolling）](#路线图rolling)
  - [当前状态（T0）](#当前状态t0)
  - [许可证](#许可证)

vSphere / VMware / Docker / Podman 全面技术体系库

本仓库旨在系统化梳理虚拟化与容器化的原理、架构与实践，覆盖 vSphere、ESXi、vCenter、NSX、vSAN 以及 Docker、Podman 等核心技术，参考国际知名大学课程、权威标准与企业最佳实践，持续更新。

## 仓库结构

```text
./
├─ ai.md                     # 项目目标与推进指南
├─ README.md                 # 根导航（本文件）
├─ Container/                # 容器化（Docker / Podman 等）
├─ vShpere_VMware/           # VMware vSphere 技术体系
└─ formal_container/         # 形式化分析与对标（标准/课程/最佳实践）
```

## 快速开始

- 阅读 `ai.md` 了解目标、范围与推进节奏
- 进入 `vShpere_VMware/` 与 `Container/` 分别获取虚拟化与容器化主题内容
- 若用于学习：从各目录 `README.md` 的学习路径开始
- 若用于落地：优先参考 各专题「最佳实践」「Checklist」「落地指南」章节

### 重点入口（新增）

- vSphere 安全与合规：`vShpere_VMware/09_安全与合规管理/README.md`
- 安全基线 Checklist：`vShpere_VMware/09_安全与合规管理/Checklist_基线清单.md`
- 审计 Runbook：`vShpere_VMware/09_安全与合规管理/Runbook_审计与变更操作.md`
- 自动化与编排：`vShpere_VMware/10_自动化与编排技术/README.md`
  - PowerCLI 最小可复现：`vShpere_VMware/10_自动化与编排技术/02_PowerCLI技术.md`
  - REST 集成与证据：`vShpere_VMware/10_自动化与编排技术/04_API集成开发.md`
  - 调度与编排：`vShpere_VMware/10_自动化与编排技术/05_工作流编排.md`
  - vRA/Aria 占位：`vShpere_VMware/10_自动化与编排技术/03_vRealize Automation.md`

### 本轮新增（Highlights）

- vROps/Aria Ops 指标与 KPI：`vShpere_VMware/08_性能监控与优化/02_vRealize Operations.md`
- NSX 微隔离最佳实践：`vShpere_VMware/06_网络虚拟化技术/04_网络安全管理.md`
- vCenter 离线 Lifecycle 指南：`vShpere_VMware/03_vCenter Server技术/06_Lifecycle离线安装与升级.md`
- vSAN 性能与重建策略：`vShpere_VMware/05_存储虚拟化技术/06_vSAN性能与重建策略.md`
- Tanzu 容器桥接与证据一致性：`vShpere_VMware/11_云原生与混合云/06_Tanzu容器桥接与证据一致性.md`
- ESXi 硬化脚本集合：`vShpere_VMware/02_ESXi技术详解/06_ESXi硬化脚本集合.md`
- 证据目录索引模板：`vShpere_VMware/09_安全与合规管理/Artifacts_Index.md`

## 内容规范

- 统一使用中文；必要处提供英文术语（首次出现时给出中英对照）
- 章节结构建议：概念→架构→部署→运维→安全/合规→故障处理→最佳实践→Checklist
- 引用标准与外链需注明来源（标准号、版本、年份）
- 命令/代码段使用 fenced code block，避免混用制表符与空格

### 版本锚点与引用规范（新增）

- 统一从《2025年技术标准最终对齐报告.md》检索版本与标准号，避免文档间漂移：
  - 虚拟化：vSphere/ESXi/vCenter/NSX 等版本以该文档为准
  - 容器：Docker/Kubernetes/OCI 等版本以该文档为准
  - WASM/WASI：以该文档为准
- 在各文档首次出现版本信息时，添加指向该报告对应小节的锚链接。
- 如需更新版本，仅修改该报告，并在 PR 中说明“版本锚点更新”。

## 对标与参考

- 标准：ISO/IEC 27001、ISO/IEC 20000、NIST SP 800-53、CIS Benchmarks（VMware/OS/容器）、PCI DSS、GDPR 等
- 课程与教材：参考 MIT/Stanford/UCB 等系统课程结构（操作系统、分布式系统、网络与安全）
- 厂商与产品：VMware 官方文档、Best Practices、Security Configuration Guide；CNCF 生态项目文档

## 贡献指南

1. Fork 仓库并新建分支（命名示例：feature/topic-xxx 或 docs/area-yyy）
2. 编辑对应目录文档，保持原有排版与风格
3. PR 中注明变更范围、动机、参考资料与可验证性
4. 通过基本检查：
   - Markdown 语法与代码块渲染正常
   - 目录导航与链接可达
   - 术语统一、无敏感信息

### 版本化与发布流程

1. 分支策略：main 稳定分支；feature/docs 分支按专题开发
2. 版本规范：遵循 `ai.md` 的语义化版本，更新变更日志
3. 发布检查：链接可达性、对标条款映射、命令可复现、Checklist/Runbook 完整
4. PR 模板建议包含：变更范围、动机、参考文献、验证方式、受影响目录

## 路线图（Rolling）

- vSphere 安全与合规：对标 ISO/NIST/CIS，补充审计与基线清单
- ESXi/NSX/vSAN 性能与容量：方法论与指标体系
- 容器安全：镜像与运行时安全、供应链安全（SBOM/签名）
- 自动化与编排：PowerCLI、API、GitOps 与 Aria/Tanzu 对接

## 当前状态（T0）

- vSphere 安全与合规：已提供最小可用 Checklist 与 Runbook
- vSphere 自动化与编排：已提供最小可复现实例（PowerCLI/REST/调度/证据归档），vRA/Aria 入口已就绪
- 其余专题将按路线图逐步补齐（见各目录 README 的“前置条件/可复现”）

## 许可证

本项目采用开源许可证（见 `LICENSE`）。如需商用或二次分发，请遵循相应条款。
