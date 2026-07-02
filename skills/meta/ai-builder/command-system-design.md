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
    → 方案一（轻量版）— 字符串解析 + 基础参数
ELSE IF 用户需要复杂命令系统:
    → 方案二（完整版）— commander 库 + 参数验证 + 补全
ELSE IF 用户已有命令框架:
    → 方案三（集成版）— 在现有框架上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单命令处理 | 方案一 | ✅ 可用，有边界限制 |
| 复杂命令系统 | 方案二 | ✅ 生产验证（commander） |
| 集成现有框架 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的命令系统
- **先问命令类型**：确认命令是斜杠命令、CLI 命令还是自然语言
- **命令要有帮助**：每个命令都要有帮助信息
- **参数要验证**：必填参数和类型要检查
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **自描述**：命令要包含自己的描述
2. **可发现**：支持列出所有可用命令
3. **可组合**：支持命令组合和管道
4. **可扩展**：支持添加新命令
5. **可测试**：命令可以独立测试

---

## 前置条件

### 方案一（轻量版）

无外部依赖，纯 TypeScript 实现。

### 方案二（完整版）

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |
| commander | 11.0+ | CLI 命令解析 |

---

## 方案一：轻量版

适合简单场景，无外部依赖，代码约 150 行。

### Step 1：定义命令接口

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

### Step 2：创建命令注册表

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

### Step 3：实现命令解析器

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
      
      if (part === '--') {
        // 剩余全当参数
        for (let j = i + 1; j < parts.length; j++) {
          if (command.args && argIndex < command.args.length) {
            args[command.args[argIndex].name] = parts[j];
            argIndex++;
          }
        }
        break;
      }
      
      if (part.startsWith('--')) {
        // 长选项：支持 --flag=value 和 --flag
        const eq = part.indexOf('=');
        if (eq > 2) {
          options[part.slice(2, eq)] = part.slice(eq + 1);
        } else {
          options[part.slice(2)] = true;
        }
      } else if (part.startsWith('-') && part.length > 1) {
        // 短选项：如果下一个是选项或末尾，当前就是布尔开关
        const name = part.slice(1);
        if (i + 1 < parts.length && !parts[i + 1].startsWith('-')) {
          options[name] = parts[++i];
        } else {
          options[name] = true;
        }
      } else {
        // 参数
        if (command.args && argIndex < command.args.length) {
          args[command.args[argIndex].name] = part;
          argIndex++;
        }
      }
    }
    
    // 参数验证
    if (command.args) {
      for (const arg of command.args) {
        if (arg.required && !(arg.name in args)) {
          throw new Error(`缺少必填参数: ${arg.name}`);
        }
        if (arg.name in args && arg.type === 'number') {
          const num = Number(args[arg.name]);
          if (isNaN(num)) throw new Error(`参数 ${arg.name} 必须是数字`);
          args[arg.name] = num;
        }
      }
    }
    
    return { command, args, options };
  }
}
```

### Step 4：添加命令执行器

```typescript
// commands/CommandExecutor.ts
class CommandExecutor {
  constructor(private parser: CommandParser) {}
  
  async execute(input: string): Promise<any> {
    try {
      const parsed = this.parser.parse(input);
      
      if (!parsed) {
        return { success: false, error: '命令未找到' };
      }
      
      const result = await parsed.command.execute(parsed.args, parsed.options);
      return { success: true, data: result };
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : String(error) 
      };
    }
  }
}
```

### 轻量版限制

- 不支持子命令（如 `git commit` 的 `commit` 是子命令）
- 不支持自动生成帮助文本（需手写 help 命令）
- 不支持命令补全
- 不支持 `--no-xxx` 布尔取反语法

---

## 方案二：完整版

使用 commander 库，支持参数验证、子命令、帮助生成、补全。

### 安装

```bash
npm install commander
```

### 实现

```typescript
// commands/CommanderSetup.ts
import { Command } from 'commander';

