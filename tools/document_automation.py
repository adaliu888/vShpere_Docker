#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档自动化管理系统
提供文档的自动化管理、更新、验证和质量检查功能
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import markdown
from markdown.extensions import toc, codehilite, tables

class DocumentAutomation:
    """文档自动化管理系统"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.config_file = self.root_dir / "tools" / "doc_config.yaml"
        self.load_config()
        
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "document_structure": {
                "required_sections": [
                    "摘要", "目录", "理论基础", "技术实现", 
                    "形式化证明", "实践应用", "最佳实践", "总结"
                ],
                "optional_sections": [
                    "技术对比", "发展趋势", "参考文献", "附录"
                ]
            },
            "quality_checks": {
                "min_sections": 5,
                "min_code_examples": 2,
                "require_toc": True,
                "require_abstract": True
            },
            "file_patterns": {
                "markdown": "*.md",
                "config": "*.yaml",
                "code": ["*.py", "*.rs", "*.go", "*.js"]
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
    
    def find_documents(self, pattern: str = "*.md") -> List[Path]:
        """查找文档文件"""
        documents = []
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过隐藏目录和工具目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'tools']
            for file in files:
                if file.endswith('.md'):
                    documents.append(Path(root) / file)
        return documents
    
    def analyze_document_structure(self, file_path: Path) -> Dict[str, Any]:
        """分析文档结构"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
            headers = []
            for match in header_pattern.finditer(content):
                level = len(match.group(1))
                title = match.group(2).strip()
                headers.append({"level": level, "title": title})
            
            # 检查必需章节
            required_sections = self.config["document_structure"]["required_sections"]
            found_sections = [h["title"] for h in headers]
            missing_sections = [s for s in required_sections if s not in found_sections]
            
            # 统计代码块
            code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
            
            # 统计字数
            word_count = len(content.split())
            
            return {
                "file_path": str(file_path),
                "headers": headers,
                "missing_sections": missing_sections,
                "code_blocks": len(code_blocks),
                "word_count": word_count,
                "has_toc": "目录" in found_sections,
                "has_abstract": "摘要" in found_sections,
                "structure_score": self.calculate_structure_score(headers, missing_sections)
            }
            
        except Exception as e:
            return {"error": str(e), "file_path": str(file_path)}
    
    def calculate_structure_score(self, headers: List[Dict], missing_sections: List[str]) -> int:
        """计算文档结构评分"""
        score = 100
        
        # 扣除缺失章节的分数
        score -= len(missing_sections) * 10
        
        # 检查标题层次结构
        levels = [h["level"] for h in headers]
        if levels:
            max_level = max(levels)
            if max_level > 6:
                score -= 5  # 标题层次过深
        
        # 检查是否有足够的章节
        if len(headers) < self.config["quality_checks"]["min_sections"]:
            score -= 20
        
        return max(0, score)
    
    def validate_document(self, file_path: Path) -> Dict[str, Any]:
        """验证文档质量"""
        analysis = self.analyze_document_structure(file_path)
        
        if "error" in analysis:
            return analysis
        
        quality_checks = self.config["quality_checks"]
        issues = []
        
        # 检查必需章节
        if analysis["missing_sections"]:
            issues.append(f"缺失必需章节: {', '.join(analysis['missing_sections'])}")
        
        # 检查目录
        if quality_checks["require_toc"] and not analysis["has_toc"]:
            issues.append("缺少目录")
        
        # 检查摘要
        if quality_checks["require_abstract"] and not analysis["has_abstract"]:
            issues.append("缺少摘要")
        
        # 检查代码示例
        if analysis["code_blocks"] < quality_checks["min_code_examples"]:
            issues.append(f"代码示例不足 (需要{quality_checks['min_code_examples']}个，实际{analysis['code_blocks']}个)")
        
        # 检查字数
        if analysis["word_count"] < 1000:
            issues.append("文档内容过少")
        
        return {
            "file_path": str(file_path),
            "score": analysis["structure_score"],
            "issues": issues,
            "status": "pass" if not issues else "fail",
            "analysis": analysis
        }
    
    def batch_validate(self) -> Dict[str, Any]:
        """批量验证文档"""
        documents = self.find_documents()
        results = {
            "total": len(documents),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }
        
        for doc in documents:
            validation = self.validate_document(doc)
            results["details"].append(validation)
            
            if "error" in validation:
                results["errors"] += 1
            elif validation["status"] == "pass":
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def generate_quality_report(self) -> str:
        """生成质量报告"""
        results = self.batch_validate()
        
        report = f"""# 文档质量报告

## 总体统计

- **总文档数**: {results['total']}
- **通过验证**: {results['passed']}
- **未通过验证**: {results['failed']}
- **处理错误**: {results['errors']}
- **通过率**: {results['passed']/results['total']*100:.1f}%

## 详细结果

"""
        
        for detail in results["details"]:
            if "error" in detail:
                report += f"### ❌ {Path(detail['file_path']).name}\n"
                report += f"**错误**: {detail['error']}\n\n"
            elif detail["status"] == "pass":
                report += f"### ✅ {Path(detail['file_path']).name}\n"
                report += f"**评分**: {detail['score']}/100\n\n"
            else:
                report += f"### ⚠️ {Path(detail['file_path']).name}\n"
                report += f"**评分**: {detail['score']}/100\n"
                report += f"**问题**:\n"
                for issue in detail["issues"]:
                    report += f"- {issue}\n"
                report += "\n"
        
        return report
    
    def auto_fix_common_issues(self, file_path: Path) -> bool:
        """自动修复常见问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = []
            
            # 修复标题格式
            content = re.sub(r'^(\#{1,6})\s*([^\n]+)\s*$', r'\1 \2', content, flags=re.MULTILINE)
            
            # 确保代码块有语言标识
            content = re.sub(r'```\n', '```text\n', content)
            
            # 修复列表格式
            content = re.sub(r'^(\s*)[-*+]\s+', r'\1- ', content, flags=re.MULTILINE)
            
            # 确保段落间有空行
            content = re.sub(r'\n(#{1,6})', r'\n\n\1', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 已修复格式问题: {file_path}")
                return True
            else:
                print(f"ℹ️ 无需修复: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ 修复失败 {file_path}: {e}")
            return False
    
    def create_document_template(self, file_path: Path, title: str) -> bool:
        """创建文档模板"""
        template = f"""# {title}

