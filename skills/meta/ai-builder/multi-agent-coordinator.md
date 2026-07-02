---
name: 多 Agent 协调器
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建多 Agent 协调系统。
  当用户想要实现多 Agent 协作、任务分发、团队协作时触发。
  关键词：多 Agent、协调器、coordinator、团队协作、任务分发。
---

# 多 Agent 协调器

教 AI 如何设计和构建多 Agent 协调系统，让多个 Agent 协同完成复杂任务。

## 能力概览

| 能力 | 说明 |
|------|------|
| Agent 生命周期管理 | 创建、监控、销毁 Agent |
| 任务分发 | 根据 Agent 能力分配任务 |
| 消息传递 | Agent 间通信机制 |
| 依赖管理 | 任务依赖关系和执行顺序 |
| 错误处理 | Agent 失败时的恢复机制 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单任务分发:
    → 方案一（轻量版）— 主 Agent 分发任务给子 Agent
ELSE IF 用户需要复杂协作:
    → 方案二（完整版）— 协调器 + 工作队列 + 状态机
ELSE IF 用户已有 Agent 框架:
    → 方案三（集成版）— 在现有框架上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单任务分发 | 方案一 | ✅ 生产验证 |
| 复杂协作 | 方案二 | ✅ 生产验证 |
| 集成现有框架 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的多 Agent 系统
- **先问任务类型**：确认任务是否可以并行，是否有依赖关系
- **每个 Agent 只做一件事**：不要设计"万能 Agent"
- **任务分发要明确**：哪个 Agent 做什么，输入输出是什么
- **验证每一步**：每个 Agent 完成后要验证结果
- **不要猜测需求**：让用户告诉你具体需要什么 Agent

### 设计原则

1. **单一职责**：每个 Agent 只做一件事
2. **无状态**：Agent 不保存跨任务状态
3. **可测试**：Agent 可以独立测试
4. **可恢复**：Agent 失败时可以重试或回滚
5. **可监控**：Agent 执行过程可以追踪

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |

### Python 版 ⚠️ 社区贡献，待验证

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行时 |
| asyncio | 内置 | 异步执行 |

---

## 安装步骤

### Step 1：定义 Agent 接口

**TypeScript 版：**
```typescript
// agents/types.ts
interface Agent {
  id: string;
  name: string;
  capabilities: string[];
  execute(task: Task): Promise<TaskResult>;
}

interface Task {
  id: string;
  type: string;
  input: any;
  deps?: string[];
}

interface TaskResult {
  success: boolean;
  data?: any;
  error?: string;
}
```

**验证**：定义一个简单的 Agent 类，确认类型检查通过。

### Step 2：创建协调器

**TypeScript 版：**
```typescript
// coordinator/Coordinator.ts
class Coordinator {
  private agents: Map<string, Agent> = new Map();
  private taskQueue: Task[] = [];
  
  registerAgent(agent: Agent): void {
    this.agents.set(agent.id, agent);
  }
  
  async executeTask(task: Task): Promise<TaskResult> {
    // 找到能处理此任务的 Agent
    const agent = this.findAgentForTask(task);
    if (!agent) {
      return { success: false, error: '没有能处理此任务的 Agent' };
    }
    
    // 执行任务
    return await agent.execute(task);
  }
  
  private findAgentForTask(task: Task): Agent | undefined {
    return Array.from(this.agents.values()).find(agent => 
      agent.capabilities.includes(task.type)
    );
  }
}
```

**验证**：创建协调器实例，注册 Agent，执行任务。

### Step 3：实现任务分发

**TypeScript 版：**
```typescript
// coordinator/TaskDistributor.ts
class TaskDistributor {
  constructor(private coordinator: Coordinator) {}
  
  async distributeTasks(tasks: Task[]): Promise<Map<string, TaskResult>> {
    const results = new Map<string, TaskResult>();
    
    // 按依赖关系排序
    const sorted = this.topologicalSort(tasks);
    
    // 执行任务
    for (const task of sorted) {
      const result = await this.coordinator.executeTask(task);
      results.set(task.id, result);
      
      if (!result.success) {
        // 任务失败，可以选择重试或跳过
        console.error(`任务 ${task.id} 失败: ${result.error}`);
      }
    }
    
    return results;
  }
  
  private topologicalSort(tasks: Task[]): Task[] {
    // 拓扑排序实现
    // ...
  }
}
```

**验证**：创建任务分发器，执行多个有依赖关系的任务。

### Step 4：添加消息传递

**TypeScript 版：**
```typescript
// coordinator/MessageBus.ts
class MessageBus {
  private subscribers: Map<string, Function[]> = new Map();
  
  subscribe(topic: string, callback: Function): void {
    if (!this.subscribers.has(topic)) {
      this.subscribers.set(topic, []);
    }
    this.subscribers.get(topic)!.push(callback);
  }
  
  publish(topic: string, message: any): void {
    const callbacks = this.subscribers.get(topic) || [];
    callbacks.forEach(cb => cb(message));
  }
}
```

**验证**：创建消息总线，测试订阅和发布。

---

## 使用方法

### 创建自定义 Agent

**TypeScript 示例：**
```typescript
class CodeReviewAgent implements Agent {
  id = 'code-reviewer';
  name = '代码审查 Agent';
  capabilities = ['code-review', 'security-check'];
  
  async execute(task: Task): Promise<TaskResult> {
    const { code, language } = task.input;
    
    // 执行代码审查
    const issues = await this.reviewCode(code, language);
    
    return {
      success: true,
      data: { issues }
    };
  }
  
  private async reviewCode(code: string, language: string): Promise<Issue[]> {
    // 实现代码审查逻辑
    // ...
  }
}
```

### 注册 Agent 并执行任务

```typescript
// 创建协调器
const coordinator = new Coordinator();
const distributor = new TaskDistributor(coordinator);

// 注册 Agent
coordinator.registerAgent(new CodeReviewAgent());
coordinator.registerAgent(new TestAgent());

// 定义任务
const tasks: Task[] = [
  { id: '1', type: 'code-review', input: { code: '...', language: 'typescript' } },
  { id: '2', type: 'test', input: { code: '...', framework: 'jest' }, deps: ['1'] },
];

// 执行任务
const results = await distributor.distributeTasks(tasks);
```

---

## 目录结构

```
coordinator/
├── types.ts           # 类型定义
├── Coordinator.ts     # 协调器
├── TaskDistributor.ts # 任务分发
├── MessageBus.ts      # 消息传递
└── agents/
    ├── CodeReviewAgent.ts
    ├── TestAgent.ts
    └── DeployAgent.ts
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 任务未执行 | 没有能处理此任务的 Agent | 检查 Agent 的 capabilities |
| 任务执行超时 | Agent 处理时间过长 | 增加 timeout 或优化 Agent |
| 循环依赖 | 任务依赖关系有环 | 检查 deps 配置 |
| 消息丢失 | 订阅者未注册 | 检查 subscribe 调用 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| Agent 管理 | RegisterAgent, UnregisterAgent | Agent 生命周期 |
| 任务分发 | DistributeTask, CancelTask | 任务管理 |
| 消息传递 | Subscribe, Publish, Send | Agent 间通信 |
| 状态查询 | GetAgentStatus, GetTaskStatus | 监控 |
