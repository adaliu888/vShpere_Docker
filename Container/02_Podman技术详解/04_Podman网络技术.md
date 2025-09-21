# Podman网络技术

## 目录

- [Podman网络技术](#podman网络技术)
  - [1. 网络后端与模式](#1-网络后端与模式)
  - [2. netavark/aardvark-dns](#2-netavarkaardvark-dns)
  - [3. rootless 网络：slirp4netns/pasta](#3-rootless-网络slirp4netnspasta)
  - [4. IPv6 与高级特性](#4-ipv6-与高级特性)
  - [5. 故障诊断与调优](#5-故障诊断与调优)
  - [6. 实操示例](#6-实操示例)
- [创建自定义网络并启用 IPv6](#创建自定义网络并启用-ipv6)
- [rootless 使用 pasta](#rootless-使用-pasta)
  - [7. 故障清单与排查](#7-故障清单与排查)
  - [8. FAQ](#8-faq)

- [Podman网络技术](#podman网络技术)
  - [1. 网络后端与模式](#1-网络后端与模式)
  - [2. netavark/aardvark-dns](#2-netavarkaardvark-dns)
  - [3. rootless 网络：slirp4netns/pasta](#3-rootless-网络slirp4netnspasta)
  - [4. IPv6 与高级特性](#4-ipv6-与高级特性)
  - [5. 故障诊断与调优](#5-故障诊断与调优)
  - [6. 实操示例](#6-实操示例)
- [创建自定义网络并启用 IPv6](#创建自定义网络并启用-ipv6)
- [rootless 使用 pasta](#rootless-使用-pasta)
  - [7. 故障清单与排查](#7-故障清单与排查)
  - [8. FAQ](#8-faq)

- [Podman网络技术](#podman网络技术)
  - [目录](#目录)
  - [1. 网络后端与模式](#1-网络后端与模式)
  - [2. netavark/aardvark-dns](#2-netavarkaardvark-dns)
  - [3. rootless 网络：slirp4netns/pasta](#3-rootless-网络slirp4netnspasta)
  - [4. IPv6 与高级特性](#4-ipv6-与高级特性)
  - [5. 故障诊断与调优](#5-故障诊断与调优)
- [6. 实操示例](#6-实操示例)
- [7. 故障清单与排查](#7-故障清单与排查)
- [8. FAQ](#8-faq)

## 1. 网络后端与模式

- Bridge/Host/None/Pod；与 Docker 语义差异

## 2. netavark/aardvark-dns

- 架构、功能点与与 CNI 差异

## 3. rootless 网络：slirp4netns/pasta

- 性能、端口限制与调优要点

## 4. IPv6 与高级特性

- IPv6 规划、macvlan、vlan 等

## 5. 故障诊断与调优

- `podman network inspect`、iptables/nftables 规则核对

（待补充：典型拓扑与问题清单）

## 6. 实操示例

```bash
# 创建自定义网络并启用 IPv6
podman network create --subnet 10.10.0.0/24 --ipv6 --subnet fd00:10:10::/64 app-net
podman run -d --name web --network app-net -p 8080:80 nginx:alpine

# rootless 使用 pasta
podman run --network pasta -d --name web2 nginx:alpine
```

## 7. 故障清单与排查

- 端口未通：确认 rootless 与低端口限制；检查主机防火墙与转发表。
- IPv6 未生效：检查发行版 IPv6 启用与 `netavark` 版本；核对子网配置。
- 性能问题：评估 slirp4netns 与 pasta 的差异；考虑 macvlan/host 网络。

## 8. FAQ

- 与 Docker 的 bridge 有何差异？Podman 默认 `netavark`，配置模型与细节不同，IPv6 体验更佳。
