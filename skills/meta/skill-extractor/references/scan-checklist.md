# 扫描清单

项目扫描是阶段 1 的核心工作。这份清单定义了"读什么文件、看什么模式"。

---

## 扫描顺序

按以下顺序读取文件，逐步建立对项目的理解：

### 第一步：项目概况（必读）

| 文件 | 作用 | 看什么 |
|------|------|--------|
| `README.md` | 项目意图 | 项目做什么、核心功能列表、架构图、快速开始 |
| `README.{en,zh,ja,ko}.md` | 多语言 README | 同上，取最完整版本 |
| `CHANGELOG.md` | 版本历史 | 功能演进轨迹，哪些是核心功能 |
| `LICENSE` | 许可证 | 是否允许提取复用 |

### 第二步：依赖和技术栈（必读）

| 文件 | 语言 | 看什么 |
|------|------|--------|
| `package.json` | Node/TS | dependencies + devDependencies + scripts + workspaces |
| `pyproject.toml` | Python | dependencies + project metadata + entry points |
| `requirements.txt` | Python | 依赖列表 |
| `Cargo.toml` | Rust | dependencies + workspace members |
| `go.mod` | Go | module path + requires |
| `pom.xml` / `build.gradle` | Java | dependencies + modules |

**关键信号**：
- 有 `workspaces` 字段 → monorepo，需要逐包分析
- 有 `entry points` → 找到 CLI/API 入口
- 依赖中有 `openai` / `anthropic` / `langchain` → AI 项目
- 依赖中有 `fastapi` / `express` / `gin` → Web 服务

### 第三步：目录结构（必读）

扫描整个项目的目录树，重点看：

```
项目根目录
├── src/            # 源码主目录 → 看子目录划分
├── packages/       # monorepo 包目录 → 每个包独立分析
├── lib/            # 库代码
├── cmd/            # CLI 命令（Go 风格）
├── internal/       # 内部模块（Go 风格）
├── tests/          # 测试 → 看测什么功能
├── docs/           # 文档 → 补充理解
├── examples/       # 示例 → 看用法
├── config/         # 配置 → 看支持哪些配置项
└── scripts/        # 脚本 → 看构建/部署流程
```

**识别模式**：
- `src/` 下按功能分目录 → 每个目录可能是一个功能点
- `packages/` 下每个包 → 可能是独立功能点
- `src/core/` + `src/utils/` + `src/api/` → 核心逻辑 vs 工具 vs 接口

### 第四步：入口文件（重要）

找到项目的入口文件，理解核心调用链路：

| 语言 | 入口文件位置 |
|------|-------------|
| Node/TS | `package.json` 的 `main` / `bin` 字段指向的文件 |
| Python | `pyproject.toml` 的 `entry_points` / `__main__.py` |
| Rust | `src/main.rs` + `src/lib.rs` |
| Go | `main.go` / `cmd/` 目录 |

**看什么**：
- 初始化流程 → 了解依赖注入和模块加载
- 路由注册 → 了解 API 端点
- 插件/扩展注册 → 了解扩展点

### 第五步：核心模块（按需）

根据前四步的结果，深入阅读关键模块的源码：

**优先看**：
- 模块入口文件（`index.ts` / `__init__.py` / `mod.rs`）
- 接口定义（`types.ts` / `interfaces.py` / `traits.rs`）
- 核心实现类（带 `Manager` / `Provider` / `Handler` / `Registry` 的文件）

**识别可复用模式**：
- Provider 模式 → 可提取为可扩展的接口层
- Registry 模式 → 可提取为插件/扩展系统
- Pipeline/Chain 模式 → 可提取为中间件系统
- Factory 模式 → 可提取为对象创建系统

### 第六步：配置和扩展点（按需）

| 文件 | 看什么 |
|------|--------|
| `config/*.yml` | 支持的配置项、默认值 |
| `*.schema.json` | 配置 schema |
| `plugins/` / `extensions/` | 扩展系统设计 |
| `middleware/` | 中间件链 |
| `decorators/` | 装饰器/注解系统 |

---

## 扫描策略

### 小型项目（<20 个源码文件）

全量扫描，每个文件都看一遍。

### 中型项目（20-100 个源码文件）

1. 先读配置文件和目录结构
2. 识别核心模块（3-5 个）
3. 深入阅读核心模块的入口和接口
4. 其他模块只看文件名和导出

### 大型项目（>100 个源码文件）

1. 先读配置文件和目录结构
2. 如果是 monorepo，按 package 逐个分析
3. 每个 package 内部按中型项目策略
4. 建议分批拆解，一次只拆 1-2 个 package

### Monorepo 特殊处理

如果检测到 monorepo（`workspaces` 字段或 `packages/` 目录）：

1. 列出所有 package
2. 对每个 package 独立执行扫描流程
3. 分析 package 之间的依赖关系
4. 在功能点清单中标注来源包

---

## 功能点识别信号

以下模式暗示可提取的功能点：

| 信号 | 可能的功能点 | 示例 |
|------|-------------|------|
| 有 `Provider` / `Adapter` 类 | 可扩展的接口层 | LLM Provider、数据库 Adapter |
| 有 `Registry` / `Manager` 类 | 注册/管理系统 | 插件系统、技能管理 |
| 有 `schema` / `validation` 逻辑 | 数据验证系统 | 参数校验、配置验证 |
| 有 `middleware` / `pipeline` | 中间件系统 | 请求处理链 |
| 有 `plugin` / `extension` 目录 | 扩展系统 | 自定义命令、自定义工具 |
| 有 `cli` / `command` 目录 | CLI 框架 | 命令注册、参数解析 |
| 有 `memory` / `context` 逻辑 | 记忆/上下文系统 | 对话历史、知识库 |
| 有 `tool` / `function` 调用 | 工具调用系统 | Function calling、工具执行 |
| 有 `prompt` / `template` 逻辑 | 提示词系统 | 模板渲染、prompt 管理 |

---

## 输出要求

扫描完成后，必须输出结构化的功能点清单（见 SKILL.md 阶段 1 的输出格式）。

**每个功能点必须包含**：
- 名称（简短，小写连字符）
- 类型（tool/skill/agent）
- 层级（core/action/identity/meta）
- 来源包/模块路径
- 一句话说明

**推荐拆解顺序的排序逻辑**：
1. 低难度高价值：独立性强、依赖少、复用价值高
2. 中难度高价值：有一定依赖但价值大
3. 高难度：依赖复杂或需要较多改造
