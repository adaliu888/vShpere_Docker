#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档生成器
自动生成项目文档、API文档、用户手册等
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import argparse
import re

class DocumentationGenerator:
    """文档生成器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.tools_dir = self.root_dir / "tools"
        self.docs_dir = self.root_dir / "docs"
        self.templates_dir = self.tools_dir / "templates"
        
    def create_docs_structure(self) -> bool:
        """创建文档目录结构"""
        try:
            directories = [
                "docs",
                "docs/guides",
                "docs/api",
                "docs/examples",
                "docs/templates",
                "docs/images"
            ]
            
            for dir_path in directories:
                full_path = self.root_dir / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ 创建目录: {dir_path}")
            
            return True
        except Exception as e:
            print(f"❌ 创建文档目录结构失败: {e}")
            return False
    
    def generate_api_documentation(self) -> bool:
        """生成API文档"""
        try:
            api_doc_content = '''# API文档

## 概述

本文档描述了文档自动化管理系统的API接口。

## 核心模块

### 1. SimpleTOCUpdater

简化版目录更新工具。

#### 主要方法

##### `__init__(root_dir: str = ".")`
初始化目录更新器。

**参数:**
- `root_dir`: 根目录路径，默认为当前目录

##### `find_markdown_files() -> List[Path]`
查找所有Markdown文件。

**返回值:**
- `List[Path]`: Markdown文件路径列表

##### `extract_headers(content: str) -> List[Tuple[int, str, str]]`
提取标题信息。

**参数:**
- `content`: 文档内容

**返回值:**
- `List[Tuple[int, str, str]]`: 标题信息列表 (级别, 标题, 原始内容)

##### `generate_toc(headers: List[Tuple[int, str, str]]) -> str`
生成目录。

**参数:**
- `headers`: 标题信息列表

**返回值:**
- `str`: 生成的目录内容

##### `update_toc_in_file(file_path: Path) -> bool`
更新文件中的目录。

**参数:**
- `file_path`: 文件路径

**返回值:**
- `bool`: 更新是否成功

##### `batch_update_toc() -> Dict[str, int]`
批量更新目录。

**返回值:**
- `Dict[str, int]`: 处理结果统计

### 2. DocumentAutomation

文档自动化管理系统。

#### 主要方法

##### `__init__(root_dir: str = ".")`
初始化文档自动化系统。

**参数:**
- `root_dir`: 根目录路径

##### `load_config() -> Dict[str, Any]`
加载配置文件。

**返回值:**
- `Dict[str, Any]`: 配置信息

##### `validate_document(file_path: Path) -> Dict[str, Any]`
验证单个文档。

**参数:**
- `file_path`: 文档路径

**返回值:**
- `Dict[str, Any]`: 验证结果

##### `batch_validate() -> Dict[str, Any]`
批量验证所有文档。

**返回值:**
- `Dict[str, Any]`: 批量验证结果

##### `fix_document(file_path: Path) -> bool`
修复单个文档。

**参数:**
- `file_path`: 文档路径

**返回值:**
- `bool`: 修复是否成功

##### `create_template(file_path: Path, title: str) -> bool`
创建文档模板。

**参数:**
- `file_path`: 模板文件路径
- `title`: 文档标题

**返回值:**
- `bool`: 创建是否成功

### 3. ComprehensiveAutomation

综合自动化管理系统。

#### 主要方法

##### `__init__(root_dir: str = ".")`
初始化综合自动化系统。

**参数:**
- `root_dir`: 根目录路径

##### `quick_update() -> bool`
快速更新模式。

**返回值:**
- `bool`: 更新是否成功

##### `full_automation() -> bool`
完整自动化流程。

**返回值:**
- `bool`: 流程是否成功

##### `maintenance_mode() -> bool`
维护模式。

**返回值:**
- `bool`: 维护是否成功

##### `interactive_mode() -> None`
交互模式。

## 配置文件

### doc_config.yaml

文档自动化管理配置文件。

#### 主要配置项

##### document_structure
文档结构配置。

- `required_sections`: 必需章节列表
- `min_sections`: 最小章节数量
- `min_code_examples`: 最小代码示例数量
- `require_toc`: 是否要求目录
- `require_abstract`: 是否要求摘要

##### quality_checks
质量检查配置。

- `min_word_count`: 最小字数
- `max_line_length`: 最大行长度
- `require_code_language`: 是否要求代码块有语言标识
- `check_links`: 是否检查链接

##### format_rules
格式规则配置。

- `fix_headers`: 是否修复标题格式
- `fix_lists`: 是否修复列表格式
- `fix_code_blocks`: 是否修复代码块格式
- `fix_spacing`: 是否修复间距

## 使用示例

### 基本使用

```python
from tools.simple_toc_updater import SimpleTOCUpdater

# 创建更新器
updater = SimpleTOCUpdater(".")

# 批量更新目录
results = updater.batch_update_toc()
print(f"成功更新: {results['success']} 个文件")
```

### 文档验证

```python
from tools.document_automation import DocumentAutomation

# 创建自动化系统
automation = DocumentAutomation(".")

# 验证文档质量
results = automation.batch_validate()
print(f"验证完成: {results['summary']['total_files']} 个文件")
```

### 综合自动化

```python
from tools.comprehensive_automation import ComprehensiveAutomation

# 创建综合系统
comprehensive = ComprehensiveAutomation(".")

# 运行完整自动化流程
success = comprehensive.full_automation()
if success:
    print("自动化流程完成")
```

## 错误处理

### 常见错误

1. **文件编码错误**
   - 错误: `'utf-8' codec can't decode byte`
   - 解决: 确保文件使用UTF-8编码

2. **权限错误**
   - 错误: `Permission denied`
   - 解决: 检查文件写入权限

3. **依赖缺失**
   - 错误: `ModuleNotFoundError`
   - 解决: 安装所需依赖或使用简化版工具

### 错误处理最佳实践

```python
try:
    # 执行操作
    result = updater.update_toc_in_file(file_path)
    if result:
        print(f"✅ 更新成功: {file_path}")
    else:
        print(f"⚠️  跳过: {file_path}")
except Exception as e:
    print(f"❌ 更新失败 {file_path}: {e}")
```

## 性能优化

### 批量处理优化

- 使用批量处理而不是单个文件处理
- 并行处理多个文件
- 缓存重复计算结果

### 内存优化

- 流式处理大文件
- 及时释放不需要的对象
- 使用生成器而不是列表

## 扩展开发

### 添加新的验证规则

```python
def custom_validation_rule(content: str) -> List[str]:
    """自定义验证规则"""
    issues = []
    # 实现验证逻辑
    return issues
```

### 添加新的格式修复

```python
def custom_format_fix(content: str) -> str:
    """自定义格式修复"""
    # 实现修复逻辑
    return fixed_content
```

---

**API文档版本**: v1.0  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
            
            api_doc_path = self.docs_dir / "api" / "README.md"
            with open(api_doc_path, 'w', encoding='utf-8') as f:
                f.write(api_doc_content)
            
            print("✅ API文档生成成功")
            return True
            
        except Exception as e:
            print(f"❌ 生成API文档失败: {e}")
            return False
    
    def generate_user_guide(self) -> bool:
        """生成用户指南"""
        try:
            user_guide_content = '''# 用户指南

## 快速开始

### 1. 环境准备

#### 系统要求
- Python 3.8+
- 操作系统: Windows, Linux, macOS
- 内存: 至少512MB可用内存
- 磁盘: 至少100MB可用空间

#### 安装Python
如果系统没有Python，请从 [python.org](https://www.python.org/downloads/) 下载安装。

#### 安装UV (推荐)
```bash
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 项目设置

#### 克隆项目
```bash
git clone <repository-url>
cd document-automation
```

#### 安装依赖
```bash
# 使用UV (推荐)
uv sync

# 或使用pip
pip install -r requirements.txt
```

#### 运行设置脚本
```bash
uv run python tools/project_setup.py
```

### 3. 基本使用

#### 快速更新目录
```bash
# 更新所有文档的目录
uv run python tools/simple_toc_updater.py .
```

#### 验证文档质量
```bash
# 验证所有文档
uv run python tools/document_automation.py --validate

# 生成质量报告
uv run python tools/document_automation.py --report
```

#### 使用综合系统
```bash
# 交互模式
uv run python tools/comprehensive_automation.py

# 快速模式
uv run python tools/comprehensive_automation.py --mode quick
```

## 详细功能

### 目录管理

#### 自动生成目录
系统会自动从Markdown文档中提取标题，并生成标准的目录结构。

**支持的标题格式:**
```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
```

**生成的目录格式:**
```markdown
## 目录

- [一级标题](#一级标题)
  - [二级标题](#二级标题)
    - [三级标题](#三级标题)
```

#### 目录更新策略
- **替换模式**: 替换现有目录
- **创建模式**: 为没有目录的文档创建目录
- **智能模式**: 自动检测并选择合适的方式

### 质量检查

#### 结构检查
- 检查必需章节是否存在
- 验证章节数量是否满足要求
- 检查目录是否完整

#### 格式检查
- 验证标题格式是否正确
- 检查列表格式是否统一
- 确保代码块有语言标识

#### 内容检查
- 统计文档字数
- 检查代码示例数量
- 验证链接是否有效

### 格式修复

#### 自动修复功能
- 修复标题格式问题
- 统一列表格式
- 确保代码块有语言标识
- 修复段落间距

#### 修复策略
- **保守模式**: 只修复明显的格式问题
- **积极模式**: 全面修复所有格式问题
- **自定义模式**: 根据配置进行修复

## 配置管理

### 配置文件

配置文件位于 `tools/doc_config.yaml`，包含以下主要部分：

#### 文档结构配置
```yaml
document_structure:
  required_sections:
    - "摘要"
    - "目录"
    - "理论基础"
  min_sections: 5
  min_code_examples: 2
  require_toc: true
  require_abstract: true
```

#### 质量检查配置
```yaml
quality_checks:
  min_word_count: 500
  max_line_length: 120
  require_code_language: true
  check_links: true
```

#### 格式规则配置
```yaml
format_rules:
  fix_headers: true
  fix_lists: true
  fix_code_blocks: true
  fix_spacing: true
```

### 自定义配置

#### 添加必需章节
```yaml
document_structure:
  required_sections:
    - "摘要"
    - "目录"
    - "理论基础"
    - "技术实现"
    - "实践应用"
    - "最佳实践"
    - "总结"
    - "参考文献"  # 新增章节
```

#### 调整质量要求
```yaml
quality_checks:
  min_word_count: 1000  # 提高字数要求
  max_line_length: 100  # 降低行长度限制
```

## 高级功能

### 批量处理

#### 批量更新目录
```bash
# 更新所有文档
uv run python tools/simple_toc_updater.py .

# 指定目录
uv run python tools/simple_toc_updater.py /path/to/docs
```

#### 批量验证质量
```bash
# 验证所有文档
uv run python tools/document_automation.py --validate

# 生成详细报告
uv run python tools/document_automation.py --report
```

### 模板管理

#### 创建文档模板
```bash
# 创建新文档模板
uv run python tools/document_automation.py --template "新文档.md" "文档标题"
```

#### 使用模板
生成的模板包含标准的文档结构，可以直接使用。

### 集成开发

#### Git钩子集成
系统可以自动创建Git钩子，在提交时自动检查文档质量。

```bash
# 设置Git钩子
uv run python tools/ci_cd_integration.py --setup
```

#### CI/CD集成
支持GitHub Actions等CI/CD平台，自动运行文档检查。

## 故障排除

### 常见问题

#### 1. Python未找到
**问题**: 提示"Python未找到"
**解决**: 
- 确保Python已正确安装
- 检查PATH环境变量
- 使用完整路径运行Python

#### 2. 依赖包缺失
**问题**: 提示"模块未找到"
**解决**:
- 使用简化版工具（无需额外依赖）
- 安装所需依赖包
- 使用UV管理依赖

#### 3. 文件权限问题
**问题**: 无法写入文件
**解决**:
- 检查文件权限
- 以管理员身份运行
- 检查磁盘空间

#### 4. 编码问题
**问题**: 中文显示乱码
**解决**:
- 确保文件使用UTF-8编码
- 检查系统编码设置
- 使用支持UTF-8的编辑器

### 调试模式

#### 启用详细输出
```bash
# 显示详细处理信息
uv run python tools/simple_toc_updater.py . 2>&1 | tee debug.log
```

#### 检查系统状态
```bash
# 查看系统状态
uv run python tools/comprehensive_automation.py --mode status
```

## 最佳实践

### 日常使用

1. **定期维护**
   - 每周运行一次快速更新
   - 每月运行一次完整检查
   - 新文档创建后立即更新目录

2. **质量保证**
   - 提交前运行质量检查
   - 关注质量报告中的问题
   - 及时修复发现的问题

3. **版本控制**
   - 使用Git管理文档版本
   - 重要修改前创建备份
   - 记录重要变更

### 团队协作

1. **统一标准**
   - 制定文档编写标准
   - 统一使用自动化工具
   - 定期培训团队成员

2. **流程规范**
   - 建立文档审查流程
   - 使用CI/CD自动检查
   - 定期评估和改进

3. **工具集成**
   - 集成到开发流程
   - 自动化质量检查
   - 持续改进工具

## 技术支持

### 获取帮助

1. **查看文档**
   - 阅读用户指南
   - 查看API文档
   - 参考示例代码

2. **社区支持**
   - 提交Issue
   - 参与讨论
   - 贡献代码

3. **专业支持**
   - 联系技术支持
   - 定制开发服务
   - 培训服务

### 贡献指南

1. **报告问题**
   - 详细描述问题
   - 提供复现步骤
   - 包含系统信息

2. **提交改进**
   - Fork项目
   - 创建功能分支
   - 提交Pull Request

3. **代码规范**
   - 遵循代码风格
   - 添加测试用例
   - 更新文档

---

**用户指南版本**: v1.0  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
            
            user_guide_path = self.docs_dir / "guides" / "user_guide.md"
            with open(user_guide_path, 'w', encoding='utf-8') as f:
                f.write(user_guide_content)
            
            print("✅ 用户指南生成成功")
            return True
            
        except Exception as e:
            print(f"❌ 生成用户指南失败: {e}")
            return False
    
    def generate_examples(self) -> bool:
        """生成示例文档"""
        try:
            examples = [
                {
                    "name": "basic_usage.md",
                    "title": "基本使用示例",
                    "content": '''# 基本使用示例

## 快速开始

### 1. 更新单个文档目录

```python
from tools.simple_toc_updater import SimpleTOCUpdater

# 创建更新器
updater = SimpleTOCUpdater(".")

# 更新指定文件
file_path = Path("example.md")
success = updater.update_toc_in_file(file_path)
if success:
    print("目录更新成功")
```

### 2. 批量更新所有文档

```python
# 批量更新
results = updater.batch_update_toc()
print(f"成功: {results['success']}, 跳过: {results['skipped']}")
```

### 3. 验证文档质量

```python
from tools.document_automation import DocumentAutomation

# 创建自动化系统
automation = DocumentAutomation(".")

# 验证单个文档
file_path = Path("example.md")
result = automation.validate_document(file_path)
print(f"问题数量: {result['total_issues']}")
```

## 命令行使用

### 基本命令

```bash
# 更新目录
uv run python tools/simple_toc_updater.py .

# 验证质量
uv run python tools/document_automation.py --validate

# 生成报告
uv run python tools/document_automation.py --report
```

### 高级命令

```bash
# 交互模式
uv run python tools/comprehensive_automation.py

# 快速模式
uv run python tools/comprehensive_automation.py --mode quick

# 完整模式
uv run python tools/comprehensive_automation.py --mode full
```
'''
                },
                {
                    "name": "advanced_usage.md",
                    "title": "高级使用示例",
                    "content": '''# 高级使用示例

## 自定义配置

### 1. 修改配置文件

```yaml
# tools/doc_config.yaml
document_structure:
  required_sections:
    - "摘要"
    - "目录"
    - "技术分析"
    - "实现方案"
    - "测试验证"
    - "总结"
  min_sections: 6
  min_code_examples: 3

quality_checks:
  min_word_count: 1000
  max_line_length: 100
  require_code_language: true
```

### 2. 自定义验证规则

```python
def custom_validation(content: str) -> List[str]:
    """自定义验证规则"""
    issues = []
    
    # 检查是否包含特定关键词
    if "TODO" in content:
        issues.append("文档包含未完成的TODO项")
    
    # 检查代码块数量
    code_blocks = content.count("```")
    if code_blocks < 4:
        issues.append("代码示例数量不足")
    
    return issues
```

## 集成开发

### 1. Git钩子集成

```bash
# 设置Git钩子
uv run python tools/ci_cd_integration.py --setup

# 手动运行CI流程
uv run python tools/ci_cd_integration.py --run-ci
```

### 2. 自动化脚本

```python
#!/usr/bin/env python3
"""自动化文档处理脚本"""

from tools.comprehensive_automation import ComprehensiveAutomation

def main():
    automation = ComprehensiveAutomation(".")
    
    # 运行完整自动化流程
    success = automation.full_automation()
    
    if success:
        print("✅ 文档处理完成")
        return 0
    else:
        print("❌ 文档处理失败")
        return 1

if __name__ == "__main__":
    exit(main())
```

## 性能优化

### 1. 并行处理

```python
import concurrent.futures
from pathlib import Path

def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    updater = SimpleTOCUpdater(".")
    return updater.update_toc_in_file(file_path)

def batch_process_parallel(files: List[Path]) -> Dict[str, int]:
    """并行批量处理"""
    results = {"success": 0, "failed": 0}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_file = {executor.submit(process_file, f): f for f in files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            if future.result():
                results["success"] += 1
            else:
                results["failed"] += 1
    
    return results
```

### 2. 缓存优化

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=128)
def get_file_hash(file_path: str) -> str:
    """获取文件哈希值"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def should_update_file(file_path: Path) -> bool:
    """判断文件是否需要更新"""
    current_hash = get_file_hash(str(file_path))
    # 检查缓存中的哈希值
    # 如果相同则跳过更新
    return True  # 简化示例
