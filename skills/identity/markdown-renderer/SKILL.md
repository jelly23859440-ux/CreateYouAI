---
name: markdown-renderer
layer: identity
category: knowledge
status: unverified
description: >
  将 Markdown 渲染为终端彩色输出，支持代码高亮、表格、列表。
  当用户需要在终端显示格式化文档、渲染 README、查看 Markdown 文件时触发。
  关键词：Markdown 渲染、终端显示、彩色输出、代码高亮、表格渲染。
---

# Markdown 终端渲染器

将 Markdown 文本渲染为终端彩色输出，支持丰富的格式化特性。

## 功能特性

- 支持标题、粗体、斜体、删除线
- 代码块语法高亮（支持多种语言）
- 表格渲染（对齐、边框）
- 列表（有序、无序、任务列表）
- 链接和图片引用
- 引用块
- 水平分割线
- 支持 UTF-8 字符和 Emoji

## 前置条件

- Python 3.7+
- rich 库（推荐）或 colorama 库
- 终端支持 ANSI 颜色（Windows 10+ 或现代终端）

## 安装步骤

### 推荐方式：使用 rich

```bash
pip install rich>=13.0.0
```

### 备选方式：使用 colorama

```bash
pip install colorama>=0.4.6
```

### 验证安装

```bash
python -c "import rich; print(rich.__version__)"
```

## 使用方法

### 基础用法

```python
from rich.console import Console
from rich.markdown import Markdown

def render_markdown(text: str) -> None:
    """
    将 Markdown 文本渲染为终端彩色输出
    
    Args:
        text: Markdown 格式的文本
    """
    console = Console()
    md = Markdown(text)
    console.print(md)

# 使用示例
if __name__ == "__main__":
    markdown_text = """
# 标题一

## 标题二

这是一段 **粗体** 和 *斜体* 文本。

### 代码示例

```python
def hello_world():
    print("Hello, World!")
    return True
```

### 表格

| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25   | 北京 |
| 李四 | 30   | 上海 |

### 列表

- 项目一
- 项目二
  - 子项目 A
  - 子项目 B

### 任务列表

- [x] 完成任务一
- [ ] 进行任务二
- [ ] 计划任务三

> 这是一段引用文本。

---

更多内容请访问 [GitHub](https://github.com)。
"""
    render_markdown(markdown_text)
```

### 高级用法：自定义渲染

```python
from rich.console import Console
from rich.markdown import Markdown
from rich.theme import Theme
from rich.syntax import Syntax

class MarkdownRenderer:
    """自定义 Markdown 渲染器"""
    
    def __init__(self, theme: str = "monokai"):
        """
        初始化渲染器
        
        Args:
            theme: 代码高亮主题（monokai, friendly, dracula 等）
        """
        self.console = Console()
        self.theme = theme
    
    def render_file(self, file_path: str) -> None:
        """
        渲染 Markdown 文件
        
        Args:
            file_path: Markdown 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.render_text(content)
        except FileNotFoundError:
            self.console.print(f"[red]错误：文件未找到 - {file_path}[/red]")
        except Exception as e:
            self.console.print(f"[red]错误：{e}[/red]")
    
    def render_text(self, text: str) -> None:
        """
        渲染 Markdown 文本
        
        Args:
            text: Markdown 文本
        """
        md = Markdown(text)
        self.console.print(md)
    
    def render_with_line_numbers(self, text: str) -> None:
        """
        带行号渲染 Markdown
        
        Args:
            text: Markdown 文本
        """
        lines = text.split('\n')
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i:3d} | {line}")
        
        numbered_text = '\n'.join(numbered_lines)
        md = Markdown(numbered_text)
        self.console.print(md)

# 使用示例
if __name__ == "__main__":
    renderer = MarkdownRenderer()
    
    # 渲染文本
    renderer.render_text("# 测试标题\n\n这是一个段落。")
    
    # 渲染文件（如果存在）
    # renderer.render_file("README.md")
```

### 集成到现有项目

```python
import sys
from rich.console import Console
from rich.markdown import Markdown

def display_readme(readme_path: str = "README.md") -> bool:
    """
    显示 README 文件内容
    
    Args:
        readme_path: README 文件路径
        
    Returns:
        是否成功显示
    """
    console = Console()
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        console.print(Markdown(content))
        return True
    except FileNotFoundError:
        console.print(f"[yellow]警告：{readme_path} 未找到[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]错误：{e}[/red]")
        return False

# 在命令行中使用
if __name__ == "__main__":
    if len(sys.argv) > 1:
        display_readme(sys.argv[1])
    else:
        display_readme()
```

## 问题排查

### 问题 1：终端不显示颜色

**症状**：输出为纯文本，没有颜色。

**原因**：
- Windows 终端不支持 ANSI 颜色
- 终端模拟器配置问题

**解决方案**：
```python
# 方法1：启用 Windows VT100 支持
import os
os.system('')

# 方法2：使用 colorama 初始化
from colorama import init
init()

# 方法3：设置环境变量
import os
os.environ['FORCE_COLOR'] = '1'
```

### 问题 2：中文乱码

**症状**：中文字符显示为乱码或问号。

**解决方案**：
```python
# 确保文件使用 UTF-8 编码
with open('file.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 或者在文件开头添加编码声明
# -*- coding: utf-8 -*-
```

### 问题 3：代码块没有高亮

**症状**：代码块显示为普通文本。

**原因**：未指定语言或语言不支持。

**解决方案**：
```python
# 确保代码块指定语言
```python
def example():
    pass
```

# 或者使用 rich 的 Syntax 类单独渲染代码
from rich.syntax import Syntax
code = "print('Hello')"
syntax = Syntax(code, "python", theme="monokai")
console.print(syntax)
```

### 问题 4：表格对齐问题

**症状**：表格列不对齐。

**解决方案**：
```python
# 确保 Markdown 表格语法正确
# 使用 | 分隔列，第二行为分隔符
"""
| 左对齐 | 居中对齐 | 右对齐 |
|:-------|:-------:|-------:|
| 内容   | 内容    | 内容   |
"""
```

## 依赖

| 依赖 | 版本 | 类型 | 说明 |
|------|------|------|------|
| Python | 3.7+ | 必需 | 运行环境 |
| rich | ≥13.0.0 | 推荐 | 功能完整的终端美化库 |
| colorama | ≥0.4.6 | 可选 | 轻量级颜色支持 |

## Agent 执行规范

### 核心约束
- **编码统一**：始终使用 UTF-8 编码读取文件
- **错误处理**：文件不存在时给出友好提示
- **性能考虑**：大文件（>1MB）分块渲染
- **兼容性**：同时支持 rich 和 colorama 两种方案

### 最佳实践
- 优先使用 rich 库，功能更完整
- 代码块指定语言以获得高亮
- 表格保持对齐格式
- 避免在渲染时修改原始 Markdown 内容
