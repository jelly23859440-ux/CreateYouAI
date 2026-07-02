---
name: code-search
category: code
description: 使用 ripgrep 搜索代码库，支持正则表达式和文件类型过滤
version: 1.0.0
author: CreateYouAI
tags: [search, code, ripgrep, regex]
requirements: [ripgrep]
platform: [windows, linux, macos]
difficulty: beginner
---

# Code Search (代码搜索工具)

使用 ripgrep 在代码库中快速搜索文本、正则表达式模式，支持文件类型过滤。

## 功能特性

- 正则表达式搜索
- 文件类型过滤（按扩展名）
- 上下文行数控制
- 大小写敏感/不敏感
- 多文件批量搜索
- 结果高亮显示

## 安装依赖

### Windows (winget)
```powershell
winget install BurntSushi.ripgrep.MSVC
```

### Windows (Chocolatey)
```powershell
choco install ripgrep
```

### macOS (Homebrew)
```bash
brew install ripgrep
```

### Linux (apt)
```bash
sudo apt install ripgrep
```

## 使用方法

### 命令行直接使用

```bash
# 基本搜索
rg "pattern" /path/to/search

# 正则表达式搜索
rg "\d{4}-\d{2}-\d{2}" --glob "*.py"

# 按文件类型过滤
rg "TODO" -t py -t js

# 显示上下文
rg "error" -C 3

# 忽略大小写
rg "error" -i

# 只显示文件名
rg "pattern" -l
```

### Python 代码示例

```python
"""
code_search.py - 代码搜索工具
使用 ripgrep 搜索代码库
"""
import subprocess
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SearchResult:
    """搜索结果"""
    file: str
    line: int
    column: int
    match: str
    context_before: str = ""
    context_after: str = ""


class CodeSearcher:
    """代码搜索器"""
    
    def __init__(self, ripgrep_path: str = "rg"):
        """
        初始化搜索器
        
        Args:
            ripgrep_path: ripgrep 可执行文件路径
        """
        self.ripgrep_path = ripgrep_path
        self._verify_ripgrep()
    
    def _verify_ripgrep(self) -> None:
        """验证 ripgrep 是否可用"""
        try:
            subprocess.run(
                [self.ripgrep_path, "--version"],
                capture_output=True,
                check=True
            )
        except FileNotFoundError:
            raise RuntimeError(
                "ripgrep 未安装。请运行: winget install BurntSushi.ripgrep.MSVC"
            )
    
    def search(
        self,
        pattern: str,
        path: str = ".",
        file_types: Optional[List[str]] = None,
        ignore_case: bool = False,
        context_lines: int = 0,
        max_results: int = 100
    ) -> List[SearchResult]:
        """
        搜索代码
        
        Args:
            pattern: 搜索模式（支持正则表达式）
            path: 搜索路径
            file_types: 文件类型过滤列表（如 ['py', 'js']）
            ignore_case: 是否忽略大小写
            context_lines: 上下文行数
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        cmd = [self.ripgrep_path, pattern, path]
        
        if ignore_case:
            cmd.append("-i")
        
        if file_types:
            for ft in file_types:
                cmd.extend(["-t", ft])
        
        if context_lines > 0:
            cmd.extend(["-C", str(context_lines)])
        
        # 使用 --no-heading 获取详细输出
        cmd.extend(["--no-heading", "-n"])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
        except Exception as e:
            raise RuntimeError(f"搜索失败: {e}")
        
        return self._parse_output(result.stdout, max_results)
    
    def _parse_output(self, output: str, max_results: int) -> List[SearchResult]:
        """解析 ripgrep 输出"""
        results = []
        lines = output.strip().split('\n')
        
        for line in lines[:max_results]:
            if not line:
                continue
            
            # 格式: file:line:col:content
            match = re.match(r'^(.+?):(\d+):(\d+):(.+)$', line)
            if match:
                results.append(SearchResult(
                    file=match.group(1),
                    line=int(match.group(2)),
                    column=int(match.group(3)),
                    match=match.group(4).strip()
                ))
        
        return results
    
    def search_files(
        self,
        pattern: str,
        extensions: Optional[List[str]] = None,
        directory: str = ".",
        ignore_case: bool = False
    ) -> Dict[str, List[int]]:
        """
        搜索文件并返回匹配行号
        
        Args:
            pattern: 搜索模式
            extensions: 文件扩展名过滤
            directory: 搜索目录
            ignore_case: 是否忽略大小写
            
        Returns:
            {文件路径: [匹配行号列表]}
        """
        cmd = [self.ripgrep_path, pattern, directory, "-l"]
        
        if ignore_case:
            cmd.append("-i")
        
        if extensions:
            for ext in extensions:
                cmd.extend(["-g", f"*.{ext}"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        file_lines = {}
        for f in files:
            if f:
                line_cmd = [self.ripgrep_path, pattern, f, "-n"]
                if ignore_case:
                    line_cmd.append("-i")
                
                line_result = subprocess.run(line_cmd, capture_output=True, text=True)
                lines = []
                for line in line_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 2:
                            try:
                                lines.append(int(parts[1]))
                            except ValueError:
                                pass
                file_lines[f] = lines
        
        return file_lines
    
    def count_matches(
        self,
        pattern: str,
        path: str = ".",
        ignore_case: bool = False
    ) -> int:
        """
        统计匹配数量
        
        Args:
            pattern: 搜索模式
            path: 搜索路径
            ignore_case: 是否忽略大小写
            
        Returns:
            匹配总数
        """
        cmd = [self.ripgrep_path, pattern, path, "-c"]
        
        if ignore_case:
            cmd.append("-i")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        total = 0
        
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                count_str = line.split(':')[-1]
                try:
                    total += int(count_str)
                except ValueError:
                    pass
        
        return total


# 使用示例
if __name__ == "__main__":
    searcher = CodeSearcher()
    
    # 搜索所有 Python 文件中的 TODO
    results = searcher.search(
        pattern="TODO|FIXME|HACK",
        path="./src",
        file_types=["py"],
        ignore_case=True,
        context_lines=2
    )
    
    print(f"找到 {len(results)} 个匹配:")
    for r in results:
        print(f"  {r.file}:{r.line} - {r.match}")
```

## 使用示例

```python
from code_search import CodeSearcher

# 初始化
searcher = CodeSearcher()

# 搜索 Python 文件中的函数定义
results = searcher.search(
    pattern=r"def \w+\(",
    path="./my_project",
    file_types=["py"]
)

for r in results:
    print(f"{r.file}:{r.line} - {r.match}")

# 统计匹配数
count = searcher.count_matches(
    pattern="import",
    path="./src",
    ignore_case=True
)
print(f"总共找到 {count} 个 import 语句")
```

## 故障排除

### 问题：ripgrep 未找到
```
错误: ripgrep 未安装
```
**解决**: 安装 ripgrep
```powershell
winget install BurntSushi.ripgrep.MSVC
```

### 问题：正则表达式语法错误
```
错误: regex parse error
```
**解决**: 检查正则表达式语法，使用在线工具验证

### 问题：权限被拒绝
```
错误: Permission denied
```
**解决**: 以管理员身份运行，或检查文件权限

## 参考链接

- [ripgrep 官方文档](https://github.com/BurntSushi/ripgrep)
- [正则表达式语法](https://docs.rs/regex/latest/regex/#syntax)
