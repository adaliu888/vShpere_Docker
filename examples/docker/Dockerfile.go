# Go容器编排器Dockerfile
FROM golang:1.21-alpine as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    git \
    ca-certificates \
    tzdata

# 复制go mod文件
COPY examples/go/go.mod examples/go/go.sum ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY examples/go/ ./

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o container_orchestrator .

# 运行时镜像
FROM alpine:latest

# 安装运行时依赖
RUN apk --no-cache add \
    ca-certificates \
    curl \
    docker-cli

# 创建非root用户
RUN adduser -D -s /bin/sh appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制二进制文件
COPY --from=builder /app/container_orchestrator /app/container_orchestrator

# 复制配置文件
COPY examples/docker/config /app/config

# 创建日志目录
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令
CMD ["./container_orchestrator"]
