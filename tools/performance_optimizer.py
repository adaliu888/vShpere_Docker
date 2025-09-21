#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化工具
提供系统性能分析、优化建议和自动优化功能
"""

import os
import sys
import json
import time
import psutil
import threading
import multiprocessing
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
import argparse
import cProfile
import pstats
import io
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import gc
import tracemalloc

@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    memory_peak: float
    disk_io_read: int
    disk_io_write: int
    network_io_sent: int
    network_io_recv: int
    process_count: int
    thread_count: int

@dataclass
class OptimizationResult:
    """优化结果"""
    optimization_type: str
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    improvement_percent: float
    description: str
    recommendations: List[str]

class PerformanceOptimizer:
    """性能优化工具"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.tools_dir = self.root_dir / "tools"
        self.reports_dir = self.root_dir / "tools" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 性能数据存储
        self.performance_history = []
        self.optimization_results = []
        
        # 监控状态
        self.monitoring_active = False
        self.monitor_thread = None
        
        # 性能基准
        self.baseline_metrics = None
        
    def collect_performance_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            process = psutil.Process()
            memory_peak = process.memory_info().rss / (1024**2)  # MB
            
            # 磁盘I/O
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes if disk_io else 0
            disk_write = disk_io.write_bytes if disk_io else 0
            
            # 网络I/O
            network_io = psutil.net_io_counters()
            net_sent = network_io.bytes_sent if network_io else 0
            net_recv = network_io.bytes_recv if network_io else 0
            
            # 进程和线程数
            process_count = len(psutil.pids())
            thread_count = threading.active_count()
            
            return PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                memory_peak=memory_peak,
                disk_io_read=disk_read,
                disk_io_write=disk_write,
                network_io_sent=net_sent,
                network_io_recv=net_recv,
                process_count=process_count,
                thread_count=thread_count
            )
        except Exception as e:
            print(f"❌ 收集性能指标失败: {e}")
            return None
    
    def start_performance_monitoring(self, interval: int = 5, duration: int = 60):
        """启动性能监控"""
        if self.monitoring_active:
            print("⚠️  性能监控已在运行")
            return
        
        self.monitoring_active = True
        self.performance_history.clear()
        
        def monitor_loop():
            start_time = time.time()
            while self.monitoring_active and (time.time() - start_time) < duration:
                metrics = self.collect_performance_metrics()
                if metrics:
                    self.performance_history.append(metrics)
                time.sleep(interval)
            self.monitoring_active = False
        
        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"🚀 性能监控已启动，间隔: {interval}秒，持续时间: {duration}秒")
    
    def stop_performance_monitoring(self):
        """停止性能监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️  性能监控已停止")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """分析性能数据"""
        if not self.performance_history:
            return {"error": "没有性能数据"}
        
        # 计算统计信息
        cpu_values = [m.cpu_usage for m in self.performance_history]
        memory_values = [m.memory_usage for m in self.performance_history]
        memory_peak_values = [m.memory_peak for m in self.performance_history]
        
        analysis = {
            "monitoring_period": {
                "start": self.performance_history[0].timestamp,
                "end": self.performance_history[-1].timestamp,
                "duration_seconds": len(self.performance_history) * 5,  # 假设5秒间隔
                "sample_count": len(self.performance_history)
            },
            "cpu_analysis": {
                "average": sum(cpu_values) / len(cpu_values),
                "maximum": max(cpu_values),
                "minimum": min(cpu_values),
                "trend": self._calculate_trend(cpu_values)
            },
            "memory_analysis": {
                "average_usage_percent": sum(memory_values) / len(memory_values),
                "maximum_usage_percent": max(memory_values),
                "average_peak_mb": sum(memory_peak_values) / len(memory_peak_values),
                "maximum_peak_mb": max(memory_peak_values),
                "trend": self._calculate_trend(memory_values)
            },
            "performance_issues": self._identify_performance_issues(),
            "recommendations": self._generate_recommendations()
        }
        
        return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return "稳定"
        
        # 简单线性趋势分析
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "上升"
        elif second_avg < first_avg * 0.9:
            return "下降"
        else:
            return "稳定"
    
    def _identify_performance_issues(self) -> List[Dict[str, Any]]:
        """识别性能问题"""
        issues = []
        
        if not self.performance_history:
            return issues
        
        # CPU使用率问题
        cpu_values = [m.cpu_usage for m in self.performance_history]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)
        
        if avg_cpu > 80:
            issues.append({
                "type": "cpu_usage",
                "severity": "high" if avg_cpu > 90 else "medium",
                "description": f"CPU使用率过高，平均: {avg_cpu:.1f}%",
                "recommendation": "优化CPU密集型操作，考虑并行处理"
            })
        
        if max_cpu > 95:
            issues.append({
                "type": "cpu_peak",
                "severity": "critical",
                "description": f"CPU使用率峰值过高: {max_cpu:.1f}%",
                "recommendation": "检查是否有CPU密集型任务需要优化"
            })
        
        # 内存使用问题
        memory_values = [m.memory_usage for m in self.performance_history]
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)
        
        if avg_memory > 85:
            issues.append({
                "type": "memory_usage",
                "severity": "high" if avg_memory > 95 else "medium",
                "description": f"内存使用率过高，平均: {avg_memory:.1f}%",
                "recommendation": "优化内存使用，检查内存泄漏"
            })
        
        # 内存峰值问题
        memory_peak_values = [m.memory_peak for m in self.performance_history]
        max_peak = max(memory_peak_values)
        
        if max_peak > 1000:  # 1GB
            issues.append({
                "type": "memory_peak",
                "severity": "medium",
                "description": f"内存峰值过高: {max_peak:.1f}MB",
                "recommendation": "优化内存分配，考虑使用生成器或流式处理"
            })
        
        return issues
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if not self.performance_history:
            return recommendations
        
        # 基于性能数据生成建议
        cpu_values = [m.cpu_usage for m in self.performance_history]
        memory_values = [m.memory_usage for m in self.performance_history]
        
        avg_cpu = sum(cpu_values) / len(cpu_values)
        avg_memory = sum(memory_values) / len(memory_values)
        
        if avg_cpu > 70:
            recommendations.extend([
                "考虑使用多线程或多进程并行处理",
                "优化算法复杂度，减少CPU密集型操作",
                "使用缓存减少重复计算"
            ])
        
        if avg_memory > 80:
            recommendations.extend([
                "优化内存使用，及时释放不需要的对象",
                "使用生成器替代列表，减少内存占用",
                "考虑分批处理大文件"
            ])
        
        # 通用建议
        recommendations.extend([
            "定期清理临时文件和缓存",
            "使用性能分析工具识别瓶颈",
            "考虑使用更高效的数据结构"
        ])
        
        return list(set(recommendations))  # 去重
    
    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """分析函数性能"""
        try:
            # 开始性能分析
            pr = cProfile.Profile()
            pr.enable()
            
            # 执行函数
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # 停止性能分析
            pr.disable()
            
            # 获取分析结果
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
            ps.print_stats()
            profile_output = s.getvalue()
            
            return {
                "function_name": func.__name__,
                "execution_time": end_time - start_time,
                "result": result,
                "profile_output": profile_output,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "function_name": func.__name__,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def optimize_file_processing(self, file_paths: List[Path], 
                                processing_func: Callable) -> OptimizationResult:
        """优化文件处理性能"""
        try:
            # 记录优化前的指标
            before_metrics = self.collect_performance_metrics()
            before_time = time.time()
            
            # 原始处理方式
            results = []
            for file_path in file_paths:
                result = processing_func(file_path)
                results.append(result)
            
            before_duration = time.time() - before_time
            
            # 优化后的处理方式（并行处理）
            after_time = time.time()
            
            # 使用线程池并行处理
            with ThreadPoolExecutor(max_workers=min(len(file_paths), multiprocessing.cpu_count())) as executor:
                future_results = [executor.submit(processing_func, file_path) for file_path in file_paths]
                optimized_results = [future.result() for future in future_results]
            
            after_duration = time.time() - after_time
            
            # 记录优化后的指标
            after_metrics = self.collect_performance_metrics()
            
            # 计算改进百分比
            improvement = ((before_duration - after_duration) / before_duration * 100) if before_duration > 0 else 0
            
            optimization_result = OptimizationResult(
                optimization_type="parallel_processing",
                before_metrics={
                    "duration": before_duration,
                    "cpu_usage": before_metrics.cpu_usage if before_metrics else 0,
                    "memory_usage": before_metrics.memory_usage if before_metrics else 0
                },
                after_metrics={
                    "duration": after_duration,
                    "cpu_usage": after_metrics.cpu_usage if after_metrics else 0,
                    "memory_usage": after_metrics.memory_usage if after_metrics else 0
                },
                improvement_percent=improvement,
                description=f"使用并行处理优化文件处理，处理了{len(file_paths)}个文件",
                recommendations=[
                    "使用ThreadPoolExecutor进行并行处理",
                    "根据CPU核心数调整线程池大小",
                    "考虑使用ProcessPoolExecutor处理CPU密集型任务"
                ]
            )
            
            self.optimization_results.append(optimization_result)
            
            return optimization_result
            
        except Exception as e:
            return OptimizationResult(
                optimization_type="parallel_processing",
                before_metrics={},
                after_metrics={},
                improvement_percent=0,
                description=f"优化失败: {str(e)}",
                recommendations=["检查错误日志，修复问题后重试"]
            )
    
    def optimize_memory_usage(self, data_processing_func: Callable, 
                             data_source: Any) -> OptimizationResult:
        """优化内存使用"""
        try:
            # 记录优化前的内存使用
            before_metrics = self.collect_performance_metrics()
            before_memory = before_metrics.memory_peak if before_metrics else 0
            
            # 强制垃圾回收
            gc.collect()
            
            # 执行优化前的处理
            before_time = time.time()
            result = data_processing_func(data_source)
            before_duration = time.time() - before_time
            
            # 清理内存
            del result
            gc.collect()
            
            # 记录优化后的内存使用
            after_metrics = self.collect_performance_metrics()
            after_memory = after_metrics.memory_peak if after_metrics else 0
            
            # 计算内存使用改进
            memory_improvement = ((before_memory - after_memory) / before_memory * 100) if before_memory > 0 else 0
            
            optimization_result = OptimizationResult(
                optimization_type="memory_optimization",
                before_metrics={
                    "memory_peak_mb": before_memory,
                    "duration": before_duration
                },
                after_metrics={
                    "memory_peak_mb": after_memory,
                    "duration": before_duration
                },
                improvement_percent=memory_improvement,
                description="通过垃圾回收和内存管理优化内存使用",
                recommendations=[
                    "及时释放不需要的对象",
                    "使用生成器替代列表",
                    "定期调用gc.collect()清理内存"
                ]
            )
            
            self.optimization_results.append(optimization_result)
            
            return optimization_result
            
        except Exception as e:
            return OptimizationResult(
                optimization_type="memory_optimization",
                before_metrics={},
                after_metrics={},
                improvement_percent=0,
                description=f"内存优化失败: {str(e)}",
                recommendations=["检查内存使用模式，识别内存泄漏"]
            )
    
    def benchmark_tool_performance(self, tool_path: Path, test_data: str) -> Dict[str, Any]:
        """基准测试工具性能"""
        try:
            # 创建测试数据
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(test_data)
                test_file = f.name
            
            # 运行基准测试
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / (1024**2)
            
            result = subprocess.run([
                sys.executable, str(tool_path), test_file
            ], capture_output=True, text=True, timeout=60)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / (1024**2)
            
            # 清理测试文件
            try:
                os.unlink(test_file)
            except Exception:
                pass
            
            return {
                "tool_name": tool_path.name,
                "execution_time": end_time - start_time,
                "memory_usage_mb": end_memory - start_memory,
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "output_size": len(result.stdout),
                "error_size": len(result.stderr),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "tool_name": tool_path.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """生成优化报告"""
        try:
            performance_analysis = self.analyze_performance()
            
            report = {
                "report_time": datetime.now().isoformat(),
                "performance_analysis": performance_analysis,
                "optimization_results": [asdict(result) for result in self.optimization_results],
                "recommendations": {
                    "immediate": [],
                    "short_term": [],
                    "long_term": []
                },
                "summary": {
                    "total_optimizations": len(self.optimization_results),
                    "average_improvement": sum(r.improvement_percent for r in self.optimization_results) / len(self.optimization_results) if self.optimization_results else 0,
                    "performance_issues_count": len(performance_analysis.get("performance_issues", [])),
                    "recommendations_count": len(performance_analysis.get("recommendations", []))
                }
            }
            
            # 分类建议
            if performance_analysis.get("performance_issues"):
                for issue in performance_analysis["performance_issues"]:
                    if issue["severity"] == "critical":
                        report["recommendations"]["immediate"].append(issue["recommendation"])
                    elif issue["severity"] == "high":
                        report["recommendations"]["short_term"].append(issue["recommendation"])
                    else:
                        report["recommendations"]["long_term"].append(issue["recommendation"])
            
            return report
            
        except Exception as e:
            return {"error": f"生成优化报告失败: {str(e)}"}
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> bool:
        """保存报告"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"performance_report_{timestamp}.json"
            
            filepath = self.reports_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 性能报告已保存: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 保存性能报告失败: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='性能优化工具')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--monitor', action='store_true', help='启动性能监控')
    parser.add_argument('--analyze', action='store_true', help='分析性能数据')
    parser.add_argument('--optimize', help='运行优化测试')
    parser.add_argument('--benchmark', help='基准测试工具')
    parser.add_argument('--report', action='store_true', help='生成优化报告')
    parser.add_argument('--interval', type=int, default=5, help='监控间隔（秒）')
    parser.add_argument('--duration', type=int, default=60, help='监控持续时间（秒）')
    
    args = parser.parse_args()
    
    optimizer = PerformanceOptimizer(args.root)
    
    print("=" * 50)
    print("🚀 性能优化工具")
    print("=" * 50)
    
    if args.monitor:
        optimizer.start_performance_monitoring(args.interval, args.duration)
        try:
            time.sleep(args.duration)
        except KeyboardInterrupt:
            pass
        finally:
            optimizer.stop_performance_monitoring()
    elif args.analyze:
        analysis = optimizer.analyze_performance()
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    elif args.optimize:
        print(f"运行优化测试: {args.optimize}")
    elif args.benchmark:
        tool_path = Path(args.benchmark)
        if tool_path.exists():
            test_data = "# 测试文档\n\n## 章节1\n\n测试内容。\n"
            result = optimizer.benchmark_tool_performance(tool_path, test_data)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 工具不存在: {tool_path}")
    elif args.report:
        report = optimizer.generate_optimization_report()
        optimizer.save_report(report)
    else:
        print("请指定操作")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()
