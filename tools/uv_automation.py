#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UV集成自动化工具
利用已安装的uv环境进行文档自动化管理
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

class UVAutomation:
    """UV集成自动化工具"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.uv_available = self.check_uv_availability()
        
    def check_uv_availability(self) -> bool:
        """检查uv是否可用"""
        try:
            result = subprocess.run(['uv', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ 检测到uv: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("⚠️  uv不可用，将使用系统Python")
        return False
    
    def create_uv_project(self) -> bool:
        """创建uv项目配置"""
        try:
            # 创建pyproject.toml
            pyproject_content = '''[project]
name = "document-automation"
version = "1.0.0"
description = "文档自动化管理工具"
requires-python = ">=3.8"
dependencies = [
    "pyyaml>=6.0",
    "markdown>=3.4",
]

[project.scripts]
doc-auto = "tools.document_automation:main"
toc-update = "tools.simple_toc_updater:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.0",
    "black>=23.0",
    "flake8>=6.0",
]
'''
            
            pyproject_path = self.root_dir / "pyproject.toml"
            with open(pyproject_path, 'w', encoding='utf-8') as f:
                f.write(pyproject_content)
            
            print("✅ 已创建pyproject.toml")
            return True
            
        except Exception as e:
            print(f"❌ 创建uv项目失败: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """安装依赖"""
        if not self.uv_available:
            print("⚠️  uv不可用，跳过依赖安装")
            return True
        
        try:
            print("📦 安装依赖...")
            result = subprocess.run(['uv', 'sync'], 
                                  cwd=self.root_dir,
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ 依赖安装完成")
                return True
            else:
                print(f"❌ 依赖安装失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 依赖安装超时")
            return False
        except Exception as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    
    def run_with_uv(self, script: str, args: List[str] = None) -> bool:
        """使用uv运行脚本"""
        if not self.uv_available:
            # 回退到系统Python
            return self.run_with_python(script, args)
        
        try:
            cmd = ['uv', 'run', 'python', script]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(cmd, cwd=self.root_dir, 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ 执行失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 执行超时")
            return False
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            return False
    
    def run_with_python(self, script: str, args: List[str] = None) -> bool:
        """使用系统Python运行脚本"""
        try:
            cmd = [sys.executable, script]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(cmd, cwd=self.root_dir,
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ 执行失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            return False
    
    def update_toc_all(self) -> bool:
        """更新所有文档的目录"""
        print("📝 更新所有文档的目录...")
        return self.run_with_uv("tools/simple_toc_updater.py", ["."])
    
    def create_toc_missing(self) -> bool:
        """为没有目录的文档创建目录"""
        print("📝 为没有目录的文档创建目录...")
        return self.run_with_uv("tools/auto_toc_generator.py", 
                               ["--root", ".", "--all", "--create"])
    
    def batch_process(self) -> bool:
        """批量处理所有文档"""
        print("📝 批量处理所有文档...")
        
        # 步骤1: 更新现有目录
        print("步骤1: 更新现有目录...")
        if not self.run_with_uv("tools/auto_toc_generator.py", 
                               ["--root", ".", "--all", "--update"]):
            print("⚠️  更新目录失败，继续执行...")
        
        # 步骤2: 创建缺失的目录
        print("步骤2: 创建缺失的目录...")
        if not self.create_toc_missing():
            print("⚠️  创建目录失败，继续执行...")
        
        # 步骤3: 生成报告
        print("步骤3: 生成处理报告...")
        return self.run_with_uv("tools/simple_toc_updater.py", ["."])
    
    def setup_project(self) -> bool:
        """设置项目"""
        print("🚀 设置文档自动化项目...")
        
        # 创建uv项目配置
        if not self.create_uv_project():
            return False
        
        # 安装依赖
        if not self.install_dependencies():
            return False
        
        print("✅ 项目设置完成！")
        return True

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UV集成文档自动化工具')
    parser.add_argument('action', choices=[
        'setup', 'update-toc', 'create-toc', 'batch', 'simple'
    ], help='执行的操作')
    parser.add_argument('--root', default='.', help='根目录路径')
    
    args = parser.parse_args()
    
    automation = UVAutomation(args.root)
    
    print("=" * 50)
    print("🚀 UV集成文档自动化工具")
    print("=" * 50)
    
    if args.action == 'setup':
        success = automation.setup_project()
    elif args.action == 'update-toc':
        success = automation.update_toc_all()
    elif args.action == 'create-toc':
        success = automation.create_toc_missing()
    elif args.action == 'batch':
        success = automation.batch_process()
    elif args.action == 'simple':
        success = automation.run_with_uv("tools/simple_toc_updater.py", ["."])
    else:
        print(f"❌ 未知操作: {args.action}")
        success = False
    
    print("=" * 50)
    if success:
        print("✅ 操作完成！")
    else:
        print("❌ 操作失败！")
    print("=" * 50)

if __name__ == "__main__":
    main()
