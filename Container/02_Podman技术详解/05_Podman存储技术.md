# Podman存储技术

## 目录

- [Podman存储技术](#podman存储技术)
  - [目录](#目录)
  - [1. containers/storage 驱动](#1-containersstorage-驱动)
  - [2. 数据卷与绑定挂载](#2-数据卷与绑定挂载)
  - [3. 性能与一致性](#3-性能与一致性)
  - [4. 备份与迁移](#4-备份与迁移)
  - [5. 故障与恢复](#5-故障与恢复)
  - [6. 实操示例](#6-实操示例)
  - [7. 故障清单与排查](#7-故障清单与排查)
  - [8. FAQ](#8-faq)
  - [9. 基线模板（建议）](#9-基线模板建议)

## 1. containers/storage 驱动

- overlay/btrfs/zfs/vfs 特性与适配

## 2. 数据卷与绑定挂载

- `podman volume` 与挂载标签（`:z/:Z`）

## 3. 性能与一致性

- 文件系统语义、IO 限制与 cgroups 交互

## 4. 备份与迁移

- 卷备份、镜像复制、离线分发

## 5. 故障与恢复

- 权限与标签问题、层损坏与恢复

（待补充：推荐配置与基准方法）

## 6. 实操示例

```bash
# 创建并使用数据卷
podman volume create data
podman run --rm -v data:/data alpine:3.20 sh -lc 'dd if=/dev/zero of=/data/file bs=1M count=64 && ls -lh /data'
```

## 7. 故障清单与排查

- 权限拒绝：检查 SELinux 标签（:z/:Z）与用户映射；确认 rootless 路径权限。
- Overlay 报错：核对内核与驱动；避免跨文件系统绑定；查看 `dmesg`。
- 性能异常：评估宿主磁盘与文件系统；限制 IO 并监控指标。

## 8. FAQ

- rootless 卷在哪里？通常位于 `$XDG_RUNTIME_DIR` 或用户家目录的容器存储路径。

## 9. 基线模板（建议）

- 使用 containers/storage overlay 驱动；rootless 路径规划与配额；卷优先。
- 明确挂载标签与权限；采集磁盘/延迟指标，设置容量告警。
