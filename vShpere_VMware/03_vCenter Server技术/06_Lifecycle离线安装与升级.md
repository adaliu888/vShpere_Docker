# vCenter Lifecycle Manager 离线安装与升级（最小可用）

## 1. 目标

- 在无外网或受限网络下完成 vCenter/ESXi 的镜像与补丁管理、升级与证据归档

## 2. 前置条件

- 离线介质：官方 Depot/ISO 与校验哈希；内部制品库/NFS/HTTP 服务
- 维护窗口与回滚点（备份/快照）；统一 NTP/证书

## 3. 离线镜像准备

- 下载 vLCM Depot（离线 bundle）并校验 SHA256
- 将 Depot 导入到 vLCM 或离线 Lifecycle 工具
- 若有自定义驱动/厂商 Addon，合并至自定义镜像配置文件

## 4. 基线与合规

- 创建安全补丁基线，附加至目标集群
- 生成合规报告并归档 CSV/JSON 与哈希

## 5. 升级流程（摘要）

1) 进入维护窗口，确认主机进入维护模式计划
2) 在测试群集先行验证镜像合规与兼容矩阵
3) 执行群集滚动升级（按一台/一批次策略），监控任务与日志
4) 验证版本/功能/性能基线，退出维护窗口

## 6. 证据与归档

```text
artifacts/
  YYYY-MM-DD/
    lcm-compliance.csv
    lcm-upgrade-plan.json
    lcm-execution.log
    manifest.json
    manifest.sha256
```

manifest 字段建议：cluster、imageProfile、baseline、precheck、tickets、hashes、rollback

## 7. 回滚策略

- 镜像验证失败：回退至上一个已验证镜像；恢复快照
- 部分主机失败：隔离失败主机，完成其余主机的维护后再处理

## 8. 参考与交叉链接

- `../09_安全与合规管理/Runbook_审计与变更操作.md`
- `../10_自动化与编排技术/05_工作流编排.md`
