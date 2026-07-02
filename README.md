# CreateYouAI

Modular AI Skill repository. Build your own AI like stacking LEGO blocks.

模块化 AI Skill 仓库，像搭积木一样构建你自己的 AI。

---

## What is a Skill?

A Skill is a set of instructions for AI. When a user says "I want to do X", the AI reads the corresponding Skill and knows how to help.

Skill 是一份给 AI 看的说明书。用户说"我要做 X"，AI 读取对应的 Skill，就知道怎么帮用户实现。

---

## How it works / 工作原理

1. User describes what AI they want / 用户描述想做什么 AI
2. AI scans available Skills / AI 扫描可用的 Skill
3. AI picks the right combination / AI 挑选合适的组合
4. AI helps build it step by step / AI 帮用户逐步构建

---

## Contribute / 贡献 Skill

**Welcome to contribute! We need your skills. / 欢迎贡献！我们需要你的 Skill。**

> Tell your AI: "我想贡献一个 skill" / 告诉你的 AI："我想贡献一个 skill"
>
> AI 会读取 `contribute` Skill，帮你完成整个贡献流程。

### 快速贡献流程

1. **Fork** this repository / Fork 本仓库
2. **Write** a Skill following [SKILL-FORMAT.md](SKILL-FORMAT.md) / 按 SKILL-FORMAT.md 写 Skill
3. **Submit** a PR / 提交 PR

### 三种贡献方式

| 方式 | 适合谁 | 说明 |
|------|--------|------|
| [贡献 Skill](skills/meta/contribute/SKILL.md) | 有代码能力 | 写一个可运行的 Skill |
| [提想法](ideas/) | 有想法但不会写 | 提交想法，让社区帮你实现 |
| [反馈问题](https://github.com/jelly23859440-ux/CreateYouAI/issues) | 所有人 | 报告问题或建议改进 |

### Skill 格式要求

```yaml
---
name: 技能名称
layer: action          # core / action / identity / meta
category: code         # code / web / file / device / ...
description: >
  一句话描述 + 触发关键词
---
```

详细格式见 [SKILL-FORMAT.md](SKILL-FORMAT.md)

---

## Quick Start / 快速开始

Tell your AI: "我想做一个 XX 的 AI" / 告诉你的 AI："我想做一个 XX 的 AI"

The AI will read the `ai-builder` Skill and automatically pick the right combination from this repository.

AI 会读取 `ai-builder` Skill，自动从仓库挑选合适的组合。

---

## Skill Overview / 技能概览

| Layer | Category | Count | Description |
|-------|----------|-------|-------------|
| 🧩 meta | ai-builder | 10 | 智能组合（架构设计指南） |
| 🧩 meta | contribute | 1 | 社区贡献 |
| 🧩 meta | mcp-adapter | 1 | MCP 工具适配 |
| ⚡ action | code | 3 | 代码操作（沙箱、搜索、Git Diff） |
| ⚡ action | web | 2 | 网络操作（抓取、API 测试） |
| ⚡ action | file | 4 | 文件操作（PDF、CSV、图片、日志） |
| ⚡ action | device | 3 | 设备交互（语音、SSH、邮件） |
| 🧠 core | - | 5 | 核心能力（定时任务、Token、摘要、记忆、数据库） |
| 🎭 identity | - | 2 | 身份层（Markdown 渲染、Frontmatter 解析） |
| **Total** | | **31** | |

---

## Skill Categories / 分类详情

```
skills/
├── meta/              🧩 元能力层（12 个）
│   ├── ai-builder/      🧩 智能组合（10 个架构设计）
│   ├── contribute/      🤝 社区贡献
│   └── mcp-adapter/     🔌 MCP 工具适配
│
├── action/            ⚡ 执行能力层（12 个）
│   ├── code/            💻 代码操作（3 个）
│   ├── web/             🌐 网络操作（2 个）
│   ├── file/            📁 文件操作（4 个）
│   └── device/          📱 设备交互（3 个）
│
├── core/              🧠 核心能力层（5 个）
│   ├── cron-scheduler/  ⏰ 定时任务
│   ├── token-estimator/ 🔢 Token 估算
│   ├── text-summarizer/ 📝 文本摘要
│   ├── memory-extractor/🧠 记忆提取
│   └── db-query/        🗄️ 数据库查询
│
└── identity/          🎭 身份层（2 个）
    ├── markdown-renderer/📄 Markdown 渲染
    └── frontmatter-parser/📋 Frontmatter 解析
```

---

## License

MIT
