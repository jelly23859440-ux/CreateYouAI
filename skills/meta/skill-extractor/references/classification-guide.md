# 分类标准

定义如何将功能点按类型（type）和层级（layer）分类。这是阶段 1 扫描和阶段 3 生成的核心依据。

---

## 类型（Type）

类型描述功能点的"产物形态"——拆解后生成什么。

| 类型 | 说明 | 产物 | 判断信号 |
|------|------|------|----------|
| `tool` | 可执行的工具 | scripts/ 下的脚本 | 有可独立运行的代码，接受输入产出输出 |
| `skill` | 技能文档 | SKILL.md + references/ | 是工作流/最佳实践/配置指南，不需要可执行脚本 |
| `agent` | Agent 配置 | SKILL.md（含人格/行为定义） | 定义 Agent 的人格、角色、行为模式 |

### 类型判断流程

```
功能点有可执行的代码吗？
├── 是 → 代码可以独立运行吗？
│   ├── 是 → type: tool
│   └── 否（需要框架支撑）→ 是框架的核心能力吗？
│       ├── 是 → type: skill（描述如何使用框架能力）
│       └── 否 → type: skill
└── 否 → 是行为模式/人格定义吗？
    ├── 是 → type: agent
    └── 否 → type: skill
```

### 类型示例

| 功能点 | 类型 | 理由 |
|--------|------|------|
| 文件操作工具 | `tool` | 有可执行的脚本，接受路径输入，产出文件操作结果 |
| API 调用工具 | `tool` | 有可执行的脚本，接受参数，返回 API 响应 |
| Git 工作流 | `skill` | 是最佳实践文档，不需要可执行脚本 |
| 代码审查流程 | `skill` | 是工作流指南 |
| 助手人格定义 | `agent` | 定义 Agent 的角色和行为模式 |
| 安全策略配置 | `agent` | 定义 Agent 的安全约束 |

---

## 层级（Layer）

层级描述功能点在 AI Agent 架构中的位置——解决什么层面的问题。

| 层级 | 说明 | 解决的问题 | 典型 Category |
|------|------|-----------|---------------|
| `core` | 核心能力 | Agent 的"大脑"——思考、记忆、推理 | conversation, reasoning, memory |
| `action` | 执行能力 | Agent 的"手脚"——操作外部世界 | code, tool, file, web, device |
| `identity` | 身份能力 | Agent "是谁"——人格、安全、知识 | personality, safety, knowledge |
| `meta` | 元能力 | 能力的能力——管理其他 skill | ai-builder, skill-learn, contribute |
| `scenarios` | 场景模板 | 预设组合——多个 skill 的编排 | coding-ai, research-ai, creative-ai, daily-ai |

### 层级判断流程

```
这个功能点做什么？

A. 直接与 LLM 交互（调用模型、管理对话、处理记忆）
   → layer: core

B. 操作外部世界（文件、网络、设备、代码执行）
   → layer: action

C. 定义 Agent 自身属性（人格、安全约束、知识库）
   → layer: identity

D. 管理其他 skill（加载、注册、发现、学习）
   → layer: meta

E. 编排多个 skill 完成特定场景（编码助手、研究助手）
   → layer: scenarios
```

### 层级示例

| 功能点 | 层级 | 理由 |
|--------|------|------|
| LLM 调用接口 | `core` | 直接与 LLM 交互，是大脑的核心能力 |
| 对话记忆管理 | `core` | 管理对话上下文，是大脑的记忆 |
| 工具调用框架 | `core` | 调用工具是核心推理能力的延伸 |
| 文件读写 | `action` | 操作文件系统 |
| HTTP 请求 | `action` | 操作网络 |
| 代码执行 | `action` | 执行代码 |
| 人格设定 | `identity` | 定义 Agent 是谁 |
| 安全沙箱 | `identity` | 安全约束 |
| 知识库管理 | `identity` | Agent 的知识 |
| Skill 加载系统 | `meta` | 管理其他 skill 的加载 |
| 扩展系统 | `meta` | 管理插件/扩展 |
| Skill 提取器 | `meta` | 从项目提取 skill（本 skill 自身） |
| 编码助手模板 | `scenarios` | 编排多个 skill 用于编码场景 |

---

## Category 细分

每个 layer 下有具体的 category，用于更精确的分类：

### core 层

| Category | 说明 | 示例功能点 |
|----------|------|-----------|
| `conversation` | 对话管理 | 多轮对话、上下文窗口管理 |
| `reasoning` | 推理能力 | 思维链、ReAct、规划 |
| `memory` | 记忆系统 | 短期记忆、长期记忆、向量存储 |

### action 层

| Category | 说明 | 示例功能点 |
|----------|------|-----------|
| `code` | 代码执行 | 代码沙箱、脚本执行 |
| `tool` | 工具调用 | 函数调用、工具注册 |
| `file` | 文件操作 | 读写、搜索、监控 |
| `web` | 网络操作 | HTTP、爬虫、API 调用 |
| `device` | 设备交互 | 音频、摄像头、IoT |

### identity 层

| Category | 说明 | 示例功能点 |
|----------|------|-----------|
| `personality` | 人格设定 | 角色定义、语气风格 |
| `safety` | 安全策略 | 输入过滤、输出审查、沙箱 |
| `knowledge` | 知识库 | RAG、知识注入、文档加载 |

### meta 层

| Category | 说明 | 示例功能点 |
|----------|------|-----------|
| `ai-builder` | Agent 构建 | 框架搭建、Agent 组装 |
| `skill-learn` | 技能学习 | 从项目提取 skill、技能进化 |
| `contribute` | 贡献流程 | skill 格式标准、贡献指南 |

### scenarios 层

| Category | 说明 | 示例功能点 |
|----------|------|-----------|
| `coding-ai` | 编码助手 | 代码生成、审查、重构 |
| `research-ai` | 研究助手 | 文献搜索、数据分析 |
| `creative-ai` | 创意助手 | 写作、设计、头脑风暴 |
| `daily-ai` | 日常助手 | 日程、邮件、自动化 |

---

## 分类决策表

常见功能点的快速分类参考：

| 功能点 | type | layer | category |
|--------|------|-------|----------|
| LLM Provider（多模型统一调用） | skill | core | reasoning |
| Tool Calling（工具调用框架） | skill | core | tool |
| 对话记忆管理 | skill | core | memory |
| 文件操作工具 | tool | action | file |
| HTTP 请求工具 | tool | action | web |
| 代码沙箱执行 | tool | action | code |
| Skill 加载系统 | skill | meta | skill-learn |
| 扩展/插件系统 | skill | meta | ai-builder |
| 助手人格定义 | agent | identity | personality |
| 输入安全过滤 | skill | identity | safety |
| 知识库 RAG | skill | identity | knowledge |
| 编码助手模板 | skill | scenarios | coding-ai |

---

## 边界情况

### 一个功能点跨多个层级

取主要层级，在 SKILL.md 的"功能说明"中注明次要层级。

示例：Tool Calling 框架
- 主要层级：`core`（工具调用是核心推理能力的延伸）
- 次要层级：`action`（调用的是 action 层的工具）
- 处理：layer 设为 `core`，在说明中注明"也涉及 action 层"

### 一个功能点包含多个类型

拆分成多个 skill。

示例：一个文件操作模块既有可执行脚本又有使用指南
- skill 1: `file-operations`（type: tool, layer: action, category: file）— 可执行脚本
- skill 2: `file-workflow`（type: skill, layer: action, category: file）— 最佳实践

### 不确定分类时

优先判断 layer（更容易确定），type 默认为 `skill`。
在功能点清单中标注"⚠️ 分类待确认"，让用户在阶段 2 决定。
