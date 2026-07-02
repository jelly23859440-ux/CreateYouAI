---
name: 工具系统构建器
layer: meta
category: ai-builder
description: >
  教 AI 如何帮用户设计和构建模块化的工具系统。
  当用户想要设计工具注册、工具执行、权限控制、工具编排时触发。
  关键词：工具系统、工具注册、tool registry、tool execution、MCP、工具模块化。
---

# 工具系统构建器

教 AI 如何帮用户设计和构建模块化的工具系统，支持多种技术栈。

## 能力概览

| 能力 | 说明 |
|------|------|
| 工具注册表设计 | 中央管理所有工具，按需加载 |
| 工具执行引擎 | Schema 验证 → 权限检查 → 执行 → 返回 |
| 权限系统设计 | auto/prompt/rule/deny 四种模式 |
| MCP 集成 | 扩展外部工具能力 |
| 并行执行 | 拓扑排序，支持依赖链 |

## 构建方案选择

**先问用户技术栈，再选方案：**

```
IF 用户用 TypeScript/Node.js:
    → 方案一（TypeScript 版）— 生产验证，推荐
ELSE IF 用户用 Python:
    → 方案二（Python 版）— 社区贡献，待验证
ELSE IF 用户用其他语言:
    → 方案三（通用架构模式）— 社区贡献，待验证
```

| 你的技术栈 | 推荐方案 | 状态 |
|-----------|----------|------|
| TypeScript/Node.js | 方案一 | ✅ 生产验证 |
| Python | 方案二 | ⚠️ 社区贡献，待验证 |
| Go/Rust/Java/其他 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的工具系统（CLI/API/Agent）
- **先问技术栈**：确认用户使用的语言和框架
- **每个工具只做一件事**：不要设计"万能工具"
- **权限规则必须明确**：读操作自动批准，写操作需确认，危险操作需特别确认
- **验证每一步**：每个工具实现后要有测试用例
- **不要猜测需求**：让用户告诉你具体需要什么工具

### 设计原则

1. **单一职责**：每个工具只做一件事
2. **自包含**：工具目录包含所有需要的文件
3. **无状态**：工具不保存跨调用状态
4. **可测试**：工具可以独立测试
5. **幂等**：相同输入产生相同输出（尽可能）

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Zod | v4+ | Schema 验证 |
| Node.js | 18+ | 运行时 |
| React | 18+ | UI 渲染（可选） |

### Python 版 ⚠️ 社区贡献，待验证

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行时 |
| Pydantic | v2+ | Schema 验证 |
| Rich | 13+ | 终端 UI（可选） |

### 通用版 ⚠️ 社区贡献，待验证

无特殊依赖，只需支持接口/协议定义的语言。

---

## 安装步骤

### Step 1：创建工具注册表

根据技术栈选择实现：

**TypeScript 版：**
```typescript
// tools/registry.ts
class ToolRegistry {
  private tools: Map<string, Tool> = new Map();
  
  register(tool: Tool): void {
    this.tools.set(tool.name, tool);
  }
  
  get(name: string): Tool | undefined {
    return this.tools.get(name);
  }
  
  getAll(): Tool[] {
    return Array.from(this.tools.values());
  }
  
  getForContext(context: ToolContext): Tool[] {
    return this.getAll().filter(tool => 
      tool.isAvailable?.(context) ?? true
    );
  }
}
```

**Python 版 ⚠️ 社区贡献，待验证：**
```python
# tools/registry.py
from typing import Dict, List, Optional

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)
    
    def get_all(self) -> List[Tool]:
        return list(self._tools.values())
    
    def get_for_context(self, context: ToolContext) -> List[Tool]:
        return [t for t in self.get_all() if t.is_available(context)]
```

**验证**：创建注册表实例，注册一个测试工具，确认能获取。

### Step 2：定义工具接口

