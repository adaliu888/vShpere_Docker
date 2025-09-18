# 容器技术知识体系

## 项目目标

- 建立覆盖 Docker / Podman / Kubernetes 的体系化知识库，贯穿原理—实现—实践—对标—选型。
- 提供工程化落地指南（安全、运维、监控、合规），服务企业级生产环境。
- 对齐 2025 年主流版本与标准，持续更新，形成可复用的组织级知识资产。

## 适用人群与前置

- 适用人群: 平台工程（Platform）、SRE、DevOps、应用研发、架构师、安全与合规人员。
- 前置要求: 基本 Linux 操作、网络/存储基础、Git 基础；进阶章节建议具备容器与编排实战经验。

## 目录结构

```text
Container/
├── README.md                    # 容器技术总览
├── 01_Docker技术详解/           # Docker技术深度解析
│   ├── 01_Docker架构原理.md
│   ├── 02_Docker容器管理.md
│   ├── 03_Docker镜像技术.md
│   ├── 04_Docker网络技术.md
│   ├── 05_Docker存储技术.md
│   └── 06_Docker安全机制.md
├── 02_Podman技术详解/           # Podman技术深度解析
│   ├── 01_Podman架构原理.md
│   ├── 02_Podman容器管理.md
│   ├── 03_Podman镜像技术.md
│   ├── 04_Podman网络技术.md
│   ├── 05_Podman存储技术.md
│   └── 06_Podman安全机制.md
├── 03_Kubernetes技术详解/       # Kubernetes技术深度解析
│   ├── 01_Kubernetes架构原理.md
│   ├── 02_Pod管理技术.md
│   ├── 03_服务发现与负载均衡.md
│   ├── 04_存储管理技术.md
│   ├── 05_网络策略与安全.md
│   └── 06_监控与日志管理.md
├── 04_容器编排技术/             # 容器编排技术详解
│   ├── 01_Docker_Swarm技术.md
│   ├── 02_Kubernetes编排.md
│   ├── 03_OpenShift技术.md
│   └── 04_容器编排对比分析.md
├── 05_容器安全技术/             # 容器安全技术详解
│   ├── 01_容器安全威胁分析.md
│   ├── 02_容器安全防护技术.md
│   ├── 03_容器镜像安全.md
│   ├── 04_容器运行时安全.md
│   └── 05_容器网络安全.md
├── 06_容器监控与运维/           # 容器监控运维技术
│   ├── 01_容器监控技术.md
│   ├── 02_容器日志管理.md
│   ├── 03_容器性能调优.md
│   ├── 04_容器故障诊断.md
│   └── 05_容器自动化运维.md
├── 07_容器技术标准/             # 容器技术标准规范
│   ├── 01_OCI标准详解.md
│   ├── 02_CNCF标准详解.md
│   ├── 03_容器技术标准对比.md
│   └── 04_容器技术规范实施.md
├── 08_容器技术实践案例/         # 容器技术实践案例
│   ├── 01_企业级容器化实践.md
│   ├── 02_微服务容器化案例.md
│   ├── 03_DevOps容器化实践.md
│   └── 04_容器技术最佳实践.md
└── 09_容器技术发展趋势/         # 容器技术发展趋势
    ├── 01_2025年容器技术趋势.md
    ├── 02_新兴容器技术分析.md
    ├── 03_容器技术投资建议.md
    └── 04_容器技术未来展望.md
```

## 技术覆盖范围

### 核心技术

- **Docker**: 容器化技术的开创者和标准制定者
- **Podman**: 无守护进程的容器管理工具
- **Kubernetes**: 容器编排和管理的行业标准
- **OpenShift**: 企业级Kubernetes平台

### 技术领域

- **容器技术**: 容器化、镜像管理、运行时技术
- **编排技术**: 容器编排、服务发现、负载均衡
- **安全技术**: 容器安全、镜像安全、运行时安全
- **监控运维**: 容器监控、日志管理、性能调优
- **标准规范**: OCI标准、CNCF标准、技术规范

