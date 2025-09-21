@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   文档自动化管理工具 - Windows版本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.6+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 获取脚本参数
set ACTION=%1
if "%ACTION%"=="" (
    echo 使用方法:
    echo   %~nx0 update-toc     - 更新所有文档的目录
    echo   %~nx0 create-toc     - 为没有目录的文档创建目录
    echo   %~nx0 batch          - 批量处理所有文档
    echo   %~nx0 simple         - 使用简化版工具快速更新
    echo   %~nx0 help           - 显示帮助信息
    echo.
    pause
    exit /b 0
)

if "%ACTION%"=="help" (
    echo 详细帮助信息:
    echo.
    echo update-toc: 更新所有现有文档的目录
    echo   - 自动检测并更新现有目录
    echo   - 保持原有目录位置
    echo   - 适用于文档内容有修改的情况
    echo.
    echo create-toc: 为没有目录的文档创建目录
    echo   - 只为没有目录的文档创建新目录
    echo   - 不会覆盖现有目录
    echo   - 适用于新文档或缺少目录的文档
    echo.
    echo batch: 批量处理所有文档
    echo   - 更新现有目录
    echo   - 创建缺失的目录
    echo   - 生成处理报告
    echo.
    echo simple: 使用简化版工具快速更新
    echo   - 无需额外依赖
    echo   - 快速处理
    echo   - 推荐日常使用
    echo.
    pause
    exit /b 0
)

echo 🚀 开始执行: %ACTION%
echo.

REM 切换到脚本所在目录的父目录
cd /d "%~dp0.."

if "%ACTION%"=="simple" (
    echo 📝 使用简化版工具快速更新目录...
    python tools/simple_toc_updater.py .
    goto :end
)

if "%ACTION%"=="update-toc" (
    echo 📝 更新所有文档的目录...
    python tools/auto_toc_generator.py --root . --all --update
    goto :end
)

if "%ACTION%"=="create-toc" (
    echo 📝 为没有目录的文档创建目录...
    python tools/auto_toc_generator.py --root . --all --create
    goto :end
)

if "%ACTION%"=="batch" (
    echo 📝 批量处理所有文档...
    echo.
    echo 步骤1: 更新现有目录...
    python tools/auto_toc_generator.py --root . --all --update
    echo.
    echo 步骤2: 创建缺失的目录...
    python tools/auto_toc_generator.py --root . --all --create
    echo.
    echo 步骤3: 生成处理报告...
    python tools/simple_toc_updater.py . > tools/batch_report.txt 2>&1
    echo.
    echo 📊 处理完成！报告已保存到 tools/batch_report.txt
    goto :end
)

echo ❌ 未知操作: %ACTION%
echo 使用 %~nx0 help 查看帮助信息
exit /b 1

:end
echo.
echo ✅ 操作完成！
echo.
echo 💡 提示:
echo   - 所有Markdown文档的目录已自动更新
echo   - 无需手工修改目录
echo   - 可以随时重新运行此脚本
echo.
pause