```
'''
                }
            ]
            
            for example in examples:
                example_path = self.docs_dir / "examples" / example["name"]
                with open(example_path, 'w', encoding='utf-8') as f:
                    f.write(example["content"])
                print(f"✅ 生成示例: {example['name']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 生成示例文档失败: {e}")
            return False
    
    def generate_index(self) -> bool:
        """生成文档索引"""
        try:
            index_content = f'''# 文档索引

## 概述

本文档索引提供了文档自动化管理系统的完整文档导航。

## 主要文档

### 用户文档
- [用户指南](guides/user_guide.md) - 完整的用户使用指南
- [快速开始](guides/quick_start.md) - 快速上手指南
- [配置说明](guides/configuration.md) - 详细配置说明

### API文档
- [API参考](api/README.md) - 完整的API文档
- [模块文档](api/modules.md) - 模块详细说明
- [接口规范](api/interfaces.md) - 接口规范文档

### 示例文档
- [基本使用示例](examples/basic_usage.md) - 基本使用示例
- [高级使用示例](examples/advanced_usage.md) - 高级使用示例
- [集成示例](examples/integration.md) - 集成开发示例

### 开发文档
- [开发指南](development/README.md) - 开发指南
- [贡献指南](development/contributing.md) - 贡献指南
- [发布说明](development/releases.md) - 发布说明

## 工具文档

### 核心工具
- [simple_toc_updater.py](../tools/simple_toc_updater.py) - 简化版目录更新工具
- [document_automation.py](../tools/document_automation.py) - 文档自动化管理系统
- [comprehensive_automation.py](../tools/comprehensive_automation.py) - 综合自动化管理系统

### 辅助工具
- [project_setup.py](../tools/project_setup.py) - 项目初始化设置
- [ci_cd_integration.py](../tools/ci_cd_integration.py) - CI/CD集成
- [documentation_generator.py](../tools/documentation_generator.py) - 文档生成器

### 配置文件
- [doc_config.yaml](../tools/doc_config.yaml) - 文档配置文件
- [pyproject.toml](../pyproject.toml) - 项目配置文件
- [requirements.txt](../requirements.txt) - 依赖列表

## 快速导航

### 新用户
1. 阅读 [用户指南](guides/user_guide.md)
2. 查看 [基本使用示例](examples/basic_usage.md)
3. 运行 [快速开始](guides/quick_start.md)

### 开发者
1. 阅读 [开发指南](development/README.md)
2. 查看 [API文档](api/README.md)
3. 参考 [高级使用示例](examples/advanced_usage.md)

### 管理员
1. 阅读 [配置说明](guides/configuration.md)
2. 查看 [CI/CD集成](ci_cd_integration.md)
3. 参考 [部署指南](deployment/README.md)

## 文档结构

```
docs/
├── guides/           # 用户指南
├── api/             # API文档
├── examples/        # 示例文档
├── development/     # 开发文档
├── deployment/      # 部署文档
└── images/          # 图片资源
```

## 更新日志

### v1.0 ({datetime.now().strftime('%Y-%m-%d')})
- ✅ 创建基础文档结构
- ✅ 生成用户指南
- ✅ 生成API文档
- ✅ 创建示例文档
- ✅ 建立文档索引

## 贡献

欢迎为文档做出贡献：

1. 报告文档问题
2. 改进文档内容
3. 添加新的示例
4. 翻译文档

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 讨论交流: [Discussions]

---

**文档索引版本**: v1.0  
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
            
            index_path = self.docs_dir / "README.md"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            print("✅ 文档索引生成成功")
            return True
            
        except Exception as e:
            print(f"❌ 生成文档索引失败: {e}")
            return False
    
    def generate_all_documentation(self) -> bool:
        """生成所有文档"""
        print("🚀 开始生成文档...")
        
        # 创建文档目录结构
        if not self.create_docs_structure():
            return False
        
        # 生成各种文档
        steps = [
            ("生成API文档", self.generate_api_documentation),
            ("生成用户指南", self.generate_user_guide),
            ("生成示例文档", self.generate_examples),
            ("生成文档索引", self.generate_index)
        ]
        
        for step_name, step_func in steps:
            print(f"🔄 {step_name}...")
            if not step_func():
                print(f"❌ {step_name}失败")
                return False
            print(f"✅ {step_name}完成")
        
        print("🎉 所有文档生成完成！")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='文档生成器')
    parser.add_argument('--root', default='.', help='根目录路径')
    parser.add_argument('--api', action='store_true', help='生成API文档')
    parser.add_argument('--guide', action='store_true', help='生成用户指南')
    parser.add_argument('--examples', action='store_true', help='生成示例文档')
    parser.add_argument('--index', action='store_true', help='生成文档索引')
    parser.add_argument('--all', action='store_true', help='生成所有文档')
    
    args = parser.parse_args()
    
    generator = DocumentationGenerator(args.root)
    
    print("=" * 50)
    print("🚀 文档生成器")
    print("=" * 50)
    
    if args.all:
        success = generator.generate_all_documentation()
    elif args.api:
        success = generator.generate_api_documentation()
    elif args.guide:
        success = generator.generate_user_guide()
    elif args.examples:
        success = generator.generate_examples()
    elif args.index:
        success = generator.generate_index()
    else:
        print("请指定要生成的文档类型")
        print("使用 --help 查看详细帮助")
        return 1
    
    if success:
        print("✅ 文档生成完成")
        return 0
    else:
        print("❌ 文档生成失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
