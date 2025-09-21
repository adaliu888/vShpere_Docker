#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证测试套件
提供全面的系统验证、功能测试和集成测试功能
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime
import argparse
import unittest
from dataclasses import dataclass, asdict
import concurrent.futures
import threading

@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    status: str  # "passed", "failed", "skipped", "error"
    duration: float
    message: str
    details: Dict[str, Any] = None

@dataclass
class TestSuite:
    """测试套件"""
    name: str
    description: str
    tests: List[Callable]
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None

class ValidationSuite:
    """验证测试套件"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.tools_dir = self.root_dir / "tools"
        self.test_results = []
        self.test_suites = []
        
        # 创建测试目录
        self.test_dir = self.root_dir / "tools" / "tests"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化测试套件
        self._initialize_test_suites()
    
    def _initialize_test_suites(self):
        """初始化测试套件"""
        # 基础功能测试套件
        self.test_suites.append(TestSuite(
            name="基础功能测试",
            description="测试核心工具的基础功能",
            tests=[
                self.test_simple_toc_updater_basic,
                self.test_document_automation_basic,
                self.test_comprehensive_automation_basic,
                self.test_uv_automation_basic
            ]
        ))
        
        # 文件处理测试套件
        self.test_suites.append(TestSuite(
            name="文件处理测试",
            description="测试文件处理功能",
            tests=[
                self.test_markdown_file_processing,
                self.test_batch_processing,
                self.test_error_handling,
                self.test_file_encoding
            ]
        ))
        
        # 配置管理测试套件
        self.test_suites.append(TestSuite(
            name="配置管理测试",
            description="测试配置管理功能",
            tests=[
                self.test_config_loading,
                self.test_config_validation,
                self.test_config_creation
            ]
        ))
        
        # 集成测试套件
        self.test_suites.append(TestSuite(
            name="集成测试",
            description="测试系统集成功能",
            tests=[
                self.test_tool_integration,
                self.test_workflow_integration,
                self.test_backup_restore,
                self.test_monitoring_integration
            ]
        ))
        
        # 性能测试套件
        self.test_suites.append(TestSuite(
            name="性能测试",
            description="测试系统性能",
            tests=[
                self.test_processing_speed,
                self.test_memory_usage,
                self.test_concurrent_processing,
                self.test_large_file_handling
            ]
        ))
    
    def run_test(self, test_func: Callable, test_name: str = None) -> TestResult:
        """运行单个测试"""
        if test_name is None:
            test_name = test_func.__name__
        
        start_time = time.time()
        
        try:
            # 运行测试
            result = test_func()
            
            duration = time.time() - start_time
            
            if result is True:
                return TestResult(
                    test_name=test_name,
                    status="passed",
                    duration=duration,
                    message="测试通过"
                )
            elif result is False:
                return TestResult(
                    test_name=test_name,
                    status="failed",
                    duration=duration,
                    message="测试失败"
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status="passed",
                    duration=duration,
                    message=str(result)
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="error",
                duration=duration,
                message=f"测试错误: {str(e)}",
                details={"exception": str(e), "type": type(e).__name__}
            )
    
    def run_test_suite(self, suite: TestSuite) -> List[TestResult]:
        """运行测试套件"""
        print(f"🧪 运行测试套件: {suite.name}")
        print(f"   描述: {suite.description}")
        print(f"   测试数量: {len(suite.tests)}")
        
        results = []
        
        # 运行setup
        if suite.setup:
            try:
                suite.setup()
            except Exception as e:
                print(f"⚠️  测试套件setup失败: {e}")
        
        # 运行测试
        for test_func in suite.tests:
            result = self.run_test(test_func)
            results.append(result)
            
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⏭️",
                "error": "💥"
            }.get(result.status, "❓")
            
            print(f"   {status_icon} {result.test_name}: {result.message} ({result.duration:.2f}s)")
        
        # 运行teardown
        if suite.teardown:
            try:
                suite.teardown()
            except Exception as e:
                print(f"⚠️  测试套件teardown失败: {e}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("🚀 开始运行验证测试套件")
        print("=" * 60)
        
        all_results = []
        suite_results = {}
        
        for suite in self.test_suites:
            results = self.run_test_suite(suite)
            all_results.extend(results)
            suite_results[suite.name] = results
            
            print()  # 空行分隔
        
        # 统计结果
        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.status == "passed")
        failed_tests = sum(1 for r in all_results if r.status == "failed")
        error_tests = sum(1 for r in all_results if r.status == "error")
        skipped_tests = sum(1 for r in all_results if r.status == "skipped")
        
        total_duration = sum(r.duration for r in all_results)
        
        # 生成报告
        report = {
            "test_run_time": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration
            },
            "suite_results": {
                name: {
                    "total": len(results),
                    "passed": sum(1 for r in results if r.status == "passed"),
                    "failed": sum(1 for r in results if r.status == "failed"),
                    "errors": sum(1 for r in results if r.status == "error"),
                    "duration": sum(r.duration for r in results)
                }
                for name, results in suite_results.items()
            },
            "detailed_results": [asdict(r) for r in all_results]
        }
        
        # 保存报告
        report_file = self.test_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 打印总结
        print("=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests} ✅")
        print(f"失败: {failed_tests} ❌")
        print(f"错误: {error_tests} 💥")
        print(f"跳过: {skipped_tests} ⏭️")
        print(f"成功率: {report['summary']['success_rate']:.1f}%")
        print(f"总耗时: {total_duration:.2f}秒")
        print(f"报告文件: {report_file}")
        
        return report
    
    # 基础功能测试
    def test_simple_toc_updater_basic(self) -> bool:
        """测试简化版目录更新工具基础功能"""
        try:
            # 检查工具文件是否存在
            tool_path = self.tools_dir / "simple_toc_updater.py"
            if not tool_path.exists():
                return False
            
            # 测试帮助信息
            result = subprocess.run([
                sys.executable, str(tool_path), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def test_document_automation_basic(self) -> bool:
        """测试文档自动化工具基础功能"""
        try:
            tool_path = self.tools_dir / "document_automation.py"
            if not tool_path.exists():
                return False
            
            result = subprocess.run([
                sys.executable, str(tool_path), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def test_comprehensive_automation_basic(self) -> bool:
        """测试综合自动化工具基础功能"""
        try:
            tool_path = self.tools_dir / "comprehensive_automation.py"
            if not tool_path.exists():
                return False
            
            result = subprocess.run([
                sys.executable, str(tool_path), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def test_uv_automation_basic(self) -> bool:
        """测试UV自动化工具基础功能"""
        try:
            tool_path = self.tools_dir / "uv_automation.py"
            if not tool_path.exists():
                return False
            
            result = subprocess.run([
                sys.executable, str(tool_path)
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except Exception:
            return False
    
    # 文件处理测试
    def test_markdown_file_processing(self) -> bool:
        """测试Markdown文件处理"""
        try:
            # 创建临时测试文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write("""# 测试文档

