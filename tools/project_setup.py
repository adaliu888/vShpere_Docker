#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目初始化设置脚本
自动设置文档自动化管理项目的完整环境
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import argparse

class ProjectSetup:
    """项目初始化设置"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.tools_dir = self.root_dir / "tools"
        self.setup_log = []
        
    def log(self, message: str, level: str = "INFO") -> None:
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.setup_log.append(log_entry)
        print(log_entry)
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """检查前置条件"""
        self.log("检查前置条件...")
        
        checks = {
            "python": False,
            "uv": False,
            "git": False,
            "tools_dir": False
        }
        
        # 检查Python
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                checks["python"] = True
                self.log(f"Python版本: {result.stdout.strip()}")
        except Exception as e:
            self.log(f"Python检查失败: {e}", "ERROR")
        
        # 检查uv
        try:
            result = subprocess.run(['uv', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                checks["uv"] = True
                self.log(f"UV版本: {result.stdout.strip()}")
        except Exception as e:
            self.log(f"UV检查失败: {e}", "WARN")
        
        # 检查Git
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                checks["git"] = True
                self.log(f"Git版本: {result.stdout.strip()}")
        except Exception as e:
            self.log(f"Git检查失败: {e}", "WARN")
        
        # 检查工具目录
        if self.tools_dir.exists():
            checks["tools_dir"] = True
            self.log("工具目录存在")
        else:
            self.log("工具目录不存在，将创建", "WARN")
        
        return checks
    
    def create_directories(self) -> bool:
        """创建必要的目录结构"""
        self.log("创建目录结构...")
        
        directories = [
            "tools",
            "tools/reports",
            "tools/backups",
            "tools/logs",
            "tools/templates",
            "tools/tests",
            "docs",
            "docs/guides",
            "docs/examples"
        ]
        
        for dir_path in directories:
            full_path = self.root_dir / dir_path
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                self.log(f"创建目录: {dir_path}")
            except Exception as e:
                self.log(f"创建目录失败 {dir_path}: {e}", "ERROR")
                return False
        
        return True
    
    def create_pyproject_toml(self) -> bool:
        """创建pyproject.toml文件"""
        self.log("创建pyproject.toml...")
        
        pyproject_content = '''[project]
name = "document-automation"
version = "1.0.0"
description = "文档自动化管理工具"
requires-python = ">=3.8"
dependencies = [
    "pyyaml>=6.0",
    "markdown>=3.4",
    "click>=8.0",
]

[project.scripts]
doc-auto = "tools.document_automation:main"
toc-update = "tools.simple_toc_updater:main"
project-setup = "tools.project_setup:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "black>=23.0",
    "flake8>=6.0",
    "mypy>=1.0",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''
        
        try:
            pyproject_path = self.root_dir / "pyproject.toml"
            with open(pyproject_path, 'w', encoding='utf-8') as f:
                f.write(pyproject_content)
            self.log("pyproject.toml创建成功")
            return True
        except Exception as e:
            self.log(f"pyproject.toml创建失败: {e}", "ERROR")
            return False
    
    def create_gitignore(self) -> bool:
        """创建.gitignore文件"""
        self.log("创建.gitignore...")
        
        gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
tools/reports/*.md
tools/backups/*
tools/logs/*
!tools/reports/.gitkeep
!tools/backups/.gitkeep
!tools/logs/.gitkeep

# Temporary files
*.tmp
*.temp
*.log
'''
        
        try:
            gitignore_path = self.root_dir / ".gitignore"
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            self.log(".gitignore创建成功")
            return True
        except Exception as e:
            self.log(f".gitignore创建失败: {e}", "ERROR")
            return False
    
    def create_readme(self) -> bool:
        """创建README.md文件"""
        self.log("创建README.md...")
        
        readme_content = f'''# 文档自动化管理系统

## 项目概述

本项目提供了一套完整的文档自动化管理工具，解决文档目录手工修改、质量检查、格式修复等问题。

## 快速开始

### 1. 环境要求

- Python 3.8+
- UV (推荐) 或 pip
- Git (可选)

### 2. 安装依赖

```bash
# 使用UV (推荐)
uv sync

# 或使用pip
pip install -r requirements.txt
```

### 3. 快速使用

```bash
# 更新所有文档目录
uv run python tools/simple_toc_updater.py .

# 或使用批处理脚本
tools\\run_automation.bat simple
```

## 主要功能

- ✅ **目录自动生成**: 自动提取标题并生成目录
- ✅ **批量处理**: 一次处理所有文档
- ✅ **质量检查**: 自动检查文档结构和格式
- ✅ **格式修复**: 自动修复常见格式问题
- ✅ **报告生成**: 生成详细的处理报告

## 工具说明

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| simple_toc_updater.py | 目录更新 | 日常使用 |
| document_automation.py | 质量检查 | 质量保证 |
| comprehensive_automation.py | 综合管理 | 完整流程 |

## 配置说明

配置文件: `tools/doc_config.yaml`

主要配置项:
- `required_sections`: 必需章节列表
- `min_sections`: 最小章节数量
- `min_code_examples`: 最小代码示例数量

## 使用指南

详细使用指南请参考: [自动化工具使用指南_2025.md](自动化工具使用指南_2025.md)

## 项目状态

- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **版本**: v1.0
- **状态**: 活跃开发中

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License
'''
        
        try:
            readme_path = self.root_dir / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            self.log("README.md创建成功")
            return True
        except Exception as e:
            self.log(f"README.md创建失败: {e}", "ERROR")
            return False
    
    def create_requirements_txt(self) -> bool:
        """创建requirements.txt文件"""
        self.log("创建requirements.txt...")
        
        requirements_content = '''# 核心依赖
pyyaml>=6.0
markdown>=3.4
click>=8.0

# 开发依赖
pytest>=7.0
black>=23.0
flake8>=6.0
mypy>=1.0
'''
        
        try:
            requirements_path = self.root_dir / "requirements.txt"
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            self.log("requirements.txt创建成功")
            return True
        except Exception as e:
            self.log(f"requirements.txt创建失败: {e}", "ERROR")
            return False
    
    def create_keep_files(self) -> bool:
        """创建.gitkeep文件"""
        self.log("创建.gitkeep文件...")
        
        keep_dirs = [
            "tools/reports",
            "tools/backups", 
            "tools/logs"
        ]
        
        for dir_path in keep_dirs:
            keep_file = self.root_dir / dir_path / ".gitkeep"
            try:
                keep_file.touch()
                self.log(f"创建.gitkeep: {dir_path}")
            except Exception as e:
                self.log(f"创建.gitkeep失败 {dir_path}: {e}", "ERROR")
                return False
        
        return True
    
    def install_dependencies(self) -> bool:
        """安装依赖"""
        self.log("安装依赖...")
        
        # 检查是否有uv
        try:
            result = subprocess.run(['uv', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # 使用uv安装
                self.log("使用UV安装依赖...")
                result = subprocess.run(['uv', 'sync'], 
                                      cwd=self.root_dir,
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    self.log("UV依赖安装成功")
                    return True
                else:
                    self.log(f"UV依赖安装失败: {result.stderr}", "ERROR")
        except Exception:
            pass
        
        # 回退到pip
        self.log("使用pip安装依赖...")
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                                  cwd=self.root_dir,
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.log("pip依赖安装成功")
                return True
            else:
                self.log(f"pip依赖安装失败: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"pip安装失败: {e}", "ERROR")
            return False
    
    def run_initial_test(self) -> bool:
        """运行初始测试"""
        self.log("运行初始测试...")
        
        try:
            # 测试简单工具
            result = subprocess.run([sys.executable, 'tools/simple_toc_updater.py', '--help'], 
                                  cwd=self.root_dir,
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log("简单工具测试通过")
            else:
                self.log(f"简单工具测试失败: {result.stderr}", "ERROR")
                return False
            
            # 测试综合工具
            result = subprocess.run([sys.executable, 'tools/comprehensive_automation.py', '--mode', 'status'], 
                                  cwd=self.root_dir,
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.log("综合工具测试通过")
            else:
                self.log(f"综合工具测试失败: {result.stderr}", "ERROR")
                return False
            
            return True
        except Exception as e:
            self.log(f"初始测试失败: {e}", "ERROR")
            return False
    
    def generate_setup_report(self) -> str:
        """生成设置报告"""
        report_lines = [
            "# 项目设置报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 设置日志",
            ""
        ]
        
        for log_entry in self.setup_log:
            report_lines.append(f"- {log_entry}")
        
        report_lines.extend([
            "",
            "## 下一步",
            "",
            "1. 运行快速测试:",
            "   ```bash",
            "   uv run python tools/simple_toc_updater.py .",
            "   ```",
            "",
            "2. 查看系统状态:",
            "   ```bash",
            "   uv run python tools/comprehensive_automation.py --mode status",
            "   ```",
            "",
            "3. 开始使用:",
            "   ```bash",
            "   uv run python tools/comprehensive_automation.py",
            "   ```",
            "",
            "## 文件结构",
            "",
            "```",
            ".",
            "├── tools/",
            "│   ├── simple_toc_updater.py",
            "│   ├── document_automation.py",
            "│   ├── comprehensive_automation.py",
            "│   ├── doc_config.yaml",
            "│   ├── reports/",
            "│   ├── backups/",
            "│   └── logs/",
            "├── docs/",
            "├── pyproject.toml",
            "├── requirements.txt",
            "├── .gitignore",
            "└── README.md",
            "```"
        ])
        
        return "\n".join(report_lines)
    
    def setup_project(self) -> bool:
        """设置项目"""
        self.log("开始项目设置...")
        
        # 检查前置条件
        checks = self.check_prerequisites()
        if not checks["python"]:
            self.log("Python不可用，无法继续", "ERROR")
            return False
        
        # 创建目录结构
        if not self.create_directories():
            return False
        
        # 创建配置文件
        if not self.create_pyproject_toml():
            return False
        
        if not self.create_gitignore():
            return False
        
        if not self.create_readme():
            return False
        
        if not self.create_requirements_txt():
            return False
        
        if not self.create_keep_files():
            return False
        
        # 安装依赖
        if not self.install_dependencies():
            self.log("依赖安装失败，但项目结构已创建", "WARN")
        
        # 运行初始测试
        if not self.run_initial_test():
            self.log("初始测试失败，但项目结构已创建", "WARN")
        
        # 生成设置报告
        report = self.generate_setup_report()
        report_path = self.tools_dir / "setup_report.md"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            self.log(f"设置报告已生成: {report_path}")
        except Exception as e:
            self.log(f"设置报告生成失败: {e}", "ERROR")
        
        self.log("项目设置完成！")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='项目初始化设置')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--skip-deps', action='store_true', help='跳过依赖安装')
    
    args = parser.parse_args()
    
    setup = ProjectSetup(args.root)
    
    print("=" * 50)
    print("🚀 项目初始化设置")
    print("=" * 50)
    
    if setup.setup_project():
        print("\n✅ 项目设置成功！")
        print("\n📋 下一步:")
        print("1. 运行快速测试:")
        print("   uv run python tools/simple_toc_updater.py .")
        print("2. 查看系统状态:")
        print("   uv run python tools/comprehensive_automation.py --mode status")
        print("3. 开始使用:")
        print("   uv run python tools/comprehensive_automation.py")
    else:
        print("\n❌ 项目设置失败！")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
