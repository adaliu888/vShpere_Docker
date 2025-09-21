#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版目录管理工具
使用uv管理Python环境，提供完整的自动化功能
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import argparse

class EnhancedTOCManager:
    """增强版目录管理器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.config = self.load_config()
        self.stats = {
            "processed": 0,
            "updated": 0,
            "created": 0,
            "skipped": 0,
            "errors": 0
        }
        
    def load_config(self) -> Dict:
        """加载配置"""
        config_file = self.root_dir / "tools" / "toc_config.json"
        default_config = {
            "toc_title": "## 目录",
            "toc_patterns": [
                r'^## 目录\s*$',
                r'^## Table of Contents\s*$',
                r'^## 目錄\s*$'
            ],
            "header_pattern": r'^(#{1,6})\s+(.+)$',
            "exclude_dirs": [".git", "tools", "__pycache__", ".vscode", "node_modules"],
            "exclude_files": ["README.md", "CHANGELOG.md"],
            "auto_backup": True,
            "backup_dir": "backups",
            "verbose": True
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
        
        return default_config
    
    def save_config(self):
        """保存配置"""
        config_file = self.root_dir / "tools" / "toc_config.json"
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def log(self, message: str, level: str = "INFO"):
        """日志输出"""
        if self.config.get("verbose", True):
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def find_markdown_files(self) -> List[Path]:
        """查找所有Markdown文件"""
        md_files = []
        exclude_dirs = set(self.config.get("exclude_dirs", []))
        exclude_files = set(self.config.get("exclude_files", []))
        
        for root, dirs, files in os.walk(self.root_dir):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.md') and file not in exclude_files:
                    md_files.append(Path(root) / file)
        
        return md_files
    
    def extract_headers(self, content: str) -> List[Tuple[int, str, str]]:
        """提取标题信息"""
        headers = []
        header_pattern = re.compile(self.config["header_pattern"], re.MULTILINE)
        
        for match in header_pattern.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            
            # 跳过目录标题本身
            if title not in ["目录", "Table of Contents", "目錄"]:
                headers.append((level, title, match.group(0)))
        
        return headers
    
    def generate_anchor(self, title: str) -> str:
        """生成锚点链接"""
        # 移除特殊字符，转换为小写，用连字符连接
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def generate_toc(self, headers: List[Tuple[int, str, str]]) -> str:
        """生成目录"""
        if not headers:
            return ""
        
        toc_lines = [self.config["toc_title"], ""]
        
        for level, title, _ in headers:
            indent = "  " * (level - 1)
            anchor = self.generate_anchor(title)
            toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        toc_lines.append("")
        return "\n".join(toc_lines)
    
    def backup_file(self, file_path: Path) -> bool:
        """备份文件"""
        if not self.config.get("auto_backup", True):
            return True
        
        try:
            backup_dir = self.root_dir / self.config.get("backup_dir", "backups")
            backup_dir.mkdir(exist_ok=True)
            
            # 创建带时间戳的备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            # 复制文件
            with open(file_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            self.log(f"已备份: {backup_path}")
            return True
            
        except Exception as e:
            self.log(f"备份失败 {file_path}: {e}", "ERROR")
            return False
    
    def update_toc_in_file(self, file_path: Path) -> bool:
        """更新文件中的目录"""
        try:
            self.stats["processed"] += 1
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            headers = self.extract_headers(content)
            if not headers:
                self.log(f"跳过 {file_path}: 没有找到标题")
                self.stats["skipped"] += 1
                return False
            
            # 生成新目录
            new_toc = self.generate_toc(headers)
            
            # 检查是否已有目录
            has_toc = False
            for pattern in self.config["toc_patterns"]:
                if re.search(pattern, content, re.MULTILINE):
                    has_toc = True
                    break
            
            # 备份文件
            if not self.backup_file(file_path):
                self.log(f"跳过 {file_path}: 备份失败", "WARNING")
                self.stats["skipped"] += 1
                return False
            
            # 更新或插入目录
            if has_toc:
                # 替换现有目录
                for pattern in self.config["toc_patterns"]:
                    if re.search(pattern, content, re.MULTILINE):
                        updated_content = re.sub(
                            pattern, new_toc, content, count=1, flags=re.MULTILINE
                        )
                        break
                else:
                    updated_content = content
                self.stats["updated"] += 1
                action = "更新"
            else:
                # 插入新目录
                updated_content = self.insert_toc(content, new_toc)
                self.stats["created"] += 1
                action = "创建"
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            self.log(f"✅ {action}目录: {file_path}")
            return True
            
        except Exception as e:
            self.log(f"❌ 处理失败 {file_path}: {e}", "ERROR")
            self.stats["errors"] += 1
            return False
    
    def insert_toc(self, content: str, new_toc: str) -> str:
        """插入目录到合适位置"""
        # 尝试在摘要后插入
        summary_patterns = [
            r'^(## 摘要.*?)(?=##)',
            r'^(## 概述.*?)(?=##)',
            r'^(## 简介.*?)(?=##)',
            r'^(## Abstract.*?)(?=##)'
        ]
        
        for pattern in summary_patterns:
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                return re.sub(
                    pattern, r'\1\n' + new_toc + '\n', content, count=1, flags=re.MULTILINE | re.DOTALL
                )
        
        # 在第一个标题前插入
        first_header_pattern = re.compile(r'^(#{1,6}\s+.+)$', re.MULTILINE)
        match = first_header_pattern.search(content)
        if match:
            pos = match.start()
            return content[:pos] + new_toc + '\n\n' + content[pos:]
        
        # 在文档开头插入
        lines = content.split('\n')
        if len(lines) > 1:
            lines.insert(1, '')
            lines.insert(2, new_toc)
            lines.insert(3, '')
            return '\n'.join(lines)
        else:
            return content + '\n\n' + new_toc + '\n'
    
    def batch_update(self, files: Optional[List[Path]] = None) -> Dict[str, int]:
        """批量更新目录"""
        if files is None:
            files = self.find_markdown_files()
        
        self.log(f"开始处理 {len(files)} 个文件...")
        
        for file_path in files:
            self.update_toc_in_file(file_path)
        
        return self.stats
    
    def validate_toc(self, file_path: Path) -> Dict[str, any]:
        """验证目录质量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            headers = self.extract_headers(content)
            if not headers:
                return {"valid": False, "reason": "没有找到标题"}
            
            # 检查是否有目录
            has_toc = any(re.search(pattern, content, re.MULTILINE) 
                         for pattern in self.config["toc_patterns"])
            
            if not has_toc:
                return {"valid": False, "reason": "缺少目录"}
            
            # 检查目录完整性
            toc_headers = []
            for pattern in self.config["toc_patterns"]:
                match = re.search(pattern, content, re.MULTILINE)
                if match:
                    # 提取目录内容
                    toc_start = match.end()
                    next_header = re.search(r'^#{1,6}\s+', content[toc_start:], re.MULTILINE)
                    if next_header:
                        toc_content = content[toc_start:toc_start + next_header.start()]
                        # 解析目录项
                        toc_items = re.findall(r'\[([^\]]+)\]', toc_content)
                        toc_headers = [item.strip() for item in toc_items]
                    break
            
            # 检查目录与标题的匹配度
            doc_titles = [title for _, title, _ in headers]
            missing_in_toc = [title for title in doc_titles if title not in toc_headers]
            extra_in_toc = [title for title in toc_headers if title not in doc_titles]
            
            return {
                "valid": len(missing_in_toc) == 0 and len(extra_in_toc) == 0,
                "headers_count": len(headers),
                "toc_count": len(toc_headers),
                "missing_in_toc": missing_in_toc,
                "extra_in_toc": extra_in_toc
            }
            
        except Exception as e:
            return {"valid": False, "reason": f"验证失败: {e}"}
    
    def generate_report(self) -> str:
        """生成处理报告"""
        report = f"""# 目录管理处理报告

## 处理统计

- **总处理文件**: {self.stats['processed']}
- **成功更新**: {self.stats['updated']}
- **成功创建**: {self.stats['created']}
- **跳过文件**: {self.stats['skipped']}
- **处理错误**: {self.stats['errors']}

## 处理时间

- **开始时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **处理状态**: {'完成' if self.stats['errors'] == 0 else '部分完成'}

## 配置信息

- **根目录**: {self.root_dir}
- **目录标题**: {self.config['toc_title']}
- **自动备份**: {'启用' if self.config.get('auto_backup') else '禁用'}
- **详细日志**: {'启用' if self.config.get('verbose') else '禁用'}

"""
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='增强版目录管理工具')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--file', help='指定单个文件')
    parser.add_argument('--update', action='store_true', help='更新现有目录')
    parser.add_argument('--create', action='store_true', help='为没有目录的文件创建目录')
    parser.add_argument('--all', action='store_true', help='处理所有文件')
    parser.add_argument('--validate', help='验证指定文件的目录质量')
    parser.add_argument('--config', action='store_true', help='显示当前配置')
    parser.add_argument('--report', action='store_true', help='生成处理报告')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    manager = EnhancedTOCManager(args.root)
    
    if args.verbose:
        manager.config["verbose"] = True
    
    if args.config:
        print("当前配置:")
        print(json.dumps(manager.config, indent=2, ensure_ascii=False))
        return
    
    if args.file:
        # 处理单个文件
        file_path = Path(args.file)
        if args.update or args.create:
            manager.update_toc_in_file(file_path)
        elif args.validate:
            result = manager.validate_toc(file_path)
            print(f"验证结果: {result}")
        else:
            print("请指定 --update, --create 或 --validate 选项")
    elif args.all:
        # 处理所有文件
        if args.update or args.create:
            stats = manager.batch_update()
            print(f"\n处理完成:")
            print(f"✅ 成功: {stats['updated'] + stats['created']}")
            print(f"⏭️ 跳过: {stats['skipped']}")
            print(f"❌ 错误: {stats['errors']}")
        else:
            print("请指定 --update 或 --create 选项")
    else:
        print("请指定处理方式: --file, --all")
        print("使用 --help 查看详细帮助")
    
    if args.report:
        report = manager.generate_report()
        report_file = Path(args.root) / "toc_management_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"处理报告已生成: {report_file}")

if __name__ == "__main__":
    main()