**TypeScript 版：**
```typescript
// tools/types.ts
type ToolResult<T> = 
  | { success: true; data: T }
  | { success: false; error: string };

interface Tool<Input = any, Output = any> {
  name: string;
  description: string;
  inputSchema: ZodSchema<Input>;
  permission: PermissionModel;
  execute(input: Input, context: ToolContext): Promise<ToolResult<Output>>;
  isAvailable?: (context: ToolContext) => boolean;
}
```

**Python 版 ⚠️ 社区贡献，待验证：**
```python
# tools/types.py
from typing import Any, Generic, TypeVar, Optional, Callable
from pydantic import BaseModel

Input = TypeVar('Input', bound=BaseModel)
Output = TypeVar('Output', bound=BaseModel)

class ToolResult(BaseModel, Generic[Output]):
    success: bool
    data: Optional[Output] = None
    error: Optional[str] = None

class Tool(Generic[Input, Output]):
    name: str
    description: str
    input_schema: type[Input]
    permission: PermissionModel
    
    def execute(self, input: Input, context: ToolContext) -> ToolResult[Output]:
        raise NotImplementedError
    
    def is_available(self, context: ToolContext) -> bool:
        return True
```

**验证**：定义一个简单的工具类，确认类型检查通过。

### Step 3：实现权限系统

**TypeScript 版：**
```typescript
// tools/permissions.ts
type PermissionModel = 
  | { type: 'auto' }
  | { type: 'prompt' }
  | { type: 'rule', rules: PermissionRule[] }
  | { type: 'deny' };

interface PermissionRule<Input> {
  condition: (input: Input, context: ToolContext) => boolean;
  action: 'allow' | 'deny' | 'prompt';
  reason?: string;
}
```

**Python 版 ⚠️ 社区贡献，待验证：**
```python
# tools/permissions.py
from typing import Callable, List, Literal, Union

class PermissionRule:
    def __init__(
        self,
        condition: Callable[[Any, ToolContext], bool],
        action: Literal['allow', 'deny', 'prompt'],
        reason: str = ''
    ):
        self.condition = condition
        self.action = action
        self.reason = reason

PermissionModel = Union[
    Literal['auto'],
    Literal['prompt'],
    Literal['deny'],
    tuple[Literal['rule'], List[PermissionRule]]
]
```

**验证**：创建权限规则，测试条件函数。

### Step 4：添加工具执行引擎

**TypeScript 版：**
```typescript
// tools/executor.ts
async function executeTool(
  tool: Tool,
  input: any,
  context: ToolContext
): Promise<ToolResult> {
  const validatedInput = tool.inputSchema.parse(input);
  const permission = await checkPermission(tool, validatedInput, context);
  if (permission.denied) {
    return { success: false, error: permission.reason };
  }
  const result = await tool.execute(validatedInput, context);
  logToolExecution(tool.name, validatedInput, result);
  return result;
}
```

**Python 版 ⚠️ 社区贡献，待验证：**
```python
# tools/executor.py
async def execute_tool(
    tool: Tool,
    input_data: Any,
    context: ToolContext
) -> ToolResult:
    validated_input = tool.input_schema.parse_obj(input_data)
    permission = await check_permission(tool, validated_input, context)
    if permission.denied:
        return ToolResult(success=False, error=permission.reason)
    result = await tool.execute(validated_input, context)
    log_tool_execution(tool.name, validated_input, result)
    return result
```

**验证**：创建一个测试工具，执行并验证结果。

### Step 5：集成 MCP（可选）

如果用户已有 MCP 服务器，添加适配器：

```typescript
function adaptMCPTool(mcpTool: MCPTool): Tool {
  return {
    name: mcpTool.name,
    description: mcpTool.description,
    inputSchema: mcpJsonSchemaToZod(mcpTool.inputSchema),
    permission: { type: 'prompt' },
    execute: async (input, context) => {
      const server = context.mcpServers.find(s => 
        s.tools.includes(mcpTool.name)
      );
      return server.callTool(mcpTool.name, input);
    },
  };
}
```

**验证**：连接 MCP 服务器，调用一个工具。

