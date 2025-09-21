#!/bin/bash
# 文档自动化管理脚本
# 解决目录手工修改问题，实现自动化管理

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    # 检查必要的Python包
    python3 -c "import yaml, markdown" 2>/dev/null || {
        print_warning "缺少必要的Python包，正在安装..."
        pip3 install pyyaml markdown
    }
}

# 自动更新所有文档的目录
auto_update_toc() {
    print_info "开始自动更新所有文档的目录..."
    
    python3 tools/auto_toc_generator.py --root . --all --update
    
    print_success "目录更新完成"
}

# 为没有目录的文档创建目录
create_missing_toc() {
    print_info "为没有目录的文档创建目录..."
    
    python3 tools/auto_toc_generator.py --root . --all --create
    
    print_success "目录创建完成"
}

# 验证文档质量
validate_documents() {
    print_info "开始验证文档质量..."
    
    python3 tools/document_automation.py --root . --validate
    
    print_success "文档验证完成"
}

# 生成质量报告
generate_report() {
    print_info "生成文档质量报告..."
    
    python3 tools/document_automation.py --root . --report
    
    print_success "质量报告已生成: 文档质量报告.md"
}

# 自动修复格式问题
auto_fix_format() {
    print_info "开始自动修复格式问题..."
    
    # 查找所有Markdown文件
    find . -name "*.md" -not -path "./tools/*" -not -path "./.git/*" | while read -r file; do
        print_info "修复文件: $file"
        python3 tools/document_automation.py --root . --fix "$file"
    done
    
    print_success "格式修复完成"
}

# 创建新文档模板
create_template() {
    local file_path="$1"
    local title="$2"
    
    if [ -z "$file_path" ] || [ -z "$title" ]; then
        print_error "用法: $0 create-template <文件路径> <标题>"
        exit 1
    fi
    
    print_info "创建文档模板: $file_path"
    python3 tools/document_automation.py --root . --template "$file_path" "$title"
    
    print_success "文档模板已创建: $file_path"
}

# 批量处理所有文档
batch_process() {
    print_info "开始批量处理所有文档..."
    
    # 1. 创建缺失的目录
    create_missing_toc
    
    # 2. 更新现有目录
    auto_update_toc
    
    # 3. 修复格式问题
    auto_fix_format
    
    # 4. 验证文档质量
    validate_documents
    
    # 5. 生成质量报告
    generate_report
    
    print_success "批量处理完成"
}

# 显示帮助信息
show_help() {
    echo "文档自动化管理工具"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  update-toc          自动更新所有文档的目录"
    echo "  create-toc          为没有目录的文档创建目录"
    echo "  validate            验证文档质量"
    echo "  report              生成质量报告"
    echo "  fix-format          自动修复格式问题"
    echo "  create-template     创建新文档模板"
    echo "  batch               批量处理所有文档"
    echo "  help                显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 update-toc                    # 更新所有目录"
    echo "  $0 create-template new.md '新文档' # 创建模板"
    echo "  $0 batch                         # 批量处理"
}

# 主函数
main() {
    # 检查Python环境
    check_python
    
    # 切换到脚本所在目录的父目录
    cd "$(dirname "$0")/.."
    
    case "${1:-help}" in
        "update-toc")
            auto_update_toc
            ;;
        "create-toc")
            create_missing_toc
            ;;
        "validate")
            validate_documents
            ;;
        "report")
            generate_report
            ;;
        "fix-format")
            auto_fix_format
            ;;
        "create-template")
            create_template "$2" "$3"
            ;;
        "batch")
            batch_process
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@"
