# Docker网络技术

## 目录

- [Docker网络技术](#docker网络技术)
  - [目录](#目录)
  - [1. 网络模式与适用场景](#1-网络模式与适用场景)
  - [2. Bridge/Host/None 细节](#2-bridgehostnone-细节)
  - [3. Overlay 与跨主机互联](#3-overlay-与跨主机互联)
  - [4. IPv6 与策略控制](#4-ipv6-与策略控制)
  - [5. 故障诊断与调优](#5-故障诊断与调优)

## 1. 网络模式与适用场景

- 单机、跨主机、性能与隔离权衡

## 2. Bridge/Host/None 细节

- Docker 网桥、端口映射、NAT/iptables 交互

## 3. Overlay 与跨主机互联

- VXLAN/加密、MTU、常见坑点

## 4. IPv6 与策略控制

- IPv6 启用、地址规划、策略与安全

## 5. 故障诊断与调优

- `docker network inspect`、tcpdump、路由与冲突定位

（待补充：Overlay 与 K8s/CNI 对接注意事项）