### 应用场景

- **企业级应用**: 大型企业容器化改造
- **微服务架构**: 微服务容器化部署
- **DevOps实践**: CI/CD容器化流水线
- **云原生应用**: 云原生应用开发部署

## 学习路径

### 初学者路径

1. 学习容器基础概念
2. 掌握Docker基本操作
3. 了解容器镜像技术
4. 学习容器网络和存储

### 进阶路径

1. 深入学习Docker高级特性
2. 掌握Podman技术
3. 学习Kubernetes基础
4. 了解容器编排技术

### 专家路径

1. 精通Kubernetes高级特性
2. 掌握容器安全技术
3. 学习容器监控运维
4. 研究容器技术发展趋势

## 技术特色

### 深度解析

- 从原理到实践的完整技术栈
- 基于最新技术标准和规范
- 结合企业级实践案例
- 提供技术选型指导

### 国际对标

- 对标国际知名大学课程
- 遵循国际技术标准
- 参考国际最佳实践
- 跟踪国际技术趋势

### 实用导向

- 提供完整的学习路径
- 包含丰富的实践案例
- 支持技术认证准备
- 提供职业发展指导

## 使用方式

- 按“学习路径”循序阅读；或按主题纵向检索（网络/存储/安全/编排/实践）。
- 与 `formal_container/` 体系文档交叉参考：标准与形式化论证、矩阵对比、项目总结等。
- 企业实践可直接复用“最佳实践”“基线清单”“Runbook”章节材料。

## 版本与兼容策略（对齐至 2025）

- 标准：遵循 OCI（Image/Runtime/Distribution）、CNCF 相关规范；引用最新草案时明确标注。
- 运行时与引擎：Docker Engine（含 BuildKit）、containerd、CRI-O、Podman、crun/runc、gVisor/Kata。
- 平台：Linux 为一等公民；Windows/macOS 通过 Desktop/虚拟化层说明差异与注意事项。
- 文档中涉及的命令、API、配置项，若存在版本差异，将在文末“版本差异说明”标注最小兼容版本与变更要点。

## 文档约定

- 术语对齐 OCI/CNCF 词汇；首次出现给出中英文对照与缩写，例如：容器运行时（Container Runtime, CR）。
- 命令行统一采用等宽字体与块级代码；涉及破坏性操作明确“风险提示”。
- 架构图使用 ASCII 或引用 SVG/PNG 资源；若为示意图将在标题处标记。
- 配置与策略示例均提供“最小可用样例 + 安全基线建议”。

## 贡献指南

