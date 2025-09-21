#!/bin/bash

# 文档自动化管理工具 - Linux/Mac版本

echo ""
echo "========================================"
echo "   文档自动化管理工具 - Linux/Mac版本"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到Python，请先安装Python 3.6+"
    echo "Ubuntu/Debian: sudo apt install python3"
    echo "CentOS/RHEL: sudo yum install python3"
    echo "macOS: brew install python3"
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# 获取脚本参数
ACTION=$1
if [ -z "$ACTION" ]; then
    echo "使用方法:"
    echo "  $0 update-toc     - 更新所有文档的目录"
    echo "  $0 create-toc     - 为没有目录的文档创建目录"
    echo "  $0 batch          - 批量处理所有文档"
    echo "  $0 simple         - 使用简化版工具快速更新"
    echo "  $0 help           - 显示帮助信息"
    echo ""
    exit 0
fi

if [ "$ACTION" = "help" ]; then
    echo "详细帮助信息:"
    echo ""
    echo "update-toc: 更新所有现有文档的目录"
    echo "  - 自动检测并更新现有目录"
    echo "  - 保持原有目录位置"
    echo "  - 适用于文档内容有修改的情况"
    echo ""
    echo "create-toc: 为没有目录的文档创建目录"
    echo "  - 只为没有目录的文档创建新目录"
    echo "  - 不会覆盖现有目录"
    echo "  - 适用于新文档或缺少目录的文档"
    echo ""
    echo "batch: 批量处理所有文档"
    echo "  - 更新现有目录"
    echo "  - 创建缺失的目录"
    echo "  - 生成处理报告"
    echo ""
    echo "simple: 使用简化版工具快速更新"
    echo "  - 无需额外依赖"
    echo "  - 快速处理"
    echo "  - 推荐日常使用"
    echo ""
    exit 0
fi

echo "🚀 开始执行: $ACTION"
echo ""

# 切换到脚本所在目录的父目录
cd "$(dirname "$0")/.."

case $ACTION in
    "simple")
        echo "📝 使用简化版工具快速更新目录..."
        $PYTHON_CMD tools/simple_toc_updater.py .
        ;;
    "update-toc")
        echo "📝 更新所有文档的目录..."
        $PYTHON_CMD tools/auto_toc_generator.py --root . --all --update
        ;;
    "create-toc")
        echo "📝 为没有目录的文档创建目录..."
        $PYTHON_CMD tools/auto_toc_generator.py --root . --all --create
        ;;
    "batch")
        echo "📝 批量处理所有文档..."
        echo ""
        echo "步骤1: 更新现有目录..."
        $PYTHON_CMD tools/auto_toc_generator.py --root . --all --update
        echo ""
        echo "步骤2: 创建缺失的目录..."
        $PYTHON_CMD tools/auto_toc_generator.py --root . --all --create
        echo ""
        echo "步骤3: 生成处理报告..."
        $PYTHON_CMD tools/simple_toc_updater.py . > tools/batch_report.txt 2>&1
        echo ""
        echo "📊 处理完成！报告已保存到 tools/batch_report.txt"
        ;;
    *)
        echo "❌ 未知操作: $ACTION"
        echo "使用 $0 help 查看帮助信息"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成！"
echo ""
echo "💡 提示:"
echo "  - 所有Markdown文档的目录已自动更新"
echo "  - 无需手工修改目录"
echo "  - 可以随时重新运行此脚本"
echo ""