---
name: 状态管理设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建应用状态管理系统。
  当用户想要实现状态存储、状态同步、状态持久化时触发。
  关键词：状态管理、state management、状态存储、状态同步。
---

# 状态管理设计

教 AI 如何设计和构建应用状态管理系统，让 Agent 能管理复杂状态。

## 能力概览

| 能力 | 说明 |
|------|------|
| 状态存储 | 集中管理应用状态 |
| 状态订阅 | 状态变化时通知订阅者 |
| 状态持久化 | 将状态保存到磁盘 |
| 状态同步 | 多个组件之间同步状态 |
| 状态回滚 | 支持撤销和重做 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单状态管理:
    → 方案一（轻量版）— 全局变量 + 事件发射器
ELSE IF 用户需要响应式状态管理:
    → 方案二（完整版）— 状态订阅 + 自动更新
ELSE IF 用户已有状态管理库:
    → 方案三（集成版）— 在现有库上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单状态管理 | 方案一 | ✅ 生产验证 |
| 响应式状态管理 | 方案二 | ✅ 生产验证 |
| 集成现有库 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的状态管理
- **先问状态类型**：确认要管理什么类型的状态（UI 状态、业务状态、会话状态）
- **状态要集中管理**：不要分散在多个地方
- **状态变化要可追踪**：记录每次状态变化
- **状态要可持久化**：支持保存到磁盘
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **单一数据源**：所有状态集中在一个地方
2. **只读状态**：状态不能直接修改，只能通过 action 修改
3. **纯函数更新**：状态更新函数必须是纯函数
4. **可追踪**：记录每次状态变化的原因
5. **可持久化**：支持保存到磁盘

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

---

## 安装步骤

### Step 1：定义状态接口

**TypeScript 版：**
```typescript
// state/types.ts
interface State<T> {
  get(): T;
  set(value: T): void;
  update(updater: (current: T) => T): void;
  subscribe(listener: (value: T) => void): () => void;
}

interface AppState {
  messages: Message[];
  tools: Tool[];
  permissions: PermissionState;
  settings: Settings;
}
```

**验证**：定义一个简单的状态接口，确认类型检查通过。

### Step 2：创建状态存储

**TypeScript 版：**
```typescript
// state/Store.ts
class Store<T> implements State<T> {
  private value: T;
  private listeners: Set<(value: T) => void> = new Set();
  
  constructor(initialValue: T) {
    this.value = initialValue;
  }
  
  get(): T {
    return this.value;
  }
  
  set(value: T): void {
    this.value = value;
    this.notify();
  }
  
  update(updater: (current: T) => T): void {
    this.value = updater(this.value);
    this.notify();
  }
  
  subscribe(listener: (value: T) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
  
  private notify(): void {
    this.listeners.forEach(listener => listener(this.value));
  }
}
```

**验证**：创建状态存储实例，测试状态更新和订阅。

### Step 3：实现状态持久化

**TypeScript 版：**
```typescript
// state/PersistedStore.ts
import * as fs from 'fs';

class PersistedStore<T> extends Store<T> {
  private filePath: string;
  
  constructor(initialValue: T, filePath: string) {
    super(initialValue);
    this.filePath = filePath;
    this.load();
  }
  
  set(value: T): void {
    super.set(value);
    this.save();
  }
  
  update(updater: (current: T) => T): void {
    super.update(updater);
    this.save();
  }
  
  private load(): void {
    try {
      if (fs.existsSync(this.filePath)) {
        const data = fs.readFileSync(this.filePath, 'utf-8');
        super.set(JSON.parse(data));
      }
    } catch (error) {
      console.error('加载状态失败:', error);
    }
  }
  
  private save(): void {
    try {
      fs.writeFileSync(this.filePath, JSON.stringify(this.get(), null, 2));
    } catch (error) {
      console.error('保存状态失败:', error);
    }
  }
}
```

**验证**：创建持久化状态存储，测试保存和加载。

### Step 4：添加状态组合

**TypeScript 版：**
```typescript
// state/combineStores.ts
function combineStores<T extends Record<string, any>>(
  stores: { [K in keyof T]: Store<T[K]> }
): Store<T> {
  const combined = new Store<T>({} as T);
  
  // 订阅每个子 store 的变化
  Object.entries(stores).forEach(([key, store]) => {
    store.subscribe(value => {
      combined.update(current => ({
        ...current,
        [key]: value
      }));
    });
  });
  
  return combined;
}
```

**验证**：创建组合状态，测试多个状态的同步。

---

## 使用方法

### 创建状态存储

```typescript
const messagesStore = new Store<Message[]>([]);
const settingsStore = new PersistedStore<Settings>(
  { theme: 'dark', language: 'zh' },
  './settings.json'
);
```

### 更新状态

```typescript
messagesStore.update(messages => [
  ...messages,
  { role: 'user', content: 'Hello' }
]);
```

### 订阅状态变化

```typescript
const unsubscribe = messagesStore.subscribe(messages => {
  console.log('消息更新:', messages);
});

// 取消订阅
unsubscribe();
```

### 组合状态

```typescript
const appStore = combineStores({
  messages: messagesStore,
  settings: settingsStore,
});

appStore.subscribe(state => {
  console.log('应用状态:', state);
});
```

---

## 目录结构

```
state/
├── types.ts           # 类型定义
├── Store.ts           # 状态存储
├── PersistedStore.ts  # 持久化存储
├── combineStores.ts   # 状态组合
└── middleware/
    ├── logger.ts      # 日志中间件
    └── validator.ts   # 验证中间件
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 状态未更新 | 未调用 set/update | 检查状态更新代码 |
| 订阅未触发 | 订阅者未注册 | 检查 subscribe 调用 |
| 持久化失败 | 文件权限问题 | 检查文件权限 |
| 状态不同步 | 多个 store 未组合 | 使用 combineStores |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| 状态管理 | GetState, SetState, UpdateState | CRUD 操作 |
| 状态订阅 | Subscribe, Unsubscribe | 订阅 |
| 状态持久化 | SaveState, LoadState | 持久化 |
| 状态组合 | CombineStores, MergeStores | 组合 |
