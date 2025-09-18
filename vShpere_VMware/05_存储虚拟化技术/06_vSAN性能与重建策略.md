# vSAN 性能与重建策略（最小可用）

## 1. 目标

- 建立 vSAN 性能基线与重建窗口策略，覆盖 DOM/LSOM 指标、故障域与证据归档

## 2. 指标分层（核心）

- DOM（分布式对象管理）：Read/Write Latency、Congestion、Resync I/O
- LSOM（本地存储）：Device Latency、Outstanding I/O、Cache 命中率
- 客户视角：VM I/O 延迟、吞吐、抖动（P95/P99）

## 3. 基线与阈值（建议）

- 正常运行：DOM/LSOM P95 延迟 < 5/8 ms（读/写），拥塞低于阈值
- 异常判定：超过基线且持续 ≥ N 个采样周期，并伴随 Resync 放大

## 4. 重建策略（窗口与限速）

- 窗口：业务低峰执行重建/重平衡；避免与大规模迁移/备份重叠
- 限速：按集群与磁盘组设置 Resync 限速，保障前台延迟优先
- 故障域：机架/主机级故障域设计，减少跨域重建带来的 IO 放大

## 5. 维护与容量

- 预留容量：建议 25–30% 供重建与突发；监控有效可用空间与组件数量
- 驱动与固件：遵循 HCL；版本升级纳入 Lifecycle 与回滚计划

## 6. 证据与导出（示例）

```text
artifacts/
  YYYY-MM-DD/
    vsan-dom-latency.csv
    vsan-lsom-latency.csv
    vsan-resync-io.csv
    manifest.json
    manifest.sha256
```

manifest 字段：cluster、faultDomains、timeRange、metrics、hashes、tickets

### 6.1 vSAN 重建监控与导出（示例）

```powershell
# 通过 PowerCLI 调用 vSAN API（需相应模块与权限）
$cluster = Get-Cluster -Name "Prod-Cluster"
$vsanView = Get-View -Id $cluster.ExtensionData.MoRef
# 示例：获取 vSAN 性能计数器（具体对象与路径按环境调整）
# 也可配合 RVC/vSAN Observer 导出

# 伪示例：导出 Resync I/O 与延迟（替换为实际查询）
"timestamp,metric,value" | Set-Content vsan-resync-io.csv
Get-Date -Format o | ForEach-Object { "$_,resync_iops,123" } | Add-Content vsan-resync-io.csv

# 生成清单与哈希
$date = Get-Date -Format 'yyyy-MM-dd'
New-Item -ItemType Directory -Force -Path "artifacts/$date" | Out-Null
Get-FileHash -Algorithm SHA256 vsan-resync-io.csv | Select Hash | Set-Content "artifacts/$date/vsan-resync-io.csv.sha256"
@{
  cluster = $cluster.Name
  timeRange = @{ start = (Get-Date).AddHours(-1).ToString('o'); end = (Get-Date).ToString('o') }
  artifacts = @('vsan-resync-io.csv')
} | ConvertTo-Json -Depth 5 | Set-Content "artifacts/$date/manifest.json"
(Get-FileHash -Algorithm SHA256 "artifacts/$date/manifest.json").Hash | Set-Content "artifacts/$date/manifest.sha256"
```

### 6.2 vSAN Observer 导出（可选）

```bash
# 在 RVC/vSAN Observer 主机上（示意，按版本调整命令）
vsan-observer --run-webserver --force --cluster Prod-Cluster --duration 3600 --generate-json /var/tmp/vsan-observer
tar -czf vsan-observer-$(date +%F).tar.gz /var/tmp/vsan-observer
sha256sum vsan-observer-*.tar.gz > vsan-observer-*.tar.gz.sha256
```

### 6.3 RVC 与 vSAN Performance API（示例）

```bash
# RVC 执行（示意，按环境替换登录与路径）
rvc administrator@vsphere.local@vcenter.example.com
> cd /vcenter.example.com/datacenter/computers/Prod-Cluster
> vsan.perf.stats_dump . --metrics resync_iops,dom_latency --start "1h"
> vsan.resync_dashboard . > vsan-resync-dashboard.txt
```

```powershell
# vSAN Performance API（伪示例，需对应 SDK）
$svc = Get-View ServiceInstance
$perfMgr = Get-View $svc.Content.PerfManager
# TODO: 构造 vSAN 特定的查询（按 SDK 指南），导出为 CSV
"timestamp,metric,value" | Set-Content vsan-dom-latency.csv
```

## 7. 故障与排障（摘要）

- 重建长时间占用：核对限速与热点磁盘；检查网络与拥塞点
- 延迟突增：定位 DOM/LSOM 哪一层异常；关联事件（重建、回收、策略变更）

## 8. 交叉链接

- `../08_性能监控与优化/02_vRealize Operations.md`
- `../03_vCenter Server技术/06_Lifecycle离线安装与升级.md`

## 9. 前置条件与版本兼容（新增）

- vSphere/vSAN 版本：按长期支持版本，参考兼容矩阵（vCenter × ESXi × vSAN）
- 硬件兼容性：HCL 合规（控制器/固件/驱动）；网络与 MTU 一致
- 依赖服务：NTP/证书/Syslog；vSAN Performance Service 已启用

## 10. 常见陷阱与案例（新增）

- 空间紧张导致重建反复失败：预留不足 < 25%，优先扩容或释放
- 限速过低导致重建拖期：业务低峰适当提升 Resync 限速，并观察前台延迟
- 维护窗口重叠：与备份/大规模迁移同时执行引发抖动，需避开
