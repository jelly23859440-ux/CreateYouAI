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

## Ideas / 有想法？

Have an idea for an AI skill but can't build it yourself? Submit an idea and let the community build it.

有 AI 想法但自己不会写？去 [ideas/](ideas/) 提想法，让社区帮你实现。

---

## Available Skills

| Skill | Layer | Category | Description |
|-------|-------|----------|-------------|
| [ai-builder](skills/meta/ai-builder/) | 🧩 meta | 智能组合 | Scan skills and help users build their AI / 扫描仓库，帮用户挑选组合 Skill |
| [tool-system-builder](skills/meta/ai-builder/) | 🧩 meta | 智能组合 | Design and build modular tool systems / 设计构建模块化工具系统 |
| [contribute](skills/meta/contribute/) | 🧩 meta | 社区贡献 | Submit new skills to the repository / 向仓库提交新 Skill |
| [voice-recognition](skills/action/device/voice-recognition/) | ⚡ action | 设备交互 | Local speech recognition / 本地语音识别 |

---

## Quick Start / 快速开始

Tell your AI: "我想做一个 XX 的 AI" / 告诉你的 AI："我想做一个 XX 的 AI"

The AI will read the `ai-builder` Skill and automatically pick the right combination from this repository.

AI 会读取 `ai-builder` Skill，自动从仓库挑选合适的组合。

---

## Skill Architecture / 能力架构

CreateYouAI organizes skills by what an AI Agent actually needs, not by technical domain.

CreateYouAI 按照 AI Agent 真正需要的能力来组织 Skill，而非按技术领域分类。

```
skills/
├── core/              🧠 核心能力层 —— 没有这些，Agent 不成立
│   ├── conversation/    💬 对话能力（多轮、上下文、意图识别）
│   ├── reasoning/       🧩 推理能力（规划、决策、反思）
│   └── memory/          🧠 记忆能力（热/温/冷、检索、整理）
│
├── action/            ⚡ 执行能力层 —— Agent 能"做事"
│   ├── code/            💻 代码能力（生成、调试、重构）
│   ├── tool/            🔧 工具调用（CLI、API、MCP）
│   ├── file/            📁 文件操作（读写、搜索、管理）
│   ├── web/             🌐 网络能力（浏览、抓取、搜索）
│   └── device/          📱 设备控制（语音、屏幕、硬件）
│
├── identity/          🎭 身份层 —— Agent "是谁"
│   ├── personality/     🎭 人格设定（角色、语气、风格）
│   ├── safety/          🛡️ 安全护栏（规则、过滤、限制）
│   └── knowledge/       📚 知识领域（专业、背景、偏好）
│
├── meta/              🧩 元能力层 —— 能力的能力
│   ├── ai-builder/      🧩 智能组合（扫描、挑选、组装）
│   ├── skill-learn/     📖 技能学习（从外部学习新能力）
│   └── contribute/      🤝 社区贡献（提交、审核、分享）
│
└── scenarios/         🎯 场景层 —— 预设组合模板
    ├── coding-ai/       💻 编程助手模板
    ├── research-ai/     🔬 研究助手模板
    ├── creative-ai/     🎨 创意助手模板
    └── daily-ai/        🏠 日常助手模板
```

### Layer Logic / 分层逻辑

| Layer | Logic | User Need |
|-------|-------|-----------|
| **core** | Agent's "brain" — essential | "I want an AI that can chat and remember things" |
| **action** | Agent's "hands" — add as needed | "I want an AI that can write code and browse the web" |
| **identity** | Agent's "character" — optional | "I want a professional/fun/safe AI" |
| **meta** | Capability extension | "I want an AI that can learn new skills" |
| **scenarios** | Quick-start templates | "I want a coding assistant, ready to use" |

### Design Principles / 设计原则

1. **Capabilities, not features** — Skills are organized by what the Agent needs, not by technical domain
2. **Layered composition** — Start with core, add action/identity as needed
3. **Scenario templates** — Pre-built combinations for common use cases
4. **Community-driven** — Anyone can contribute skills to any layer

---

## Contributing / 贡献

**Welcome to contribute! We need your skills. / 欢迎贡献！我们需要你的 Skill。**

1. Fork this repository / Fork 本仓库
2. Write a Skill following [SKILL-FORMAT.md](SKILL-FORMAT.md) / 按 SKILL-FORMAT.md 写 Skill
3. Submit a PR / 提交 PR

Or tell your AI: "我想贡献一个 skill" / 或告诉你的 AI："我想贡献一个 skill"

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT
