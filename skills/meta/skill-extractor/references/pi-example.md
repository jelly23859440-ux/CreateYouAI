# Pi 项目拆解实例

Pi Agent Harness 是一个完整的 AI Coding Agent 框架，从中提取了 4 个 skill。这份文档记录了完整的拆解过程，作为 skill-extractor 的参考案例。

---

## 项目概况

| 属性 | 值 |
|------|-----|
| 项目名 | Pi Agent Harness |
| 路径 | `D:\AI\参考\CODES\pi-main` |
| 语言 | TypeScript |
| 架构 | Monorepo (5 packages) |
| 版本 | 1.0.0 |
| 功能 | AI Coding Agent 框架 |

### 包结构

```
pi-main/
├── packages/
│   ├── agent/           # 核心 Agent 框架
│   ├── ai/              # LLM 调用层
│   ├── coding-agent/    # 编码 Agent 实现
│   ├── ui/              # 终端 UI
│   └── shared/          # 共享工具
├── package.json         # workspaces 配置
└── README.md
```

---

## 扫描过程

### 第一步：读 README

README 说明了 Pi 是一个 AI Coding Agent 框架，支持：
- 多 LLM 提供商
- 工具调用
- 技能系统
- 扩展机制

### 第二步：读 package.json

```json
{
  "workspaces": ["packages/*"],
  "dependencies": {
    "ai-sdk": "^3.0.0",
    "typebox": "^0.32.0"
  }
}
```

确认是 monorepo，有 5 个 package。

### 第三步：扫描目录结构

每个 package 的入口文件：
- `packages/agent/src/index.ts` → Agent 核心框架
- `packages/ai/src/index.ts` → LLM 调用层
- `packages/coding-agent/src/index.ts` → 编码 Agent
- `packages/ui/src/index.ts` → 终端 UI
- `packages/shared/src/index.ts` → 共享工具

### 第四步：识别功能点

深入阅读各 package 的核心文件，识别出 4 个可提取的功能点。

---

## 功能点清单

| # | 功能点 | 类型 | 层级 | 来源包 | 说明 |
|---|--------|------|------|--------|------|
| 1 | skill-system | skill | meta | agent | SKILL.md 格式定义、渐进加载、多位置发现 |
| 2 | llm-provider | skill | core | ai | 统一调用 30+ LLM 提供商，流式输出 |
| 3 | tool-calling | skill | core | agent | TypeBox schema 定义、执行钩子、并行模式 |
| 4 | extension-system | skill | meta | coding-agent | 事件驱动、热重载、自定义工具/命令 |

### 推荐拆解顺序

1. **skill-system**（低难度高价值）— 独立性强，无外部依赖，是 meta 层基础
2. **llm-provider**（中难度高价值）— 依赖 ai-sdk，但接口清晰，复用价值大
3. **tool-calling**（中难度高价值）— 依赖 TypeBox，与 skill-system 有弱依赖
4. **extension-system**（高难度）— 依赖事件系统，复杂度较高

---

## 拆解详情

### 1. skill-system

**来源**：`packages/agent/src/skill/`

**提取内容**：
- SKILL.md 格式定义（frontmatter + 正文结构）
- 渐进加载机制（先读 frontmatter，按需读全文）
- 多位置发现（从多个目录扫描 skill）

**生成结果**：
```
skills/meta/skill-learn/skill-system/
├── SKILL.md          # 格式规范 + 加载机制说明
└── references/
    └── format-spec.md  # 详细的 SKILL.md 格式规范
```

**SKILL.md 核心内容**：
- 定义 SKILL.md 的 frontmatter 字段（name/layer/category/status/description）
- 定义渐进加载流程（读 frontmatter → 匹配触发条件 → 按需读全文）
- 定义多位置发现策略（项目级 → 用户级 → 全局）

---

### 2. llm-provider

**来源**：`packages/ai/src/`

**提取内容**：
- 统一的 LLM 调用接口（chat/completion/embedding）
- 多提供商适配（OpenAI/Anthropic/Gemini/...）
- 流式输出处理

**生成结果**：
```
skills/core/reasoning/llm-provider/
├── SKILL.md          # 接口规范 + 使用方法
└── scripts/
    └── provider.ts   # Provider 接口定义 + 适配器模板
```

**SKILL.md 核心内容**：
- 定义 LLM Provider 接口（chat/stream/embed）
- 列出支持的提供商及配置方式
- 提供适配器实现模板

---

### 3. tool-calling

**来源**：`packages/agent/src/tool/`

**提取内容**：
- TypeBox schema 定义工具参数
- 执行钩子（before/after/error）
- 并行调用模式

**生成结果**：
```
skills/core/tool/tool-calling/
├── SKILL.md          # 工具调用规范 + 钩子机制
└── references/
    └── schema-guide.md  # TypeBox schema 编写指南
```

**SKILL.md 核心内容**：
- 定义工具注册接口（name/description/schema/handler）
- 定义执行钩子（before/after/error）
- 定义并行调用模式

---

### 4. extension-system

**来源**：`packages/coding-agent/src/extension/`

**提取内容**：
- 事件驱动的扩展机制
- 热重载支持
- 自定义工具/命令注册

**生成结果**：
```
skills/meta/ai-builder/extension-system/
├── SKILL.md          # 扩展系统设计规范
└── references/
    └── event-list.md  # 事件清单
```

**SKILL.md 核心内容**：
- 定义扩展点（工具/命令/钩子）
- 定义事件系统（事件类型 + 监听 + 触发）
- 定义热重载机制

---

## 依赖关系

```
skill-system (meta)
    ↑
    ├── tool-calling (core) — 弱依赖：工具注册用到 skill 格式
    └── extension-system (meta) — 弱依赖：扩展系统注册 skill

llm-provider (core)
    ↑
    └── tool-calling (core) — 无直接依赖，但工具调用可能用到 LLM
```

**加载顺序建议**：
1. skill-system（基础）
2. llm-provider（独立）
3. tool-calling（依赖 skill-system）
4. extension-system（依赖 skill-system）

---

## 拆解经验

### 成功的点

1. **先读 README 再读代码**：README 快速建立了项目全貌理解
2. **按 package 分析**：monorepo 逐包分析效率高
3. **先识别模式再提取代码**：Provider/Registry/Pipeline 等模式是可复用的核心
4. **保持独立性**：每个 skill 尽量减少对其他 skill 的依赖

### 踩的坑

1. **功能点太大**：最初把 tool-calling 和 extension-system 合在一起，后来发现太复杂，拆开了
2. **业务逻辑混入**：最初提取的代码包含 Pi 特定的逻辑，后来通用化了
3. **依赖未标注**：最初没标注 tool-calling 对 skill-system 的弱依赖，后来补充

### 给后续拆解的建议

1. **功能点不要太大**：一个 skill 只做一件事，太复杂的拆开
2. **先通用化再提取**：去掉项目特定逻辑后再提取代码
3. **标注依赖关系**：即使弱依赖也要标注，方便用户理解加载顺序
4. **优先拆 meta 层**：meta 层的 skill 通常被其他 skill 依赖，先拆
