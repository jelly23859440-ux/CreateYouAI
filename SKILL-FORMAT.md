# Skill 格式标准

本文档定义 Skill 的标准格式，所有贡献者必须遵守。

---

## 文件结构

```
skills/<layer>/<category>/<skill-name>/
├── SKILL.md              # 必须：给 AI 的指令文档
└── scripts/              # 可选：可执行脚本（Python/Shell/Node 等）
```

**层级说明**：

| Layer | Categories | 说明 |
|-------|------------|------|
| `core` | conversation, reasoning, memory | 核心能力层 —— Agent 的"大脑" |
| `action` | code, tool, file, web, device | 执行能力层 —— Agent 的"手脚" |
| `identity` | personality, safety, knowledge | 身份层 —— Agent "是谁" |
| `meta` | ai-builder, skill-learn, contribute | 元能力层 —— 能力的能力 |
| `scenarios` | coding-ai, research-ai, creative-ai, daily-ai | 场景层 —— 预设组合模板 |

## SKILL.md 格式

### 1. YAML Frontmatter（必须）

```yaml
---
name: 技能名称
layer: action
category: device
status: unverified
description: >
  一句话描述这个技能做什么。
  当用户提出以下意图时触发：关键词1、关键词2、关键词3。
---
```

**字段说明**：

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 技能名称，简短 |
| `layer` | string | ✅ | 所属层级：core / action / identity / meta / scenarios |
| `category` | string | ✅ | 所属分类 |
| `status` | string | ✅ | 验证状态：`unverified` / `verified` |
| `description` | string | ✅ | 功能描述 + 触发关键词 |

**status 说明**：

| 状态 | 含义 | 谁能提交 |
|------|------|----------|
| `unverified` | 代码未实际验证，可能存在 bug | 任何人 |
| `verified` | 代码已实际跑通，确认可用 | 实际验证过的用户 |

**验证流程**：
1. 原作者提交 `unverified` 版本
2. 其他用户使用后发现 bug → 提交修复版
3. 修复版通过验证 → 状态改为 `verified`，作者更新为验证者

### 2. 正文结构（建议）

```markdown
# 技能名称

## 功能说明
一句话说明这个技能做什么。

## 能力概览
表格列出所有能力/端点/命令。

## 前置条件
用户需要准备什么（软件、账号、硬件等）。

## 安装步骤
分步骤写清楚怎么安装。

## 使用方法
代码示例 + 参数说明。

## 问题排查
常见错误 + 解决方案。

## 依赖
版本号 + 必需/可选标记。
```

### 3. 写作要求

**必须做到**：
- 代码示例可直接复制使用
- 版本号写死（不要写"最新版"）
- 每个步骤有验证方法
- 错误信息写清楚原因和解决方案

**禁止**：
- 放个人路径（如 `D:\Users\xxx\...`）
- 放个人设备名（如 `Microphone (Shure MV51)`）
- 放密码、Token、密钥
- 写"应该可以"、"可能"等不确定的描述

### 4. Agent 行为约束（建议）

如果有执行规范，在文档中明确写出：

```markdown
## Agent 执行规范

### 核心约束
- **先检查再安装**：执行前检查依赖是否已安装
- **验证每一步**：安装后验证是否成功
- **不要猜测路径**：让用户告诉你实际路径
```

---

## 质量标准

| 维度 | 要求 |
|------|------|
| 完整性 | 从零开始能跑通 |
| 准确性 | 代码示例经过测试 |
| 可读性 | 非开发者也能理解 |
| 可维护性 | 版本号锁定，有排查指南 |
