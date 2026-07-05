---
name: skill-system
layer: meta
category: skill-learn
status: unverified
description: >
  技能系统：加载、注册、执行 skill。
  关键词：skill、技能、加载、注册。
---

# 技能系统

## 功能说明

技能系统管理 SKILL.md 文件的发现、解析、注册和执行。核心设计：

- **YAML frontmatter 解析**：SKILL.md 以 `---` 包裹的 YAML 头部 + Markdown 正文
- **多级发现**：用户级 > 项目级 > 显式路径，先加载优先（名称冲突时保留先注册的）
- **渐进加载**：prompt 中只放描述，执行时才加载完整内容
- **名称验证**：`[a-z0-9-]+`，最长 64 字符，不以 `-` 开头/结尾，不含 `--`

## 使用方法

```python
from skill_system import SkillSystem
from pathlib import Path

# 初始化
system = SkillSystem()

# 加载单个 skill
skill = system.load_skill(Path(".pi/skills/my-skill/SKILL.md"))

# 递归加载目录
skills = system.load_directory(Path(".pi/skills"), source="project")

# 层级加载（用户级 > 项目级 > 显式路径）
system.load_from_hierarchy(
    project_root=Path("."),
    explicit_paths=[Path("/extra/skills")]
)

# 格式化为 prompt 可用列表
prompt_text = system.format_for_prompt()

# 执行时加载完整内容
invocation = system.format_invocation(skill)
```

## 依赖

| 依赖 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ |
| PyYAML | - | ✅ |

## SKILL.md 格式规范

```markdown
---
name: my-skill
description: 这个技能做什么
disable-model-invocation: false
---

# My Skill

## 功能说明
...

## 使用方法
...
```

- `name`：小写字母+数字+短横线，最长 64 字符
- `description`：必填，为空则跳过加载
- `disable-model-invocation`：为 true 时不放入 prompt 列表

## 来源

- 原项目：pi-mini
- 来源模块：skill_system.py
- 核心文件：`scripts/skill_system.py`（精简版）
