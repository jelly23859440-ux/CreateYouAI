---
name: Markdown 终端渲染器
layer: identity
category: knowledge
status: unverified
description: >
  将 Markdown 渲染为终端彩色输出，支持代码高亮、表格、列表。
  当用户需要在终端显示格式化文档、渲染 README、查看 Markdown 文件时触发。
  关键词：Markdown 渲染、终端显示、彩色输出、代码高亮、表格渲染。
requirements:
  - name: rich
    version: ">=13.0.0"
    required: true
---

# Markdown 终端渲染器

将 Markdown 文本渲染为终端彩色输出，支持丰富的格式化特性。

## 能力概览

| 能力 | 说明 |
|------|------|
| 标题渲染 | 支持 H1-H6 |
| 文本格式 | 粗体、斜体、删除线 |
| 代码高亮 | 支持多种语言语法高亮 |
| 表格渲染 | 自动对齐和边框 |
| 列表支持 | 有序、无序、任务列表 |
| 链接引用 | 渲染超链接 |
| 引用块 | 渲染引用文本 |

## 前置条件

- Python 3.8+
- rich 库（必需）

## 安装步骤

```bash
pip install rich>=13.0.0
```

验证安装：
```bash
python -c "import rich; print(rich.__version__)"
```

## 使用方法

### 基础用法

```python
from rich.console import Console
from rich.markdown import Markdown

def render_markdown(text: str, theme: str = "monokai") -> None:
    """
    将 Markdown 文本渲染为终端彩色输出
    
    Args:
        text: Markdown 格式的文本
        theme: 代码高亮主题（monokai, friendly, dracula 等）
    """
    console = Console()
    md = Markdown(text, code_theme=theme)
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

### MarkdownRenderer 类

```python
from rich.console import Console
from rich.markdown import Markdown

class MarkdownRenderer:
    """Markdown 渲染器"""
    
    def __init__(self, theme: str = "monokai"):
        """
        初始化渲染器
        
        Args:
            theme: 代码高亮主题（monokai, friendly, dracula 等）
        """
        self.console = Console()
        self.theme = theme
    
    def render_file(self, file_path: str) -> bool:
        """
        渲染 Markdown 文件
        
        Returns:
            是否成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.render_text(content)
            return True
        except FileNotFoundError:
            self.console.print(f"[red]错误：文件未找到 - {file_path}[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]错误：{e}[/red]")
            return False
    
    def render_text(self, text: str) -> None:
        """渲染 Markdown 文本"""
        md = Markdown(text, code_theme=self.theme)
        self.console.print(md)
    
    def render_with_line_numbers(self, text: str) -> None:
        """纯文本输出带行号（不使用 Markdown 解析）"""
        for i, line in enumerate(text.split('\n'), 1):
            self.console.print(f"{i:3d} | {line}")

# 使用示例
if __name__ == "__main__":
    renderer = MarkdownRenderer(theme="dracula")
    renderer.render_text("# 测试标题\n\n这是一个段落。")
```

### 命令行用法

```bash
# 渲染 README
python -m rich.markdown README.md

# 或使用内置函数
python -c "from rich.console import Console; from rich.markdown import Markdown; Console().print(Markdown(open('README.md').read()))"
```

### 集成到项目

```python
from rich.console import Console
from rich.markdown import Markdown

def display_readme(readme_path: str = "README.md") -> bool:
    """显示 README 文件内容"""
    console = Console()
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        console.print(Markdown(content))
        return True
    except FileNotFoundError:
        console.print(f"[yellow]警告：{readme_path} 未找到[/yellow]")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        display_readme(sys.argv[1])
```

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 未安装 rich | 缺少依赖 | `pip install rich>=13.0.0` |
| 颜色不显示 | 终端不支持 ANSI | 使用 Windows 10+ 或现代终端 |
| 主题无效 | rich 默认主题 | 使用 `code_theme` 参数设置 |
| 中文乱码 | 终端编码问题 | 设置 `PYTHONIOENCODING=utf-8` |

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| rich | ≥13.0.0 | Markdown 渲染 |
