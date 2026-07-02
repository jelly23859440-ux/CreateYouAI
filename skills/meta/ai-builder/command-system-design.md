---
name: 命令系统设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建命令系统。
  当用户想要实现命令注册、命令解析、命令执行时触发。
  关键词：命令系统、command、命令注册、命令解析。
---

# 命令系统设计

教 AI 如何设计和构建命令系统，让 Agent 能处理用户输入的命令。

## 能力概览

| 能力 | 说明 |
|------|------|
| 命令注册 | 注册可用的命令 |
| 命令解析 | 解析用户输入的命令 |
| 命令执行 | 执行命令并返回结果 |
| 命令帮助 | 显示命令帮助信息 |
| 命令补全 | 支持命令自动补全 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单命令处理:
    → 方案一（轻量版）— 字符串解析 + switch/case
ELSE IF 用户需要复杂命令系统:
    → 方案二（完整版）— 命令注册 + 参数解析 + 帮助系统
ELSE IF 用户已有命令框架:
    → 方案三（集成版）— 在现有框架上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单命令处理 | 方案一 | ✅ 生产验证 |
| 复杂命令系统 | 方案二 | ✅ 生产验证 |
| 集成现有框架 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的命令系统
- **先问命令类型**：确认命令是斜杠命令、CLI 命令还是自然语言
- **命令要有帮助**：每个命令都要有帮助信息
- **命令要可补全**：支持自动补全
- **命令要可验证**：参数要验证
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **自描述**：命令要包含自己的描述
2. **可发现**：支持列出所有可用命令
3. **可组合**：支持命令组合和管道
4. **可扩展**：支持添加新命令
5. **可测试**：命令可以独立测试

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |
| commander | 11.0+ | CLI 命令解析（可选） |

---

## 安装步骤

### Step 1：定义命令接口

**TypeScript 版：**
```typescript
// commands/types.ts
interface Command {
  name: string;
  description: string;
  aliases?: string[];
  args?: CommandArg[];
  options?: CommandOption[];
  execute(args: any, options: any): Promise<any>;
}

interface CommandArg {
  name: string;
  description: string;
  required: boolean;
  type: 'string' | 'number' | 'boolean';
}

interface CommandOption {
  name: string;
  description: string;
  type: 'string' | 'number' | 'boolean';
  default?: any;
}
```

**验证**：定义命令接口，确认类型检查通过。

### Step 2：创建命令注册表

**TypeScript 版：**
```typescript
// commands/CommandRegistry.ts
class CommandRegistry {
  private commands: Map<string, Command> = new Map();
  
  register(command: Command): void {
    this.commands.set(command.name, command);
    if (command.aliases) {
      command.aliases.forEach(alias => {
        this.commands.set(alias, command);
      });
    }
  }
  
  get(name: string): Command | undefined {
    return this.commands.get(name);
  }
  
  getAll(): Command[] {
    const unique = new Set(this.commands.values());
    return Array.from(unique);
  }
  
  has(name: string): boolean {
    return this.commands.has(name);
  }
}
```

**验证**：创建命令注册表，注册和获取命令。

### Step 3：实现命令解析器

**TypeScript 版：**
```typescript
// commands/CommandParser.ts
class CommandParser {
  constructor(private registry: CommandRegistry) {}
  
  parse(input: string): { command: Command; args: any; options: any } | null {
    const parts = input.trim().split(/\s+/);
    const commandName = parts[0];
    
    if (!commandName) return null;
    
    const command = this.registry.get(commandName);
    if (!command) return null;
    
    const args: any = {};
    const options: any = {};
    
    // 解析参数和选项
    let argIndex = 0;
    for (let i = 1; i < parts.length; i++) {
      const part = parts[i];
      
      if (part.startsWith('--')) {
        // 选项
        const [name, value] = part.slice(2).split('=');
        options[name] = value || true;
      } else if (part.startsWith('-')) {
        // 短选项
        const name = part.slice(1);
        options[name] = parts[++i] || true;
      } else {
        // 参数
        if (command.args && argIndex < command.args.length) {
          args[command.args[argIndex].name] = part;
          argIndex++;
        }
      }
    }
    
    return { command, args, options };
  }
}
```

**验证**：创建命令解析器，测试命令解析。

### Step 4：添加命令执行器

**TypeScript 版：**
```typescript
// commands/CommandExecutor.ts
class CommandExecutor {
  constructor(private parser: CommandParser) {}
  
  async execute(input: string): Promise<any> {
    const parsed = this.parser.parse(input);
    
    if (!parsed) {
      return { success: false, error: '命令未找到' };
    }
    
    try {
      const result = await parsed.command.execute(parsed.args, parsed.options);
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}
```

**验证**：创建命令执行器，测试命令执行。

---

## 使用方法

### 注册命令

```typescript
const registry = new CommandRegistry();

registry.register({
  name: 'help',
  description: '显示帮助信息',
  aliases: ['h', '?'],
  execute: async () => {
    const commands = registry.getAll();
    return commands.map(c => `${c.name}: ${c.description}`).join('\n');
  }
});
```

### 解析和执行命令

```typescript
const parser = new CommandParser(registry);
const executor = new CommandExecutor(parser);

const result = await executor.execute('help');
console.log(result);
```

---

## 目录结构

```
commands/
├── types.ts             # 类型定义
├── CommandRegistry.ts   # 命令注册表
├── CommandParser.ts     # 命令解析器
├── CommandExecutor.ts   # 命令执行器
└── commands/
    ├── help.ts          # 帮助命令
    ├── exit.ts          # 退出命令
    └── config.ts        # 配置命令
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 命令未找到 | 命令未注册 | 检查命令注册 |
| 参数解析错误 | 参数格式错误 | 检查参数格式 |
| 命令执行失败 | 命令实现错误 | 检查命令实现 |
| 帮助信息缺失 | 未添加描述 | 添加命令描述 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| 命令管理 | RegisterCommand, UnregisterCommand | 生命周期 |
| 命令解析 | ParseCommand, ParseArgs | 解析 |
| 命令执行 | ExecuteCommand, RunCommand | 执行 |
| 命令帮助 | GetHelp, ListCommands | 帮助 |
