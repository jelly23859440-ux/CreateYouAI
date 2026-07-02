---
name: 查询引擎设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建 LLM 查询引擎。
  当用户想要实现 LLM 调用、流式响应、工具调用循环时触发。
  关键词：查询引擎、query engine、LLM 调用、流式响应、工具调用。
---

# 查询引擎设计

教 AI 如何设计和构建 LLM 查询引擎，让 Agent 能与 LLM 交互。

## 能力概览

| 能力 | 说明 |
|------|------|
| LLM 调用 | 发送请求到 LLM API |
| 流式响应 | 实时接收 LLM 输出 |
| 工具调用循环 | LLM 调用工具 → 执行 → 返回结果 → 继续 |
| 上下文管理 | 管理对话历史和上下文窗口 |
| Token 计数 | 跟踪 token 使用量 |
| 错误重试 | API 失败时自动重试 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单 LLM 调用:
    → 方案一（轻量版）— 单次调用 + 简单循环
ELSE IF 用户需要完整 Agent:
    → 方案二（完整版）— 流式响应 + 工具调用 + 上下文管理
ELSE IF 用户已有 LLM 客户端:
    → 方案三（集成版）— 在现有客户端上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单 LLM 调用 | 方案一 | ✅ 生产验证 |
| 完整 Agent | 方案二 | ✅ 生产验证 |
| 集成现有客户端 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的查询引擎
- **先问 LLM 提供商**：确认用户使用哪个 LLM API（OpenAI、Anthropic、本地模型）
- **每次调用要记录**：记录请求、响应、token 使用量
- **流式响应要实时**：不要等全部完成再返回
- **工具调用要安全**：执行工具前要验证权限
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **可扩展**：支持多个 LLM 提供商
2. **可恢复**：API 失败时可以重试
3. **可监控**：记录每次调用的详细信息
4. **可中断**：支持取消正在进行的请求
5. **可组合**：支持链式调用和工具调用

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |
| @anthropic-ai/sdk | 0.20+ | Anthropic API（可选） |
| openai | 4.0+ | OpenAI API（可选） |

### Python 版 ⚠️ 社区贡献，待验证

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行时 |
| anthropic | 0.20+ | Anthropic API（可选） |
| openai | 1.0+ | OpenAI API（可选） |

---

## 安装步骤

### Step 1：定义查询接口

**TypeScript 版：**
```typescript
// query/types.ts
interface QueryOptions {
  model: string;
  messages: Message[];
  tools?: Tool[];
  maxTokens?: number;
  temperature?: number;
  stream?: boolean;
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: ToolCall[];
  toolResults?: ToolResult[];
}

interface QueryResult {
  message: Message;
  usage: {
    inputTokens: number;
    outputTokens: number;
  };
  stopReason: 'end_turn' | 'tool_use' | 'max_tokens';
}
```

**验证**：定义一个简单的查询接口，确认类型检查通过。

### Step 2：创建 LLM 客户端

**TypeScript 版：**
```typescript
// query/LLMClient.ts
class LLMClient {
  private apiKey: string;
  private baseUrl: string;
  
  constructor(apiKey: string, baseUrl: string = 'https://api.anthropic.com') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }
  
  async query(options: QueryOptions): Promise<QueryResult> {
    const response = await fetch(`${baseUrl}/v1/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
      },
      body: JSON.stringify({
        model: options.model,
        messages: options.messages,
        max_tokens: options.maxTokens || 1024,
        temperature: options.temperature || 0.7,
      }),
    });
    
    const data = await response.json();
    
    return {
      message: {
        role: 'assistant',
        content: data.content[0].text,
      },
      usage: {
        inputTokens: data.usage.input_tokens,
        outputTokens: data.usage.output_tokens,
      },
      stopReason: data.stop_reason,
    };
  }
}
```

**验证**：创建 LLM 客户端实例，测试 API 调用。

### Step 3：实现流式响应

**TypeScript 版：**
```typescript
// query/StreamingClient.ts
class StreamingClient {
  async *queryStream(options: QueryOptions): AsyncGenerator<string> {
    const response = await fetch(`${this.baseUrl}/v1/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.apiKey,
      },
      body: JSON.stringify({
        ...options,
        stream: true,
      }),
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.startsWith('data: '));
      
      for (const line of lines) {
        const data = JSON.parse(line.slice(6));
        if (data.type === 'content_block_delta') {
          yield data.delta.text;
        }
      }
    }
  }
}
```

**验证**：创建流式客户端，测试流式响应。

### Step 4：添加工具调用循环

**TypeScript 版：**
```typescript
// query/ToolCallingLoop.ts
class ToolCallingLoop {
  constructor(
    private client: LLMClient,
    private tools: Tool[]
  ) {}
  
  async execute(options: QueryOptions): Promise<QueryResult> {
    let messages = [...options.messages];
    
    while (true) {
      // 调用 LLM
      const result = await this.client.query({
        ...options,
        messages,
        tools: this.tools,
      });
      
      // 如果 LLM 要调用工具
      if (result.stopReason === 'tool_use') {
        const toolCalls = result.message.toolCalls || [];
        
        // 执行工具
        const toolResults = await Promise.all(
          toolCalls.map(call => this.executeTool(call))
        );
        
        // 将结果添加到消息历史
        messages.push(result.message);
        messages.push({
          role: 'user',
          content: '',
          toolResults,
        });
        
        // 继续循环
        continue;
      }
      
      // 返回最终结果
      return result;
    }
  }
  
  private async executeTool(call: ToolCall): Promise<ToolResult> {
    const tool = this.tools.find(t => t.name === call.name);
    if (!tool) {
      return { success: false, error: `工具 ${call.name} 不存在` };
    }
    
    return await tool.execute(call.input);
  }
}
```

**验证**：创建工具调用循环，测试工具调用。

---

## 使用方法

### 创建查询引擎

```typescript
const client = new LLMClient('your-api-key');
const loop = new ToolCallingLoop(client, [gitTool, bashTool]);

const result = await loop.execute({
  model: 'claude-3-5-sonnet-20241022',
  messages: [
    { role: 'user', content: '帮我查看 Git 状态' }
  ],
  maxTokens: 1024,
});

console.log(result.message.content);
```

### 使用流式响应

```typescript
const streamingClient = new StreamingClient('your-api-key');

for await (const chunk of streamingClient.queryStream({
  model: 'claude-3-5-sonnet-20241022',
  messages: [
    { role: 'user', content: '写一首诗' }
  ],
  stream: true,
})) {
  process.stdout.write(chunk);
}
```

---

## 目录结构

```
query/
├── types.ts           # 类型定义
├── LLMClient.ts       # LLM 客户端
├── StreamingClient.ts # 流式客户端
├── ToolCallingLoop.ts # 工具调用循环
└── utils/
    ├── tokenCounter.ts
    └── retryHandler.ts
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| API 调用失败 | API Key 错误 | 检查 API Key |
| 流式响应中断 | 网络问题 | 添加重试逻辑 |
| 工具调用失败 | 工具不存在 | 检查工具注册 |
| Token 超限 | 上下文过长 | 压缩上下文或截断消息 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| LLM 调用 | Query, QueryStream | 基础调用 |
| 工具调用 | ExecuteTool, CallTool | 工具执行 |
| 上下文管理 | AddMessage, TrimContext | 上下文操作 |
| Token 管理 | CountTokens, EstimateCost | Token 跟踪 |
