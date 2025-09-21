## 目录

- [04 API 集成开发（vCenter REST/SDK）](#04-api-集成开发vcenter-restsdk)
  - [扩展目标（vSphere Automation）](#扩展目标vsphere-automation)
  - [前置条件](#前置条件)
  - [认证与会话](#认证与会话)
    - [cURL（示例）](#curl示例)
- [用户名/密码认证（实验环境示例）](#用户名密码认证实验环境示例)
    - [PowerShell（Invoke-RestMethod）](#powershellinvoke-restmethod)
  - [典型查询](#典型查询)
- [主机列表](#主机列表)
- [虚拟机简表](#虚拟机简表)
  - [证据归档（最小闭环）](#证据归档最小闭环)
- [导出 VM 列表](#导出-vm-列表)
- [生成 manifest](#生成-manifest)
  - [常见问题](#常见问题)
  - [参考](#参考)
  - [vSphere REST/SDK（扩展示例）](#vsphere-restsdk扩展示例)
  - [目标](#目标)
  - [认证（示例）](#认证示例)
- [获取 Session（示意）](#获取-session示意)
  - [查询事件（最近7天）](#查询事件最近7天)
  - [查询主机与虚拟机（REST 示例）](#查询主机与虚拟机rest-示例)
- [主机](#主机)
- [虚拟机](#虚拟机)
  - [工件合并与归档](#工件合并与归档)
  - [最佳实践](#最佳实践)
  - [延伸阅读](#延伸阅读)

- [04 API 集成开发（vCenter REST/SDK）](#04-api-集成开发vcenter-restsdk)
  - [扩展目标（vSphere Automation）](#扩展目标vsphere-automation)
  - [前置条件](#前置条件)
  - [认证与会话](#认证与会话)
    - [cURL（示例）](#curl示例)
- [用户名/密码认证（实验环境示例）](#用户名密码认证实验环境示例)
    - [PowerShell（Invoke-RestMethod）](#powershellinvoke-restmethod)
  - [典型查询](#典型查询)
- [主机列表](#主机列表)
- [虚拟机简表](#虚拟机简表)
  - [证据归档（最小闭环）](#证据归档最小闭环)
- [导出 VM 列表](#导出-vm-列表)
- [生成 manifest](#生成-manifest)
  - [常见问题](#常见问题)
  - [参考](#参考)
  - [vSphere REST/SDK（扩展示例）](#vsphere-restsdk扩展示例)
  - [目标](#目标)
  - [认证（示例）](#认证示例)
- [获取 Session（示意）](#获取-session示意)
  - [查询事件（最近7天）](#查询事件最近7天)
  - [查询主机与虚拟机（REST 示例）](#查询主机与虚拟机rest-示例)
- [主机](#主机)
- [虚拟机](#虚拟机)
  - [工件合并与归档](#工件合并与归档)
  - [最佳实践](#最佳实践)
  - [延伸阅读](#延伸阅读)


# 04 API 集成开发（vCenter REST/SDK）

## 扩展目标（vSphere Automation）

- 提供 vCenter REST API 的最小可复现实例（认证、查询、导出）
- 给出 PowerShell/PowerCLI 与 cURL 两种方式，便于在不同环境执行

## 前置条件

- vCenter 7+ 或 8+，API 已启用
- 具备最小必要权限的账号或 API Token

## 认证与会话

### cURL（示例）

```bash
# 用户名/密码认证（实验环境示例）
curl -k -X POST \
  -H "Content-Type: application/json" \
  -d '{"user_name":"administrator@vsphere.local","password":"<pass>"}' \
  https://vcenter.example.com/api/session
```

返回的 `vmware-api-session-id` 用于后续请求：

```bash
curl -k -H "vmware-api-session-id: <session-id>" \
  https://vcenter.example.com/api/vcenter/datacenter
```

### PowerShell（Invoke-RestMethod）

```powershell
$base = 'https://vcenter.example.com'
$body = @{ user_name='administrator@vsphere.local'; password='<pass>' } | ConvertTo-Json
$sid = Invoke-RestMethod -Method Post -Uri "$base/api/session" -Body $body -ContentType 'application/json' -SkipCertificateCheck

$headers = @{ 'vmware-api-session-id' = $sid }
$dcs = Invoke-RestMethod -Method Get -Uri "$base/api/vcenter/datacenter" -Headers $headers -SkipCertificateCheck
$dcs | ConvertTo-Json -Depth 5 | Out-File datacenters.json -Encoding utf8
```

> 生产环境请使用受信任证书并避免明文密码，可结合企业密码库或 OIDC。

## 典型查询

```bash
# 主机列表
curl -k -H "vmware-api-session-id: <sid>" \
  https://vcenter.example.com/api/vcenter/host

# 虚拟机简表
curl -k -H "vmware-api-session-id: <sid>" \
  https://vcenter.example.com/api/vcenter/vm
```

## 证据归档（最小闭环）

```powershell
$date = Get-Date -Format 'yyyy-MM-dd'
New-Item -ItemType Directory -Force -Path "artifacts/$date" | Out-Null

# 导出 VM 列表
$vms = Invoke-RestMethod -Method Get -Uri "$base/api/vcenter/vm" -Headers $headers -SkipCertificateCheck
$vms | ConvertTo-Json -Depth 6 | Set-Content "artifacts/$date/vms.json"
Get-FileHash "artifacts/$date/vms.json" | Select Hash | Set-Content "artifacts/$date/vms.json.sha256"

# 生成 manifest
$manifest = [pscustomobject]@{
  generatedAt   = (Get-Date).ToString('s')
  source        = 'vCenter REST'
  retentionDays = 180
  artifacts     = @(
    @{ name='vms.json'; sha256=(Get-Content "artifacts/$date/vms.json.sha256").Trim() }
  )
} | ConvertTo-Json -Depth 5
$manifest | Set-Content "artifacts/$date/manifest.json"
```

## 常见问题

- 401/403：会话无效或权限不足，检查 Token/角色
- TLS 错误：请安装受信任证书或在实验环境启用跳过校验

## 参考

- VMware vCenter REST API 文档（对应产品版本）
- `01_自动化基础.md`、`02_PowerCLI技术.md`

## vSphere REST/SDK（扩展示例）

## 目标

- 提供 vSphere REST API 的认证与查询示例
- 与 PowerCLI 输出合并，形成统一证据工件

## 认证（示例）

> 实际部署请使用安全存储管理 Token/凭据；以下示例为演示用。

```bash
# 获取 Session（示意）
curl -k -X POST https://vcenter.example.com/api/session
```

PowerShell 调用：

```powershell
$vc = 'https://vcenter.example.com'
$token = '<BearerToken>'
$headers = @{ Authorization = "Bearer $token" }
```

## 查询事件（最近7天）

```powershell
$since = (Get-Date).AddDays(-7).ToString('o')
$uri = "$vc/api/vcenter/evtmgr/events?start_time=$([uri]::EscapeDataString($since))"
$resp = Invoke-RestMethod -Method GET -Uri $uri -Headers $headers -SkipCertificateCheck
$resp | ConvertTo-Json -Depth 5 | Set-Content vc_events.json
Get-FileHash -Algorithm SHA256 vc_events.json | Select Hash | Set-Content vc_events.json.sha256
```

## 查询主机与虚拟机（REST 示例）

```powershell
# 主机
$hosts = Invoke-RestMethod -Method GET -Uri "$vc/api/vcenter/host" -Headers $headers -SkipCertificateCheck
$hosts | ConvertTo-Json -Depth 5 | Set-Content hosts_rest.json

# 虚拟机
$vms = Invoke-RestMethod -Method GET -Uri "$vc/api/vcenter/vm" -Headers $headers -SkipCertificateCheck
$vms | ConvertTo-Json -Depth 5 | Set-Content vms_rest.json
```

## 工件合并与归档

```powershell
$date = Get-Date -Format 'yyyy-MM-dd'
New-Item -ItemType Directory -Force -Path "artifacts/$date" | Out-Null
foreach ($f in 'vc_events.json','hosts_rest.json','vms_rest.json') {
  if (Test-Path $f) {
    Get-FileHash -Algorithm SHA256 $f | Select Hash | Set-Content "$f.sha256"
    Move-Item $f "artifacts/$date/"
    Move-Item "$f.sha256" "artifacts/$date/"
  }
}
```

## 最佳实践

- Token 轮换与最小权限（只读/运维分权）
- 请求分页与过滤，避免超大响应
- 与 PowerCLI 结果对齐字段，便于审计与比对

## 延伸阅读

- VMware vSphere Automation API 文档（按版本）
- `../09_安全与合规管理/Runbook_审计与变更操作.md`
