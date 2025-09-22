# vRealize Operations / Aria Operations 指标与KPI（最小可用）

## 目录

- [vRealize Operations / Aria Operations 指标与KPI（最小可用）](#vrealize-operations-aria-operations-指标与kpi最小可用)
  - [1. 目标](#1-目标)
  - [2. 指标分类（建议）](#2-指标分类建议)
  - [3. KPI/SLO（样例）](#3-kpislo样例)
  - [4. 仪表板与视图（建议）](#4-仪表板与视图建议)
  - [5. 基线建立与异常检测](#5-基线建立与异常检测)
  - [6. 报表与证据导出（示例）](#6-报表与证据导出示例)
  - [7. 告警策略（建议）](#7-告警策略建议)
  - [8. 容量与成本（可选）](#8-容量与成本可选)
  - [9. 交叉链接](#9-交叉链接)

## 1. 目标

- 给出 vROps/Aria Ops 的核心指标、仪表板与告警实践，形成可落地 KPI/SLO 基线
- 提供容量与性能方法论：采样窗口、基线建立、异常检测与证据归档

## 2. 指标分类（建议）

- 计算资源：CPU 使用率/Ready/Co-Stop、内存主动/消极消耗、Balloon/Swap
- 存储资源：Datastore IOPS/Latency、Congestion、vSAN DOM/LSOM 延迟
- 网络资源：吞吐、丢包、延迟、拥塞（NSX/TOR 指标交叉）
- 平台健康：vCenter API 延迟、任务失败率、事件频度、告警处置时延
- 业务视角：每工作负载成本（vCPU/GB/IOPS）、SLA 达标率、变更窗口失败率

## 3. KPI/SLO（样例）

- SLO：关键业务 VM CPU Ready 平均 < 3%（5 分钟窗口，P95）
- SLO：Datastore 平均读/写延迟 < 5/10 ms（P95）
- KPI：主机群集超分配比（vCPU:pCPU） ≤ 4:1（按业务等级细化）
- KPI：月度容量利用率（CPU/内存/IOPS）稳定在 60–80% 区间

## 4. 仪表板与视图（建议）

- 集群容量总览：CPU/内存头寸、突发缓冲、未来 90 天预测
- vSAN 性能热图：DOM/LSOM 分层延迟、重建窗口影响
- VM 拓扑链路：VM ↔ Datastore ↔ Host ↔ Network（快速定位瓶颈）
- 合规看板：基线偏离项数量、处置时延、未关闭告警分布

## 5. 基线建立与异常检测

- 采样窗口：建议 5 分钟粒度，滚动 30 天建立基线（排除维护窗口）
- 异常定义：超过基线 P95/P99 阈值且持续 ≥ N 个采样周期
- 证据：导出异常区间的时间序列与关联事件，归档到 `artifacts/`

## 6. 报表与证据导出（示例）

```text
artifacts/
  YYYY-MM-DD/
    vrops-capacity-summary.csv
    vrops-anomaly-<metric>-<vm>.csv
    vrops-dashboard-snapshot.png
    manifest.json
    manifest.sha256
```

manifest 建议字段：reportName、timeRange、entities、metrics、generatedBy、hashes

## 7. 告警策略（建议）

- 多信号触发：CPU Ready + Datastore 延迟同时异常时提高严重级别
- 抑制与去噪：维护窗口抑制；重复告警合并；长期噪声阈值自适应
- 升级链路：SLA 风险命中触发变更评审与扩容建议（对接工单）

## 8. 容量与成本（可选）

- 单位成本模型：vCPU、GB 内存、GB 存储、IOPS 的折算与展示
- 预测：基于季节性和趋势分解（如 Prophet/ETS），给出 30/90 天建议

## 9. 交叉链接

- `../10_自动化与编排技术/05_工作流编排.md`（证据与清单一致）
- `../09_安全与合规管理/README.md`（合规看板指标口径）
