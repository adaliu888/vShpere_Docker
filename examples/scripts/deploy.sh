#!/bin/bash

# 虚拟化容器化技术演示环境部署脚本
# 支持Docker Compose和Kubernetes两种部署方式

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
虚拟化容器化技术演示环境部署脚本

用法: $0 [选项] [命令]

选项:
    -h, --help          显示此帮助信息
    -e, --env ENV       指定环境 (dev|staging|prod)
    -p, --platform PLAT 指定平台 (docker|kubernetes)
    -v, --verbose       详细输出
    -d, --dry-run       模拟运行，不执行实际操作

命令:
    build               构建所有镜像
    deploy              部署环境
    start               启动服务
    stop                停止服务
    restart             重启服务
    status              查看服务状态
    logs                查看服务日志
    clean               清理环境
    test                运行测试
    monitor             启动监控

示例:
    $0 -p docker deploy          # 使用Docker Compose部署
    $0 -p kubernetes deploy      # 使用Kubernetes部署
    $0 -e prod -p docker deploy  # 部署到生产环境
    $0 logs                      # 查看日志
    $0 test                      # 运行测试

EOF
}

# 默认配置
ENVIRONMENT="dev"
PLATFORM="docker"
VERBOSE=false
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        build|deploy|start|stop|restart|status|logs|clean|test|monitor)
            COMMAND="$1"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证环境参数
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    log_error "无效的环境: $ENVIRONMENT. 必须是 dev, staging 或 prod"
    exit 1
fi

# 验证平台参数
if [[ ! "$PLATFORM" =~ ^(docker|kubernetes)$ ]]; then
    log_error "无效的平台: $PLATFORM. 必须是 docker 或 kubernetes"
    exit 1
fi

# 验证命令参数
if [[ -z "$COMMAND" ]]; then
    log_error "必须指定一个命令"
    show_help
    exit 1
fi

# 执行命令函数
execute_command() {
    local cmd="$1"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "模拟执行: $cmd"
    else
        if [[ "$VERBOSE" == "true" ]]; then
            log_info "执行: $cmd"
        fi
        eval "$cmd"
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if [[ "$PLATFORM" == "docker" ]]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker 未安装"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            log_error "Docker Compose 未安装"
            exit 1
        fi
    elif [[ "$PLATFORM" == "kubernetes" ]]; then
        if ! command -v kubectl &> /dev/null; then
            log_error "kubectl 未安装"
            exit 1
        fi
        
        if ! command -v helm &> /dev/null; then
            log_warning "Helm 未安装，某些功能可能不可用"
        fi
    fi
    
    log_success "依赖检查完成"
}

# 构建镜像
build_images() {
    log_info "构建镜像..."
    
    cd "$PROJECT_ROOT"
    
    # 构建Rust虚拟化监控器
    log_info "构建虚拟化监控器镜像..."
    execute_command "docker build -f examples/docker/Dockerfile.rust -t virtualization-monitor:latest ."
    
    # 构建Go容器编排器
    log_info "构建容器编排器镜像..."
    execute_command "docker build -f examples/docker/Dockerfile.go -t container-orchestrator:latest ."
    
    # 构建Python语义验证器
    log_info "构建语义验证器镜像..."
    execute_command "docker build -f examples/docker/Dockerfile.python -t semantic-validator:latest ."
    
    # 构建测试客户端
    log_info "构建测试客户端镜像..."
    execute_command "docker build -f examples/docker/Dockerfile.test -t test-client:latest ."
    
    log_success "镜像构建完成"
}

# Docker Compose部署
deploy_docker() {
    log_info "使用Docker Compose部署..."
    
    cd "$PROJECT_ROOT/examples/docker"
    
    # 创建必要的目录
    execute_command "mkdir -p config logs prometheus grafana/dashboards grafana/datasources nginx ssl"
    
    # 生成配置文件
    generate_docker_configs
    
    # 启动服务
    execute_command "docker-compose up -d"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_docker_services
    
    log_success "Docker Compose部署完成"
}

