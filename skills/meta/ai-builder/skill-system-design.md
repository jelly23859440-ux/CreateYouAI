---
name: Skill 系统设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建 Skill 加载和执行系统。
  当用户想要实现 Skill 注册、Skill 加载、Skill 执行时触发。
  关键词：Skill 系统、skill loader、skill execution、插件系统。
---

# Skill 系统设计

教 AI 如何设计和构建 Skill 系统，让 Agent 能加载和执行可复用的工作流。

## 能力概览

| 能力 | 说明 |
|------|------|
| Skill 定义 | 定义 Skill 的格式和结构 |
| Skill 加载 | 从文件系统或网络加载 Skill |
| Skill 执行 | 执行 Skill 中定义的工作流 |
| Skill 发现 | 自动发现可用的 Skill |
| Skill 依赖 | 管理 Skill 之间的依赖关系 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单 Skill:
    → 方案一（轻量版）— 文件加载 + 简单执行
ELSE IF 用户需要复杂 Skill:
    → 方案二（完整版）— 动态加载 + 依赖管理 + 版本控制
ELSE IF 用户已有插件系统:
    → 方案三（集成版）— 在现有插件系统上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单 Skill | 方案一 | ✅ 生产验证 |
| 复杂 Skill | 方案二 | ✅ 生产验证 |
| 集成现有插件系统 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的 Skill 系统
- **先问 Skill 类型**：确认 Skill 是命令、工作流还是插件
- **每个 Skill 要有文档**：不要加载没有文档的 Skill
- **Skill 执行要安全**：执行前要验证权限
- **Skill 版本要管理**：不要加载过期的 Skill
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **自描述**：Skill 要包含自己的描述和使用说明
2. **可发现**：支持自动发现可用的 Skill
3. **可加载**：支持从多种来源加载 Skill
4. **可执行**：支持多种执行方式（命令、函数、脚本）
5. **可组合**：支持 Skill 之间的组合和依赖

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |
| gray-matter | 4.0+ | YAML frontmatter 解析 |

### Python 版 ⚠️ 社区贡献，待验证

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行时 |
| pyyaml | 6.0+ | YAML 解析 |

---

## 安装步骤

### Step 1：定义 Skill 格式

**TypeScript 版：**
```typescript
// skills/types.ts
interface Skill {
  name: string;
  description: string;
  version: string;
  layer: string;
  category: string;
  triggers: string[];
  content: string;
  dependencies?: string[];
}

interface SkillFrontmatter {
  name: string;
  description: string;
  version?: string;
  layer?: string;
  category?: string;
  triggers?: string[];
  dependencies?: string[];
}
```

**验证**：定义一个简单的 Skill 结构，确认类型检查通过。

### Step 2：创建 Skill 加载器

**TypeScript 版：**
```typescript
// skills/SkillLoader.ts
import * as fs from 'fs';
import * as path from 'path';
import matter from 'gray-matter';

class SkillLoader {
  private skills: Map<string, Skill> = new Map();
  
  async loadFromDirectory(dirPath: string): Promise<void> {
    const files = fs.readdirSync(dirPath);
    
    for (const file of files) {
      if (file.endsWith('.md')) {
        const filePath = path.join(dirPath, file);
        const skill = await this.loadFromFile(filePath);
        if (skill) {
          this.skills.set(skill.name, skill);
        }
      }
    }
  }
  
  async loadFromFile(filePath: string): Promise<Skill | null> {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const { data, content: body } = matter(content);
      
      return {
        name: data.name,
        description: data.description,
        version: data.version || '1.0.0',
        layer: data.layer || 'action',
        category: data.category || 'other',
        triggers: data.triggers || [],
        content: body,
        dependencies: data.dependencies || [],
      };
    } catch (error) {
      console.error(`加载 Skill 失败: ${filePath}`, error);
      return null;
    }
  }
  
  getSkill(name: string): Skill | undefined {
    return this.skills.get(name);
  }
  
  getAllSkills(): Skill[] {
    return Array.from(this.skills.values());
  }
}
```

