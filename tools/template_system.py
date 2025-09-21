#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理系统
提供文档模板的创建、管理、应用和自定义功能
"""

import os
import sys
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import argparse
import re
from dataclasses import dataclass, asdict
from jinja2 import Template, Environment, FileSystemLoader

@dataclass
class TemplateInfo:
    """模板信息"""
    name: str
    description: str
    category: str
    tags: List[str]
    created_at: str
    updated_at: str
    file_path: str
    variables: Dict[str, Any]
    usage_count: int = 0

class TemplateSystem:
    """模板管理系统"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.templates_dir = self.root_dir / "tools" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.templates_dir / "template_metadata.json"
        self.metadata = self.load_metadata()
        
        # 初始化Jinja2环境
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # 注册自定义过滤器
        self.jinja_env.filters['date_format'] = self._date_format_filter
        self.jinja_env.filters['title_case'] = self._title_case_filter
        
    def load_metadata(self) -> Dict[str, Any]:
        """加载模板元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载模板元数据失败: {e}")
        
        return {
            "templates": {},
            "categories": {
                "技术文档": "技术分析、架构设计、实现方案等文档",
                "项目文档": "项目计划、总结、报告等文档",
                "用户文档": "用户指南、操作手册、教程等文档",
                "API文档": "接口文档、开发文档等",
                "学术文档": "论文、研究报告、分析报告等"
            },
            "settings": {
                "auto_update_metadata": True,
                "default_category": "技术文档",
                "template_extension": ".md.j2"
            }
        }
    
    def save_metadata(self) -> bool:
        """保存模板元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存模板元数据失败: {e}")
            return False
    
    def create_template(self, name: str, description: str, category: str = None, 
                       template_content: str = None, variables: Dict[str, Any] = None) -> bool:
        """创建模板"""
        try:
            if category is None:
                category = self.metadata["settings"]["default_category"]
            
            if variables is None:
                variables = {}
            
            # 生成模板文件名
            template_filename = f"{name}{self.metadata['settings']['template_extension']}"
            template_path = self.templates_dir / template_filename
            
            # 检查模板是否已存在
            if template_path.exists():
                print(f"⚠️  模板已存在: {name}")
                return False
            
            # 如果没有提供内容，使用默认模板
            if template_content is None:
                template_content = self._get_default_template(category)
            
            # 创建模板文件
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # 创建模板信息
            template_info = TemplateInfo(
                name=name,
                description=description,
                category=category,
                tags=[],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                file_path=str(template_path.relative_to(self.templates_dir)),
                variables=variables
            )
            
            # 保存元数据
            self.metadata["templates"][name] = asdict(template_info)
            self.save_metadata()
            
            print(f"✅ 模板创建成功: {name}")
            print(f"   文件路径: {template_path}")
            print(f"   类别: {category}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建模板失败: {e}")
            return False
    
    def _get_default_template(self, category: str) -> str:
        """获取默认模板内容"""
        templates = {
            "技术文档": '''# {{ title }}

## 摘要

{{ abstract }}

## 目录

<!-- 目录将由自动化工具生成 -->

## 1. 概述

### 1.1 背景

{{ background }}

### 1.2 目标

{{ objectives }}

## 2. 技术分析

### 2.1 现状分析

{{ current_analysis }}

### 2.2 技术选型

{{ technology_selection }}

## 3. 设计方案

### 3.1 架构设计

{{ architecture_design }}

### 3.2 实现方案

{{ implementation_plan }}

## 4. 实施计划

### 4.1 开发计划

{{ development_plan }}

### 4.2 测试计划

{{ testing_plan }}

## 5. 风险评估

{{ risk_assessment }}

## 6. 总结

{{ summary }}

## 参考文献

{{ references }}

---

**创建时间**: {{ creation_date }}  
**作者**: {{ author }}  
**版本**: {{ version }}  
**状态**: {{ status }}
''',
            
            "项目文档": '''# {{ title }}

## 项目概述

### 项目背景

{{ project_background }}

### 项目目标

{{ project_objectives }}

### 项目范围

{{ project_scope }}

## 项目计划

### 时间计划

{{ timeline }}

### 资源计划

{{ resource_plan }}

### 里程碑

{{ milestones }}

## 项目团队

{{ team_members }}

## 项目风险

{{ project_risks }}

## 项目总结

{{ project_summary }}

---

**项目开始时间**: {{ start_date }}  
**项目结束时间**: {{ end_date }}  
**项目经理**: {{ project_manager }}  
**项目状态**: {{ project_status }}
''',
            
            "用户文档": '''# {{ title }}

## 概述

{{ overview }}

## 快速开始

### 环境要求

{{ requirements }}

### 安装步骤

{{ installation_steps }}

## 使用指南

### 基本使用

{{ basic_usage }}

### 高级功能

{{ advanced_features }}

## 配置说明

{{ configuration }}

## 常见问题

{{ faq }}

## 故障排除

{{ troubleshooting }}

## 更新日志

{{ changelog }}

---

**文档版本**: {{ version }}  
**最后更新**: {{ last_updated }}  
**维护者**: {{ maintainer }}
''',
            
            "API文档": '''# {{ title }} API文档

## 概述

{{ api_overview }}

## 认证

{{ authentication }}

## 端点列表

### {{ endpoint_name }}

**URL**: `{{ endpoint_url }}`  
**方法**: `{{ http_method }}`  
**描述**: {{ endpoint_description }}

#### 请求参数

{{ request_parameters }}

#### 响应格式

{{ response_format }}

#### 示例

{{ examples }}

## 错误代码

{{ error_codes }}

## 速率限制

{{ rate_limits }}

---

**API版本**: {{ api_version }}  
**基础URL**: {{ base_url }}  
**文档版本**: {{ doc_version }}
''',
            
            "学术文档": '''# {{ title }}

## 摘要

{{ abstract }}

**关键词**: {{ keywords }}

## 1. 引言

### 1.1 研究背景

{{ research_background }}

### 1.2 研究问题

{{ research_questions }}

### 1.3 研究目标

{{ research_objectives }}

## 2. 文献综述

{{ literature_review }}

## 3. 研究方法

{{ research_methodology }}

## 4. 研究结果

{{ research_results }}

## 5. 讨论

{{ discussion }}

## 6. 结论

{{ conclusions }}

## 参考文献

{{ references }}

## 附录

{{ appendices }}

---

**作者**: {{ authors }}  
**机构**: {{ institution }}  
**日期**: {{ date }}  
**DOI**: {{ doi }}
'''
        }
        
        return templates.get(category, templates["技术文档"])
    
    def list_templates(self, category: str = None) -> None:
        """列出模板"""
        templates = self.metadata["templates"]
        
        if not templates:
            print("📋 没有找到模板")
            return
        
        print("📋 模板列表:")
        print("=" * 80)
        print(f"{'名称':<20} {'类别':<15} {'描述':<30} {'创建时间':<15}")
        print("-" * 80)
        
        for name, info in templates.items():
            if category and info["category"] != category:
                continue
            
            description = info["description"][:27] + "..." if len(info["description"]) > 30 else info["description"]
            created_date = info["created_at"][:10]
            
            print(f"{name:<20} {info['category']:<15} {description:<30} {created_date:<15}")
    
    def get_template(self, name: str) -> Optional[TemplateInfo]:
        """获取模板信息"""
        if name not in self.metadata["templates"]:
            return None
        
        info_dict = self.metadata["templates"][name]
        return TemplateInfo(**info_dict)
    
    def apply_template(self, template_name: str, output_path: str, 
                      variables: Dict[str, Any] = None) -> bool:
        """应用模板"""
        try:
            template_info = self.get_template(template_name)
            if not template_info:
                print(f"❌ 模板不存在: {template_name}")
                return False
            
            # 加载模板
            template_path = self.templates_dir / template_info.file_path
            if not template_path.exists():
                print(f"❌ 模板文件不存在: {template_path}")
                return False
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 准备变量
            if variables is None:
                variables = {}
            
            # 添加默认变量
            default_vars = {
                "title": "未命名文档",
                "creation_date": datetime.now().strftime("%Y-%m-%d"),
                "author": "未知作者",
                "version": "1.0",
                "status": "草稿"
            }
            default_vars.update(variables)
            
            # 渲染模板
            template = Template(template_content)
            rendered_content = template.render(**default_vars)
            
            # 保存输出文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered_content)
            
            # 更新使用计数
            self.metadata["templates"][template_name]["usage_count"] += 1
            self.metadata["templates"][template_name]["updated_at"] = datetime.now().isoformat()
            self.save_metadata()
            
            print(f"✅ 模板应用成功: {template_name}")
            print(f"   输出文件: {output_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 应用模板失败: {e}")
            return False
    
    def update_template(self, name: str, content: str = None, 
                       description: str = None, variables: Dict[str, Any] = None) -> bool:
        """更新模板"""
        try:
            if name not in self.metadata["templates"]:
                print(f"❌ 模板不存在: {name}")
                return False
            
            template_info = self.get_template(name)
            template_path = self.templates_dir / template_info.file_path
            
            # 更新内容
            if content is not None:
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 更新元数据
            if description is not None:
                self.metadata["templates"][name]["description"] = description
            
            if variables is not None:
                self.metadata["templates"][name]["variables"] = variables
            
            self.metadata["templates"][name]["updated_at"] = datetime.now().isoformat()
            self.save_metadata()
            
            print(f"✅ 模板更新成功: {name}")
            return True
            
        except Exception as e:
            print(f"❌ 更新模板失败: {e}")
            return False
    
    def delete_template(self, name: str) -> bool:
        """删除模板"""
        try:
            if name not in self.metadata["templates"]:
                print(f"❌ 模板不存在: {name}")
                return False
            
            template_info = self.get_template(name)
            template_path = self.templates_dir / template_info.file_path
            
            # 删除模板文件
            if template_path.exists():
                template_path.unlink()
            
            # 删除元数据
            del self.metadata["templates"][name]
            self.save_metadata()
            
            print(f"✅ 模板删除成功: {name}")
            return True
            
        except Exception as e:
            print(f"❌ 删除模板失败: {e}")
            return False
    
    def clone_template(self, source_name: str, target_name: str, 
                      description: str = None) -> bool:
        """克隆模板"""
        try:
            source_info = self.get_template(source_name)
            if not source_info:
                print(f"❌ 源模板不存在: {source_name}")
                return False
            
            # 读取源模板内容
            source_path = self.templates_dir / source_info.file_path
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建新模板
            new_description = description or f"基于 {source_name} 的模板"
            return self.create_template(
                name=target_name,
                description=new_description,
                category=source_info.category,
                template_content=content,
                variables=source_info.variables
            )
            
        except Exception as e:
            print(f"❌ 克隆模板失败: {e}")
            return False
    
    def export_template(self, name: str, export_path: str) -> bool:
        """导出模板"""
        try:
            template_info = self.get_template(name)
            if not template_info:
                print(f"❌ 模板不存在: {name}")
                return False
            
            # 创建导出包
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取模板内容
            template_path = self.templates_dir / template_info.file_path
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建导出数据
            export_data = {
                "template_info": asdict(template_info),
                "template_content": content,
                "export_time": datetime.now().isoformat(),
                "export_version": "1.0"
            }
            
            # 保存导出文件
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 模板导出成功: {name}")
            print(f"   导出文件: {export_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 导出模板失败: {e}")
            return False
    
    def import_template(self, import_path: str) -> bool:
        """导入模板"""
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                print(f"❌ 导入文件不存在: {import_path}")
                return False
            
            # 读取导入数据
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            template_info = import_data["template_info"]
            content = import_data["template_content"]
            
            # 检查模板是否已存在
            if template_info["name"] in self.metadata["templates"]:
                print(f"⚠️  模板已存在: {template_info['name']}")
                return False
            
            # 创建模板
            return self.create_template(
                name=template_info["name"],
                description=template_info["description"],
                category=template_info["category"],
                template_content=content,
                variables=template_info["variables"]
            )
            
        except Exception as e:
            print(f"❌ 导入模板失败: {e}")
            return False
    
    def search_templates(self, query: str) -> List[str]:
        """搜索模板"""
        results = []
        query_lower = query.lower()
        
        for name, info in self.metadata["templates"].items():
            # 搜索名称
            if query_lower in name.lower():
                results.append(name)
                continue
            
            # 搜索描述
            if query_lower in info["description"].lower():
                results.append(name)
                continue
            
            # 搜索类别
            if query_lower in info["category"].lower():
                results.append(name)
                continue
            
            # 搜索标签
            for tag in info.get("tags", []):
                if query_lower in tag.lower():
                    results.append(name)
                    break
        
        return list(set(results))  # 去重
    
    def get_template_statistics(self) -> Dict[str, Any]:
        """获取模板统计信息"""
        templates = self.metadata["templates"]
        
        if not templates:
            return {"error": "没有模板数据"}
        
        # 按类别统计
        category_stats = {}
        for info in templates.values():
            category = info["category"]
            if category not in category_stats:
                category_stats[category] = 0
            category_stats[category] += 1
        
        # 使用统计
        total_usage = sum(info["usage_count"] for info in templates.values())
        most_used = max(templates.items(), key=lambda x: x[1]["usage_count"])
        
        return {
            "total_templates": len(templates),
            "category_distribution": category_stats,
            "total_usage": total_usage,
            "most_used_template": {
                "name": most_used[0],
                "usage_count": most_used[1]["usage_count"]
            },
            "recent_templates": [
                name for name, info in sorted(
                    templates.items(), 
                    key=lambda x: x[1]["created_at"], 
                    reverse=True
                )[:5]
            ]
        }
    
    def _date_format_filter(self, date_str: str, format_str: str = "%Y-%m-%d") -> str:
        """日期格式化过滤器"""
        try:
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime(format_str)
            return str(date_str)
        except Exception:
            return str(date_str)
    
    def _title_case_filter(self, text: str) -> str:
        """标题格式化过滤器"""
        return text.title()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='模板管理系统')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--create', help='创建模板')
    parser.add_argument('--list', action='store_true', help='列出模板')
    parser.add_argument('--apply', nargs=2, metavar=('TEMPLATE', 'OUTPUT'), help='应用模板')
    parser.add_argument('--update', help='更新模板')
    parser.add_argument('--delete', help='删除模板')
    parser.add_argument('--clone', nargs=2, metavar=('SOURCE', 'TARGET'), help='克隆模板')
    parser.add_argument('--export', nargs=2, metavar=('TEMPLATE', 'PATH'), help='导出模板')
    parser.add_argument('--import', dest='import_path', help='导入模板')
    parser.add_argument('--search', help='搜索模板')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--category', help='指定类别')
    parser.add_argument('--description', help='模板描述')
    
    args = parser.parse_args()
    
    template_system = TemplateSystem(args.root)
    
    print("=" * 50)
    print("🚀 模板管理系统")
    print("=" * 50)
    
    if args.create:
        template_system.create_template(
            name=args.create,
            description=args.description or "新模板",
            category=args.category
        )
    elif args.list:
        template_system.list_templates(args.category)
    elif args.apply:
        template_system.apply_template(args.apply[0], args.apply[1])
    elif args.update:
        template_system.update_template(args.update)
    elif args.delete:
        template_system.delete_template(args.delete)
    elif args.clone:
        template_system.clone_template(args.clone[0], args.clone[1])
    elif args.export:
        template_system.export_template(args.export[0], args.export[1])
    elif args.import_path:
        template_system.import_template(args.import_path)
    elif args.search:
        results = template_system.search_templates(args.search)
        print(f"搜索结果: {results}")
    elif args.stats:
        stats = template_system.get_template_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print("请指定操作")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()
