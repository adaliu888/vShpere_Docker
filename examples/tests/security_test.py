#!/usr/bin/env python3
"""
安全测试套件
用于测试虚拟化容器化技术演示环境的安全性和漏洞
"""

import asyncio
import json
import time
import requests
import subprocess
import os
from typing import Dict, List, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityTestSuite:
    """安全测试套件"""
    
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    async def run_all_security_tests(self) -> Dict[str, Any]:
        """运行所有安全测试"""
        logger.info("开始运行安全测试套件")
        
        test_methods = [
            self.test_authentication_bypass,
            self.test_sql_injection,
            self.test_xss_attacks,
            self.test_csrf_protection,
            self.test_directory_traversal,
            self.test_command_injection,
            self.test_file_upload_vulnerabilities,
            self.test_information_disclosure,
            self.test_session_management,
            self.test_input_validation,
            self.test_authorization_bypass,
            self.test_secure_headers,
            self.test_ssl_tls_configuration,
            self.test_container_security,
            self.test_network_security,
        ]
        
        results = {
            "total_tests": len(test_methods),
            "passed": 0,
            "failed": 0,
            "vulnerabilities_found": 0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "medium_vulnerabilities": 0,
            "low_vulnerabilities": 0,
            "test_results": [],
            "start_time": time.time(),
        }
        
        for test_method in test_methods:
            try:
                test_name = test_method.__name__
                logger.info(f"运行安全测试: {test_name}")
                
                start_time = time.time()
                vulnerability_level = await test_method()
                duration = time.time() - start_time
                
                if vulnerability_level == "NONE":
                    results["passed"] += 1
                    status = "PASSED"
                else:
                    results["failed"] += 1
                    results["vulnerabilities_found"] += 1
                    
                    if vulnerability_level == "CRITICAL":
                        results["critical_vulnerabilities"] += 1
                    elif vulnerability_level == "HIGH":
                        results["high_vulnerabilities"] += 1
                    elif vulnerability_level == "MEDIUM":
                        results["medium_vulnerabilities"] += 1
                    elif vulnerability_level == "LOW":
                        results["low_vulnerabilities"] += 1
                    
                    status = f"VULNERABILITY_{vulnerability_level}"
                
                results["test_results"].append({
                    "name": test_name,
                    "status": status,
                    "vulnerability_level": vulnerability_level,
                    "duration": duration,
                    "description": self.get_test_description(test_name)
                })
                
                logger.info(f"安全测试完成: {test_name} - {status}")
                
            except Exception as e:
                results["failed"] += 1
                results["test_results"].append({
                    "name": test_method.__name__,
                    "status": "ERROR",
                    "vulnerability_level": "UNKNOWN",
                    "duration": time.time() - start_time,
                    "error": str(e),
                    "description": self.get_test_description(test_method.__name__)
                })
                
                logger.error(f"安全测试出错: {test_method.__name__}: {e}")
        
        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]
        
        return results
    
    def get_test_description(self, test_name: str) -> str:
        """获取测试描述"""
        descriptions = {
            "test_authentication_bypass": "测试身份验证绕过漏洞",
            "test_sql_injection": "测试SQL注入漏洞",
            "test_xss_attacks": "测试跨站脚本攻击",
            "test_csrf_protection": "测试CSRF保护",
            "test_directory_traversal": "测试目录遍历漏洞",
            "test_command_injection": "测试命令注入漏洞",
            "test_file_upload_vulnerabilities": "测试文件上传漏洞",
            "test_information_disclosure": "测试信息泄露",
            "test_session_management": "测试会话管理",
            "test_input_validation": "测试输入验证",
            "test_authorization_bypass": "测试授权绕过",
            "test_secure_headers": "测试安全头",
            "test_ssl_tls_configuration": "测试SSL/TLS配置",
            "test_container_security": "测试容器安全",
            "test_network_security": "测试网络安全",
        }
        return descriptions.get(test_name, "未知测试")
    
    async def test_authentication_bypass(self) -> str:
        """测试身份验证绕过"""
        vulnerabilities = []
        
        # 测试直接访问受保护资源
        protected_endpoints = [
            "/api/admin/users",
            "/api/admin/config",
            "/api/admin/logs",
            "/admin/dashboard",
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = self.session.get(f"{self.base_url}:8080{endpoint}")
                if response.status_code == 200:
                    vulnerabilities.append(f"未授权访问: {endpoint}")
            except requests.exceptions.RequestException:
                pass
        
        # 测试弱密码
        weak_passwords = ["admin", "password", "123456", "qwerty", ""]
        for password in weak_passwords:
            try:
                login_data = {"username": "admin", "password": password}
                response = self.session.post(f"{self.base_url}:8080/api/login", json=login_data)
                if response.status_code == 200:
                    vulnerabilities.append(f"弱密码登录成功: {password}")
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现身份验证绕过漏洞: {vulnerabilities}")
            return "HIGH"
        
        return "NONE"
    
    async def test_sql_injection(self) -> str:
        """测试SQL注入"""
        vulnerabilities = []
        
        # SQL注入payload
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1' OR 1=1 --",
            "admin'--",
            "' OR 1=1 LIMIT 1 --",
        ]
        
        # 测试登录接口
        for payload in sql_payloads:
            try:
                login_data = {"username": payload, "password": "test"}
                response = self.session.post(f"{self.base_url}:8080/api/login", json=login_data)
                
                # 检查响应中是否包含数据库错误信息
                if any(keyword in response.text.lower() for keyword in 
                      ["sql", "mysql", "postgresql", "database", "syntax error"]):
                    vulnerabilities.append(f"SQL注入漏洞: {payload}")
            except requests.exceptions.RequestException:
                pass
        
        # 测试搜索接口
        for payload in sql_payloads:
            try:
                response = self.session.get(f"{self.base_url}:8080/api/search?q={payload}")
                if any(keyword in response.text.lower() for keyword in 
                      ["sql", "mysql", "postgresql", "database", "syntax error"]):
                    vulnerabilities.append(f"搜索SQL注入: {payload}")
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现SQL注入漏洞: {vulnerabilities}")
            return "CRITICAL"
        
        return "NONE"
    
    async def test_xss_attacks(self) -> str:
        """测试跨站脚本攻击"""
        vulnerabilities = []
        
        # XSS payload
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
        ]
        
        # 测试输入字段
        for payload in xss_payloads:
            try:
                # 测试主机名输入
                host_data = {"name": payload, "ip_address": "192.168.1.100"}
                response = self.session.post(f"{self.base_url}:8080/api/hosts", json=host_data)
                
                # 检查响应中是否包含未转义的payload
                if payload in response.text and "<script>" in payload:
                    vulnerabilities.append(f"存储型XSS: {payload}")
                
                # 测试搜索功能
                response = self.session.get(f"{self.base_url}:8080/api/search?q={payload}")
                if payload in response.text and "<script>" in payload:
                    vulnerabilities.append(f"反射型XSS: {payload}")
                    
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现XSS漏洞: {vulnerabilities}")
            return "HIGH"
        
        return "NONE"
    
    async def test_csrf_protection(self) -> str:
        """测试CSRF保护"""
        vulnerabilities = []
        
        # 测试CSRF令牌
        try:
            # 获取CSRF令牌
            response = self.session.get(f"{self.base_url}:8080/api/csrf-token")
            csrf_token = response.json().get("token") if response.status_code == 200 else None
            
            if not csrf_token:
                vulnerabilities.append("缺少CSRF令牌")
            else:
                # 测试没有CSRF令牌的请求
                host_data = {"name": "test", "ip_address": "192.168.1.100"}
                response = self.session.post(f"{self.base_url}:8080/api/hosts", json=host_data)
                if response.status_code == 200:
                    vulnerabilities.append("CSRF保护未生效")
                
        except requests.exceptions.RequestException:
            vulnerabilities.append("CSRF令牌端点不可用")
        
        if vulnerabilities:
            logger.warning(f"发现CSRF漏洞: {vulnerabilities}")
            return "MEDIUM"
        
        return "NONE"
    
    async def test_directory_traversal(self) -> str:
        """测试目录遍历"""
        vulnerabilities = []
        
        # 目录遍历payload
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        
        for payload in traversal_payloads:
            try:
                response = self.session.get(f"{self.base_url}:8080/api/files?path={payload}")
                
                # 检查是否返回了系统文件内容
                if any(keyword in response.text.lower() for keyword in 
                      ["root:", "administrator", "localhost", "127.0.0.1"]):
                    vulnerabilities.append(f"目录遍历漏洞: {payload}")
                    
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现目录遍历漏洞: {vulnerabilities}")
            return "HIGH"
        
        return "NONE"
    
    async def test_command_injection(self) -> str:
        """测试命令注入"""
        vulnerabilities = []
        
        # 命令注入payload
        command_payloads = [
            "; ls -la",
            "| whoami",
            "&& id",
            "`cat /etc/passwd`",
            "$(whoami)",
            "; cat /etc/passwd",
        ]
        
        for payload in command_payloads:
            try:
                # 测试ping功能
                ping_data = {"host": f"127.0.0.1{payload}"}
                response = self.session.post(f"{self.base_url}:8080/api/ping", json=ping_data)
                
                # 检查响应中是否包含命令执行结果
                if any(keyword in response.text.lower() for keyword in 
                      ["uid=", "gid=", "root", "bin", "daemon"]):
                    vulnerabilities.append(f"命令注入漏洞: {payload}")
                    
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现命令注入漏洞: {vulnerabilities}")
            return "CRITICAL"
        
        return "NONE"
    
    async def test_file_upload_vulnerabilities(self) -> str:
        """测试文件上传漏洞"""
        vulnerabilities = []
        
        # 测试恶意文件上传
        malicious_files = [
            ("test.php", "<?php system($_GET['cmd']); ?>"),
            ("test.jsp", "<% Runtime.getRuntime().exec(request.getParameter(\"cmd\")); %>"),
            ("test.asp", "<% eval request(\"cmd\") %>"),
            ("test.exe", b"MZ\x90\x00"),  # PE文件头
        ]
        
        for filename, content in malicious_files:
            try:
                files = {"file": (filename, content, "application/octet-stream")}
                response = self.session.post(f"{self.base_url}:8080/api/upload", files=files)
                
                if response.status_code == 200:
                    vulnerabilities.append(f"恶意文件上传成功: {filename}")
                    
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现文件上传漏洞: {vulnerabilities}")
            return "HIGH"
        
        return "NONE"
    
    async def test_information_disclosure(self) -> str:
        """测试信息泄露"""
        vulnerabilities = []
        
        # 测试敏感信息泄露
        sensitive_endpoints = [
            "/.env",
            "/config.json",
            "/.git/config",
            "/api/debug",
            "/api/version",
            "/api/status",
            "/error",
            "/debug",
        ]
        
        for endpoint in sensitive_endpoints:
            try:
                response = self.session.get(f"{self.base_url}:8080{endpoint}")
                
                if response.status_code == 200:
                    # 检查是否包含敏感信息
                    sensitive_keywords = [
                        "password", "secret", "key", "token", "api_key",
                        "database", "connection", "admin", "root"
                    ]
                    
                    if any(keyword in response.text.lower() for keyword in sensitive_keywords):
                        vulnerabilities.append(f"信息泄露: {endpoint}")
                        
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现信息泄露: {vulnerabilities}")
            return "MEDIUM"
        
        return "NONE"
    
    async def test_session_management(self) -> str:
        """测试会话管理"""
        vulnerabilities = []
        
        try:
            # 测试会话固定
            response1 = self.session.get(f"{self.base_url}:8080/api/login")
            session_id_1 = self.session.cookies.get("session_id")
            
            response2 = self.session.get(f"{self.base_url}:8080/api/login")
            session_id_2 = self.session.cookies.get("session_id")
            
            if session_id_1 == session_id_2:
                vulnerabilities.append("会话固定漏洞")
            
            # 测试会话超时
            # 这里需要模拟长时间等待，实际测试中可以缩短时间
            time.sleep(1)  # 简化测试
            
            # 测试会话劫持
            if session_id_1:
                # 尝试使用相同的会话ID
                self.session.cookies.set("session_id", session_id_1)
                response = self.session.get(f"{self.base_url}:8080/api/protected")
                if response.status_code == 200:
                    vulnerabilities.append("会话劫持漏洞")
                    
        except requests.exceptions.RequestException:
            pass
        
        if vulnerabilities:
            logger.warning(f"发现会话管理漏洞: {vulnerabilities}")
            return "MEDIUM"
        
        return "NONE"
    
    async def test_input_validation(self) -> str:
        """测试输入验证"""
        vulnerabilities = []
        
        # 测试各种输入验证
        invalid_inputs = [
            ("name", "a" * 10000),  # 超长输入
            ("ip_address", "999.999.999.999"),  # 无效IP
            ("port", "99999"),  # 无效端口
            ("email", "invalid-email"),  # 无效邮箱
            ("url", "not-a-url"),  # 无效URL
        ]
        
        for field, invalid_value in invalid_inputs:
            try:
                data = {field: invalid_value}
                response = self.session.post(f"{self.base_url}:8080/api/hosts", json=data)
                
                if response.status_code == 200:
                    vulnerabilities.append(f"输入验证不足: {field}")
                    
            except requests.exceptions.RequestException:
                pass
        
        if vulnerabilities:
            logger.warning(f"发现输入验证漏洞: {vulnerabilities}")
            return "LOW"
        
        return "NONE"
    
    async def test_authorization_bypass(self) -> str:
        """测试授权绕过"""
        vulnerabilities = []
        
        # 测试权限提升
        try:
            # 尝试以普通用户身份访问管理员功能
            user_data = {"username": "user", "password": "user123"}
            response = self.session.post(f"{self.base_url}:8080/api/login", json=user_data)
            
            if response.status_code == 200:
                # 尝试访问管理员接口
                admin_endpoints = [
                    "/api/admin/users",
                    "/api/admin/config",
                    "/api/admin/logs",
                ]
                
                for endpoint in admin_endpoints:
                    response = self.session.get(f"{self.base_url}:8080{endpoint}")
                    if response.status_code == 200:
                        vulnerabilities.append(f"权限提升: {endpoint}")
                        
        except requests.exceptions.RequestException:
            pass
        
        if vulnerabilities:
            logger.warning(f"发现授权绕过漏洞: {vulnerabilities}")
            return "HIGH"
        
        return "NONE"
    
    async def test_secure_headers(self) -> str:
        """测试安全头"""
        vulnerabilities = []
        
        try:
            response = self.session.get(f"{self.base_url}:8080/")
            headers = response.headers
            
            # 检查必要的安全头
            required_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": ["DENY", "SAMEORIGIN"],
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": None,  # 存在即可
                "Content-Security-Policy": None,  # 存在即可
            }
            
            for header, expected_value in required_headers.items():
                if header not in headers:
                    vulnerabilities.append(f"缺少安全头: {header}")
                elif expected_value and headers[header] not in expected_value:
                    vulnerabilities.append(f"安全头配置错误: {header}")
                    
        except requests.exceptions.RequestException:
            pass
        
        if vulnerabilities:
            logger.warning(f"发现安全头问题: {vulnerabilities}")
            return "MEDIUM"
        
        return "NONE"
    
    async def test_ssl_tls_configuration(self) -> str:
        """测试SSL/TLS配置"""
        vulnerabilities = []
        
        try:
            # 测试HTTPS配置
            https_url = self.base_url.replace("http://", "https://")
            response = self.session.get(f"{https_url}:8080/", verify=False, timeout=5)
            
            # 检查SSL证书
            if hasattr(response, 'cert'):
                cert = response.cert
                # 这里可以添加更多证书检查逻辑
                
        except requests.exceptions.RequestException:
            # HTTPS可能不可用，这是可以接受的
            pass
        
        # 测试HTTP到HTTPS重定向
        try:
            response = self.session.get(f"{self.base_url}:8080/", allow_redirects=False)
            if response.status_code not in [301, 302]:
                vulnerabilities.append("缺少HTTP到HTTPS重定向")
        except requests.exceptions.RequestException:
            pass
        
        if vulnerabilities:
            logger.warning(f"发现SSL/TLS配置问题: {vulnerabilities}")
            return "MEDIUM"
        
        return "NONE"
    
    async def test_container_security(self) -> str:
        """测试容器安全"""
        vulnerabilities = []
        
        try:
            # 检查容器是否以root用户运行
            response = self.session.get(f"{self.base_url}:8080/api/system/info")
            if response.status_code == 200:
                system_info = response.json()
                if system_info.get("user") == "root":
                    vulnerabilities.append("容器以root用户运行")
            
            # 检查容器资源限制
            response = self.session.get(f"{self.base_url}:8080/api/system/resources")
            if response.status_code == 200:
                resources = response.json()
                if not resources.get("memory_limit"):
                    vulnerabilities.append("缺少内存限制")
                if not resources.get("cpu_limit"):
                    vulnerabilities.append("缺少CPU限制")
                    
        except requests.exceptions.RequestException:
            pass
        
        if vulnerabilities:
            logger.warning(f"发现容器安全问题: {vulnerabilities}")
            return "MEDIUM"
        
        return "NONE"
    
    async def test_network_security(self) -> str:
        """测试网络安全"""
        vulnerabilities = []
        
        try:
            # 测试端口扫描
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
            open_ports = []
            
            for port in common_ports:
                try:
                    response = self.session.get(f"{self.base_url}:{port}", timeout=1)
                    open_ports.append(port)
                except requests.exceptions.RequestException:
                    pass
            
            if len(open_ports) > 5:  # 如果开放端口过多
                vulnerabilities.append(f"开放端口过多: {open_ports}")
                
        except Exception:
            pass
        
        if vulnerabilities:
            logger.warning(f"发现网络安全问题: {vulnerabilities}")
            return "LOW"
        
        return "NONE"

