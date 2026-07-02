---
name: frontmatter-parser
layer: identity
category: knowledge
status: unverified
description: >
  解析 YAML frontmatter，提取 Markdown 文件元数据。
  当用户需要读取文件头信息、提取文档属性、处理静态网站元数据时触发。
  关键词：YAML 解析、frontmatter、元数据提取、Markdown 头部、文档属性。
---

# Frontmatter 解析器

解析 Markdown 文件中的 YAML frontmatter，提取结构化元数据。

## 功能特性

- 解析 YAML frontmatter（`---` 包围的内容）
- 支持嵌套 YAML 结构
- 提取标题、作者、日期、标签等元数据
- 处理多行字符串和特殊字符
- 支持自定义分隔符
- 错误容忍（无效 YAML 不会崩溃）
- 支持批量处理多个文件

## 前置条件

- Python 3.7+
- pyyaml 库

## 安装步骤

### 安装依赖

```bash
pip install pyyaml>=6.0.0
```

### 验证安装

```bash
python -c "import yaml; print(yaml.__version__)"
```

## 使用方法

### 基础用法

```python
import yaml
from typing import Dict, Any, Optional, Tuple

def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    解析 Markdown 文件的 frontmatter
    
    Args:
        content: 文件内容（字符串）
        
    Returns:
        (元数据字典, 正文内容)
    """
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_yaml = parts[1].strip()
            body = parts[2].strip()
            
            try:
                metadata = yaml.safe_load(frontmatter_yaml) or {}
                return metadata, body
            except yaml.YAMLError:
                return {}, content
    
    return {}, content

# 使用示例
if __name__ == "__main__":
    sample_content = """---
title: Python 入门指南
author: 张三
date: 2024-01-15
tags:
  - Python
  - 编程
  - 教程
categories:
  - 技术
  - 学习
---

# Python 入门指南

本文将介绍 Python 的基础知识。

## 安装 Python

...（正文内容）
"""
    
    metadata, body = parse_frontmatter(sample_content)
    
    print("元数据：")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    print("\n正文预览：")
    print(body[:100] + "...")
```

### 高级用法：完整解析器类

```python
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FrontmatterData:
    """Frontmatter 数据结构"""
    metadata: Dict[str, Any]
    body: str
    raw_frontmatter: str
    line_count: int
    has_frontmatter: bool

class FrontmatterParser:
    """Frontmatter 解析器"""
    
    DEFAULT_SEPARATOR = '---'
    
    def __init__(self, separator: str = '---'):
        """
        初始化解析器
        
        Args:
            separator: frontmatter 分隔符（默认 '---'）
        """
        self.separator = separator
        self._compiled_pattern = re.compile(
            rf'^{re.escape(separator)}\s*\n(.*?)\n{re.escape(separator)}\s*\n',
            re.DOTALL | re.MULTILINE
        )
    
    def parse(self, content: str) -> FrontmatterData:
        """
        解析内容字符串
        
        Args:
            content: 文件内容
            
        Returns:
            FrontmatterData 对象
        """
        match = self._compiled_pattern.match(content)
        
        if not match:
            return FrontmatterData(
                metadata={},
                body=content,
                raw_frontmatter="",
                line_count=content.count('\n') + 1,
                has_frontmatter=False
            )
        
        raw_frontmatter = match.group(1)
        body = content[match.end():]
        
        try:
            metadata = yaml.safe_load(raw_frontmatter) or {}
        except yaml.YAMLError as e:
            metadata = {"_error": str(e)}
        
        return FrontmatterData(
            metadata=metadata,
            body=body.strip(),
            raw_frontmatter=raw_frontmatter,
            line_count=body.count('\n') + 1,
            has_frontmatter=True
        )
    
    def parse_file(self, file_path: Union[str, Path]) -> FrontmatterData:
        """
        解析文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            FrontmatterData 对象
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件未找到: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse(content)
    
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        快速提取元数据
        
        Args:
            content: 文件内容
            
        Returns:
            元数据字典
        """
        data = self.parse(content)
        return data.metadata
    
    def extract_field(self, content: str, field: str, default: Any = None) -> Any:
        """
        提取单个字段
        
        Args:
            content: 文件内容
            field: 字段名（支持点号分隔，如 'author.name'）
            default: 默认值
            
        Returns:
            字段值
        """
        metadata = self.extract_metadata(content)
        
        # 支持嵌套字段访问
        keys = field.split('.')
        value = metadata
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def extract_tags(self, content: str) -> List[str]:
        """
        提取标签列表
        
        Args:
            content: 文件内容
            
        Returns:
            标签列表
        """
        tags = self.extract_field(content, 'tags', [])
        if isinstance(tags, str):
            return [tags]
        return tags or []
    
    def extract_date(self, content: str, field: str = 'date') -> Optional[datetime]:
        """
        提取日期字段
        
        Args:
            content: 文件内容
            date_field: 日期字段名
            
        Returns:
            datetime 对象或 None
        """
        date_str = self.extract_field(content, field)
        
        if not date_str:
            return None
        
        if isinstance(date_str, datetime):
            return date_str
        
        # 尝试多种日期格式
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d',
            '%d/%m/%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except ValueError:
                continue
        
        return None
    
    def validate_frontmatter(self, content: str, required_fields: List[str]) -> Dict[str, Any]:
        """
        验证 frontmatter 是否包含必要字段
        
        Args:
            content: 文件内容
            required_fields: 必须存在的字段列表
            
        Returns:
            验证结果 {'valid': bool, 'missing': List[str], 'metadata': Dict}
        """
        metadata = self.extract_metadata(content)
        missing = [field for field in required_fields if field not in metadata]
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'metadata': metadata
        }
    
    def update_metadata(self, content: str, updates: Dict[str, Any]) -> str:
        """
        更新 frontmatter 元数据
        
        Args:
            content: 原始文件内容
            updates: 要更新的字段
            
        Returns:
            更新后的内容
        """
        data = self.parse(content)
        
        if not data.has_frontmatter:
            # 创建新的 frontmatter
            new_frontmatter = yaml.dump(updates, default_flow_style=False, allow_unicode=True)
            return f"{self.separator}\n{new_frontmatter}{self.separator}\n\n{content}"
        
        # 更新现有 frontmatter
        metadata = data.metadata.copy()
        metadata.update(updates)
        
        new_frontmatter = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)
        return f"{self.separator}\n{new_frontmatter}{self.separator}\n\n{data.body}"

# 使用示例
if __name__ == "__main__":
    parser = FrontmatterParser()
    
    # 解析字符串
    content = """---
title: 我的博客文章
author:
  name: 李四
  email: lisi@example.com
date: 2024-01-20
tags: [Python, 教程]
categories:
  - 技术
  - 编程
published: true
---

# 文章标题

这是文章内容。
"""
    
    # 解析并获取数据
    data = parser.parse(content)
    print(f"有 frontmatter: {data.has_frontmatter}")
    print(f"元数据: {data.metadata}")
    print(f"正文行数: {data.line_count}")
    
    # 提取特定字段
    title = parser.extract_field(content, 'title')
    author_name = parser.extract_field(content, 'author.name')
    tags = parser.extract_tags(content)
    date = parser.extract_date(content)
    
    print(f"\n标题: {title}")
    print(f"作者: {author_name}")
    print(f"标签: {tags}")
    print(f"日期: {date}")
    
    # 验证必要字段
    validation = parser.validate_frontmatter(content, ['title', 'date', 'author'])
    print(f"\n验证结果: {'通过' if validation['valid'] else '失败'}")
    if validation['missing']:
        print(f"缺失字段: {validation['missing']}")
```

