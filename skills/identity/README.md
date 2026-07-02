# Identity Skills / 身份层

Agent "是谁"——人格、安全、知识领域。

## Skills

| Skill | 依赖 | 说明 |
|-------|------|------|
| [markdown-renderer](markdown-renderer/SKILL.md) | rich | Markdown 终端彩色渲染器 |
| [frontmatter-parser](frontmatter-parser/SKILL.md) | pyyaml | YAML Frontmatter 解析器 |

## 快速安装

```bash
pip install rich pyyaml
```

## 说明

这两个 Skill 主要用于：
- **markdown-renderer** — 在终端中美观显示 Markdown 内容（代码高亮、表格、列表）
- **frontmatter-parser** — 解析 Markdown 文件中的 YAML 元数据（用于 Skill 加载、配置管理等）