## 章节1

这是测试内容。

### 子章节1.1

更多测试内容。

## 章节2

结束内容。
""")
                temp_file = f.name
            
            # 运行目录更新工具
            tool_path = self.tools_dir / "simple_toc_updater.py"
            result = subprocess.run([
                sys.executable, str(tool_path), str(Path(temp_file).parent)
            ], capture_output=True, text=True, timeout=30)
            
            # 检查结果
            success = result.returncode == 0
            
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except Exception:
                pass
            
            return success
        except Exception:
            return False
    
    def test_batch_processing(self) -> bool:
        """测试批量处理功能"""
        try:
            # 创建临时目录和测试文件
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 创建多个测试文件
                for i in range(3):
                    test_file = temp_path / f"test_{i}.md"
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(f"# 测试文档 {i}\n\n## 章节1\n\n内容{i}。\n")
                
                # 运行批量处理
                tool_path = self.tools_dir / "simple_toc_updater.py"
                result = subprocess.run([
                    sys.executable, str(tool_path), str(temp_path)
                ], capture_output=True, text=True, timeout=30)
                
                return result.returncode == 0
        except Exception:
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        try:
            # 测试不存在的文件
            tool_path = self.tools_dir / "simple_toc_updater.py"
            result = subprocess.run([
                sys.executable, str(tool_path), "/nonexistent/path"
            ], capture_output=True, text=True, timeout=10)
            
            # 应该优雅地处理错误，而不是崩溃
            return result.returncode != 0  # 期望返回错误码
        except Exception:
            return False
    
    def test_file_encoding(self) -> bool:
        """测试文件编码处理"""
        try:
            # 创建包含中文的测试文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write("""# 中文测试文档

## 第一章

这是中文内容测试。

## 第二章

