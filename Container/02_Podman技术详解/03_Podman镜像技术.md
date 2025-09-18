# Podman镜像技术

## 目录

- [Podman镜像技术](#podman镜像技术)
  - [目录](#目录)
  - [1. 镜像结构与元数据（OCI）](#1-镜像结构与元数据oci)
  - [2. buildah 构建与缓存优化](#2-buildah-构建与缓存优化)
  - [3. 多架构镜像与 manifest](#3-多架构镜像与-manifest)
  - [4. 镜像签名、策略与供应链](#4-镜像签名策略与供应链)
  - [5. skopeo 分发与复制](#5-skopeo-分发与复制)
  - [6. 最佳实践与 FAQ](#6-最佳实践与-faq)
- [7. 实操示例](#7-实操示例)
- [8. 故障清单与排查](#8-故障清单与排查)
- [9. FAQ](#9-faq)

## 1. 镜像结构与元数据（OCI）

- 与 Docker 兼容的 OCI Image；Config/Manifest/Labels。

## 2. buildah 构建与缓存优化

- rootless 友好；分层与缓存；容器内/外构建对比。

## 3. 多架构镜像与 manifest

- `buildah manifest` / `podman manifest` 管理与推送。

## 4. 镜像签名、策略与供应链

- Sigstore/policy.json、SBOM 与漏洞扫描集成。

## 5. skopeo 分发与复制

- 仓库间复制/验证；air-gap 环境分发。

## 6. 最佳实践与 FAQ

- 最小基镜、可复现构建、策略门禁。

（待补充：buildah 与 skopeo 实操片段）

## 7. 实操示例

```bash
# 使用 buildah 构建并推送多架构镜像
buildah build --platform linux/amd64,linux/arm64 -t registry.local/demo:1.0 .
buildah manifest create registry.local/demo:1.0
buildah manifest add registry.local/demo:1.0 docker://registry.local/demo:1.0
buildah manifest push --all registry.local/demo:1.0 docker://registry.local/demo:1.0

# 使用 skopeo 在仓库间复制
skopeo copy docker://docker.io/library/alpine:3.20 docker://registry.local/mirror/alpine:3.20
```

## 8. 故障清单与排查

- 构建缓存失效：检查层顺序与上下文变更，使用 BuildKit/`--mount=type=cache`。
- 签名策略阻断：核对 `policy.json` 与信任根配置；查看 skopeo 检验输出。
- 推送失败：检查凭证与镜像大小、网络与 MTU；重试策略。

## 9. FAQ

- 与 Dockerfile 兼容性？buildah 支持 Dockerfile，亦支持更细粒度命令集。
- 如何生成 SBOM？结合 syft、tern 等工具在 CI 中生成并附加。