## 摘要

- 文档目标和范围
- 主要技术内容概述
- 适用人群和前置要求

## 目录

- [理论基础](#理论基础)
- [技术实现](#技术实现)
- [实践应用](#实践应用)
- [最佳实践](#最佳实践)
- [总结](#总结)

## 理论基础

### 核心概念

- 关键术语定义
- 技术原理说明
- 数学公式和形式化定义

### 技术架构

- 系统架构图
- 组件关系说明
- 数据流和控制流

## 技术实现

### 实现原理

- 详细技术实现
- 算法和数据结构
- 性能优化策略

### 代码示例

```python
# Python代码示例
def example_function():
    pass
```

```rust
// Rust代码示例
fn example_function() {{
    // 实现代码
}}
```

## 实践应用

### 部署配置

- 环境准备
- 安装步骤
- 配置参数

### 运维管理

- 监控指标
- 故障诊断
- 性能调优

## 最佳实践

### 设计原则

- 架构设计原则
- 安全设计原则
- 性能设计原则

### 实施指南

- 实施步骤
- 注意事项
- 常见问题

## 总结

- 主要贡献总结
- 技术要点回顾
- 学习建议

## 参考文献

- 技术标准引用
- 学术论文引用
- 官方文档引用

---

**文档版本**: v1.0  
**创建日期**: {datetime.now().strftime('%Y-%m-%d')}  
**最后更新**: {datetime.now().strftime('%Y-%m-%d')}  
**审核状态**: 待审核
"""
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"✅ 已创建文档模板: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 创建失败 {file_path}: {e}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文档自动化管理系统')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--validate', action='store_true', help='验证文档质量')
    parser.add_argument('--report', action='store_true', help='生成质量报告')
    parser.add_argument('--fix', help='修复指定文件的格式问题')
    parser.add_argument('--template', nargs=2, metavar=('FILE', 'TITLE'), help='创建文档模板')
    
    args = parser.parse_args()
    
    automation = DocumentAutomation(args.root)
    
    if args.validate:
        results = automation.batch_validate()
        print(f"验证完成: {results['passed']}/{results['total']} 通过")
    
    if args.report:
        report = automation.generate_quality_report()
        report_file = Path(args.root) / "文档质量报告.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"质量报告已生成: {report_file}")
    
    if args.fix:
        file_path = Path(args.fix)
        automation.auto_fix_common_issues(file_path)
    
    if args.template:
        file_path, title = args.template
        automation.create_document_template(Path(file_path), title)

if __name__ == "__main__":
    main()