async def main():
    """主函数"""
    print("虚拟化容器化技术安全测试启动...")
    
    # 运行安全测试
    security_suite = SecurityTestSuite()
    security_results = await security_suite.run_all_security_tests()
    
    print(f"\n安全测试结果:")
    print(f"总测试数: {security_results['total_tests']}")
    print(f"通过: {security_results['passed']}")
    print(f"失败: {security_results['failed']}")
    print(f"发现漏洞: {security_results['vulnerabilities_found']}")
    print(f"严重漏洞: {security_results['critical_vulnerabilities']}")
    print(f"高危漏洞: {security_results['high_vulnerabilities']}")
    print(f"中危漏洞: {security_results['medium_vulnerabilities']}")
    print(f"低危漏洞: {security_results['low_vulnerabilities']}")
    print(f"总耗时: {security_results['total_duration']:.2f}秒")
    
    # 显示详细结果
    print(f"\n详细测试结果:")
    for result in security_results['test_results']:
        status_icon = "✅" if result['status'] == "PASSED" else "❌"
        print(f"  {status_icon} {result['name']}: {result['status']} ({result['vulnerability_level']})")
        if result.get('error'):
            print(f"    错误: {result['error']}")
    
    # 保存测试结果
    with open("security_test_results.json", "w") as f:
        json.dump(security_results, f, indent=2)
    
    print(f"\n安全测试结果已保存到 security_test_results.json")
    
    # 返回退出码
    if security_results['critical_vulnerabilities'] > 0 or security_results['high_vulnerabilities'] > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())
