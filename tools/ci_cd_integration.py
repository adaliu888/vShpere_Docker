#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD集成脚本
提供持续集成和持续部署的自动化功能
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import argparse

class CICDIntegration:
    """CI/CD集成管理"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.github_dir = self.root_dir / ".github"
        self.workflows_dir = self.github_dir / "workflows"
        
    def create_github_workflow(self, workflow_name: str, workflow_config: Dict[str, Any]) -> bool:
        """创建GitHub工作流"""
        try:
            # 确保目录存在
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成工作流文件
            workflow_content = self.generate_workflow_yaml(workflow_config)
            
            # 写入文件
            workflow_path = self.workflows_dir / f"{workflow_name}.yml"
            with open(workflow_path, 'w', encoding='utf-8') as f:
                f.write(workflow_content)
            
            print(f"✅ 已创建GitHub工作流: {workflow_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建GitHub工作流失败: {e}")
            return False
    
    def generate_workflow_yaml(self, config: Dict[str, Any]) -> str:
        """生成工作流YAML内容"""
        workflow_template = f'''name: {config.get('name', '文档自动化')}

on:
  push:
    branches: {config.get('branches', ['main', 'develop'])}
    paths:
      - '**/*.md'
      - 'tools/**'
  pull_request:
    branches: {config.get('branches', ['main'])}
    paths:
      - '**/*.md'
      - 'tools/**'
  schedule:
    - cron: '{config.get('schedule', '0 2 * * *')}'

jobs:
  document-validation:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v4
      
    - name: 设置Python
      uses: actions/setup-python@v4
      with:
        python-version: '{config.get('python_version', '3.9')}'
        
    - name: 安装UV
      uses: astral-sh/setup-uv@v2
      with:
        version: "latest"
        
    - name: 安装依赖
      run: |
        uv sync
        
    - name: 验证文档质量
      run: |
        uv run python tools/document_automation.py --validate
        
    - name: 生成质量报告
      run: |
        uv run python tools/document_automation.py --report
        
    - name: 更新文档目录
      run: |
        uv run python tools/simple_toc_updater.py .
        
    - name: 上传质量报告
      uses: actions/upload-artifact@v3
      with:
        name: quality-report
        path: tools/quality_report.md
'''
        return workflow_template
    
    def create_git_hooks(self) -> bool:
        """创建Git钩子"""
        try:
            git_hooks_dir = self.root_dir / ".git" / "hooks"
            if not git_hooks_dir.exists():
                print("⚠️  Git仓库未初始化，跳过钩子创建")
                return False
            
            # 创建pre-commit钩子
            pre_commit_content = '''#!/bin/bash
# 文档自动化管理 - Pre-commit钩子

echo "🔍 检查文档格式..."

# 检查是否有Markdown文件变更
if git diff --cached --name-only | grep -q '\\.md$'; then
    echo "📝 发现Markdown文件变更，运行格式检查..."
    
    # 运行格式检查
    if command -v uv &> /dev/null; then
        uv run python tools/document_automation.py --validate
    else
        python tools/document_automation.py --validate
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ 文档格式检查失败，请修复后重试"
        exit 1
    fi
    
    echo "✅ 文档格式检查通过"
fi

echo "✅ Pre-commit检查完成"
'''
            
            pre_commit_path = git_hooks_dir / "pre-commit"
            with open(pre_commit_path, 'w', encoding='utf-8') as f:
                f.write(pre_commit_content)
            pre_commit_path.chmod(0o755)
            
            # 创建post-commit钩子
            post_commit_content = '''#!/bin/bash
# 文档自动化管理 - Post-commit钩子

echo "🔄 自动更新文档目录..."

# 检查是否有Markdown文件变更
if git diff HEAD~1 --name-only | grep -q '\\.md$'; then
    echo "📝 发现Markdown文件变更，自动更新目录..."
    
    # 运行目录更新
    if command -v uv &> /dev/null; then
        uv run python tools/simple_toc_updater.py .
    else
        python tools/simple_toc_updater.py .
    fi
    
    # 检查是否有目录更新
    if [ -n "$(git status --porcelain)" ]; then
        echo "📝 目录已更新，自动提交..."
        git add .
        git commit -m "自动更新文档目录 [skip ci]"
    fi
fi

echo "✅ Post-commit处理完成"
'''
            
            post_commit_path = git_hooks_dir / "post-commit"
            with open(post_commit_path, 'w', encoding='utf-8') as f:
                f.write(post_commit_content)
            post_commit_path.chmod(0o755)
            
            print("✅ Git钩子创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建Git钩子失败: {e}")
            return False
    
    def create_dockerfile(self) -> bool:
        """创建Dockerfile"""
        try:
            dockerfile_content = '''# 文档自动化管理 - Docker镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# 安装UV
RUN pip install uv

# 复制项目文件
COPY . .

# 安装Python依赖
RUN uv sync

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 创建非root用户
RUN useradd -m -u 1000 docuser && chown -R docuser:docuser /app
USER docuser

# 默认命令
CMD ["uv", "run", "python", "tools/comprehensive_automation.py", "--mode", "interactive"]
'''
            
            dockerfile_path = self.root_dir / "Dockerfile"
            with open(dockerfile_path, 'w', encoding='utf-8') as f:
                f.write(dockerfile_content)
            
            print("✅ Dockerfile创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建Dockerfile失败: {e}")
            return False
    
    def create_docker_compose(self) -> bool:
        """创建docker-compose.yml"""
        try:
            compose_content = '''version: '3.8'

services:
  document-automation:
    build: .
    volumes:
      - .:/app
      - ./tools/reports:/app/tools/reports
      - ./tools/backups:/app/tools/backups
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    command: ["uv", "run", "python", "tools/comprehensive_automation.py", "--mode", "interactive"]
    
  document-validator:
    build: .
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    command: ["uv", "run", "python", "tools/document_automation.py", "--validate"]
    
  toc-updater:
    build: .
    volumes:
      - .:/app
    environment:
      - PYTHONPATH=/app
      - PYTHONUNBUFFERED=1
    command: ["uv", "run", "python", "tools/simple_toc_updater.py", "."]
'''
            
            compose_path = self.root_dir / "docker-compose.yml"
            with open(compose_path, 'w', encoding='utf-8') as f:
                f.write(compose_content)
            
            print("✅ docker-compose.yml创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建docker-compose.yml失败: {e}")
            return False
    
    def create_makefile(self) -> bool:
        """创建Makefile"""
        try:
            makefile_content = '''# 文档自动化管理 - Makefile

.PHONY: help setup test validate update-toc clean docker-build docker-run

help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

setup: ## 设置项目环境
	uv sync

test: ## 运行测试
	uv run python tools/comprehensive_automation.py --mode status

validate: ## 验证文档质量
	uv run python tools/document_automation.py --validate

update-toc: ## 更新所有文档目录
	uv run python tools/simple_toc_updater.py .

report: ## 生成质量报告
	uv run python tools/document_automation.py --report

clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf tools/reports/*.md
	rm -rf tools/backups/*
	rm -rf tools/logs/*

docker-build: ## 构建Docker镜像
	docker build -t document-automation .

docker-run: ## 运行Docker容器
	docker run -it --rm -v $(PWD):/app document-automation

docker-compose-up: ## 启动Docker Compose服务
	docker-compose up

docker-compose-down: ## 停止Docker Compose服务
	docker-compose down

ci: validate update-toc report ## 运行CI流程

dev: setup test ## 开发环境设置
'''
            
            makefile_path = self.root_dir / "Makefile"
            with open(makefile_path, 'w', encoding='utf-8') as f:
                f.write(makefile_content)
            
            print("✅ Makefile创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建Makefile失败: {e}")
            return False
    
    def create_ci_config(self) -> bool:
        """创建CI配置文件"""
        try:
            # 创建GitHub Actions工作流
            workflow_config = {
                'name': '文档自动化管理',
                'branches': ['main', 'develop'],
                'python_version': '3.9',
                'schedule': '0 2 * * *'
            }
            
            if not self.create_github_workflow('document-automation', workflow_config):
                return False
            
            # 创建Git钩子
            if not self.create_git_hooks():
                print("⚠️  Git钩子创建失败，但继续执行")
            
            # 创建Docker文件
            if not self.create_dockerfile():
                return False
            
            if not self.create_docker_compose():
                return False
            
            # 创建Makefile
            if not self.create_makefile():
                return False
            
            print("✅ CI/CD配置创建完成")
            return True
            
        except Exception as e:
            print(f"❌ 创建CI配置失败: {e}")
            return False
    
    def run_ci_pipeline(self) -> bool:
        """运行CI流水线"""
        print("🚀 运行CI流水线...")
        
        steps = [
            ("验证文档质量", ["uv", "run", "python", "tools/document_automation.py", "--validate"]),
            ("更新文档目录", ["uv", "run", "python", "tools/simple_toc_updater.py", "."]),
            ("生成质量报告", ["uv", "run", "python", "tools/document_automation.py", "--report"])
        ]
        
        for step_name, cmd in steps:
            print(f"🔄 {step_name}...")
            try:
                result = subprocess.run(cmd, cwd=self.root_dir, 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"✅ {step_name}完成")
                else:
                    print(f"❌ {step_name}失败: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ {step_name}失败: {e}")
                return False
        
        print("✅ CI流水线完成")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CI/CD集成管理')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--setup', action='store_true', help='设置CI/CD配置')
    parser.add_argument('--run-ci', action='store_true', help='运行CI流水线')
    
    args = parser.parse_args()
    
    cicd = CICDIntegration(args.root)
    
    print("=" * 50)
    print("🚀 CI/CD集成管理")
    print("=" * 50)
    
    if args.setup:
        if cicd.create_ci_config():
            print("✅ CI/CD配置设置完成")
        else:
            print("❌ CI/CD配置设置失败")
            return 1
    elif args.run_ci:
        if cicd.run_ci_pipeline():
            print("✅ CI流水线运行完成")
        else:
            print("❌ CI流水线运行失败")
            return 1
    else:
        print("请指定操作: --setup 或 --run-ci")
        print("使用 --help 查看详细帮助")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
