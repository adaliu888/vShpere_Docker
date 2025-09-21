#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版目录更新工具
不依赖外部库，纯Python实现
"""

import os
import re
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
            if title != "目录":  # 跳过目录标题本身
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
            return False
        
        # 生成新目录
        new_toc = generate_toc(headers)
        
        # 查找并替换现有目录
        toc_pattern = re.compile(r'^## 目录\s*$', re.MULTILINE)
        
        if toc_pattern.search(content):
            # 替换现有目录
            updated_content = toc_pattern.sub(new_toc, content, count=1)
        else:
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
        
        print(f"✅ 已更新目录: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败 {file_path}: {e}")
        return False

def find_markdown_files(root_dir="."):
    """查找所有Markdown文件"""
    md_files = []
    for root, dirs, files in os.walk(root_dir):
        # 跳过隐藏目录和工具目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'tools']
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    return md_files

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("简化版目录更新工具")
        print("用法: python simple_toc_updater.py [目录路径]")
        print("示例: python simple_toc_updater.py .")
        return
    
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    md_files = find_markdown_files(root_dir)
    
    print(f"找到 {len(md_files)} 个Markdown文件")
    
    success_count = 0
    for file_path in md_files:
        if update_toc_in_file(file_path):
            success_count += 1
    
    print(f"\n处理完成: {success_count}/{len(md_files)} 个文件成功更新")

if __name__ == "__main__":
    main()
