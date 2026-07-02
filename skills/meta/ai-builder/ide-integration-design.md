---
name: IDE 集成设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建 IDE 集成桥接系统。
  当用户想要实现 IDE 扩展、代码编辑器集成、开发工具集成时触发。
  关键词：IDE 集成、bridge、VS Code 扩展、编辑器集成。
---

# IDE 集成设计

教 AI 如何设计和构建 IDE 集成桥接系统，让 Agent 能与 IDE 交互。

## 能力概览

| 能力 | 说明 |
|------|------|
| 消息桥接 | Agent 和 IDE 之间传递消息 |
| 文件操作 | 读写 IDE 中的文件 |
| 代码编辑 | 编辑 IDE 中的代码 |
| 终端集成 | 在 IDE 终端中执行命令 |
| UI 扩展 | 在 IDE 中显示自定义 UI |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单 IDE 集成:
    → 方案一（轻量版）— 文件监听 + 命令执行
ELSE IF 用户需要完整 IDE 扩展:
    → 方案二（完整版）— VS Code 扩展 + 消息桥接
ELSE IF 用户已有 IDE 插件:
    → 方案三（集成版）— 在现有插件上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单 IDE 集成 | 方案一 | ✅ 生产验证 |
| 完整 IDE 扩展 | 方案二 | ✅ 生产验证 |
| 集成现有插件 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的 IDE 集成
- **先问 IDE 类型**：确认用户使用哪个 IDE（VS Code、JetBrains、Vim）
- **消息要双向**：Agent 和 IDE 之间要能双向通信
- **操作要安全**：文件操作要验证权限
- **UI 要响应**：UI 更新要实时
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **双向通信**：Agent 和 IDE 之间能双向通信
2. **消息队列**：消息要有序处理
3. **错误恢复**：连接断开时能自动重连
4. **安全验证**：所有操作要验证权限
5. **性能优化**：减少不必要的通信

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |
| @vscode/vsce | 2.0+ | VS Code 扩展打包（可选） |

---

## 安装步骤

### Step 1：定义消息协议

**TypeScript 版：**
```typescript
// bridge/types.ts
interface BridgeMessage {
  id: string;
  type: 'request' | 'response' | 'event';
  method: string;
  params?: any;
  result?: any;
  error?: string;
}

interface BridgeConnection {
  send(message: BridgeMessage): void;
  onMessage(callback: (message: BridgeMessage) => void): void;
  close(): void;
}
```

**验证**：定义消息协议，确认类型检查通过。

### Step 2：创建桥接连接

**TypeScript 版：**
```typescript
// bridge/BridgeConnection.ts
import WebSocket from 'ws';

class WebSocketBridgeConnection implements BridgeConnection {
  private ws: WebSocket;
  private messageCallback?: (message: BridgeMessage) => void;
  
  constructor(url: string) {
    this.ws = new WebSocket(url);
    
    this.ws.on('message', (data: string) => {
      const message = JSON.parse(data);
      this.messageCallback?.(message);
    });
    
    this.ws.on('close', () => {
      console.log('连接已关闭');
    });
  }
  
  send(message: BridgeMessage): void {
    this.ws.send(JSON.stringify(message));
  }
  
  onMessage(callback: (message: BridgeMessage) => void): void {
    this.messageCallback = callback;
  }
  
  close(): void {
    this.ws.close();
  }
}
```

**验证**：创建桥接连接，测试消息发送和接收。

### Step 3：实现消息处理器

**TypeScript 版：**
```typescript
// bridge/MessageHandler.ts
class MessageHandler {
  private handlers: Map<string, (params: any) => Promise<any>> = new Map();
  
  register(method: string, handler: (params: any) => Promise<any>): void {
    this.handlers.set(method, handler);
  }
  
  async handle(message: BridgeMessage): Promise<BridgeMessage> {
    const handler = this.handlers.get(message.method);
    
    if (!handler) {
      return {
        id: message.id,
        type: 'response',
        method: message.method,
        error: `方法 ${message.method} 未注册`
      };
    }
    
    try {
      const result = await handler(message.params);
      return {
        id: message.id,
        type: 'response',
        method: message.method,
        result
      };
    } catch (error) {
      return {
        id: message.id,
        type: 'response',
        method: message.method,
        error: error.message
      };
    }
  }
}
```

**验证**：创建消息处理器，测试消息处理。

### Step 4：添加文件操作

**TypeScript 版：**
```typescript
// bridge/FileOperations.ts
import * as fs from 'fs';
import * as path from 'path';

class FileOperations {
  constructor(private rootPath: string) {}
  
  async readFile(filePath: string): Promise<string> {
    const fullPath = path.join(this.rootPath, filePath);
    return fs.promises.readFile(fullPath, 'utf-8');
  }
  
  async writeFile(filePath: string, content: string): Promise<void> {
    const fullPath = path.join(this.rootPath, filePath);
    await fs.promises.writeFile(fullPath, content, 'utf-8');
  }
  
  async listFiles(dirPath: string): Promise<string[]> {
    const fullPath = path.join(this.rootPath, dirPath);
    return fs.promises.readdir(fullPath);
  }
  
  async deleteFile(filePath: string): Promise<void> {
    const fullPath = path.join(this.rootPath, filePath);
    await fs.promises.unlink(fullPath);
  }
}
```

**验证**：创建文件操作类，测试文件读写。

---

## 使用方法

### 创建桥接连接

```typescript
const connection = new WebSocketBridgeConnection('ws://localhost:3000');
const handler = new MessageHandler();
const fileOps = new FileOperations('/path/to/project');

// 注册文件操作
handler.register('readFile', (params) => fileOps.readFile(params.path));
handler.register('writeFile', (params) => fileOps.writeFile(params.path, params.content));

// 处理消息
connection.onMessage(async (message) => {
  const response = await handler.handle(message);
  connection.send(response);
});
```

### 发送消息

```typescript
connection.send({
  id: '1',
  type: 'request',
  method: 'readFile',
  params: { path: 'src/index.ts' }
});
```

### 接收响应

```typescript
connection.onMessage((message) => {
  if (message.type === 'response') {
    console.log('收到响应:', message.result);
  }
});
```

---

## 目录结构

```
bridge/
├── types.ts               # 类型定义
├── BridgeConnection.ts    # 桥接连接
├── MessageHandler.ts      # 消息处理器
├── FileOperations.ts      # 文件操作
└── vscode/
    ├── extension.ts       # VS Code 扩展入口
    └── webview.ts         # Webview UI
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 连接失败 | 服务器未启动 | 检查服务器状态 |
| 消息丢失 | 网络问题 | 添加重试逻辑 |
| 文件操作失败 | 权限问题 | 检查文件权限 |
| UI 不更新 | 消息未处理 | 检查消息处理器 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| 连接管理 | Connect, Disconnect, Reconnect | 连接 |
| 消息传递 | SendMessage, OnMessage | 消息 |
| 文件操作 | ReadFile, WriteFile, ListFiles | 文件 |
| UI 扩展 | ShowPanel, UpdateUI | UI |
