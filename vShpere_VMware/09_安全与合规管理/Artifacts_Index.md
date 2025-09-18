# Artifacts 顶层索引模板（证据目录）

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
