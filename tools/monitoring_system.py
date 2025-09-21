#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控和报告系统
提供系统性能监控、使用统计、健康检查和报告生成功能
"""

import os
import sys
import json
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import argparse
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    disk_usage: float
    disk_free: int
    disk_total: int
    process_count: int
    load_average: Tuple[float, float, float]

@dataclass
class DocumentMetrics:
    """文档指标"""
    timestamp: str
    total_files: int
    total_size: int
    processed_files: int
    failed_files: int
    skipped_files: int
    processing_time: float
    success_rate: float

@dataclass
class OperationLog:
    """操作日志"""
    timestamp: str
    operation: str
    status: str
    duration: float
    files_processed: int
    error_message: Optional[str] = None

class MonitoringSystem:
    """监控和报告系统"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.logs_dir = self.root_dir / "tools" / "logs"
        self.reports_dir = self.root_dir / "tools" / "reports"
        
        # 创建目录
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化日志
        self.setup_logging()
        
        # 数据存储
        self.system_metrics = deque(maxlen=1000)  # 保留最近1000条记录
        self.document_metrics = deque(maxlen=1000)
        self.operation_logs = deque(maxlen=1000)
        
        # 统计信息
        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_files_processed": 0,
            "total_processing_time": 0.0,
            "start_time": datetime.now().isoformat()
        }
        
        # 监控线程
        self.monitoring_active = False
        self.monitor_thread = None
        
    def setup_logging(self):
        """设置日志"""
        log_file = self.logs_dir / f"monitoring_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage(str(self.root_dir))
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 系统负载（Linux/Mac）
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                load_avg = (0.0, 0.0, 0.0)  # Windows不支持
            
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_total=memory.total,
                disk_usage=disk.percent,
                disk_free=disk.free,
                disk_total=disk.total,
                process_count=process_count,
                load_average=load_avg
            )
        except Exception as e:
            self.logger.error(f"收集系统指标失败: {e}")
            return None
    
    def collect_document_metrics(self, operation_result: Dict[str, Any]) -> DocumentMetrics:
        """收集文档指标"""
        try:
            total_files = operation_result.get("total_files", 0)
            processed_files = operation_result.get("success", 0)
            failed_files = operation_result.get("failed", 0)
            skipped_files = operation_result.get("skipped", 0)
            processing_time = operation_result.get("processing_time", 0.0)
            
            success_rate = (processed_files / total_files * 100) if total_files > 0 else 0.0
            
            # 计算总大小
            total_size = 0
            for file_path in self.root_dir.rglob("*.md"):
                try:
                    total_size += file_path.stat().st_size
                except Exception:
                    pass
            
            return DocumentMetrics(
                timestamp=datetime.now().isoformat(),
                total_files=total_files,
                total_size=total_size,
                processed_files=processed_files,
                failed_files=failed_files,
                skipped_files=skipped_files,
                processing_time=processing_time,
                success_rate=success_rate
            )
        except Exception as e:
            self.logger.error(f"收集文档指标失败: {e}")
            return None
    
    def log_operation(self, operation: str, status: str, duration: float, 
                     files_processed: int, error_message: str = None):
        """记录操作日志"""
        log_entry = OperationLog(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            status=status,
            duration=duration,
            files_processed=files_processed,
            error_message=error_message
        )
        
        self.operation_logs.append(log_entry)
        
        # 更新统计信息
        self.stats["total_operations"] += 1
        if status == "success":
            self.stats["successful_operations"] += 1
        else:
            self.stats["failed_operations"] += 1
        
        self.stats["total_files_processed"] += files_processed
        self.stats["total_processing_time"] += duration
        
        # 记录到日志文件
        if status == "success":
            self.logger.info(f"操作成功: {operation}, 处理文件: {files_processed}, 耗时: {duration:.2f}s")
        else:
            self.logger.error(f"操作失败: {operation}, 错误: {error_message}")
    
    def start_monitoring(self, interval: int = 60):
        """启动监控"""
        if self.monitoring_active:
            self.logger.warning("监控已在运行")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.logger.info(f"监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("监控已停止")
    
    def _monitor_loop(self, interval: int):
        """监控循环"""
        while self.monitoring_active:
            try:
                # 收集系统指标
                system_metrics = self.collect_system_metrics()
                if system_metrics:
                    self.system_metrics.append(system_metrics)
                
                # 检查系统健康状态
                self._check_system_health(system_metrics)
                
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(interval)
    
    def _check_system_health(self, metrics: SystemMetrics):
        """检查系统健康状态"""
        if not metrics:
            return
        
        # CPU使用率检查
        if metrics.cpu_percent > 90:
            self.logger.warning(f"CPU使用率过高: {metrics.cpu_percent:.1f}%")
        
        # 内存使用率检查
        if metrics.memory_percent > 90:
            self.logger.warning(f"内存使用率过高: {metrics.memory_percent:.1f}%")
        
        # 磁盘使用率检查
        if metrics.disk_usage > 90:
            self.logger.warning(f"磁盘使用率过高: {metrics.disk_usage:.1f}%")
        
        # 系统负载检查
        if metrics.load_average[0] > 10:  # 1分钟平均负载
            self.logger.warning(f"系统负载过高: {metrics.load_average[0]:.2f}")
    
    def generate_system_report(self) -> Dict[str, Any]:
        """生成系统报告"""
        try:
            if not self.system_metrics:
                return {"error": "没有系统指标数据"}
            
            # 计算平均值
            cpu_avg = sum(m.cpu_percent for m in self.system_metrics) / len(self.system_metrics)
            memory_avg = sum(m.memory_percent for m in self.system_metrics) / len(self.system_metrics)
            disk_avg = sum(m.disk_usage for m in self.system_metrics) / len(self.system_metrics)
            
            # 获取最新指标
            latest = self.system_metrics[-1]
            
            report = {
                "report_time": datetime.now().isoformat(),
                "monitoring_period": {
                    "start": self.system_metrics[0].timestamp,
                    "end": latest.timestamp,
                    "duration_minutes": len(self.system_metrics)
                },
                "system_health": {
                    "cpu_usage": {
                        "current": latest.cpu_percent,
                        "average": cpu_avg,
                        "max": max(m.cpu_percent for m in self.system_metrics),
                        "min": min(m.cpu_percent for m in self.system_metrics)
                    },
                    "memory_usage": {
                        "current": latest.memory_percent,
                        "average": memory_avg,
                        "max": max(m.memory_percent for m in self.system_metrics),
                        "min": min(m.memory_percent for m in self.system_metrics),
                        "used_gb": latest.memory_used / (1024**3),
                        "total_gb": latest.memory_total / (1024**3)
                    },
                    "disk_usage": {
                        "current": latest.disk_usage,
                        "average": disk_avg,
                        "max": max(m.disk_usage for m in self.system_metrics),
                        "min": min(m.disk_usage for m in self.system_metrics),
                        "free_gb": latest.disk_free / (1024**3),
                        "total_gb": latest.disk_total / (1024**3)
                    },
                    "process_count": latest.process_count,
                    "load_average": latest.load_average
                },
                "alerts": self._generate_alerts()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成系统报告失败: {e}")
            return {"error": str(e)}
    
    def generate_operation_report(self) -> Dict[str, Any]:
        """生成操作报告"""
        try:
            if not self.operation_logs:
                return {"error": "没有操作日志数据"}
            
            # 按操作类型分组
            operations = defaultdict(list)
            for log in self.operation_logs:
                operations[log.operation].append(log)
            
            # 计算统计信息
            operation_stats = {}
            for op_name, logs in operations.items():
                total_count = len(logs)
                success_count = sum(1 for log in logs if log.status == "success")
                total_duration = sum(log.duration for log in logs)
                total_files = sum(log.files_processed for log in logs)
                
                operation_stats[op_name] = {
                    "total_operations": total_count,
                    "successful_operations": success_count,
                    "failed_operations": total_count - success_count,
                    "success_rate": (success_count / total_count * 100) if total_count > 0 else 0,
                    "total_duration": total_duration,
                    "average_duration": total_duration / total_count if total_count > 0 else 0,
                    "total_files_processed": total_files,
                    "average_files_per_operation": total_files / total_count if total_count > 0 else 0
                }
            
            report = {
                "report_time": datetime.now().isoformat(),
                "operation_period": {
                    "start": self.operation_logs[0].timestamp,
                    "end": self.operation_logs[-1].timestamp,
                    "total_operations": len(self.operation_logs)
                },
                "overall_stats": self.stats,
                "operation_stats": operation_stats,
                "recent_operations": [
                    {
                        "timestamp": log.timestamp,
                        "operation": log.operation,
                        "status": log.status,
                        "duration": log.duration,
                        "files_processed": log.files_processed,
                        "error_message": log.error_message
                    }
                    for log in list(self.operation_logs)[-10:]  # 最近10次操作
                ]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成操作报告失败: {e}")
            return {"error": str(e)}
    
    def generate_document_report(self) -> Dict[str, Any]:
        """生成文档报告"""
        try:
            if not self.document_metrics:
                return {"error": "没有文档指标数据"}
            
            # 计算统计信息
            latest = self.document_metrics[-1]
            total_files = sum(m.total_files for m in self.document_metrics)
            total_processed = sum(m.processed_files for m in self.document_metrics)
            total_failed = sum(m.failed_files for m in self.document_metrics)
            total_time = sum(m.processing_time for m in self.document_metrics)
            
            report = {
                "report_time": datetime.now().isoformat(),
                "document_period": {
                    "start": self.document_metrics[0].timestamp,
                    "end": latest.timestamp,
                    "total_operations": len(self.document_metrics)
                },
                "current_status": {
                    "total_files": latest.total_files,
                    "total_size_mb": latest.total_size / (1024**2),
                    "processed_files": latest.processed_files,
                    "failed_files": latest.failed_files,
                    "skipped_files": latest.skipped_files,
                    "success_rate": latest.success_rate
                },
                "overall_stats": {
                    "total_files_processed": total_processed,
                    "total_files_failed": total_failed,
                    "total_processing_time": total_time,
                    "average_processing_time": total_time / len(self.document_metrics) if self.document_metrics else 0,
                    "overall_success_rate": (total_processed / (total_processed + total_failed) * 100) if (total_processed + total_failed) > 0 else 0
                },
                "trend_analysis": self._analyze_trends()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成文档报告失败: {e}")
            return {"error": str(e)}
    
    def _generate_alerts(self) -> List[Dict[str, Any]]:
        """生成告警"""
        alerts = []
        
        if not self.system_metrics:
            return alerts
        
        latest = self.system_metrics[-1]
        
        # CPU告警
        if latest.cpu_percent > 90:
            alerts.append({
                "type": "warning",
                "metric": "cpu_usage",
                "value": latest.cpu_percent,
                "threshold": 90,
                "message": f"CPU使用率过高: {latest.cpu_percent:.1f}%"
            })
        
        # 内存告警
        if latest.memory_percent > 90:
            alerts.append({
                "type": "warning",
                "metric": "memory_usage",
                "value": latest.memory_percent,
                "threshold": 90,
                "message": f"内存使用率过高: {latest.memory_percent:.1f}%"
            })
        
        # 磁盘告警
        if latest.disk_usage > 90:
            alerts.append({
                "type": "critical",
                "metric": "disk_usage",
                "value": latest.disk_usage,
                "threshold": 90,
                "message": f"磁盘使用率过高: {latest.disk_usage:.1f}%"
            })
        
        return alerts
    
    def _analyze_trends(self) -> Dict[str, Any]:
        """分析趋势"""
        if len(self.document_metrics) < 2:
            return {"error": "数据不足，无法分析趋势"}
        
        # 分析成功率趋势
        recent_metrics = list(self.document_metrics)[-5:]  # 最近5次
        success_rates = [m.success_rate for m in recent_metrics]
        
        if len(success_rates) >= 2:
            trend = "上升" if success_rates[-1] > success_rates[0] else "下降"
        else:
            trend = "稳定"
        
        return {
            "success_rate_trend": trend,
            "recent_success_rates": success_rates,
            "performance_trend": "稳定"  # 可以添加更多趋势分析
        }
    
    def save_report(self, report: Dict[str, Any], report_type: str) -> bool:
        """保存报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_report_{timestamp}.json"
            filepath = self.reports_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"报告已保存: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
            return False
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        try:
            system_report = self.generate_system_report()
            operation_report = self.generate_operation_report()
            document_report = self.generate_document_report()
            
            comprehensive_report = {
                "report_time": datetime.now().isoformat(),
                "report_type": "comprehensive",
                "system_report": system_report,
                "operation_report": operation_report,
                "document_report": document_report,
                "summary": {
                    "monitoring_active": self.monitoring_active,
                    "total_metrics_collected": len(self.system_metrics),
                    "total_operations_logged": len(self.operation_logs),
                    "total_document_metrics": len(self.document_metrics)
                }
            }
            
            return comprehensive_report
            
        except Exception as e:
            self.logger.error(f"生成综合报告失败: {e}")
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            current_metrics = self.collect_system_metrics()
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_active": self.monitoring_active,
                "current_metrics": asdict(current_metrics) if current_metrics else None,
                "stats": self.stats,
                "data_counts": {
                    "system_metrics": len(self.system_metrics),
                    "operation_logs": len(self.operation_logs),
                    "document_metrics": len(self.document_metrics)
                }
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取系统状态失败: {e}")
            return {"error": str(e)}

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='监控和报告系统')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--start', action='store_true', help='启动监控')
    parser.add_argument('--stop', action='store_true', help='停止监控')
    parser.add_argument('--status', action='store_true', help='查看系统状态')
    parser.add_argument('--system-report', action='store_true', help='生成系统报告')
    parser.add_argument('--operation-report', action='store_true', help='生成操作报告')
    parser.add_argument('--document-report', action='store_true', help='生成文档报告')
    parser.add_argument('--comprehensive-report', action='store_true', help='生成综合报告')
    parser.add_argument('--interval', type=int, default=60, help='监控间隔（秒）')
    
    args = parser.parse_args()
    
    monitoring = MonitoringSystem(args.root)
    
    print("=" * 50)
    print("🚀 监控和报告系统")
    print("=" * 50)
    
    if args.start:
        monitoring.start_monitoring(args.interval)
        print("监控已启动，按Ctrl+C停止")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitoring.stop_monitoring()
    elif args.stop:
        monitoring.stop_monitoring()
    elif args.status:
        status = monitoring.get_system_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif args.system_report:
        report = monitoring.generate_system_report()
        monitoring.save_report(report, "system")
        print("系统报告已生成")
    elif args.operation_report:
        report = monitoring.generate_operation_report()
        monitoring.save_report(report, "operation")
        print("操作报告已生成")
    elif args.document_report:
        report = monitoring.generate_document_report()
        monitoring.save_report(report, "document")
        print("文档报告已生成")
    elif args.comprehensive_report:
        report = monitoring.generate_comprehensive_report()
        monitoring.save_report(report, "comprehensive")
        print("综合报告已生成")
    else:
        print("请指定操作")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()
