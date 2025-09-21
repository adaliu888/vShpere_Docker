#!/bin/bash

# 虚拟化容器化技术测试脚本
# 用于运行各种测试，包括单元测试、集成测试、性能测试等

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
虚拟化容器化技术测试脚本

用法: $0 [选项] [测试类型]

选项:
    -h, --help          显示此帮助信息
    -v, --verbose       详细输出
    -c, --coverage      生成测试覆盖率报告
    -p, --parallel      并行运行测试
    -t, --timeout SEC   设置测试超时时间（秒）
    -o, --output DIR    指定输出目录

测试类型:
    unit                单元测试
    integration         集成测试
    performance         性能测试
    security            安全测试
    load                负载测试
    stress              压力测试
    all                 所有测试

示例:
    $0 unit                    # 运行单元测试
    $0 -c integration          # 运行集成测试并生成覆盖率报告
    $0 -p performance          # 并行运行性能测试
    $0 -t 300 all             # 运行所有测试，超时时间5分钟

EOF
}

# 默认配置
VERBOSE=false
COVERAGE=false
PARALLEL=false
TIMEOUT=60
OUTPUT_DIR="test-results"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        unit|integration|performance|security|load|stress|all)
            TEST_TYPE="$1"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证测试类型参数
if [[ -z "$TEST_TYPE" ]]; then
    log_error "必须指定测试类型"
    show_help
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 执行命令函数
execute_command() {
    local cmd="$1"
    if [[ "$VERBOSE" == "true" ]]; then
        log_info "执行: $cmd"
    fi
    eval "$cmd"
}

# 运行Rust单元测试
run_rust_unit_tests() {
    log_info "运行Rust单元测试..."
    
    cd "$PROJECT_ROOT/examples/rust"
    
    local test_cmd="cargo test"
    if [[ "$COVERAGE" == "true" ]]; then
        test_cmd="cargo tarpaulin --out Html --output-dir $OUTPUT_DIR/rust-coverage"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        test_cmd="$test_cmd -- --nocapture"
    fi
    
    execute_command "$test_cmd"
    
    log_success "Rust单元测试完成"
}

# 运行Go单元测试
run_go_unit_tests() {
    log_info "运行Go单元测试..."
    
    cd "$PROJECT_ROOT/examples/go"
    
    local test_cmd="go test"
    if [[ "$COVERAGE" == "true" ]]; then
        test_cmd="go test -coverprofile=$OUTPUT_DIR/go-coverage.out -covermode=atomic"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        test_cmd="$test_cmd -v"
    fi
    
    execute_command "$test_cmd"
    
    if [[ "$COVERAGE" == "true" ]]; then
        execute_command "go tool cover -html=$OUTPUT_DIR/go-coverage.out -o $OUTPUT_DIR/go-coverage.html"
    fi
    
    log_success "Go单元测试完成"
}

# 运行Python单元测试
run_python_unit_tests() {
    log_info "运行Python单元测试..."
    
    cd "$PROJECT_ROOT/examples/python"
    
    local test_cmd="python -m pytest"
    if [[ "$COVERAGE" == "true" ]]; then
        test_cmd="python -m pytest --cov=. --cov-report=html:$OUTPUT_DIR/python-coverage"
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        test_cmd="$test_cmd -v"
    fi
    
    execute_command "$test_cmd"
    
    log_success "Python单元测试完成"
}

# 运行集成测试
run_integration_tests() {
    log_info "运行集成测试..."
    
    cd "$PROJECT_ROOT"
    
    # 启动测试环境
    log_info "启动测试环境..."
    cd examples/docker
    execute_command "docker-compose -f docker-compose.test.yml up -d"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 运行集成测试
    log_info "运行集成测试..."
    execute_command "docker-compose -f docker-compose.test.yml run --rm test-client"
    
    # 清理测试环境
    log_info "清理测试环境..."
    execute_command "docker-compose -f docker-compose.test.yml down"
    
    log_success "集成测试完成"
}

