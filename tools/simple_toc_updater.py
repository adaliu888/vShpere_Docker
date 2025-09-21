#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版目录更新工具
无需额外依赖，直接使用Python标准库
解决目录手工修改问题
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

class SimpleTOCUpdater:
    """简化版目录更新器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
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
        
        toc_lines = ["## 目录", ""]
        
        for level, title, _ in headers:
            # 生成目录项
            indent = "  " * (level - 1)
            anchor = self.generate_anchor(title)
            toc_lines.append(f"{indent}- [{title}](#{anchor})")
        
        toc_lines.append("")
        return "\n".join(toc_lines)
    
    def update_toc_in_file(self, file_path: Path) -> bool:
        """更新文件中的目录"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            headers = self.extract_headers(content)
            if not headers:
                print(f"⚠️  跳过 {file_path}: 没有找到标题")
                return False
            
            # 生成新目录
            new_toc = self.generate_toc(headers)
            
            # 查找并替换现有目录
            if self.toc_pattern.search(content):
                # 替换现有目录
                updated_content = self.toc_pattern.sub(
                    new_toc, content, count=1
                )
                print(f"✅ 已更新目录: {file_path}")
            else:
                # 在摘要后插入目录
                summary_pattern = re.compile(r'^(## 摘要.*?)(?=##)', re.MULTILINE | re.DOTALL)
                if summary_pattern.search(content):
                    updated_content = summary_pattern.sub(
                        r'\1\n' + new_toc + '\n', content, count=1
                    )
                    print(f"✅ 已创建目录: {file_path}")
                else:
                    # 在文档开头插入目录
                    lines = content.split('\n')
                    if len(lines) > 1:
                        lines.insert(1, '')
                        lines.insert(2, new_toc)
                        lines.insert(3, '')
                        updated_content = '\n'.join(lines)
                        print(f"✅ 已创建目录: {file_path}")
                    else:
                        updated_content = content + '\n\n' + new_toc + '\n'
                        print(f"✅ 已创建目录: {file_path}")
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return True
            
        except Exception as e:
            print(f"❌ 更新失败 {file_path}: {e}")
            return False
    
    def batch_update_toc(self) -> Dict[str, int]:
        """批量更新目录"""
        files = self.find_markdown_files()
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        print(f"🔍 找到 {len(files)} 个Markdown文件")
        print("=" * 50)
        
        for file_path in files:
            if self.update_toc_in_file(file_path):
                results["success"] += 1
            else:
                results["skipped"] += 1
        
        return results

def main():
    """主函数"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "."
    
    print("🚀 启动简化版目录更新工具")
    print(f"📁 工作目录: {root_dir}")
    print("=" * 50)
    
    updater = SimpleTOCUpdater(root_dir)
    results = updater.batch_update_toc()
    
    print("=" * 50)
    print("📊 处理结果:")
    print(f"✅ 成功: {results['success']}")
    print(f"⏭️  跳过: {results['skipped']}")
    print(f"❌ 失败: {results['failed']}")
    
    if results['success'] > 0:
        print("\n🎉 目录更新完成！现在所有文档都有自动生成的目录了。")
    else:
        print("\n⚠️  没有文件被更新。请检查文件路径和内容。")

if __name__ == "__main__":
    main()