#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份和恢复系统
提供文档的自动备份、版本管理和恢复功能
"""

import os
import sys
import shutil
import json
import gzip
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import argparse
import hashlib

class BackupSystem:
    """备份和恢复系统"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.backup_dir = self.root_dir / "tools" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata = self.load_metadata()
        
    def load_metadata(self) -> Dict[str, Any]:
        """加载备份元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  加载备份元数据失败: {e}")
        
        return {
            "backups": {},
            "settings": {
                "max_backups": 10,
                "compression": True,
                "include_git": False,
                "backup_patterns": ["**/*.md", "tools/**/*.py", "tools/**/*.yaml"]
            }
        }
    
    def save_metadata(self) -> bool:
        """保存备份元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存备份元数据失败: {e}")
            return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def get_backup_name(self, backup_type: str = "manual") -> str:
        """生成备份名称"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{backup_type}_{timestamp}"
    
    def create_backup(self, backup_name: str = None, backup_type: str = "manual", 
                     description: str = "") -> bool:
        """创建备份"""
        try:
            if backup_name is None:
                backup_name = self.get_backup_name(backup_type)
            
            backup_path = self.backup_dir / backup_name
            
            # 创建备份目录
            backup_path.mkdir(exist_ok=True)
            
            # 收集要备份的文件
            files_to_backup = self.collect_files_to_backup()
            
            if not files_to_backup:
                print("⚠️  没有找到要备份的文件")
                return False
            
            # 创建备份
            backup_info = {
                "name": backup_name,
                "type": backup_type,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "files": {},
                "total_size": 0,
                "file_count": len(files_to_backup)
            }
            
            for file_path in files_to_backup:
                relative_path = file_path.relative_to(self.root_dir)
                backup_file_path = backup_path / relative_path
                
                # 创建目录
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(file_path, backup_file_path)
                
                # 记录文件信息
                file_info = {
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "hash": self.calculate_file_hash(file_path),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                
                backup_info["files"][str(relative_path)] = file_info
                backup_info["total_size"] += file_info["size"]
            
            # 压缩备份
            if self.metadata["settings"]["compression"]:
                compressed_path = self.backup_dir / f"{backup_name}.tar.gz"
                with tarfile.open(compressed_path, "w:gz") as tar:
                    tar.add(backup_path, arcname=backup_name)
                
                # 删除未压缩的目录
                shutil.rmtree(backup_path)
                backup_path = compressed_path
                backup_info["compressed"] = True
                backup_info["compressed_size"] = backup_path.stat().st_size
            else:
                backup_info["compressed"] = False
            
            # 保存备份信息
            self.metadata["backups"][backup_name] = backup_info
            self.save_metadata()
            
            print(f"✅ 备份创建成功: {backup_name}")
            print(f"   文件数量: {backup_info['file_count']}")
            print(f"   总大小: {self.format_size(backup_info['total_size'])}")
            if backup_info.get("compressed"):
                print(f"   压缩后大小: {self.format_size(backup_info['compressed_size'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建备份失败: {e}")
            return False
    
    def collect_files_to_backup(self) -> List[Path]:
        """收集要备份的文件"""
        files_to_backup = []
        patterns = self.metadata["settings"]["backup_patterns"]
        
        for pattern in patterns:
            for file_path in self.root_dir.glob(pattern):
                if file_path.is_file():
                    # 跳过备份目录本身
                    if "backups" in str(file_path):
                        continue
                    # 跳过Git目录（除非设置包含）
                    if not self.metadata["settings"]["include_git"] and ".git" in str(file_path):
                        continue
                    files_to_backup.append(file_path)
        
        return list(set(files_to_backup))  # 去重
    
    def list_backups(self) -> None:
        """列出所有备份"""
        if not self.metadata["backups"]:
            print("📋 没有找到备份")
            return
        
        print("📋 备份列表:")
        print("=" * 80)
        print(f"{'名称':<30} {'类型':<10} {'创建时间':<20} {'文件数':<8} {'大小':<12}")
        print("-" * 80)
        
        for backup_name, backup_info in sorted(
            self.metadata["backups"].items(), 
            key=lambda x: x[1]["created_at"], 
            reverse=True
        ):
            size = backup_info.get("compressed_size", backup_info["total_size"])
            print(f"{backup_name:<30} {backup_info['type']:<10} "
                  f"{backup_info['created_at'][:19]:<20} "
                  f"{backup_info['file_count']:<8} "
                  f"{self.format_size(size):<12}")
    
    def restore_backup(self, backup_name: str, target_dir: str = None) -> bool:
        """恢复备份"""
        try:
            if backup_name not in self.metadata["backups"]:
                print(f"❌ 备份不存在: {backup_name}")
                return False
            
            backup_info = self.metadata["backups"][back_name]
            
            # 确定备份文件路径
            if backup_info.get("compressed"):
                backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            else:
                backup_file = self.backup_dir / backup_name
            
            if not backup_file.exists():
                print(f"❌ 备份文件不存在: {backup_file}")
                return False
            
            # 确定目标目录
            if target_dir is None:
                target_dir = self.root_dir
            else:
                target_dir = Path(target_dir)
            
            print(f"🔄 恢复备份: {backup_name}")
            print(f"   目标目录: {target_dir}")
            
            # 恢复文件
            if backup_info.get("compressed"):
                # 解压缩备份
                with tarfile.open(backup_file, "r:gz") as tar:
                    tar.extractall(self.backup_dir)
                
                # 复制文件到目标目录
                extracted_dir = self.backup_dir / backup_name
                for file_info in backup_info["files"].values():
                    source_file = extracted_dir / file_info["path"]
                    target_file = target_dir / file_info["path"]
                    
                    if source_file.exists():
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, target_file)
                
                # 清理临时目录
                shutil.rmtree(extracted_dir)
            else:
                # 直接复制文件
                backup_dir = self.backup_dir / backup_name
                for file_info in backup_info["files"].values():
                    source_file = backup_dir / file_info["path"]
                    target_file = target_dir / file_info["path"]
                    
                    if source_file.exists():
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, target_file)
            
            print(f"✅ 备份恢复成功: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ 恢复备份失败: {e}")
            return False
    
    def delete_backup(self, backup_name: str) -> bool:
        """删除备份"""
        try:
            if backup_name not in self.metadata["backups"]:
                print(f"❌ 备份不存在: {backup_name}")
                return False
            
            backup_info = self.metadata["backups"][backup_name]
            
            # 删除备份文件
            if backup_info.get("compressed"):
                backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            else:
                backup_file = self.backup_dir / backup_name
            
            if backup_file.exists():
                if backup_file.is_file():
                    backup_file.unlink()
                else:
                    shutil.rmtree(backup_file)
            
            # 从元数据中删除
            del self.metadata["backups"][backup_name]
            self.save_metadata()
            
            print(f"✅ 备份删除成功: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ 删除备份失败: {e}")
            return False
    
    def cleanup_old_backups(self) -> bool:
        """清理旧备份"""
        try:
            max_backups = self.metadata["settings"]["max_backups"]
            backups = list(self.metadata["backups"].items())
            
            if len(backups) <= max_backups:
                print("📋 备份数量在限制范围内，无需清理")
                return True
            
            # 按创建时间排序，删除最旧的备份
            backups.sort(key=lambda x: x[1]["created_at"])
            to_delete = backups[:-max_backups]
            
            print(f"🧹 清理 {len(to_delete)} 个旧备份...")
            
            for backup_name, _ in to_delete:
                self.delete_backup(backup_name)
            
            print("✅ 旧备份清理完成")
            return True
            
        except Exception as e:
            print(f"❌ 清理旧备份失败: {e}")
            return False
    
    def compare_backups(self, backup1: str, backup2: str) -> None:
        """比较两个备份"""
        try:
            if backup1 not in self.metadata["backups"]:
                print(f"❌ 备份不存在: {backup1}")
                return
            
            if backup2 not in self.metadata["backups"]:
                print(f"❌ 备份不存在: {backup2}")
                return
            
            info1 = self.metadata["backups"][backup1]
            info2 = self.metadata["backups"][backup2]
            
            print(f"📊 比较备份: {backup1} vs {backup2}")
            print("=" * 60)
            
            files1 = set(info1["files"].keys())
            files2 = set(info2["files"].keys())
            
            # 只在备份1中的文件
            only_in_1 = files1 - files2
            # 只在备份2中的文件
            only_in_2 = files2 - files1
            # 两个备份都有的文件
            common = files1 & files2
            
            print(f"只在 {backup1} 中: {len(only_in_1)} 个文件")
            for file_path in sorted(only_in_1):
                print(f"  + {file_path}")
            
            print(f"只在 {backup2} 中: {len(only_in_2)} 个文件")
            for file_path in sorted(only_in_2):
                print(f"  - {file_path}")
            
            # 比较共同文件的差异
            different_files = []
            for file_path in common:
                hash1 = info1["files"][file_path]["hash"]
                hash2 = info2["files"][file_path]["hash"]
                if hash1 != hash2:
                    different_files.append(file_path)
            
            print(f"内容不同的文件: {len(different_files)} 个")
            for file_path in sorted(different_files):
                print(f"  ~ {file_path}")
            
            print(f"相同的文件: {len(common) - len(different_files)} 个")
            
        except Exception as e:
            print(f"❌ 比较备份失败: {e}")
    
    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def auto_backup(self) -> bool:
        """自动备份"""
        try:
            # 检查是否需要自动备份
            last_backup = None
            for backup_info in self.metadata["backups"].values():
                if backup_info["type"] == "auto":
                    if last_backup is None or backup_info["created_at"] > last_backup["created_at"]:
                        last_backup = backup_info
            
            # 如果距离上次自动备份超过24小时，则创建新备份
            if last_backup:
                last_time = datetime.fromisoformat(last_backup["created_at"])
                if datetime.now() - last_time < timedelta(hours=24):
                    print("📋 距离上次自动备份不足24小时，跳过")
                    return True
            
            # 创建自动备份
            return self.create_backup(backup_type="auto", description="自动备份")
            
        except Exception as e:
            print(f"❌ 自动备份失败: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='备份和恢复系统')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--create', help='创建备份')
    parser.add_argument('--list', action='store_true', help='列出备份')
    parser.add_argument('--restore', help='恢复备份')
    parser.add_argument('--delete', help='删除备份')
    parser.add_argument('--cleanup', action='store_true', help='清理旧备份')
    parser.add_argument('--compare', nargs=2, metavar=('BACKUP1', 'BACKUP2'), help='比较备份')
    parser.add_argument('--auto', action='store_true', help='自动备份')
    
    args = parser.parse_args()
    
    backup_system = BackupSystem(args.root)
    
    print("=" * 50)
    print("🚀 备份和恢复系统")
    print("=" * 50)
    
    if args.create:
        backup_system.create_backup(backup_name=args.create)
    elif args.list:
        backup_system.list_backups()
    elif args.restore:
        backup_system.restore_backup(args.restore)
    elif args.delete:
        backup_system.delete_backup(args.delete)
    elif args.cleanup:
        backup_system.cleanup_old_backups()
    elif args.compare:
        backup_system.compare_backups(args.compare[0], args.compare[1])
    elif args.auto:
        backup_system.auto_backup()
    else:
        print("请指定操作")
        print("使用 --help 查看详细帮助")

if __name__ == "__main__":
    main()
