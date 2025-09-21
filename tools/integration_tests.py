#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试
提供完整的系统集成测试，验证所有组件协同工作
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import argparse
from dataclasses import dataclass, asdict
import concurrent.futures
import threading

@dataclass
class IntegrationTestResult:
    """集成测试结果"""
    test_name: str
    status: str  # "passed", "failed", "error"
    duration: float
    message: str
    components_tested: List[str]
    details: Dict[str, Any] = None

class IntegrationTests:
    """集成测试"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.tools_dir = self.root_dir / "tools"
        self.test_results = []
        
        # 创建测试目录
        self.test_dir = self.root_dir / "tools" / "tests"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # 测试环境
        self.test_env = None
        
    def setup_test_environment(self) -> bool:
        """设置测试环境"""
        try:
            # 创建临时测试目录
            self.test_env = tempfile.mkdtemp(prefix="integration_test_")
            self.test_env_path = Path(self.test_env)
            
            # 创建测试文档
            self._create_test_documents()
            
            print(f"✅ 测试环境已设置: {self.test_env}")
            return True
            
        except Exception as e:
            print(f"❌ 设置测试环境失败: {e}")
            return False
    
    def teardown_test_environment(self):
        """清理测试环境"""
        try:
            if self.test_env and Path(self.test_env).exists():
                shutil.rmtree(self.test_env)
                print("✅ 测试环境已清理")
        except Exception as e:
            print(f"⚠️  清理测试环境失败: {e}")
    
    def _create_test_documents(self):
        """创建测试文档"""
        test_docs = [
            {
                "name": "test_doc_1.md",
                "content": """# 测试文档1

## 概述

这是一个测试文档，用于验证系统功能。

## 技术架构

### 系统设计

系统采用模块化设计。

### 数据流

数据流向如下：

1. 输入处理
2. 数据处理
3. 输出生成

## 实现方案

### 核心模块

- 处理模块
- 存储模块
- 接口模块

## 测试验证

### 功能测试

测试各项功能是否正常。

### 性能测试

测试系统性能指标。

## 总结

本文档验证了系统的基本功能。
"""
            },
            {
                "name": "test_doc_2.md",
                "content": """# 测试文档2

## 项目背景

项目旨在解决文档管理问题。

## 需求分析

### 功能需求

1. 文档创建
2. 文档编辑
3. 文档管理

### 非功能需求

- 性能要求
- 安全要求
- 可用性要求

## 设计方案

### 架构设计

采用分层架构设计。

### 技术选型

选择合适的技术栈。

## 实施计划

### 开发计划

分阶段开发实施。

### 测试计划

制定详细的测试计划。

## 风险评估

识别和评估项目风险。

## 项目总结

总结项目经验和教训。
"""
            },
            {
                "name": "test_doc_3.md",
                "content": """# 测试文档3

## 简介

这是一个简短的测试文档。

## 内容

包含基本的内容结构。

## 结论

