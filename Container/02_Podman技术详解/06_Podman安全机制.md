# Podman安全机制

## 目录

- [Podman安全机制](#podman安全机制)
  - [目录](#目录)
  - [1. Rootless 与权限模型](#1-rootless-与权限模型)
  - [2. 策略与供应链安全](#2-策略与供应链安全)
  - [3. 运行时与网络安全](#3-运行时与网络安全)
  - [4. 沙箱运行时与隔离增强](#4-沙箱运行时与隔离增强)
  - [5. 安全基线与合规](#5-安全基线与合规)
  - [6. 故障与应急响应](#6-故障与应急响应)
  - [7. 实操清单](#7-实操清单)
  - [8. 故障清单与排查](#8-故障清单与排查)
  - [9. FAQ](#9-faq)
  - [10. 基线模板（建议）](#10-基线模板建议)

## 1. Rootless 与权限模型

- userns/subuid/subgid、capabilities、seccomp、SELinux/AppArmor

## 2. 策略与供应链安全

- policy.json、签名与验证、SBOM、漏洞扫描

## 3. 运行时与网络安全

- 只读根、最小权限、最小暴露端口、网络策略

## 4. 沙箱运行时与隔离增强

- Kata/gVisor 适用场景与权衡

## 5. 安全基线与合规

- 加固清单、日志审计、秘密管理

## 6. 故障与应急响应

- 逃逸迹象、封堵与取证、镜像回滚

（待补充：基线模板与策略示例）

## 7. 实操清单

- 默认 rootless 运行；`subuid/subgid` 配置；限制 capabilities；启用 seccomp/SELinux。
- 只读根与 tmpfs 写路径；密钥与凭证脱敏；启用审计。

## 8. 故障清单与排查

- 策略拒绝：检查 policy.json 与签名链路；查看 audit 日志。
- 权限异常：核对 userns 映射、SELinux/AppArmor 标签、挂载选项。

## 9. FAQ

- 如何选择 crun/runc？多数发行版默认 crun，cgroups v2 支持更佳、开销更小。

## 10. 基线模板（建议）

- 默认 rootless、配置 subuid/subgid；限制 capabilities；启用 seccomp 与 SELinux。
- 只读根与 tmpfs 写路径；策略签名与镜像来源白名单；监控策略与审计。
