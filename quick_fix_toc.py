#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复目录工具
一键解决所有目录问题，无需复杂配置
"""

import os
import re
import sys
from pathlib import Path

def extract_headers(content):
    """提取标题"""
    headers = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # 匹配Markdown标题
        match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            if title not in ["目录", "Table of Contents", "目錄"]:  # 跳过目录标题本身
                headers.append((level, title, i))
    
    return headers

def generate_anchor(title):
    """生成锚点链接"""
    # 移除特殊字符，转换为小写，用连字符连接
    anchor = re.sub(r'[^\w\s-]', '', title.lower())
    anchor = re.sub(r'[-\s]+', '-', anchor)
    return anchor.strip('-')

def generate_toc(headers):
    """生成目录"""
    if not headers:
        return ""
    
    toc_lines = ["## 目录", ""]
    
    for level, title, _ in headers:
        indent = "  " * (level - 1)
        anchor = generate_anchor(title)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    
    toc_lines.append("")
    return "\n".join(toc_lines)

def update_toc_in_file(file_path):
    """更新文件中的目录"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题
        headers = extract_headers(content)
        if not headers:
            print(f"⏭️ 跳过 {file_path}: 没有找到标题")
            return False
        
        # 生成新目录
        new_toc = generate_toc(headers)
        
        # 查找并替换现有目录
        toc_patterns = [
            r'^## 目录\s*$',
            r'^## Table of Contents\s*$',
            r'^## 目錄\s*$'
        ]
        
        has_toc = False
        for pattern in toc_patterns:
            if re.search(pattern, content, re.MULTILINE):
                has_toc = True
                updated_content = re.sub(pattern, new_toc, content, count=1, flags=re.MULTILINE)
                break
        
        if not has_toc:
            # 插入新目录
            # 尝试在摘要后插入
            summary_patterns = [
                r'^(## 摘要.*?)(?=##)',
                r'^(## 概述.*?)(?=##)',
                r'^(## 简介.*?)(?=##)',
                r'^(## Abstract.*?)(?=##)'
            ]
            
            inserted = False
            for pattern in summary_patterns:
                if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                    updated_content = re.sub(
                        pattern, r'\1\n' + new_toc + '\n', content, count=1, flags=re.MULTILINE | re.DOTALL
                    )
                    inserted = True
                    break
            
            if not inserted:
                # 在第一个标题前插入
                first_header_pattern = re.compile(r'^(#{1,6}\s+.+)$', re.MULTILINE)
                match = first_header_pattern.search(content)
                if match:
                    pos = match.start()
                    updated_content = content[:pos] + new_toc + '\n\n' + content[pos:]
                else:
                    # 在文档开头插入
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
        
        action = "更新" if has_toc else "创建"
        print(f"✅ {action}目录: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def find_markdown_files(root_dir="."):
    """查找所有Markdown文件"""
    md_files = []
    exclude_dirs = {".git", "tools", "__pycache__", ".vscode", "node_modules", "venv", "env"}
    exclude_files = {"README.md", "CHANGELOG.md", "LICENSE.md"}
    
    for root, dirs, files in os.walk(root_dir):
        # 过滤排除的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.md') and file not in exclude_files:
                md_files.append(Path(root) / file)
    
    return md_files

def main():
    """主函数"""
    print("🚀 快速修复目录工具")
    print("=" * 50)
    
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    md_files = find_markdown_files(root_dir)
    
    print(f"📁 找到 {len(md_files)} 个Markdown文件")
    print()
    
    success_count = 0
    for file_path in md_files:
        if update_toc_in_file(file_path):
            success_count += 1
    
    print()
    print("=" * 50)
    print(f"🎉 处理完成: {success_count}/{len(md_files)} 个文件成功处理")
    
    if success_count == len(md_files):
        print("✨ 所有文件都已成功处理！")
    elif success_count > 0:
        print("⚠️ 部分文件处理成功")
    else:
        print("❌ 没有文件被处理")

if __name__ == "__main__":
    main()