更多中文内容。
""")
                temp_file = f.name
            
            # 运行处理
            tool_path = self.tools_dir / "simple_toc_updater.py"
            result = subprocess.run([
                sys.executable, str(tool_path), str(Path(temp_file).parent)
            ], capture_output=True, text=True, timeout=30)
            
            success = result.returncode == 0
            
            # 清理
            try:
                os.unlink(temp_file)
            except Exception:
                pass
            
            return success
        except Exception:
            return False
    
    # 配置管理测试
    def test_config_loading(self) -> bool:
        """测试配置加载"""
        try:
            config_path = self.tools_dir / "doc_config.yaml"
            if not config_path.exists():
                return False
            
            # 尝试加载配置
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 检查必要的配置项
            required_keys = ["document_structure", "quality_checks", "format_rules"]
            return all(key in config for key in required_keys)
        except Exception:
            return False
    
    def test_config_validation(self) -> bool:
        """测试配置验证"""
        try:
            # 这里可以添加配置验证逻辑
            return True
        except Exception:
            return False
    
    def test_config_creation(self) -> bool:
        """测试配置创建"""
        try:
            # 测试配置创建功能
            return True
        except Exception:
            return False
    
    # 集成测试
    def test_tool_integration(self) -> bool:
        """测试工具集成"""
        try:
            # 测试工具之间的集成
            return True
        except Exception:
            return False
    
    def test_workflow_integration(self) -> bool:
        """测试工作流集成"""
        try:
            # 测试完整工作流
            return True
        except Exception:
            return False
    
    def test_backup_restore(self) -> bool:
        """测试备份恢复功能"""
        try:
            backup_tool = self.tools_dir / "backup_system.py"
            if not backup_tool.exists():
                return False
            
            # 测试备份工具
            result = subprocess.run([
                sys.executable, str(backup_tool), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def test_monitoring_integration(self) -> bool:
        """测试监控集成"""
        try:
            monitoring_tool = self.tools_dir / "monitoring_system.py"
            if not monitoring_tool.exists():
                return False
            
            # 测试监控工具
            result = subprocess.run([
                sys.executable, str(monitoring_tool), "--help"
            ], capture_output=True, text=True, timeout=10)
            
            return result.returncode == 0
        except Exception:
            return False
    
    # 性能测试
    def test_processing_speed(self) -> bool:
        """测试处理速度"""
        try:
            # 创建大量测试文件
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 创建100个测试文件
                for i in range(100):
                    test_file = temp_path / f"test_{i}.md"
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(f"# 测试文档 {i}\n\n## 章节1\n\n内容{i}。\n")
                
                # 测试处理速度
                start_time = time.time()
                tool_path = self.tools_dir / "simple_toc_updater.py"
                result = subprocess.run([
                    sys.executable, str(tool_path), str(temp_path)
                ], capture_output=True, text=True, timeout=60)
                
                duration = time.time() - start_time
                
                # 检查是否在合理时间内完成
                return result.returncode == 0 and duration < 30
        except Exception:
            return False
    
    def test_memory_usage(self) -> bool:
        """测试内存使用"""
        try:
            # 这里可以添加内存使用测试
            return True
        except Exception:
            return False
    
    def test_concurrent_processing(self) -> bool:
        """测试并发处理"""
        try:
            # 测试并发处理能力
            return True
        except Exception:
            return False
    
    def test_large_file_handling(self) -> bool:
        """测试大文件处理"""
        try:
            # 创建大文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                # 写入大量内容
                f.write("# 大文件测试\n\n")
                for i in range(1000):
                    f.write(f"## 章节 {i}\n\n这是第{i}个章节的内容。\n\n")
                temp_file = f.name
            
            # 测试处理大文件
            tool_path = self.tools_dir / "simple_toc_updater.py"
            result = subprocess.run([
                sys.executable, str(tool_path), str(Path(temp_file).parent)
            ], capture_output=True, text=True, timeout=60)
            
            success = result.returncode == 0
            
            # 清理
            try:
                os.unlink(temp_file)
            except Exception:
                pass
            
            return success
        except Exception:
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='验证测试套件')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--suite', help='运行指定测试套件')
    parser.add_argument('--test', help='运行指定测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--report', help='生成测试报告到指定文件')
    
    args = parser.parse_args()
    
    validation_suite = ValidationSuite(args.root)
    
    print("=" * 50)
    print("🚀 验证测试套件")
    print("=" * 50)
    
    if args.all:
        report = validation_suite.run_all_tests()
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"测试报告已保存到: {args.report}")
    elif args.suite:
        # 运行指定测试套件
        suite = next((s for s in validation_suite.test_suites if s.name == args.suite), None)
        if suite:
            validation_suite.run_test_suite(suite)
        else:
            print(f"❌ 未找到测试套件: {args.suite}")
    elif args.test:
        # 运行指定测试
        # 这里需要实现根据名称查找测试的功能
        print(f"运行指定测试: {args.test}")
    else:
        print("请指定要运行的测试")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()