### 批量处理文件

```python
from pathlib import Path
from typing import List, Dict
import json

def batch_parse_frontmatter(directory: str, pattern: str = "*.md") -> List[Dict]:
    """
    批量解析目录下所有 Markdown 文件的 frontmatter
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
        
    Returns:
        解析结果列表
    """
    parser = FrontmatterParser()
    results = []
    
    for file_path in Path(directory).glob(pattern):
        try:
            data = parser.parse_file(file_path)
            results.append({
                'file': str(file_path),
                'metadata': data.metadata,
                'has_frontmatter': data.has_frontmatter,
                'body_length': len(data.body)
            })
        except Exception as e:
            results.append({
                'file': str(file_path),
                'error': str(e)
            })
    
    return results

# 使用示例
if __name__ == "__main__":
    results = batch_parse_frontmatter("./docs", "*.md")
    
    # 保存为 JSON
    with open('metadata_report.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"处理了 {len(results)} 个文件")
    valid_count = sum(1 for r in results if r.get('has_frontmatter', False))
    print(f"其中 {valid_count} 个文件有 frontmatter")
```

## 问题排查

### 问题 1：YAML 解析错误

**症状**：`yaml.YAMLError` 异常。

**原因**：
- YAML 语法错误（缩进不正确、特殊字符未转义）
- 冒号后缺少空格
- 未加引号的特殊字符串

**解决方案**：
```python
# 1. 使用 try-except 处理解析错误
try:
    metadata = yaml.safe_load(frontmatter)
except yaml.YAMLError as e:
    print(f"YAML 解析错误: {e}")
    # 尝试修复常见问题
    fixed = frontmatter.replace(': ', ':')  # 修复冒号后无空格
    metadata = yaml.safe_load(fixed)

# 2. 为特殊值加引号
# 错误：title: 网站：首页
# 正确：title: "网站：首页"
```

### 问题 2：UTF-8 编码问题

**症状**：中文字符解析异常。

**解决方案**：
```python
# 确保使用 UTF-8 编码读取文件
with open('file.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 或者在文件开头添加编码声明
# -*- coding: utf-8 -*-
```

### 问题 3：嵌套结构解析不正确

**症状**：嵌套字典/列表结构丢失。

**解决方案**：
```python
# 正确的 YAML 嵌套格式
"""
author:
  name: 张三
  email: zhangsan@example.com
tags:
  - Python
  - 教程
"""

# 避免的格式
"""
author: name: 张三, email: zhangsan@example.com
tags: Python, 教程
"""
```

### 问题 4：日期格式不统一

**症状**：日期字段无法转换为 datetime 对象。

**解决方案**：
```python
# 使用标准 ISO 格式
date: 2024-01-15
date: 2024-01-15T10:30:00
date: "2024-01-15"  # 加引号避免 YAML 误解析
```

## 依赖

| 依赖 | 版本 | 类型 | 说明 |
|------|------|------|------|
| Python | 3.7+ | 必需 | 运行环境 |
| pyyaml | ≥6.0.0 | 必需 | YAML 解析库 |

## Agent 执行规范

### 核心约束
- **安全解析**：始终使用 `yaml.safe_load()` 而非 `yaml.load()`
- **错误处理**：解析失败时返回空字典或默认值
- **编码统一**：始终使用 UTF-8 编码
- **类型检查**：验证提取的字段类型是否符合预期

### 最佳实践
- 为复杂嵌套结构添加类型注解
- 使用 dataclass 或 TypedDict 定义元数据结构
- 批量处理时记录解析错误
- 定期备份重要的 frontmatter 数据