---

## 使用方法

### 创建自定义工具

**TypeScript 示例：**
```typescript
import { z } from 'zod';
import { buildTool } from '../Tool';

const GitToolSchema = z.object({
  command: z.enum(['status', 'diff', 'log', 'commit', 'push', 'pull'])
    .describe('Git 命令'),
  args: z.string().optional().describe('额外参数'),
});

export const GitTool = buildTool({
  name: 'Git',
  description: '执行 Git 操作',
  inputSchema: GitToolSchema,
  permission: {
    type: 'rule',
    rules: [
      {
        condition: (input, ctx) => ['status', 'diff', 'log'].includes(input.command),
        action: 'allow',
      },
      {
        condition: (input, ctx) => ['commit', 'push', 'pull'].includes(input.command),
        action: 'prompt',
      },
    ],
  },
  execute: async (input, context) => {
    const result = await execGit(input.command, input.args, context.cwd);
    return { success: true, data: { output: result.stdout } };
  },
});
```

**Python 示例：**
```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from tools import Tool, ToolResult, PermissionRule

class GitInput(BaseModel):
    command: Literal['status', 'diff', 'log', 'commit', 'push', 'pull'] = Field(
        description='Git 命令'
    )
    args: Optional[str] = Field(None, description='额外参数')

class GitOutput(BaseModel):
    output: str

class GitTool(Tool[GitInput, GitOutput]):
    name = 'Git'
    description = '执行 Git 操作'
    input_schema = GitInput
    permission = ('rule', [
        PermissionRule(
            condition=lambda input, ctx: input.command in ['status', 'diff', 'log'],
            action='allow'
        ),
        PermissionRule(
            condition=lambda input, ctx: input.command in ['commit', 'push', 'pull'],
            action='prompt'
        ),
    ])
    
    async def execute(self, input: GitInput, context: ToolContext) -> ToolResult[GitOutput]:
        result = await exec_git(input.command, input.args, context.cwd)
        return ToolResult(success=True, data=GitOutput(output=result.stdout))
```

### 注册工具

```typescript
// TypeScript
const registry = new ToolRegistry();
registry.register(new GitTool());
registry.register(new BashTool());
```

```python
# Python
registry = ToolRegistry()
registry.register(GitTool())
registry.register(BashTool())
```

### 执行工具

```typescript
// TypeScript
const result = await executeTool(registry.get('Git'), 
  { command: 'status' }, context);
```

```python
# Python
result = await execute_tool(registry.get('Git'), 
  GitInput(command='status'), context)
```

---

## 目录结构

```
tools/
├── registry.ts/py       # 工具注册表
├── types.ts/py          # 类型定义
├── executor.ts/py       # 执行引擎
├── permissions.ts/py    # 权限系统
├── GitTool/
│   ├── index.ts/py      # 工具实现
│   └── schema.ts/py     # 输入 schema
├── BashTool/
│   ├── index.ts/py
│   └── schema.ts/py
└── FileTool/
    ├── index.ts/py
    └── schema.ts/py
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 工具未被调用 | Schema 验证失败 | 检查输入参数是否符合 schema |
| 权限被拒绝 | 违反权限规则 | 检查 permission 配置 |
| 工具执行超时 | 操作时间过长 | 增加 timeout 或优化执行逻辑 |
| MCP 工具不可用 | 服务器未连接 | 检查 MCP 服务器配置 |
| 并行执行卡住 | 存在循环依赖 | 检查 deps 配置 |

---

## 工具分类

| 类别 | 工具示例 | 权限 |
|------|----------|------|
| 文件操作 | FileRead, FileWrite, Glob, Grep | 读自动批准，写需确认 |
| 命令执行 | Bash, PowerShell | 需确认 |
| 网络请求 | WebFetch, WebSearch | 自动批准 |
| Agent 协作 | Agent, SendMessage | 需确认 |
| 任务管理 | TaskCreate, TaskUpdate | 自动批准 |