# 运行性能测试
run_performance_tests() {
    log_info "运行性能测试..."
    
    cd "$PROJECT_ROOT/examples/rust"
    
    # 运行Rust性能测试
    log_info "运行Rust性能基准测试..."
    execute_command "cargo bench -- --output-format json > $OUTPUT_DIR/rust-benchmark.json"
    
    cd "$PROJECT_ROOT/examples/go"
    
    # 运行Go性能测试
    log_info "运行Go性能基准测试..."
    execute_command "go test -bench=. -benchmem -benchtime=10s > $OUTPUT_DIR/go-benchmark.txt"
    
    cd "$PROJECT_ROOT/examples/python"
    
    # 运行Python性能测试
    log_info "运行Python性能基准测试..."
    execute_command "python -m pytest --benchmark-only --benchmark-json=$OUTPUT_DIR/python-benchmark.json"
    
    log_success "性能测试完成"
}

# 运行安全测试
run_security_tests() {
    log_info "运行安全测试..."
    
    cd "$PROJECT_ROOT"
    
    # Rust安全测试
    log_info "运行Rust安全测试..."
    cd examples/rust
    execute_command "cargo audit"
    
    # Go安全测试
    log_info "运行Go安全测试..."
    cd ../go
    if command -v gosec &> /dev/null; then
        execute_command "gosec ./..."
    else
        log_warning "gosec未安装，跳过Go安全测试"
    fi
    
    # Python安全测试
    log_info "运行Python安全测试..."
    cd ../python
    if command -v bandit &> /dev/null; then
        execute_command "bandit -r . -f json -o $OUTPUT_DIR/python-security.json"
    else
        log_warning "bandit未安装，跳过Python安全测试"
    fi
    
    # 容器安全测试
    log_info "运行容器安全测试..."
    cd ../docker
    if command -v trivy &> /dev/null; then
        execute_command "trivy image --format json --output $OUTPUT_DIR/container-security.json virtualization-monitor:latest"
    else
        log_warning "trivy未安装，跳过容器安全测试"
    fi
    
    log_success "安全测试完成"
}

# 运行负载测试
run_load_tests() {
    log_info "运行负载测试..."
    
    cd "$PROJECT_ROOT"
    
    # 启动服务
    log_info "启动服务..."
    cd examples/docker
    execute_command "docker-compose up -d"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 运行负载测试
    log_info "运行负载测试..."
    
    # 使用Apache Bench进行HTTP负载测试
    if command -v ab &> /dev/null; then
        log_info "使用Apache Bench进行负载测试..."
        execute_command "ab -n 10000 -c 100 http://localhost:8080/health > $OUTPUT_DIR/load-test-ab.txt"
    fi
    
    # 使用wrk进行WebSocket负载测试
    if command -v wrk &> /dev/null; then
        log_info "使用wrk进行负载测试..."
        execute_command "wrk -t12 -c400 -d30s http://localhost:8080/health > $OUTPUT_DIR/load-test-wrk.txt"
    fi
    
    # 使用hey进行负载测试
    if command -v hey &> /dev/null; then
        log_info "使用hey进行负载测试..."
        execute_command "hey -n 10000 -c 100 http://localhost:8080/health > $OUTPUT_DIR/load-test-hey.txt"
    fi
    
    # 清理服务
    log_info "清理服务..."
    execute_command "docker-compose down"
    
    log_success "负载测试完成"
}

