@echo off
REM 文档自动化管理脚本 (Windows版本)
REM 解决目录手工修改问题，实现自动化管理

setlocal enabledelayedexpansion

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python未安装，请先安装Python
    exit /b 1
)

REM 检查必要的Python包
python -c "import yaml, markdown" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] 缺少必要的Python包，正在安装...
    pip install pyyaml markdown
)

REM 切换到脚本所在目录的父目录
cd /d "%~dp0\.."

if "%1"=="update-toc" (
    echo [INFO] 开始自动更新所有文档的目录...
    python tools/auto_toc_generator.py --root . --all --update
    echo [SUCCESS] 目录更新完成
    goto :eof
)

if "%1"=="create-toc" (
    echo [INFO] 为没有目录的文档创建目录...
    python tools/auto_toc_generator.py --root . --all --create
    echo [SUCCESS] 目录创建完成
    goto :eof
)

if "%1"=="validate" (
    echo [INFO] 开始验证文档质量...
    python tools/document_automation.py --root . --validate
    echo [SUCCESS] 文档验证完成
    goto :eof
)

if "%1"=="report" (
    echo [INFO] 生成文档质量报告...
    python tools/document_automation.py --root . --report
    echo [SUCCESS] 质量报告已生成: 文档质量报告.md
    goto :eof
)

if "%1"=="fix-format" (
    echo [INFO] 开始自动修复格式问题...
    for /r . %%f in (*.md) do (
        if not "%%f"=="%~dp0*" (
            echo [INFO] 修复文件: %%f
            python tools/document_automation.py --root . --fix "%%f"
        )
    )
    echo [SUCCESS] 格式修复完成
    goto :eof
)

if "%1"=="create-template" (
    if "%2"=="" (
        echo [ERROR] 用法: %0 create-template ^<文件路径^> ^<标题^>
        exit /b 1
    )
    if "%3"=="" (
        echo [ERROR] 用法: %0 create-template ^<文件路径^> ^<标题^>
        exit /b 1
    )
    echo [INFO] 创建文档模板: %2
    python tools/document_automation.py --root . --template "%2" "%3"
    echo [SUCCESS] 文档模板已创建: %2
    goto :eof
)

if "%1"=="batch" (
    echo [INFO] 开始批量处理所有文档...
    
    echo [INFO] 1. 创建缺失的目录...
    python tools/auto_toc_generator.py --root . --all --create
    
    echo [INFO] 2. 更新现有目录...
    python tools/auto_toc_generator.py --root . --all --update
    
    echo [INFO] 3. 修复格式问题...
    for /r . %%f in (*.md) do (
        if not "%%f"=="%~dp0*" (
            python tools/document_automation.py --root . --fix "%%f"
        )
    )
    
    echo [INFO] 4. 验证文档质量...
    python tools/document_automation.py --root . --validate
    
    echo [INFO] 5. 生成质量报告...
    python tools/document_automation.py --root . --report
    
    echo [SUCCESS] 批量处理完成
    goto :eof
)

REM 显示帮助信息
echo 文档自动化管理工具
echo.
echo 用法: %0 [命令] [参数]
echo.
echo 命令:
echo   update-toc          自动更新所有文档的目录
echo   create-toc          为没有目录的文档创建目录
echo   validate            验证文档质量
echo   report              生成质量报告
echo   fix-format          自动修复格式问题
echo   create-template     创建新文档模板
echo   batch               批量处理所有文档
echo   help                显示帮助信息
echo.
echo 示例:
echo   %0 update-toc                    # 更新所有目录
echo   %0 create-template new.md "新文档" # 创建模板
echo   %0 batch                         # 批量处理
