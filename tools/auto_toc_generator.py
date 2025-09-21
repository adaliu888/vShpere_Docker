#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化目录生成工具
解决手工修改目录的问题，实现主题修改时目录自动生成和更新
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import markdown
from markdown.extensions import toc

class AutoTOCGenerator:
    """自动化目录生成器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.md_files = []
        self.toc_pattern = re.compile(r'^## 目录\s*$', re.MULTILINE)
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
    def find_markdown_files(self) -> List[Path]:
        """查找所有Markdown文件"""
        md_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过隐藏目录和工具目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'tools']
            for file in files:
                if file.endswith('.md'):
                    md_files.append(Path(root) / file)
        return md_files
    
    def extract_headers(self, content: str) -> List[Tuple[int, str, str]]:
        """提取标题信息"""
        headers = []
        for match in self.header_pattern.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            # 跳过目录标题本身
            if title != "目录":
                headers.append((level, title, match.group(0)))
        return headers
    
    def generate_toc(self, headers: List[Tuple[int, str, str]]) -> str:
        """生成目录"""
        if not headers:
            return ""
        
        toc_lines = ["## 目录", ""]
        current_level = 1
        
        for level, title, _ in headers:
            # 调整缩进
            if level > current_level:
                # 增加缩进
                for _ in range(level - current_level):
                    pass
            elif level < current_level:
                # 减少缩进
                pass
            
            # 生成目录项
            indent = "  " * (level - 1)
            anchor = self.generate_anchor(title)
            toc_lines.append(f"{indent}- [{title}](#{anchor})")
            current_level = level
        
        toc_lines.append("")
        return "\n".join(toc_lines)
    
    def generate_anchor(self, title: str) -> str:
        """生成锚点链接"""
        # 移除特殊字符，转换为小写，用连字符连接
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        anchor = re.sub(r'[-\s]+', '-', anchor)
        return anchor.strip('-')
    
    def update_toc_in_file(self, file_path: Path) -> bool:
        """更新文件中的目录"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            headers = self.extract_headers(content)
            if not headers:
                return False
            
            # 生成新目录
            new_toc = self.generate_toc(headers)
            
            # 查找并替换现有目录
            if self.toc_pattern.search(content):
                # 替换现有目录
                updated_content = self.toc_pattern.sub(
                    new_toc, content, count=1
                )
            else:
                # 在摘要后插入目录
                summary_pattern = re.compile(r'^(## 摘要.*?)(?=##)', re.MULTILINE | re.DOTALL)
                if summary_pattern.search(content):
                    updated_content = summary_pattern.sub(
                        r'\1\n' + new_toc + '\n', content, count=1
                    )
                else:
                    # 在文档开头插入目录
                    updated_content = content.replace(
                        content.split('\n')[0] + '\n',
                        content.split('\n')[0] + '\n\n' + new_toc + '\n'
                    )
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已更新目录: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 更新失败 {file_path}: {e}")
            return False
    
    def batch_update_toc(self, files: List[Path] = None) -> Dict[str, int]:
        """批量更新目录"""
        if files is None:
            files = self.find_markdown_files()
        
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for file_path in files:
            if self.update_toc_in_file(file_path):
                results["success"] += 1
            else:
                results["skipped"] += 1
        
        return results
    
    def create_toc_template(self, file_path: Path) -> bool:
        """为没有目录的文件创建目录模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已有目录
            if self.toc_pattern.search(content):
                return False
            
            # 提取标题
            headers = self.extract_headers(content)
            if not headers:
                return False
            
            # 生成目录
            new_toc = self.generate_toc(headers)
            
            # 在摘要后插入目录
            summary_pattern = re.compile(r'^(## 摘要.*?)(?=##)', re.MULTILINE | re.DOTALL)
            if summary_pattern.search(content):
                updated_content = summary_pattern.sub(
                    r'\1\n' + new_toc + '\n', content, count=1
                )
            else:
                # 在文档开头插入目录
                lines = content.split('\n')
                if len(lines) > 1:
                    lines.insert(1, '')
                    lines.insert(2, new_toc)
                    lines.insert(3, '')
                    updated_content = '\n'.join(lines)
                else:
                    updated_content = content + '\n\n' + new_toc + '\n'
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"✅ 已创建目录: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 创建失败 {file_path}: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自动化目录生成工具')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--file', help='指定单个文件')
    parser.add_argument('--create', action='store_true', help='为没有目录的文件创建目录')
    parser.add_argument('--update', action='store_true', help='更新现有目录')
    parser.add_argument('--all', action='store_true', help='处理所有文件')
    
    args = parser.parse_args()
    
    generator = AutoTOCGenerator(args.root)
    
    if args.file:
        # 处理单个文件
        file_path = Path(args.file)
        if args.create:
            generator.create_toc_template(file_path)
        elif args.update:
            generator.update_toc_in_file(file_path)
        else:
            print("请指定 --create 或 --update 选项")
    elif args.all:
        # 处理所有文件
        if args.create:
            files = generator.find_markdown_files()
            results = {"success": 0, "failed": 0, "skipped": 0}
            for file_path in files:
                if generator.create_toc_template(file_path):
                    results["success"] += 1
                else:
                    results["skipped"] += 1
        elif args.update:
            results = generator.batch_update_toc()
        else:
            print("请指定 --create 或 --update 选项")
            return
        
        print(f"\n📊 处理结果:")
        print(f"✅ 成功: {results['success']}")
        print(f"⏭️  跳过: {results['skipped']}")
        if 'failed' in results:
            print(f"❌ 失败: {results['failed']}")
    else:
        print("请指定处理方式: --file, --all")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()
