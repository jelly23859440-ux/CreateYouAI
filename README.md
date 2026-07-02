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

## Available Skills

| Skill | Category | Description |
|-------|----------|-------------|
| [ai-builder](skills/ai-builder/) | 🧩 meta | Scan skills and help users build their AI / 扫描仓库，帮用户挑选组合 Skill |
| [voice-recognition](skills/audio/voice-recognition/) | 🎤 audio | Local speech recognition / 本地语音识别 |
| [contribute-skill](skills/contribute-skill/) | 🧩 meta | Submit new skills to the repository / 向仓库提交新 Skill |

---

## Quick Start / 快速开始

Tell your AI: "我想做一个 XX 的 AI" / 告诉你的 AI："我想做一个 XX 的 AI"

The AI will read the `ai-builder` Skill and automatically pick the right combination from this repository.

AI 会读取 `ai-builder` Skill，自动从仓库挑选合适的组合。

---

## Skill Categories / 分类

```
skills/
├── audio/         🎤 语音音频
├── code/          💻 编程开发
├── data/          📊 数据处理
├── memory/        🧠 记忆系统
├── safety/        🛡️ 安全护栏
├── task/          📋 任务管理
├── tool/          🔧 工具集成
├── personality/   🎭 角色人格
├── conversation/  💬 对话管理
├── other/         📦 其他
└── ai-builder/    🧩 智能组合
```

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
