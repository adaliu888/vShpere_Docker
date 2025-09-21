#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合自动化管理系统
整合所有文档自动化功能，提供一站式解决方案
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import argparse

class ComprehensiveAutomation:
    """综合自动化管理系统"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.tools_dir = self.root_dir / "tools"
        self.uv_available = self.check_uv_availability()
        self.python_available = self.check_python_availability()
        
    def check_uv_availability(self) -> bool:
        """检查uv是否可用"""
        try:
            result = subprocess.run(['uv', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def check_python_availability(self) -> bool:
        """检查Python是否可用"""
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def run_command(self, cmd: List[str], description: str = "") -> bool:
        """运行命令"""
        if description:
            print(f"🔄 {description}...")
        
        try:
            result = subprocess.run(cmd, cwd=self.root_dir, 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    print(result.stdout)
                if description:
                    print(f"✅ {description}完成")
                return True
            else:
                print(f"❌ {description}失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ {description}超时")
            return False
        except Exception as e:
            print(f"❌ {description}失败: {e}")
            return False
    
    def run_python_script(self, script: str, args: List[str] = None) -> bool:
        """运行Python脚本"""
        if args is None:
            args = []
        
        if self.uv_available:
            cmd = ['uv', 'run', 'python', script] + args
        else:
            cmd = [sys.executable, script] + args
        
        return self.run_command(cmd, f"运行 {script}")
    
    def update_all_toc(self) -> bool:
        """更新所有文档的目录"""
        print("📝 更新所有文档的目录...")
        return self.run_python_script("tools/simple_toc_updater.py", ["."])
    
    def validate_documents(self) -> bool:
        """验证文档质量"""
        print("🔍 验证文档质量...")
        return self.run_python_script("tools/document_automation.py", 
                                     ["--root", ".", "--validate"])
    
    def generate_quality_report(self) -> bool:
        """生成质量报告"""
        print("📊 生成质量报告...")
        return self.run_python_script("tools/document_automation.py", 
                                     ["--root", ".", "--report"])
    
    def fix_format_issues(self, file_path: str = None) -> bool:
        """修复格式问题"""
        if file_path:
            print(f"🔧 修复文档格式: {file_path}")
            return self.run_python_script("tools/document_automation.py", 
                                         ["--root", ".", "--fix", file_path])
        else:
            print("🔧 批量修复格式问题...")
            # 这里可以实现批量修复逻辑
            return True
    
    def create_document_template(self, file_path: str, title: str) -> bool:
        """创建文档模板"""
        print(f"📄 创建文档模板: {file_path}")
        return self.run_python_script("tools/document_automation.py", 
                                     ["--root", ".", "--template", file_path, title])
    
    def setup_project(self) -> bool:
        """设置项目"""
        print("🚀 设置文档自动化项目...")
        
        # 创建必要的目录
        directories = [
            "tools/reports",
            "tools/backups",
            "tools/logs"
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {dir_path}")
        
        # 如果uv可用，设置uv项目
        if self.uv_available:
            return self.run_python_script("tools/uv_automation.py", ["setup"])
        else:
            print("⚠️  uv不可用，跳过uv项目设置")
            return True
    
    def full_automation(self) -> bool:
        """完整自动化流程"""
        print("🚀 启动完整自动化流程...")
        print("=" * 50)
        
        steps = [
            ("更新目录", self.update_all_toc),
            ("验证文档", self.validate_documents),
            ("生成报告", self.generate_quality_report),
        ]
        
        success_count = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            print(f"\n📋 步骤 {success_count + 1}/{total_steps}: {step_name}")
            if step_func():
                success_count += 1
            else:
                print(f"⚠️  {step_name}失败，继续执行...")
        
        print("\n" + "=" * 50)
        print(f"📊 自动化流程完成: {success_count}/{total_steps} 步骤成功")
        
        if success_count == total_steps:
            print("🎉 所有步骤都成功完成！")
            return True
        else:
            print("⚠️  部分步骤失败，请检查日志")
            return False
    
    def quick_update(self) -> bool:
        """快速更新（仅更新目录）"""
        print("⚡ 快速更新模式...")
        return self.update_all_toc()
    
    def maintenance_mode(self) -> bool:
        """维护模式（完整检查）"""
        print("🔧 维护模式...")
        return self.full_automation()
    
    def show_status(self) -> None:
        """显示系统状态"""
        print("📊 系统状态:")
        print(f"  - UV可用: {'✅' if self.uv_available else '❌'}")
        print(f"  - Python可用: {'✅' if self.python_available else '❌'}")
        print(f"  - 工作目录: {self.root_dir}")
        print(f"  - 工具目录: {self.tools_dir}")
        
        # 检查工具文件
        tools = [
            "simple_toc_updater.py",
            "document_automation.py",
            "uv_automation.py",
            "doc_config.yaml"
        ]
        
        print("\n🔧 工具状态:")
        for tool in tools:
            tool_path = self.tools_dir / tool
            status = "✅" if tool_path.exists() else "❌"
            print(f"  - {tool}: {status}")
    
    def interactive_mode(self) -> None:
        """交互模式"""
        print("🎯 交互模式")
        print("=" * 30)
        
        while True:
            print("\n请选择操作:")
            print("1. 快速更新目录")
            print("2. 完整自动化流程")
            print("3. 验证文档质量")
            print("4. 生成质量报告")
            print("5. 修复格式问题")
            print("6. 创建文档模板")
            print("7. 显示系统状态")
            print("8. 设置项目")
            print("0. 退出")
            
            try:
                choice = input("\n请输入选择 (0-8): ").strip()
                
                if choice == "0":
                    print("👋 再见！")
                    break
                elif choice == "1":
                    self.quick_update()
                elif choice == "2":
                    self.full_automation()
                elif choice == "3":
                    self.validate_documents()
                elif choice == "4":
                    self.generate_quality_report()
                elif choice == "5":
                    file_path = input("请输入文件路径 (回车跳过): ").strip()
                    self.fix_format_issues(file_path if file_path else None)
                elif choice == "6":
                    file_path = input("请输入文件路径: ").strip()
                    title = input("请输入文档标题: ").strip()
                    if file_path and title:
                        self.create_document_template(file_path, title)
                elif choice == "7":
                    self.show_status()
                elif choice == "8":
                    self.setup_project()
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='综合自动化管理系统')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--mode', choices=[
        'quick', 'full', 'maintenance', 'interactive', 'status'
    ], default='interactive', help='运行模式')
    parser.add_argument('--setup', action='store_true', help='设置项目')
    
    args = parser.parse_args()
    
    automation = ComprehensiveAutomation(args.root)
    
    print("=" * 50)
    print("🚀 综合自动化管理系统")
    print("=" * 50)
    
    if args.setup:
        automation.setup_project()
    elif args.mode == 'quick':
        automation.quick_update()
    elif args.mode == 'full':
        automation.full_automation()
    elif args.mode == 'maintenance':
        automation.maintenance_mode()
    elif args.mode == 'status':
        automation.show_status()
    elif args.mode == 'interactive':
        automation.interactive_mode()
    else:
        print("❌ 未知模式")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