const program = new Command();

program
  .name('my-cli')
  .description('My CLI tool')
  .version('1.0.0');

// 注册命令
program
  .command('serve')
  .description('Start the server')
  .argument('[port]', 'Port to listen on', '3000')
  .option('-h, --host <host>', 'Host to bind to', 'localhost')
  .option('--https', 'Enable HTTPS')
  .action(async (port, options) => {
    console.log(`Starting server on ${options.host}:${port}`);
  });

program
  .command('build')
  .description('Build the project')
  .argument('<target>', 'Build target')
  .option('-o, --output <dir>', 'Output directory', './dist')
  .option('-m, --mode <mode>', 'Build mode', 'production')
  .action(async (target, options) => {
    console.log(`Building ${target} to ${options.output}`);
  });

// 自动生成帮助
program.addHelpCommand('help [command]', 'Display help for a command');

// 参数验证由 commander 内部处理
// 子命令由 commander 的 command() 方法支持
// 帮助文本由 commander 自动生成
```

### 完整版优势

- ✅ 参数验证（required、type、choices）
- ✅ 子命令支持
- ✅ 自动生成帮助文本
- ✅ 命令补全（配合 inquirer）
- ✅ `--no-xxx` 布尔取反
- ✅ 版本管理

---

## 方案三：集成版

在现有命令框架上扩展。以下是一些常见框架的集成方式：

### commander 集成

```typescript
// 如果已有 commander 程序，只需添加命令
import { Command } from 'commander';

function extendExistingProgram(program: Command): void {
  program
    .command('new-command')
    .description('New command description')
    .action(async () => {
      // 实现
    });
}
```

### yargs 集成

```typescript
import yargs from 'yargs';

function extendYargs(yargs: any): void {
  yargs.command('new-command', 'New command description', () => {}, async () => {
    // 实现
  });
}
```

### 自定义框架集成

```typescript
// 如果是自定义命令框架，实现适配器
interface CommandAdapter {
  register(command: Command): void;
  parse(input: string): any;
}

class MyFrameworkAdapter implements CommandAdapter {
  constructor(private framework: MyFramework) {}
  
  register(command: Command): void {
    this.framework.addCommand(command.name, {
      description: command.description,
      handler: command.execute,
    });
  }
  
  parse(input: string): any {
    return this.framework.parse(input);
  }
}
```

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

registry.register({
  name: 'serve',
  description: '启动服务器',
  args: [
    { name: 'port', description: '端口号', required: false, type: 'number' }
  ],
  options: [
    { name: 'host', description: '主机地址', type: 'string', default: 'localhost' }
  ],
  execute: async (args, options) => {
    const port = args.port || 3000;
    const host = options.host || 'localhost';
    return `Server started on ${host}:${port}`;
  }
});
```

### 解析和执行命令

```typescript
const parser = new CommandParser(registry);
const executor = new CommandExecutor(parser);

// 简单命令
const result1 = await executor.execute('help');
console.log(result1);

// 带参数命令
const result2 = await executor.execute('serve 8080 --host 0.0.0.0');
console.log(result2);
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
    └── serve.ts         # 服务器命令
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 命令未找到 | 命令未注册或别名错误 | 检查 registry.register() |
| 参数解析错误 | 选项格式不正确 | 检查 --key=value 或 -k value 格式 |
| 必填参数缺失 | 未传 required 参数 | 检查命令定义的 args |
| 类型转换失败 | 数字参数传了字符串 | 检查 arg.type 定义 |
| 帮助信息缺失 | 未添加 description | 给命令添加 description 字段 |

---

## 命令分类

| 类别 | 命令示例 | 说明 |
|------|----------|------|
| 系统命令 | help, version, exit | 基础系统命令 |
| 项目命令 | serve, build, test | 项目操作命令 |
| 配置命令 | config, set, get | 配置管理命令 |
| 工具命令 | search, export, import | 工具类命令 |