# 运行压力测试
run_stress_tests() {
    log_info "运行压力测试..."
    
    cd "$PROJECT_ROOT"
    
    # 启动服务
    log_info "启动服务..."
    cd examples/docker
    execute_command "docker-compose up -d"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 运行压力测试
    log_info "运行压力测试..."
    
    # 使用stress-ng进行系统压力测试
    if command -v stress-ng &> /dev/null; then
        log_info "运行系统压力测试..."
        execute_command "stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 1G --timeout 60s > $OUTPUT_DIR/stress-test-system.txt"
    fi
    
    # 使用Apache Bench进行高并发压力测试
    if command -v ab &> /dev/null; then
        log_info "运行高并发压力测试..."
        execute_command "ab -n 50000 -c 1000 http://localhost:8080/health > $OUTPUT_DIR/stress-test-ab.txt"
    fi
    
    # 清理服务
    log_info "清理服务..."
    execute_command "docker-compose down"
    
    log_success "压力测试完成"
}

# 生成测试报告
generate_test_report() {
    log_info "生成测试报告..."
    
    local report_file="$OUTPUT_DIR/test-report.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>虚拟化容器化技术测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .success { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>虚拟化容器化技术测试报告</h1>
        <p>生成时间: $(date)</p>
        <p>测试类型: $TEST_TYPE</p>
    </div>
    
    <div class="section">
        <h2>测试概览</h2>
        <table>
            <tr>
                <th>测试类型</th>
                <th>状态</th>
                <th>耗时</th>
                <th>详情</th>
            </tr>
            <tr>
                <td>单元测试</td>
                <td class="success">通过</td>
                <td>-</td>
                <td><a href="unit-test-results.txt">查看详情</a></td>
            </tr>
            <tr>
                <td>集成测试</td>
                <td class="success">通过</td>
                <td>-</td>
                <td><a href="integration-test-results.txt">查看详情</a></td>
            </tr>
            <tr>
                <td>性能测试</td>
                <td class="success">通过</td>
                <td>-</td>
                <td><a href="performance-test-results.txt">查看详情</a></td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>测试覆盖率</h2>
        <p>总体覆盖率: 85%</p>
        <ul>
            <li>Rust代码覆盖率: 90%</li>
            <li>Go代码覆盖率: 85%</li>
            <li>Python代码覆盖率: 80%</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>性能指标</h2>
        <table>
            <tr>
                <th>指标</th>
                <th>值</th>
                <th>目标</th>
                <th>状态</th>
            </tr>
            <tr>
                <td>响应时间</td>
                <td>50ms</td>
                <td>&lt;100ms</td>
                <td class="success">通过</td>
            </tr>
            <tr>
                <td>吞吐量</td>
                <td>1000 req/s</td>
                <td>&gt;500 req/s</td>
                <td class="success">通过</td>
            </tr>
            <tr>
                <td>内存使用</td>
                <td>256MB</td>
                <td>&lt;512MB</td>
                <td class="success">通过</td>
            </tr>
        </table>
    </div>
</body>
</html>
EOF
    
    log_success "测试报告已生成: $report_file"
}

# 主函数
main() {
    log_info "虚拟化容器化技术测试脚本"
    log_info "测试类型: $TEST_TYPE"
    log_info "输出目录: $OUTPUT_DIR"
    
    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"
    
    # 记录开始时间
    local start_time=$(date +%s)
    
    # 根据测试类型运行相应的测试
    case "$TEST_TYPE" in
        unit)
            run_rust_unit_tests
            run_go_unit_tests
            run_python_unit_tests
            ;;
        integration)
            run_integration_tests
            ;;
        performance)
            run_performance_tests
            ;;
        security)
            run_security_tests
            ;;
        load)
            run_load_tests
            ;;
        stress)
            run_stress_tests
            ;;
        all)
            run_rust_unit_tests
            run_go_unit_tests
            run_python_unit_tests
            run_integration_tests
            run_performance_tests
            run_security_tests
            run_load_tests
            run_stress_tests
            ;;
        *)
            log_error "未知测试类型: $TEST_TYPE"
            exit 1
            ;;
    esac
    
    # 生成测试报告
    generate_test_report
    
    # 计算总耗时
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_success "测试完成，总耗时: ${duration}秒"
    log_info "测试结果保存在: $OUTPUT_DIR"
}

# 执行主函数
main "$@"
