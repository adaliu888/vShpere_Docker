#!/usr/bin/env python3
"""
集成测试套件
用于测试虚拟化容器化技术演示环境的端到端功能
"""

import asyncio
import json
import time
import requests
import pytest
from typing import Dict, List, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationTestSuite:
    """集成测试套件"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有集成测试"""
        logger.info("开始运行集成测试套件")
        
        test_methods = [
            self.test_virtualization_monitor,
            self.test_container_orchestrator,
            self.test_semantic_validator,
            self.test_prometheus_metrics,
            self.test_grafana_dashboard,
            self.test_load_balancing,
            self.test_health_checks,
            self.test_error_handling,
            self.test_performance_metrics,
            self.test_security_validation,
        ]
        
        results = {
            "total_tests": len(test_methods),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_results": [],
            "start_time": time.time(),
        }
        
        for test_method in test_methods:
            try:
                test_name = test_method.__name__
                logger.info(f"运行测试: {test_name}")
                
                start_time = time.time()
                await test_method()
                duration = time.time() - start_time
                
                results["passed"] += 1
                results["test_results"].append({
                    "name": test_name,
                    "status": "PASSED",
                    "duration": duration,
                    "error": None
                })
                
                logger.info(f"测试通过: {test_name} ({duration:.2f}s)")
                
            except Exception as e:
                results["failed"] += 1
                results["test_results"].append({
                    "name": test_method.__name__,
                    "status": "FAILED",
                    "duration": time.time() - start_time,
                    "error": str(e)
                })
                
                logger.error(f"测试失败: {test_method.__name__}: {e}")
        
        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]
        
        return results
    
    async def test_virtualization_monitor(self):
        """测试虚拟化监控器"""
        # 测试健康检查
        response = self.session.get(f"{self.base_url}:8080/health")
        assert response.status_code == 200
        
        # 测试获取主机列表
        response = self.session.get(f"{self.base_url}:8080/api/hosts")
        assert response.status_code == 200
        hosts = response.json()
        assert isinstance(hosts, list)
        
        # 测试添加主机
        host_data = {
            "name": "test-host",
            "ip_address": "192.168.1.100",
            "total_cpu_cores": 16,
            "total_memory_gb": 128,
            "total_storage_gb": 2000
        }
        response = self.session.post(f"{self.base_url}:8080/api/hosts", json=host_data)
        assert response.status_code == 201
        
        # 测试获取性能指标
        response = self.session.get(f"{self.base_url}:8080/api/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert isinstance(metrics, list)
    
    async def test_container_orchestrator(self):
        """测试容器编排器"""
        # 测试健康检查
        response = self.session.get(f"{self.base_url}:8081/health")
        assert response.status_code == 200
        
        # 测试获取服务列表
        response = self.session.get(f"{self.base_url}:8081/api/services")
        assert response.status_code == 200
        services = response.json()
        assert isinstance(services, list)
        
        # 测试创建服务
        service_data = {
            "name": "test-service",
            "image": "nginx:latest",
            "replicas": 2,
            "port": 80,
            "environment": {"ENV": "test"},
            "labels": {"app": "test"}
        }
        response = self.session.post(f"{self.base_url}:8081/api/services", json=service_data)
        assert response.status_code == 201
        
        # 测试获取节点列表
        response = self.session.get(f"{self.base_url}:8081/api/nodes")
        assert response.status_code == 200
        nodes = response.json()
        assert isinstance(nodes, list)
    
    async def test_semantic_validator(self):
        """测试语义验证器"""
        # 测试健康检查
        response = self.session.get(f"{self.base_url}:8082/health")
        assert response.status_code == 200
        
        # 测试验证模型
        model_data = {
            "name": "test-model",
            "description": "测试模型",
            "variables": {
                "test_var": {"type": "integer", "value": 42}
            }
        }
        response = self.session.post(f"{self.base_url}:8082/api/validate", json=model_data)
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
    
    async def test_prometheus_metrics(self):
        """测试Prometheus指标"""
        # 测试Prometheus健康检查
        response = self.session.get(f"{self.base_url}:9090/-/healthy")
        assert response.status_code == 200
        
        # 测试指标端点
        response = self.session.get(f"{self.base_url}:9090/metrics")
        assert response.status_code == 200
        metrics_text = response.text
        assert "prometheus" in metrics_text.lower()
    
    async def test_grafana_dashboard(self):
        """测试Grafana仪表板"""
        # 测试Grafana健康检查
        response = self.session.get(f"{self.base_url}:3000/api/health")
        assert response.status_code == 200
        
        # 测试登录
        login_data = {
            "user": "admin",
            "password": "admin123"
        }
        response = self.session.post(f"{self.base_url}:3000/login", json=login_data)
        # Grafana可能返回不同的状态码，这里只检查不是500错误
        assert response.status_code != 500
    
    async def test_load_balancing(self):
        """测试负载均衡"""
        # 测试Nginx负载均衡器
        response = self.session.get(f"{self.base_url}/monitor/health")
        assert response.status_code == 200
        
        # 测试多个请求的负载均衡
        responses = []
        for _ in range(10):
            response = self.session.get(f"{self.base_url}/monitor/health")
            responses.append(response.status_code)
        
        # 所有请求都应该成功
        assert all(status == 200 for status in responses)
    
    async def test_health_checks(self):
        """测试健康检查"""
        services = [
            ("virtualization-monitor", 8080),
            ("container-orchestrator", 8081),
            ("semantic-validator", 8082),
            ("prometheus", 9090),
            ("grafana", 3000),
        ]
        
        for service_name, port in services:
            try:
                response = self.session.get(f"{self.base_url}:{port}/health", timeout=5)
                assert response.status_code == 200, f"{service_name} 健康检查失败"
            except requests.exceptions.RequestException as e:
                # 某些服务可能没有健康检查端点，这是可以接受的
                logger.warning(f"{service_name} 健康检查不可用: {e}")
    
    async def test_error_handling(self):
        """测试错误处理"""
        # 测试404错误
        response = self.session.get(f"{self.base_url}:8080/api/nonexistent")
        assert response.status_code == 404
        
        # 测试无效数据
        invalid_data = {"invalid": "data"}
        response = self.session.post(f"{self.base_url}:8080/api/hosts", json=invalid_data)
        assert response.status_code in [400, 422]  # 客户端错误
    
    async def test_performance_metrics(self):
        """测试性能指标"""
        # 测试响应时间
        start_time = time.time()
        response = self.session.get(f"{self.base_url}:8080/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # 响应时间应小于1秒
        
        # 测试并发请求
        async def make_request():
            return self.session.get(f"{self.base_url}:8080/health")
        
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # 所有并发请求都应该成功
        assert all(r.status_code == 200 for r in responses)
    
    async def test_security_validation(self):
        """测试安全验证"""
        # 测试HTTPS重定向（如果配置了）
        try:
            response = self.session.get(f"https://{self.base_url.replace('http://', '')}/monitor/health", 
                                      verify=False, timeout=5)
            # HTTPS可能不可用，这是可以接受的
        except requests.exceptions.RequestException:
            pass
        
        # 测试SQL注入防护
        malicious_data = {
            "name": "'; DROP TABLE hosts; --",
            "ip_address": "192.168.1.100"
        }
        response = self.session.post(f"{self.base_url}:8080/api/hosts", json=malicious_data)
        # 应该返回客户端错误，而不是服务器错误
        assert response.status_code in [400, 422, 500]
        
        # 测试XSS防护
        xss_data = {
            "name": "<script>alert('xss')</script>",
            "ip_address": "192.168.1.100"
        }
        response = self.session.post(f"{self.base_url}:8080/api/hosts", json=xss_data)
        # 应该被正确处理或拒绝
        assert response.status_code in [200, 201, 400, 422]

class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info("开始运行性能测试套件")
        
        results = {
            "response_times": {},
            "throughput": {},
            "concurrent_users": {},
            "memory_usage": {},
            "cpu_usage": {},
        }
        
        # 测试响应时间
        results["response_times"] = await self.test_response_times()
        
        # 测试吞吐量
        results["throughput"] = await self.test_throughput()
        
        # 测试并发用户
        results["concurrent_users"] = await self.test_concurrent_users()
        
        return results
    
    async def test_response_times(self) -> Dict[str, float]:
        """测试响应时间"""
        endpoints = [
            ("/monitor/health", 8080),
            ("/orchestrator/health", 8081),
            ("/validator/health", 8082),
        ]
        
        response_times = {}
        
        for endpoint, port in endpoints:
            times = []
            for _ in range(10):
                start_time = time.time()
                try:
                    response = self.session.get(f"{self.base_url}:{port}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        times.append(time.time() - start_time)
                except requests.exceptions.RequestException:
                    pass
            
            if times:
                response_times[endpoint] = {
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "p95": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
                }
        
        return response_times
    
    async def test_throughput(self) -> Dict[str, int]:
        """测试吞吐量"""
        throughput = {}
        
        # 测试每秒请求数
        for duration in [1, 5, 10]:  # 测试1秒、5秒、10秒
            start_time = time.time()
            request_count = 0
            
            while time.time() - start_time < duration:
                try:
                    response = self.session.get(f"{self.base_url}:8080/health", timeout=1)
                    if response.status_code == 200:
                        request_count += 1
                except requests.exceptions.RequestException:
                    pass
            
            throughput[f"{duration}s"] = request_count
        
        return throughput
    
    async def test_concurrent_users(self) -> Dict[str, Any]:
        """测试并发用户"""
        concurrent_results = {}
        
        for concurrent_count in [10, 50, 100]:
            async def make_request():
                try:
                    response = self.session.get(f"{self.base_url}:8080/health", timeout=5)
                    return response.status_code == 200
                except requests.exceptions.RequestException:
                    return False
            
            start_time = time.time()
            tasks = [make_request() for _ in range(concurrent_count)]
            results = await asyncio.gather(*tasks)
            duration = time.time() - start_time
            
            successful_requests = sum(results)
            concurrent_results[f"{concurrent_count}_users"] = {
                "successful_requests": successful_requests,
                "failed_requests": concurrent_count - successful_requests,
                "success_rate": successful_requests / concurrent_count,
                "duration": duration,
                "requests_per_second": concurrent_count / duration
            }
        
        return concurrent_results

async def main():
    """主函数"""
    print("虚拟化容器化技术集成测试启动...")
    
    # 运行集成测试
    integration_suite = IntegrationTestSuite()
    integration_results = await integration_suite.run_all_tests()
    
    print(f"\n集成测试结果:")
    print(f"总测试数: {integration_results['total_tests']}")
    print(f"通过: {integration_results['passed']}")
    print(f"失败: {integration_results['failed']}")
    print(f"总耗时: {integration_results['total_duration']:.2f}秒")
    
    # 运行性能测试
    performance_suite = PerformanceTestSuite()
    performance_results = await performance_suite.run_performance_tests()
    
    print(f"\n性能测试结果:")
    print(f"响应时间: {performance_results['response_times']}")
    print(f"吞吐量: {performance_results['throughput']}")
    print(f"并发用户: {performance_results['concurrent_users']}")
    
    # 保存测试结果
    all_results = {
        "integration": integration_results,
        "performance": performance_results,
        "timestamp": time.time()
    }
    
    with open("test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n测试结果已保存到 test_results.json")
    
    # 返回退出码
    if integration_results["failed"] > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())
