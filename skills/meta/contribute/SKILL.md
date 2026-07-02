---
name: 贡献 Skill 到 CreateYouAI
layer: meta
category: contribute
status: unverified
description: >
  帮助用户向 CreateYouAI 仓库提交新的 Skill。
  当用户想要分享自己的 Skill、贡献代码、提交 PR 时触发。
  关键词：贡献、提交、PR、分享 skill、添加 skill、contribute。
---

# 向 CreateYouAI 贡献 Skill

帮用户把写好的 Skill 提交到 CreateYouAI 仓库。

## 前置条件

用户需要提供以下之一：
- skill 文件路径（如 `D:\my-skill\SKILL.md`）
- 直接在对话中粘贴 SKILL.md 内容

如果是粘贴内容，AI 需要先将其保存到临时文件。

## 执行流程

### Step 1：获取用户 Skill 文件

确认用户已提供 skill 文件路径或内容。如果是粘贴内容，保存到临时目录：
```
mkdir -p /tmp/contribute-skill
# 将用户粘贴的内容保存为 /tmp/contribute-skill/SKILL.md
```

### Step 2：检查 SKILL.md 格式

```python
import re
from pathlib import Path

def validate_skill(skill_path: str) -> dict:
    """
    验证 SKILL.md 格式
    
    Returns:
        {"valid": bool, "errors": list, "warnings": list}
    """
    content = Path(skill_path).read_text(encoding='utf-8')
    errors = []
    warnings = []
    
    # 检查 YAML Frontmatter
    if not content.startswith('---'):
        errors.append("缺少 YAML Frontmatter（必须以 --- 开头）")
    else:
        # 检查必需字段
        if 'name:' not in content.split('---')[1]:
            errors.append("Frontmatter 缺少 name 字段")
        if 'description:' not in content.split('---')[1]:
            errors.append("Frontmatter 缺少 description 字段")
        if 'layer:' not in content.split('---')[1]:
            warnings.append("Frontmatter 缺少 layer 字段（建议添加）")
        if 'category:' not in content.split('---')[1]:
            warnings.append("Frontmatter 缺少 category 字段（建议添加）")
    
    # 检查个人路径
    if re.search(r'[A-Z]:\\Users\\[^\\]+|[/\\]home[/\\][^/]+', content):
        errors.append("包含个人路径（如 D:\\Users\\xxx）")
    
    # 检查个人设备名
    if re.search(r'Microphone \([^)]+\)|Device Name', content):
        errors.append("包含个人设备名")
    
    # 检查敏感信息
    if re.search(r'(?i)(password|token|api_key|secret|private_key)\s*[:=]\s*["\'][^"\']{8,}', content):
        errors.append("可能包含密码或密钥")
    
    # 检查基本内容
    if '## ' not in content:
        warnings.append("缺少章节标题（建议添加 ## 功能说明 等）")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
```

如果验证失败，告诉用户具体哪里要改。

### Step 3：提取 Skill 元信息

从 YAML Frontmatter 中提取 name 和 category，用于后续步骤：

```python
import yaml

def extract_frontmatter(skill_path: str) -> dict:
    """提取 YAML Frontmatter"""
    content = Path(skill_path).read_text(encoding='utf-8')
    if not content.startswith('---'):
        return {}
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    return yaml.safe_load(parts[1]) or {}
```

### Step 4：放入正确目录

根据 Skill 的 layer 和 category 放入对应目录：

```
skills/
├── core/              🧠 核心能力层
│   ├── conversation/    💬 对话能力
│   ├── reasoning/       🧩 推理能力
│   └── memory/          🧠 记忆能力
├── action/            ⚡ 执行能力层
│   ├── code/            💻 代码能力
│   ├── tool/            🔧 工具调用
│   ├── file/            📁 文件操作
│   ├── web/             🌐 网络能力
│   └── device/          📱 设备控制
├── identity/          🎭 身份层
│   ├── personality/     🎭 人格设定
│   ├── safety/          🛡️ 安全护栏
│   └── knowledge/       📚 知识领域
├── meta/              🧩 元能力层
│   ├── ai-builder/      🧩 智能组合
│   ├── skill-learn/     📖 技能学习
│   └── contribute/      🤝 社区贡献
└── scenarios/         🎯 场景层
    ├── coding-ai/       💻 编程助手模板
    ├── research-ai/     🔬 研究助手模板
    ├── creative-ai/     🎨 创意助手模板
    └── daily-ai/        🏠 日常助手模板
```

### Step 5：创建分支并提交

```bash
# 先确保在 main 分支
git checkout main
git pull origin main

# 创建新分支（如果已存在则先删除）
branch_name="skill/<skill-name>"
git branch -D $branch_name 2>/dev/null || true
git checkout -b $branch_name

# 复制 skill 文件到正确位置
mkdir -p skills/<layer>/<category>/<skill-name>
cp <用户skill路径>/SKILL.md skills/<layer>/<category>/<skill-name>/SKILL.md

# 添加并提交
git add skills/<layer>/<category>/<skill-name>/SKILL.md
git commit -m "feat: 添加 <skill-name> skill"

# 推送
git push -u origin $branch_name
```

### Step 6：创建 PR

```bash
# 写入 PR 描述文件
cat > /tmp/pr_body.md <<'EOF'
## Skill 信息

- **名称**: <skill-name>
- **用途**: <一句话说明>
- **分类**: <layer>/<category>
- **平台**: <electron / web / python / universal>
- **依赖**: <需要安装什么>

## Checklist

- [ ] SKILL.md 格式符合 SKILL-FORMAT.md
- [ ] 代码示例可直接复制使用
- [ ] 无个人路径/密码/Token
- [ ] 已在至少一个 AI 工具中测试通过
EOF

# 创建 PR
gh pr create \
  --title "feat: 添加 <skill-name> skill" \
  --body-file /tmp/pr_body.md

# 清理临时文件
rm /tmp/pr_body.md
```

如果 `gh` 不可用，告诉用户手动去 GitHub 创建 PR：
1. 打开 https://github.com/jelly23859440-ux/CreateYouAI
2. 点 "Compare & pull request"
3. 填写 PR 标题：`feat: 添加 <skill-name> skill`
4. 粘贴 PR 描述

## 注意事项

- **占位符替换**：从 SKILL.md 的 YAML 头部提取 `name` 和 `category`，自动替换所有 `<skill-name>` 和 `<category>`
- 分支名格式：`skill/<skill-name>`
- PR 标题格式：`feat: 添加 <skill-name> skill`
- 一个 PR 只提交一个 Skill
- 提交前先 `git pull origin main` 确保最新

## 常见问题

| 错误 | 原因 | 解决 |
|------|------|------|
| `Failed to connect to github.com port 443` | SSL 配置问题 | `git config --global http.sslBackend schannel` |
| `Permission denied` | 未登录 GitHub | `gh auth login` 或用浏览器授权 |
| `remote: Permission to denied` | 没有 Fork | 先 Fork 仓库再提交 |
| `CONFLICT` | 本地不是最新 | `git pull origin main` 后重试 |
| `branch already exists` | 分支已存在 | `git branch -D <branch>` 删除后重建 |