**验证**：创建 Skill 加载器，加载一个测试 Skill。

### Step 3：实现 Skill 发现

**TypeScript 版：**
```typescript
// skills/SkillDiscovery.ts
class SkillDiscovery {
  constructor(private loader: SkillLoader) {}
  
  findSkillsForIntent(intent: string): Skill[] {
    const skills = this.loader.getAllSkills();
    
    return skills.filter(skill => {
      // 检查触发词
      if (skill.triggers.some(trigger => intent.includes(trigger))) {
        return true;
      }
      
      // 检查描述
      if (skill.description.includes(intent)) {
        return true;
      }
      
      return false;
    });
  }
  
  findSkillsByCategory(category: string): Skill[] {
    return this.loader.getAllSkills().filter(skill => 
      skill.category === category
    );
  }
  
  findSkillsByLayer(layer: string): Skill[] {
    return this.loader.getAllSkills().filter(skill => 
      skill.layer === layer
    );
  }
}
```

**验证**：创建 Skill 发现器，测试按意图查找 Skill。

### Step 4：添加 Skill 执行器

**TypeScript 版：**
```typescript
// skills/SkillExecutor.ts
class SkillExecutor {
  async execute(skill: Skill, context: any): Promise<any> {
    // 解析 Skill 内容
    const steps = this.parseSteps(skill.content);
    
    // 执行步骤
    const results = [];
    for (const step of steps) {
      const result = await this.executeStep(step, context);
      results.push(result);
      
      if (!result.success) {
        break;
      }
    }
    
    return results;
  }
  
  private parseSteps(content: string): string[] {
    // 解析 Markdown 中的步骤
    const lines = content.split('\n');
    const steps: string[] = [];
    let currentStep = '';
    
    for (const line of lines) {
      if (line.startsWith('### Step') || line.startsWith('## Step')) {
        if (currentStep) {
          steps.push(currentStep);
        }
        currentStep = line;
      } else {
        currentStep += '\n' + line;
      }
    }
    
    if (currentStep) {
      steps.push(currentStep);
    }
    
    return steps;
  }
  
  private async executeStep(step: string, context: any): Promise<any> {
    // 执行单个步骤
    // 这里可以根据步骤内容调用不同的工具
    return { success: true, data: step };
  }
}
```

**验证**：创建 Skill 执行器，测试执行一个简单的 Skill。

---

## 使用方法

### 加载 Skill

```typescript
const loader = new SkillLoader();
await loader.loadFromDirectory('./skills');

const skill = loader.getSkill('voice-recognition');
console.log(skill);
```

### 发现 Skill

```typescript
const discovery = new SkillDiscovery(loader);

const skills = discovery.findSkillsForIntent('语音识别');
console.log(skills);
```

### 执行 Skill

```typescript
const executor = new SkillExecutor();

const result = await executor.execute(skill, {
  cwd: process.cwd(),
  user: 'user123',
});

console.log(result);
```

---

## 目录结构

```
skills/
├── types.ts           # 类型定义
├── SkillLoader.ts     # Skill 加载器
├── SkillDiscovery.ts  # Skill 发现
├── SkillExecutor.ts   # Skill 执行器
└── skills/
    ├── voice-recognition.md
    ├── tool-system-builder.md
    └── multi-agent-coordinator.md
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| Skill 未加载 | 文件格式错误 | 检查 YAML frontmatter |
| Skill 未发现 | 触发词不匹配 | 检查 triggers 配置 |
| Skill 执行失败 | 依赖未满足 | 检查 dependencies |
| Skill 版本冲突 | 版本不兼容 | 检查版本号 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| Skill 管理 | LoadSkill, UnloadSkill, ReloadSkill | 生命周期 |
| Skill 发现 | FindSkill, SearchSkill, ListSkills | 发现 |
| Skill 执行 | ExecuteSkill, RunSkill, InvokeSkill | 执行 |
| Skill 依赖 | ResolveDependencies, CheckCompatibility | 依赖 |