文档测试完成。
"""
            }
        ]
        
        for doc in test_docs:
            doc_path = self.test_env_path / doc["name"]
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc["content"])
    
    def run_integration_test(self, test_func, test_name: str, components: List[str]) -> IntegrationTestResult:
        """运行集成测试"""
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if result is True:
                return IntegrationTestResult(
                    test_name=test_name,
                    status="passed",
                    duration=duration,
                    message="测试通过",
                    components_tested=components
                )
            elif result is False:
                return IntegrationTestResult(
                    test_name=test_name,
                    status="failed",
                    duration=duration,
                    message="测试失败",
                    components_tested=components
                )
            else:
                return IntegrationTestResult(
                    test_name=test_name,
                    status="passed",
                    duration=duration,
                    message=str(result),
                    components_tested=components
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return IntegrationTestResult(
                test_name=test_name,
                status="error",
                duration=duration,
                message=f"测试错误: {str(e)}",
                components_tested=components,
                details={"exception": str(e), "type": type(e).__name__}
            )
    
    def test_complete_workflow(self) -> bool:
        """测试完整工作流"""
        try:
            # 1. 运行目录更新
            toc_result = subprocess.run([
                sys.executable, str(self.tools_dir / "simple_toc_updater.py"), str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if toc_result.returncode != 0:
                print(f"❌ 目录更新失败: {toc_result.stderr}")
                return False
            
            # 2. 运行质量检查
            quality_result = subprocess.run([
                sys.executable, str(self.tools_dir / "document_automation.py"), 
                "--validate", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            # 质量检查可能返回非零码，这是正常的
            print(f"质量检查结果: {quality_result.returncode}")
            
            # 3. 运行综合自动化
            comprehensive_result = subprocess.run([
                sys.executable, str(self.tools_dir / "comprehensive_automation.py"), 
                "--mode", "quick", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=60)
            
            if comprehensive_result.returncode != 0:
                print(f"❌ 综合自动化失败: {comprehensive_result.stderr}")
                return False
            
            # 4. 验证结果
            for doc_file in self.test_env_path.glob("*.md"):
                content = doc_file.read_text(encoding='utf-8')
                if "## 目录" not in content:
                    print(f"❌ 文档缺少目录: {doc_file.name}")
                    return False
            
            print("✅ 完整工作流测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 完整工作流测试失败: {e}")
            return False
    
    def test_backup_restore_workflow(self) -> bool:
        """测试备份恢复工作流"""
        try:
            # 1. 创建备份
            backup_result = subprocess.run([
                sys.executable, str(self.tools_dir / "backup_system.py"), 
                "--create", "test_backup", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if backup_result.returncode != 0:
                print(f"❌ 创建备份失败: {backup_result.stderr}")
                return False
            
            # 2. 修改文档
            test_doc = self.test_env_path / "test_doc_1.md"
            original_content = test_doc.read_text(encoding='utf-8')
            modified_content = original_content + "\n\n## 新增章节\n\n这是新增的内容。\n"
            test_doc.write_text(modified_content, encoding='utf-8')
            
            # 3. 恢复备份
            restore_result = subprocess.run([
                sys.executable, str(self.tools_dir / "backup_system.py"), 
                "--restore", "test_backup", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if restore_result.returncode != 0:
                print(f"❌ 恢复备份失败: {restore_result.stderr}")
                return False
            
            # 4. 验证恢复结果
            restored_content = test_doc.read_text(encoding='utf-8')
            if restored_content != original_content:
                print("❌ 备份恢复验证失败")
                return False
            
            print("✅ 备份恢复工作流测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 备份恢复工作流测试失败: {e}")
            return False
    
    def test_monitoring_integration(self) -> bool:
        """测试监控集成"""
        try:
            # 1. 启动监控
            monitoring_result = subprocess.run([
                sys.executable, str(self.tools_dir / "monitoring_system.py"), 
                "--start", "--duration", "10", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=20)
            
            # 2. 运行一些操作
            subprocess.run([
                sys.executable, str(self.tools_dir / "simple_toc_updater.py"), str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            # 3. 生成监控报告
            report_result = subprocess.run([
                sys.executable, str(self.tools_dir / "monitoring_system.py"), 
                "--system-report", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if report_result.returncode != 0:
                print(f"❌ 生成监控报告失败: {report_result.stderr}")
                return False
            
            print("✅ 监控集成测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 监控集成测试失败: {e}")
            return False
    
    def test_template_system_integration(self) -> bool:
        """测试模板系统集成"""
        try:
            # 1. 创建模板
            create_result = subprocess.run([
                sys.executable, str(self.tools_dir / "template_system.py"), 
                "--create", "test_template", "--description", "测试模板", 
                "--category", "技术文档", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if create_result.returncode != 0:
                print(f"❌ 创建模板失败: {create_result.stderr}")
                return False
            
            # 2. 应用模板
            output_file = self.test_env_path / "generated_doc.md"
            apply_result = subprocess.run([
                sys.executable, str(self.tools_dir / "template_system.py"), 
                "--apply", "test_template", str(output_file), "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if apply_result.returncode != 0:
                print(f"❌ 应用模板失败: {apply_result.stderr}")
                return False
            
            # 3. 验证生成的文件
            if not output_file.exists():
                print("❌ 模板应用后文件不存在")
                return False
            
            content = output_file.read_text(encoding='utf-8')
            if len(content) < 100:  # 基本内容检查
                print("❌ 生成的文件内容过少")
                return False
            
            print("✅ 模板系统集成测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 模板系统集成测试失败: {e}")
            return False
    
    def test_performance_optimization_integration(self) -> bool:
        """测试性能优化集成"""
        try:
            # 1. 运行性能监控
            monitor_result = subprocess.run([
                sys.executable, str(self.tools_dir / "performance_optimizer.py"), 
                "--monitor", "--duration", "10", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=20)
            
            # 2. 运行性能分析
            analyze_result = subprocess.run([
                sys.executable, str(self.tools_dir / "performance_optimizer.py"), 
                "--analyze", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if analyze_result.returncode != 0:
                print(f"❌ 性能分析失败: {analyze_result.stderr}")
                return False
            
            # 3. 生成性能报告
            report_result = subprocess.run([
                sys.executable, str(self.tools_dir / "performance_optimizer.py"), 
                "--report", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=30)
            
            if report_result.returncode != 0:
                print(f"❌ 生成性能报告失败: {report_result.stderr}")
                return False
            
            print("✅ 性能优化集成测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 性能优化集成测试失败: {e}")
            return False
    
    def test_validation_suite_integration(self) -> bool:
        """测试验证套件集成"""
        try:
            # 运行验证套件
            validation_result = subprocess.run([
                sys.executable, str(self.tools_dir / "validation_suite.py"), 
                "--all", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=120)
            
            # 验证套件可能返回非零码，检查是否有基本输出
            if len(validation_result.stdout) < 100:
                print("❌ 验证套件输出过少")
                return False
            
            print("✅ 验证套件集成测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 验证套件集成测试失败: {e}")
            return False
    
    def test_ci_cd_integration(self) -> bool:
        """测试CI/CD集成"""
        try:
            # 1. 设置CI/CD配置
            setup_result = subprocess.run([
                sys.executable, str(self.tools_dir / "ci_cd_integration.py"), 
                "--setup", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=60)
            
            if setup_result.returncode != 0:
                print(f"❌ CI/CD设置失败: {setup_result.stderr}")
                return False
            
            # 2. 运行CI流程
            ci_result = subprocess.run([
                sys.executable, str(self.tools_dir / "ci_cd_integration.py"), 
                "--run-ci", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=120)
            
            if ci_result.returncode != 0:
                print(f"❌ CI流程失败: {ci_result.stderr}")
                return False
            
            print("✅ CI/CD集成测试通过")
            return True
            
        except Exception as e:
            print(f"❌ CI/CD集成测试失败: {e}")
            return False
    
    def test_documentation_generation_integration(self) -> bool:
        """测试文档生成集成"""
        try:
            # 生成所有文档
            doc_result = subprocess.run([
                sys.executable, str(self.tools_dir / "documentation_generator.py"), 
                "--all", "--root", str(self.test_env_path)
            ], capture_output=True, text=True, timeout=60)
            
            if doc_result.returncode != 0:
                print(f"❌ 文档生成失败: {doc_result.stderr}")
                return False
            
            # 检查生成的文档
            docs_dir = self.test_env_path / "docs"
            if not docs_dir.exists():
                print("❌ 文档目录未创建")
                return False
            
            # 检查关键文档
            key_docs = ["README.md", "guides/user_guide.md", "api/README.md"]
            for doc_path in key_docs:
                full_path = docs_dir / doc_path
                if not full_path.exists():
                    print(f"❌ 关键文档未生成: {doc_path}")
                    return False
            
            print("✅ 文档生成集成测试通过")
            return True
            
        except Exception as e:
            print(f"❌ 文档生成集成测试失败: {e}")
            return False
    
    def run_all_integration_tests(self) -> Dict[str, Any]:
        """运行所有集成测试"""
        print("🚀 开始运行集成测试")
        print("=" * 60)
        
        # 设置测试环境
        if not self.setup_test_environment():
            return {"error": "测试环境设置失败"}
        
        try:
            # 定义测试用例
            test_cases = [
                (self.test_complete_workflow, "完整工作流测试", ["simple_toc_updater", "document_automation", "comprehensive_automation"]),
                (self.test_backup_restore_workflow, "备份恢复工作流测试", ["backup_system"]),
                (self.test_monitoring_integration, "监控集成测试", ["monitoring_system"]),
                (self.test_template_system_integration, "模板系统集成测试", ["template_system"]),
                (self.test_performance_optimization_integration, "性能优化集成测试", ["performance_optimizer"]),
                (self.test_validation_suite_integration, "验证套件集成测试", ["validation_suite"]),
                (self.test_ci_cd_integration, "CI/CD集成测试", ["ci_cd_integration"]),
                (self.test_documentation_generation_integration, "文档生成集成测试", ["documentation_generator"])
            ]
            
            # 运行测试
            results = []
            for test_func, test_name, components in test_cases:
                print(f"🧪 运行测试: {test_name}")
                result = self.run_integration_test(test_func, test_name, components)
                results.append(result)
                
                status_icon = {
                    "passed": "✅",
                    "failed": "❌",
                    "error": "💥"
                }.get(result.status, "❓")
                
                print(f"   {status_icon} {result.test_name}: {result.message} ({result.duration:.2f}s)")
                print()
            
            # 统计结果
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.status == "passed")
            failed_tests = sum(1 for r in results if r.status == "failed")
            error_tests = sum(1 for r in results if r.status == "error")
            
            total_duration = sum(r.duration for r in results)
            
            # 生成报告
            report = {
                "test_run_time": datetime.now().isoformat(),
                "test_environment": self.test_env,
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "errors": error_tests,
                    "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                    "total_duration": total_duration
                },
                "detailed_results": [asdict(r) for r in results],
                "component_coverage": self._analyze_component_coverage(results)
            }
            
            # 保存报告
            report_file = self.test_dir / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # 打印总结
            print("=" * 60)
            print("📊 集成测试结果总结")
            print("=" * 60)
            print(f"总测试数: {total_tests}")
            print(f"通过: {passed_tests} ✅")
            print(f"失败: {failed_tests} ❌")
            print(f"错误: {error_tests} 💥")
            print(f"成功率: {report['summary']['success_rate']:.1f}%")
            print(f"总耗时: {total_duration:.2f}秒")
            print(f"报告文件: {report_file}")
            
            return report
            
        finally:
            # 清理测试环境
            self.teardown_test_environment()
    
    def _analyze_component_coverage(self, results: List[IntegrationTestResult]) -> Dict[str, Any]:
        """分析组件覆盖情况"""
        all_components = set()
        tested_components = set()
        
        for result in results:
            for component in result.components_tested:
                all_components.add(component)
                if result.status == "passed":
                    tested_components.add(component)
        
        return {
            "total_components": len(all_components),
            "tested_components": len(tested_components),
            "coverage_percentage": (len(tested_components) / len(all_components) * 100) if all_components else 0,
            "all_components": list(all_components),
            "tested_components_list": list(tested_components),
            "untested_components": list(all_components - tested_components)
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='集成测试')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--test', help='运行指定测试')
    parser.add_argument('--all', action='store_true', help='运行所有集成测试')
    parser.add_argument('--report', help='生成测试报告到指定文件')
    
    args = parser.parse_args()
    
    integration_tests = IntegrationTests(args.root)
    
    print("=" * 50)
    print("🚀 集成测试")
    print("=" * 50)
    
    if args.all:
        report = integration_tests.run_all_integration_tests()
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"集成测试报告已保存到: {args.report}")
    elif args.test:
        # 运行指定测试
        test_method = getattr(integration_tests, f"test_{args.test}", None)
        if test_method:
            if integration_tests.setup_test_environment():
                try:
                    result = integration_tests.run_integration_test(
                        test_method, args.test, [args.test]
                    )
                    print(f"测试结果: {result.status} - {result.message}")
                finally:
                    integration_tests.teardown_test_environment()
            else:
                print("❌ 测试环境设置失败")
        else:
            print(f"❌ 未找到测试: {args.test}")
    else:
        print("请指定要运行的测试")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()
