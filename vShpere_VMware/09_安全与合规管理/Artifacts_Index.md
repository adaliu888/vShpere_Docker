# Artifacts 顶层索引模板（证据目录）

## 目录

- [Artifacts 顶层索引模板（证据目录）](#artifacts-顶层索引模板证据目录)
  - [目录](#目录)
  - [1. 目录结构（仓库级）](#1-目录结构仓库级)
  - [2. manifest 汇总（索引）](#2-manifest-汇总索引)
    - [2.1 生成脚本（PowerShell 示例）](#21-生成脚本powershell-示例)
  - [3. 命名规范](#3-命名规范)
  - [4. 留存与不可变](#4-留存与不可变)
  - [5. 交叉链接](#5-交叉链接)

## 1. 目录结构（仓库级）

```text
artifacts/
  YYYY-MM-DD/
    evidence.log
    manifest.json
    manifest.sha256
    reports/
    events/
    tasks/
    configs/
    vrops/
    nsx/
```

## 2. manifest 汇总（索引）

- 每日新增在 `artifacts/YYYY-MM-DD/manifest.json`
- 可选生成仓库级 `artifacts/index.json`，聚合最近 N 日清单（含 TicketId、hashes）

### 2.1 生成脚本（PowerShell 示例）

```powershell
$root = Join-Path (Get-Location) 'artifacts'
$items = @()
Get-ChildItem $root -Directory | ForEach-Object {
  $d = $_.FullName
  $mf = Join-Path $d 'manifest.json'
  if (Test-Path $mf) {
    try {
      $json = Get-Content $mf -Raw | ConvertFrom-Json
      $items += [PSCustomObject]@{
        date = Split-Path $d -Leaf
        ticketId = $json.ticketId
        hashes = $json.hashes
        artifacts = $json.artifacts
      }
    } catch {}
  }
}
$out = @{ generatedAt = (Get-Date).ToString('o'); items = $items }
$out | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $root 'index.json') -Encoding UTF8
```

## 3. 命名规范

- 参考 `Templates_证据与对标映射.md`，保持 controlId/standard/ticketId 一致

## 4. 留存与不可变

- 建议每日打包归档并推送到 WORM/不可变存储；保留期默认 180 天

## 5. 交叉链接

- `Checklist_基线清单.md`
- `Runbook_审计与变更操作.md`
- `Templates_证据与对标映射.md`

## 6. 容器/Kubernetes 合规证据模板（新增）

为统一虚拟化与容器/K8s 的证据留存与对标映射，建议在 `artifacts/` 下新增如下子目录与模板：

```text
artifacts/YYYY-MM-DD/
  k8s/
    admission/
      gatekeeper-violations.json         # OPA/Gatekeeper 违规快照
      kyverno-reports.json               # Kyverno 报告
    images/
      sbom/*.json                        # SBOM（如 Syft/CycloneDX）
      signatures/*.sig                   # 镜像签名（Cosign/Notary）
      attestations/*.jsonl               # 供应链声明（SLSA/Provenance）
    runtime/
      audit/audit-*.json                 # 审计日志（kube-apiserver）
      events/events-*.json               # 集群事件
      policies/*.yaml                    # NetworkPolicy/PSA/PSS/PodSecurity
    cluster/
      manifests/*.yaml                   # 基线清单（RBAC/Quota/PSP替代）
      cis/cis-benchmark-report.json      # CIS K8s 基线扫描报告
      conformance/k8s-conformance.txt    # 兼容性/一致性记录
```

推荐证据映射与来源：

- 容器供应链与镜像安全：`Container/05_容器安全技术/03_容器镜像安全.md`
- 运行时与网络策略：`Container/05_容器安全技术/04_容器运行时安全.md`、`Container/05_容器安全技术/05_容器网络安全.md`
- K8s 基线与策略：`Container/03_Kubernetes技术详解/05_网络策略与安全.md`
- 标准锚点：`2025年技术标准最终对齐报告.md`（Docker 25.0、Kubernetes 1.30、OCI 1.1、CIS 基线）

对标模板建议：

- `Templates_证据与对标映射.md` 增补以下 controlId：
  - IMG.SUPPLYCHAIN：SBOM/签名/声明 → 镜像仓库/CI 产物
  - K8S.POLICY：Pod 安全/NetworkPolicy/PSA → 集群策略与审计
  - K8S.AUDIT：apiserver 审计/事件留存 → 不可变存储（WORM）
  - K8S.CIS：CIS Benchmark 报告 → 基线核验与整改追踪
