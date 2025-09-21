#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档自动化管理系统
提供完整的文档管理、质量检查、格式修复等功能
"""

import os
import re
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import argparse

class DocumentAutomation:
    """文档自动化管理系统"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.config = self.load_config()
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "errors": 0,
            "warnings": 0
        }
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = self.root_dir / "tools" / "doc_config.yaml"
        
        default_config = {
            "document_structure": {
                "required_sections": [
                    "摘要", "目录", "理论基础", "技术实现", 
                    "实践应用", "最佳实践", "总结"
                ],
                "min_sections": 5,
                "min_code_examples": 2,
                "require_toc": True,
                "require_abstract": True
            },
            "quality_checks": {
                "min_word_count": 500,
                "max_line_length": 120,
                "require_code_language": True,
                "check_links": True
            },
            "format_rules": {
                "fix_headers": True,
                "fix_lists": True,
                "fix_code_blocks": True,
                "fix_spacing": True
            },
            "file_patterns": {
                "include": ["*.md"],
                "exclude": ["node_modules/**", ".git/**", "tools/**"]
            }
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
        
        return default_config
    
    def find_markdown_files(self) -> List[Path]:
        """查找所有Markdown文件"""
        md_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过排除的目录
            dirs[:] = [d for d in dirs if not any(
                d.startswith(exclude.split('/')[0]) 
                for exclude in self.config["file_patterns"]["exclude"]
            )]
            
            for file in files:
                if file.endswith('.md'):
                    md_files.append(Path(root) / file)
        
        self.stats["total_files"] = len(md_files)
        return md_files
    
    def extract_headers(self, content: str) -> List[Tuple[int, str]]:
        """提取标题信息"""
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        headers = []
        
        for match in header_pattern.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            if title != "目录":  # 跳过目录标题本身
                headers.append((level, title))
        
        return headers
    
    def check_document_structure(self, file_path: Path, content: str) -> Dict[str, Any]:
        """检查文档结构"""
        issues = []
        headers = self.extract_headers(content)
        
        # 检查必需章节
        required_sections = self.config["document_structure"]["required_sections"]
        found_sections = [title for _, title in headers]
        
        for section in required_sections:
            if not any(section in title for title in found_sections):
                issues.append(f"缺少必需章节: {section}")
        
        # 检查章节数量
        min_sections = self.config["document_structure"]["min_sections"]
        if len(headers) < min_sections:
            issues.append(f"章节数量不足: {len(headers)} < {min_sections}")
        
        # 检查目录
        if self.config["document_structure"]["require_toc"]:
            if "## 目录" not in content:
                issues.append("缺少目录")
        
        # 检查摘要
        if self.config["document_structure"]["require_abstract"]:
            if "## 摘要" not in content and "## 概述" not in content:
                issues.append("缺少摘要或概述")
        
        return {
            "file": str(file_path),
            "issues": issues,
            "headers": headers,
            "section_count": len(headers)
        }
    
    def check_code_blocks(self, content: str) -> Dict[str, Any]:
        """检查代码块"""
        issues = []
        code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        
        # 检查代码块语言标识
        if self.config["quality_checks"]["require_code_language"]:
            for lang, code in code_blocks:
                if not lang:
                    issues.append("代码块缺少语言标识")
        
        # 检查代码示例数量
        min_examples = self.config["document_structure"]["min_code_examples"]
        if len(code_blocks) < min_examples:
            issues.append(f"代码示例数量不足: {len(code_blocks)} < {min_examples}")
        
        return {
            "code_blocks": len(code_blocks),
            "issues": issues
        }
    
    def check_format_issues(self, content: str) -> List[str]:
        """检查格式问题"""
        issues = []
        lines = content.split('\n')
        
        # 检查行长度
        max_length = self.config["quality_checks"]["max_line_length"]
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                issues.append(f"第{i}行过长: {len(line)} > {max_length}")
        
        # 检查标题格式
        header_pattern = re.compile(r'^#{1,6}\s+.+$', re.MULTILINE)
        for match in header_pattern.finditer(content):
            line = match.group(0)
            if not re.match(r'^#{1,6}\s+.+$', line):
                issues.append(f"标题格式错误: {line}")
        
        # 检查列表格式
        list_pattern = re.compile(r'^\s*[-*+]\s+', re.MULTILINE)
        for match in list_pattern.finditer(content):
            line = match.group(0)
            if not re.match(r'^\s*[-*+]\s+.+$', line):
                issues.append(f"列表格式错误: {line}")
        
        return issues
    
    def fix_format_issues(self, content: str) -> str:
        """修复格式问题"""
        if not self.config["format_rules"]["fix_headers"]:
            return content
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复标题格式
            if re.match(r'^#{1,6}[^#\s]', line):
                line = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', line)
            
            # 修复列表格式
            if re.match(r'^\s*[-*+][^-*+\s]', line):
                line = re.sub(r'^(\s*)([-*+])([^-*+\s])', r'\1\2 \3', line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def validate_document(self, file_path: Path) -> Dict[str, Any]:
        """验证单个文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文档结构
            structure_check = self.check_document_structure(file_path, content)
            
            # 检查代码块
            code_check = self.check_code_blocks(content)
            
            # 检查格式问题
            format_issues = self.check_format_issues(content)
            
            # 统计字数
            word_count = len(content.split())
            
            return {
                "file": str(file_path),
                "word_count": word_count,
                "structure": structure_check,
                "code": code_check,
                "format_issues": format_issues,
                "total_issues": len(structure_check["issues"]) + 
                              len(code_check["issues"]) + 
                              len(format_issues)
            }
            
        except Exception as e:
            self.stats["errors"] += 1
            return {
                "file": str(file_path),
                "error": str(e),
                "total_issues": 1
            }
    
    def batch_validate(self) -> Dict[str, Any]:
        """批量验证所有文档"""
        files = self.find_markdown_files()
        results = []
        
        print(f"🔍 开始验证 {len(files)} 个文档...")
        
        for file_path in files:
            result = self.validate_document(file_path)
            results.append(result)
            
            if result.get("error"):
                print(f"❌ {file_path}: {result['error']}")
            elif result["total_issues"] > 0:
                print(f"⚠️  {file_path}: {result['total_issues']} 个问题")
                self.stats["warnings"] += 1
            else:
                print(f"✅ {file_path}: 通过")
            
            self.stats["processed_files"] += 1
        
        return {
            "results": results,
            "stats": self.stats,
            "summary": self.generate_summary(results)
        }
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成验证摘要"""
        total_files = len(results)
        error_files = len([r for r in results if r.get("error")])
        warning_files = len([r for r in results if r.get("total_issues", 0) > 0])
        clean_files = total_files - error_files - warning_files
        
        # 统计常见问题
        common_issues = {}
        for result in results:
            if "structure" in result:
                for issue in result["structure"]["issues"]:
                    common_issues[issue] = common_issues.get(issue, 0) + 1
        
        return {
            "total_files": total_files,
            "clean_files": clean_files,
            "warning_files": warning_files,
            "error_files": error_files,
            "common_issues": dict(sorted(common_issues.items(), 
                                       key=lambda x: x[1], reverse=True)[:10])
        }
    
    def generate_report(self, validation_results: Dict[str, Any]) -> str:
        """生成验证报告"""
        report_lines = [
            "# 文档质量验证报告",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 总体统计",
            f"- 总文档数: {validation_results['summary']['total_files']}",
            f"- 通过验证: {validation_results['summary']['clean_files']}",
            f"- 存在问题: {validation_results['summary']['warning_files']}",
            f"- 处理错误: {validation_results['summary']['error_files']}",
            "",
            "## 常见问题",
        ]
        
        for issue, count in validation_results['summary']['common_issues'].items():
            report_lines.append(f"- {issue}: {count} 次")
        
        report_lines.extend([
            "",
            "## 详细结果",
            ""
        ])
        
        for result in validation_results['results']:
            if result.get("error"):
                report_lines.append(f"### ❌ {result['file']}")
                report_lines.append(f"错误: {result['error']}")
            elif result.get("total_issues", 0) > 0:
                report_lines.append(f"### ⚠️  {result['file']}")
                report_lines.append(f"问题数量: {result['total_issues']}")
                
                if "structure" in result and result["structure"]["issues"]:
                    report_lines.append("结构问题:")
                    for issue in result["structure"]["issues"]:
                        report_lines.append(f"- {issue}")
                
                if "code" in result and result["code"]["issues"]:
                    report_lines.append("代码问题:")
                    for issue in result["code"]["issues"]:
                        report_lines.append(f"- {issue}")
                
                if result.get("format_issues"):
                    report_lines.append("格式问题:")
                    for issue in result["format_issues"]:
                        report_lines.append(f"- {issue}")
            else:
                report_lines.append(f"### ✅ {result['file']}")
                report_lines.append("通过验证")
            
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def fix_document(self, file_path: Path) -> bool:
        """修复单个文档"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 修复格式问题
            fixed_content = self.fix_format_issues(content)
            
            # 如果内容有变化，写回文件
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"✅ 已修复: {file_path}")
                return True
            else:
                print(f"ℹ️  无需修复: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ 修复失败 {file_path}: {e}")
            return False
    
    def create_template(self, file_path: Path, title: str) -> bool:
        """创建文档模板"""
        try:
            template_content = f"""# {title}

## 摘要

本文档提供了{title}的详细分析和实现方案。

## 目录

## 理论基础

### 核心概念

### 技术原理

## 技术实现

### 架构设计

### 实现方案

## 实践应用

### 应用场景

### 案例分析

## 最佳实践

### 设计原则

### 实施建议

## 总结

## 参考文献

---

**创建时间**: {datetime.now().strftime('%Y-%m-%d')}  
**文档版本**: v1.0  
**状态**: 草稿
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print(f"✅ 已创建模板: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建模板失败 {file_path}: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文档自动化管理系统')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--validate', action='store_true', help='验证文档质量')
    parser.add_argument('--report', action='store_true', help='生成质量报告')
    parser.add_argument('--fix', help='修复指定文档')
    parser.add_argument('--template', nargs=2, metavar=('FILE', 'TITLE'), 
                       help='创建文档模板')
    
    args = parser.parse_args()
    
    automation = DocumentAutomation(args.root)
    
    print("=" * 50)
    print("🚀 文档自动化管理系统")
    print("=" * 50)
    
    if args.validate:
        results = automation.batch_validate()
        print("\n📊 验证完成！")
        print(f"总文档数: {results['summary']['total_files']}")
        print(f"通过验证: {results['summary']['clean_files']}")
        print(f"存在问题: {results['summary']['warning_files']}")
        print(f"处理错误: {results['summary']['error_files']}")
        
    elif args.report:
        results = automation.batch_validate()
        report = automation.generate_report(results)
        
        report_path = automation.root_dir / "tools" / "quality_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 质量报告已生成: {report_path}")
        
    elif args.fix:
        file_path = Path(args.fix)
        if automation.fix_document(file_path):
            print("✅ 文档修复完成")
        else:
            print("ℹ️  文档无需修复")
            
    elif args.template:
        file_path = Path(args.template[0])
        title = args.template[1]
        if automation.create_template(file_path, title):
            print("✅ 模板创建完成")
        else:
            print("❌ 模板创建失败")
            
    else:
        print("请指定操作: --validate, --report, --fix, --template")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()