1. 分支策略：feature/*、fix/*、docs/*，通过 PR 合并到 main。
2. 提交规范：遵循 Conventional Commits（如 docs(container): add version matrix 2025）。
3. 内容要求：
   - 声明数据来源与版本；给出参考链接或标准编号。
   - 图表需附原始数据或生成脚本（如适用）。
   - 涉及安全配置需标注适用范围与潜在影响。
4. 审校流程：至少一名 Reviewer 过审；新增章节需包含目录与小结。

## 维护计划

- 每季度对齐一次上游版本变更（Docker/Podman/Kubernetes/containerd/CRI-O）。
- 关键安全公告（CVE、高危变更）将滚动更新至相关章节的“安全基线”。

## 参考与对标

- OCI 规范与实现文档；CNCF Landscape/白皮书。
- Docker 官方文档、Moby 项目、BuildKit 文档。
- Podman/containers 项目文档、Red Hat 指南。
- Kubernetes 文档、SIG-Node 与 CRI 相关提案。

## Docker 与 Podman 速查对比与选型建议

| 维度 | Docker | Podman | 建议场景 |
|---|---|---|---|
| 架构 | 客户端 + 守护进程（dockerd + containerd） | 无守护进程，CLI 直连运行时 | 单机/开发：二者皆可；受限环境偏向 Podman |
| Rootless | 支持（较完善） | 一等公民，生态完备 | 多租户/合规要求高：优先 Podman |
| 网络 | 默认 bridge，生态成熟 | netavark/slirp4netns，IPv6 友好 | 复杂网络与 IPv6：Podman 更优 |
| 构建 | BuildKit/buildx 多架构成熟 | buildah 集成，rootless 体验佳 | CI rootless：Podman+buildah |
| 生态 | 插件、Compose、Desktop 丰富 | 与 Docker CLI 兼容，工具链轻量 | 桌面与培训：Docker Desktop |
| 编排 | Swarm（存量） | play kube（开发/测试） | 生产编排：K8s + containerd/CRI-O |

选型要点：

- 开发与教学：Docker（Desktop/Compose）；需 rootless 或极简依赖：Podman。
- 生产编排：优先 Kubernetes + containerd（或 CRI-O）；单机运维工具不强绑定引擎。
- 高安全隔离：结合沙箱运行时（Kata/gVisor）与策略加固。

## 进度追踪（2025Q3）

- 01_Docker技术详解/01_Docker架构原理.md：已补充 快速上手/命令速查/Rootless/故障/FAQ。
- 02_Podman技术详解/01_Podman架构原理.md：已补充 快速上手/命令速查/Rootless/故障/FAQ。
- 其余小节：规划中（见下）。

- 01_Docker技术详解/02~06：已创建骨架并填充关键小节（容器管理/镜像/网络/存储/安全）。
- 02_Podman技术详解/02：已创建并补充关键小节；03~06：已补充 实操/故障/FAQ 模块。
- 03_Kubernetes技术详解/01~06：已创建骨架并补充 实操/故障/FAQ 小节（架构/Pod 管理/服务发现/存储/网络策略/监控日志）。
- 03_Kubernetes技术详解/01：新增 升级与回滚流程（SOP）。
- 03_Kubernetes技术详解/06：新增 告警/事件映射表 与 Alert 规则模板。
- 08_容器技术实践案例/01：已创建案例骨架。
- 06_容器监控与运维/04：新增“事件-原因-处置速查表”。
- 案例文档新增“样例数据与度量模板”。

## 待补充清单（优先级从高到低）

1. 01_Docker技术详解/
   - 02_Docker容器管理.md（生命周期、健康检查、Compose V2）
   - 03_Docker镜像技术.md（多阶段/缓存/签名/供应链）
   - 04_Docker网络技术.md（bridge/overlay/macvlan、IPv6、CNI 对接）
   - 05_Docker存储技术.md（overlay2/zfs、Volume/Bind、性能与一致性）
   - 06_Docker安全机制.md（capabilities/seccomp/SELinux、rootless hardening）
2. 02_Podman技术详解/
   - 02_Podman容器管理.md（Pod/容器编组、systemd 集成）
   - 03_Podman镜像技术.md（buildah/skopeo、manifest、多架构）
   - 04_Podman网络技术.md（netavark/aardvark-dns、slirp4netns/pasta）
   - 05_Podman存储技术.md（containers/storage 驱动与策略）
   - 06_Podman安全机制.md（rootless 策略、策略引擎）
3. 03_Kubernetes技术详解/
   - 01_Kubernetes架构原理.md（控制面/节点/CRI/CNI/CSI）
   - 02_Pod管理技术.md（Probes、资源配额、Pod 安全）
   - 03_服务发现与负载均衡.md（Service/Ingress/Gateway API）
   - 04_存储管理技术.md（PV/PVC/StorageClass、快照/备份）
   - 05_网络策略与安全.md（NetworkPolicy、CNI 对比）
   - 06_监控与日志管理.md（Metrics/Tracing/Logging）

## 术语表与引用规范（新增）

- 术语：首次出现给出中英文/缩写，如 容器运行时（Container Runtime, CR）。
- 引用：标准使用编号（OCI/CNCF 草案号），外链使用 Markdown 链接并注明日期/版本。
- 代码：命令使用等宽块；破坏性操作标注“风险提示”。

说明：创建新文件前，先在此列表登记，提交信息遵循 docs(container): 前缀。
