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

| Skill | Layer | Category | Status | Description |
|-------|-------|----------|--------|-------------|
| [voice-recognition](skills/action/device/voice-recognition/) | ⚡ action | device | ✅ verified | 本地语音识别 |
| [git-diff-analyzer](skills/action/code/git-diff-analyzer/) | ⚡ action | code | ⚠️ unverified | Git Diff 分析器 |
| [code-search](skills/action/code/code-search/) | ⚡ action | code | ⚠️ unverified | 代码搜索工具 |
| [code-sandbox](skills/action/code/code-sandbox/) | ⚡ action | code | ⚠️ unverified | 代码沙箱执行 |
| [web-fetch](skills/action/web/web-fetch/) | ⚡ action | web | ⚠️ unverified | Web 抓取 + Markdown 转换 |
| [api-tester](skills/action/web/api-tester/) | ⚡ action | web | ⚠️ unverified | API 测试工具 |
| [pdf-reader](skills/action/file/pdf-reader/) | ⚡ action | file | ⚠️ unverified | PDF 读取器 |
| [csv-json-converter](skills/action/file/csv-json-converter/) | ⚡ action | file | ⚠️ unverified | CSV/JSON 转换 |
| [image-processor](skills/action/file/image-processor/) | ⚡ action | file | ⚠️ unverified | 图片处理 |
| [log-analyzer](skills/action/file/log-analyzer/) | ⚡ action | file | ⚠️ unverified | 日志分析 |
| [ssh-remote](skills/action/device/ssh-remote/) | ⚡ action | device | ⚠️ unverified | SSH 远程执行 |
| [email-sender](skills/action/device/email-sender/) | ⚡ action | device | ⚠️ unverified | 邮件发送 |
| [cron-scheduler](skills/core/cron-scheduler/) | 🧠 core | - | ⚠️ unverified | 定时任务调度 |
| [token-estimator](skills/core/token-estimator/) | 🧠 core | - | ⚠️ unverified | Token 估算 |
| [text-summarizer](skills/core/text-summarizer/) | 🧠 core | - | ⚠️ unverified | 文本摘要 |
| [memory-extractor](skills/core/memory-extractor/) | 🧠 core | - | ⚠️ unverified | 记忆提取 |
| [db-query](skills/core/db-query/) | 🧠 core | - | ⚠️ unverified | 数据库查询 |
| [markdown-renderer](skills/identity/markdown-renderer/) | 🎭 identity | - | ⚠️ unverified | Markdown 渲染 |
| [frontmatter-parser](skills/identity/frontmatter-parser/) | 🎭 identity | - | ⚠️ unverified | Frontmatter 解析 |
| [ai-builder](skills/meta/ai-builder/) | 🧩 meta | ai-builder | ⚠️ unverified | AI 构建器 |
| [contribute](skills/meta/contribute/) | 🧩 meta | contribute | ⚠️ unverified | 贡献 Skill |
| [mcp-adapter](skills/meta/mcp-adapter/) | 🧩 meta | mcp-adapter | ⚠️ unverified | MCP 适配器 |

### 验证状态说明

| Status | 含义 | 谁提交 |
|--------|------|--------|
| ✅ verified | 代码已实际跑通，确认可用 | 实际验证过的用户 |
| ⚠️ unverified | 代码未实际验证，可能存在 bug | 原作者 |

### 如何验证 Skill？

1. 选择一个 `unverified` 的 Skill
2. 按照 SKILL.md 中的代码示例实际运行
3. 如果发现 bug → 修复后提交 PR
4. 修复版通过验证 → 状态改为 `verified`，作者更新为验证者

详细格式见 [SKILL-FORMAT.md](SKILL-FORMAT.md)

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