# Kubernetes部署
deploy_kubernetes() {
    log_info "使用Kubernetes部署..."
    
    cd "$PROJECT_ROOT/examples/docker/kubernetes"
    
    # 创建命名空间
    execute_command "kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: virtualization-demo
  labels:
    name: virtualization-demo
    purpose: demonstration
EOF"
    
    # 创建配置
    generate_k8s_configs
    
    # 应用配置
    execute_command "kubectl apply -f configmaps.yaml"
    execute_command "kubectl apply -f secrets.yaml"
    execute_command "kubectl apply -f persistent-volumes.yaml"
    execute_command "kubectl apply -f deployment.yaml"
    execute_command "kubectl apply -f service.yaml"
    execute_command "kubectl apply -f ingress.yaml"
    
    # 等待部署完成
    log_info "等待部署完成..."
    execute_command "kubectl wait --for=condition=available --timeout=300s deployment/virtualization-monitor -n virtualization-demo"
    execute_command "kubectl wait --for=condition=available --timeout=300s deployment/container-orchestrator -n virtualization-demo"
    execute_command "kubectl wait --for=condition=available --timeout=300s deployment/semantic-validator -n virtualization-demo"
    
    log_success "Kubernetes部署完成"
}

# 生成Docker配置文件
generate_docker_configs() {
    log_info "生成Docker配置文件..."
    
    # Prometheus配置
    cat > prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'virtualization-monitor'
    static_configs:
      - targets: ['virtualization-monitor:8080']

  - job_name: 'container-orchestrator'
    static_configs:
      - targets: ['container-orchestrator:8080']

  - job_name: 'semantic-validator'
    static_configs:
      - targets: ['semantic-validator:8080']
EOF

    # Grafana数据源配置
    cat > grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    # Nginx配置
    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream virtualization-monitor {
        server virtualization-monitor:8080;
    }
    
    upstream container-orchestrator {
        server container-orchestrator:8080;
    }
    
    upstream semantic-validator {
        server semantic-validator:8080;
    }
    
    server {
        listen 80;
        
        location /monitor/ {
            proxy_pass http://virtualization-monitor/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
        
        location /orchestrator/ {
            proxy_pass http://container-orchestrator/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
        
        location /validator/ {
            proxy_pass http://semantic-validator/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
        
        location /grafana/ {
            proxy_pass http://grafana:3000/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
        
        location /prometheus/ {
            proxy_pass http://prometheus:9090/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
}
EOF

    log_success "Docker配置文件生成完成"
}

# 生成Kubernetes配置文件
generate_k8s_configs() {
    log_info "生成Kubernetes配置文件..."
    
    # 创建ConfigMaps
    cat > configmaps.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: virtualization-monitor-config
  namespace: virtualization-demo
data:
  config.yaml: |
    monitoring:
      interval: 30
      max_history: 1000
    logging:
      level: info

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: container-orchestrator-config
  namespace: virtualization-demo
data:
  config.yaml: |
    orchestration:
      strategy: round_robin
    docker:
      host: unix:///var/run/docker.sock

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: semantic-validator-config
  namespace: virtualization-demo
data:
  config.yaml: |
    validation:
      timeout: 30
    logging:
      level: info

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: virtualization-demo
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
EOF

    # 创建Secrets
    cat > secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: grafana-secret
  namespace: virtualization-demo
type: Opaque
data:
  admin-password: YWRtaW4xMjM=  # admin123

---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: virtualization-demo
type: Opaque
data:
  password: YWRtaW4xMjM=  # admin123

---
apiVersion: v1
kind: Secret
metadata:
  name: redis-secret
  namespace: virtualization-demo
type: Opaque
data:
  password: cmVkaXMxMjM=  # redis123
EOF

    # 创建持久化存储
    cat > persistent-volumes.yaml << EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-pvc
  namespace: virtualization-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-pvc
  namespace: virtualization-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: virtualization-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: virtualization-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
EOF

    log_success "Kubernetes配置文件生成完成"
}

# 检查Docker服务状态
check_docker_services() {
    log_info "检查Docker服务状态..."
    
    cd "$PROJECT_ROOT/examples/docker"
    
    # 获取服务状态
    execute_command "docker-compose ps"
    
    # 检查健康状态
    local services=("virtualization-monitor" "container-orchestrator" "semantic-validator" "prometheus" "grafana")
    
    for service in "${services[@]}"; do
        if execute_command "docker-compose exec $service curl -f http://localhost:8080/health 2>/dev/null || docker-compose exec $service curl -f http://localhost:9090/-/healthy 2>/dev/null || docker-compose exec $service curl -f http://localhost:3000/api/health 2>/dev/null"; then
            log_success "$service 健康检查通过"
        else
            log_warning "$service 健康检查失败"
        fi
    done
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    if [[ "$PLATFORM" == "docker" ]]; then
        cd "$PROJECT_ROOT/examples/docker"
        execute_command "docker-compose start"
    elif [[ "$PLATFORM" == "kubernetes" ]]; then
        execute_command "kubectl scale deployment --replicas=2 virtualization-monitor -n virtualization-demo"
        execute_command "kubectl scale deployment --replicas=2 container-orchestrator -n virtualization-demo"
        execute_command "kubectl scale deployment --replicas=1 semantic-validator -n virtualization-demo"
    fi
    
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    if [[ "$PLATFORM" == "docker" ]]; then
        cd "$PROJECT_ROOT/examples/docker"
        execute_command "docker-compose stop"
    elif [[ "$PLATFORM" == "kubernetes" ]]; then
        execute_command "kubectl scale deployment --replicas=0 virtualization-monitor -n virtualization-demo"
        execute_command "kubectl scale deployment --replicas=0 container-orchestrator -n virtualization-demo"
        execute_command "kubectl scale deployment --replicas=0 semantic-validator -n virtualization-demo"
    fi
    
    log_success "服务停止完成"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    stop_services
    sleep 5
    start_services
    log_success "服务重启完成"
}

# 查看服务状态
show_status() {
    log_info "查看服务状态..."
    
    if [[ "$PLATFORM" == "docker" ]]; then
        cd "$PROJECT_ROOT/examples/docker"
        execute_command "docker-compose ps"
    elif [[ "$PLATFORM" == "kubernetes" ]]; then
        execute_command "kubectl get pods -n virtualization-demo"
        execute_command "kubectl get services -n virtualization-demo"
        execute_command "kubectl get ingress -n virtualization-demo"
    fi
}

# 查看服务日志
show_logs() {
    log_info "查看服务日志..."
    
    if [[ "$PLATFORM" == "docker" ]]; then
        cd "$PROJECT_ROOT/examples/docker"
        execute_command "docker-compose logs -f --tail=100"
    elif [[ "$PLATFORM" == "kubernetes" ]]; then
        execute_command "kubectl logs -f deployment/virtualization-monitor -n virtualization-demo"
    fi
}

# 清理环境
clean_environment() {
    log_info "清理环境..."
    
    if [[ "$PLATFORM" == "docker" ]]; then
        cd "$PROJECT_ROOT/examples/docker"
        execute_command "docker-compose down -v"
        execute_command "docker system prune -f"
    elif [[ "$PLATFORM" == "kubernetes" ]]; then
        execute_command "kubectl delete namespace virtualization-demo"
    fi
    
    log_success "环境清理完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    cd "$PROJECT_ROOT"
    
    # 运行Rust测试
    log_info "运行Rust测试..."
    execute_command "cd examples/rust && cargo test"
    
    # 运行Go测试
    log_info "运行Go测试..."
    execute_command "cd examples/go && go test ./..."
    
    # 运行Python测试
    log_info "运行Python测试..."
    execute_command "cd examples/python && python -m pytest"
    
    # 运行集成测试
    log_info "运行集成测试..."
    if [[ "$PLATFORM" == "docker" ]]; then
        cd "$PROJECT_ROOT/examples/docker"
        execute_command "docker-compose run --rm test-client"
    fi
    
    log_success "测试完成"
}

# 启动监控
start_monitoring() {
    log_info "启动监控..."
    
    if [[ "$PLATFORM" == "docker" ]]; then
        log_info "访问地址:"
        log_info "  - 虚拟化监控: http://localhost:8080"
        log_info "  - 容器编排: http://localhost:8081"
        log_info "  - 语义验证: http://localhost:8082"
        log_info "  - Grafana: http://localhost:3000 (admin/admin123)"
        log_info "  - Prometheus: http://localhost:9090"
        log_info "  - Kibana: http://localhost:5601"
    elif [[ "$PLATFORM" == "kubernetes" ]]; then
        log_info "获取访问地址:"
        execute_command "kubectl get ingress -n virtualization-demo"
        execute_command "kubectl get services -n virtualization-demo"
    fi
    
    log_success "监控启动完成"
}

# 主函数
main() {
    log_info "虚拟化容器化技术演示环境部署脚本"
    log_info "环境: $ENVIRONMENT, 平台: $PLATFORM, 命令: $COMMAND"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "模拟运行模式"
    fi
    
    # 检查依赖
    check_dependencies
    
    # 执行命令
    case "$COMMAND" in
        build)
            build_images
            ;;
        deploy)
            if [[ "$PLATFORM" == "docker" ]]; then
                deploy_docker
            elif [[ "$PLATFORM" == "kubernetes" ]]; then
                deploy_kubernetes
            fi
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean_environment
            ;;
        test)
            run_tests
            ;;
        monitor)
            start_monitoring
            ;;
        *)
            log_error "未知命令: $COMMAND"
            exit 1
            ;;
    esac
    
    log_success "操作完成"
}

# 执行主函数
main "$@"
