# promote

## 目录

- [promote](#promote)
  - [目录](#目录)
  - [目标（Objectives）](#目标objectives)
  - [范围（Scope）](#范围scope)
  - [目录映射（Where to put what）](#目录映射where-to-put-what)
  - [方法（Methodology）](#方法methodology)
  - [推进路线（Roadmap）](#推进路线roadmap)
  - [产出格式（Deliverables）](#产出格式deliverables)
  - [质量门槛（Quality Gates）](#质量门槛quality-gates)
    - [验收标准（Definition of Done）](#验收标准definition-of-done)
  - [贡献规则（Contribution）](#贡献规则contribution)
  - [对标与引用（References \& Mapping）](#对标与引用references--mapping)
  - [发布与版本化（Release \& Versioning）](#发布与版本化release--versioning)

主题：虚拟化与容器化的原理、架构与应用

## 目标（Objectives）

- 建立覆盖 vSphere/VMware 与 Docker/Podman 的系统化知识库
- 以国际课程体系与权威标准为基准，形成可落地的实践指南
- 形成可对比、可评估的矩阵（功能/性能/安全/成本/运维）
- 提供学习路径与认证对接，支持从初学到专家的进阶

## 范围（Scope）

- 虚拟化：vSphere、ESXi、vCenter、vSAN、NSX、Tanzu/Aria 相关
- 容器化：Docker/Podman、镜像与运行时、编排与自动化、供应链安全
- 形式化与对标：标准、最佳实践、课程大纲、方法学与度量

## 目录映射（Where to put what）

- 形式化与对标：`./formal_container`
- vSphere/VMware 体系：`./vShpere_VMware`
- 容器与云原生：`./Container`

## 方法（Methodology）

1. 对标与抽象：以 ISO/NIST/CIS 与大学课程为“公共语言”抽象能力
2. 结构化产出：概念→架构→部署→运维→安全/合规→故障→最佳实践→Checklist
3. 可验证性：给出命令、脚本、配置示例与度量指标
4. 持续演进：滚动路线图与版本化发布

## 推进路线（Roadmap）

T0（当前迭代）

- vSphere 安全与合规：ISO/NIST/CIS 对标，补齐审计与基线清单（已完成最小可用：Checklist、Runbook、Templates）
- VMware 学习路径与认证映射：从管理员到架构师

T1（下一迭代）

- ESXi/NSX/vSAN 的性能与容量方法论与指标库
- 容器供应链安全（SBOM、签名、策略执行）

T2（后续迭代）

- 自动化与编排：PowerCLI、API、GitOps、Aria/Tanzu 集成（最小可用已覆盖 PowerCLI/REST/调度/证据归档）
- 企业案例与参考架构：按行业分场景沉淀

## 产出格式（Deliverables）

- 概览 README：每个主题目录必须含导航与学习路径（示例：`vShpere_VMware/README.md`）
- 清单与基线：Checklist、Runbook、Playbook、标准对照表（示例：`vShpere_VMware/09_安全与合规管理/Checklist_基线清单.md`、`vShpere_VMware/09_安全与合规管理/Runbook_审计与变更操作.md`、`vShpere_VMware/09_安全与合规管理/Templates_证据与对标映射.md`）
- 命令与脚本：PowerCLI/CLI/YAML 示例可直接运行（示例集中于 `vShpere_VMware/` 与 `formal_container/` 对标章节）
- 指标与度量：KPI/SLO、容量与性能基线（示例：性能/容量方法与指标库）

## 质量门槛（Quality Gates）

- 结构完整：章节齐全，不留“空壳”标题
- 可复现：命令/步骤在无外网假设下最小化依赖即可复现
- 可对标：每处引用明确版本与出处（标准号、年份、链接）
- 可维护：术语统一、导航清晰、链接可达
- 证据模板：合规模板（命名规范/映射表）与脚本示例可执行，并含校验哈希与保留期

### 验收标准（Definition of Done）

- 每个目录含 `README.md` 导航与学习路径
- 每个专题至少包含：概念/架构/部署/运维/安全合规/故障/最佳实践/Checklist 章节
- 至少一份 Checklist 与一份 Runbook，可直接按步骤执行并产出证据（本迭代已具备最小可用版本，含 Templates）
- 对标映射：需在“参考/对标”部分明确列出 ISO/NIST/CIS 的条款映射
- 命令与脚本：提供执行前置条件、适用版本与回滚说明

## 贡献规则（Contribution）

- 以最小可用文档提交；遵循各目录 README 的写作规范
- PR 必须附：变更范围、动机、参考资料与验证方式
- 审阅关注：准确性、完整性、可操作性与一致性

## 对标与引用（References & Mapping）

- 国际标准：`formal_container/02_技术标准与规范/01_国际标准概览.md`
- vSphere 体系：`vShpere_VMware/`（总览与各专题 README 导航）
- vSphere 安全与优化：`formal_container/03_vSphere_VMware技术体系/02_ESXi管理与优化.md`
- 容器标准与供应链：`formal_container/02_技术标准与规范/02_容器技术标准详解.md`
- 课程对标：`formal_container/12_国际对标分析/01_国际知名大学课程对标.md`

## 发布与版本化（Release & Versioning）

1. 语义化版本：主版本.次版本.修订（例如 0.2.1）
2. 每次发布包含：变更日志（Added/Changed/Fixed/Docs）、受影响目录列表、对标更新点
3. 文档校验：链接可达性、代码块渲染、术语检查、对标条款核对
4. 发布节奏：T0 每两周一次小版本；T1/T2 每月对齐路线图进行里程碑评审
