---
name: 权限系统设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建权限控制系统。
  当用户想要实现权限检查、权限规则、权限管理时触发。
  关键词：权限系统、permission、权限检查、权限规则。
---

# 权限系统设计

教 AI 如何设计和构建权限控制系统，让 Agent 能安全地执行操作。

## 能力概览

| 能力 | 说明 |
|------|------|
| 权限检查 | 检查操作是否被允许 |
| 权限规则 | 定义权限规则 |
| 权限模式 | 支持多种权限模式 |
| 权限审计 | 记录权限检查历史 |
| 权限继承 | 支持权限继承和覆盖 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单权限检查:
    → 方案一（轻量版）— 白名单/黑名单
ELSE IF 用户需要复杂权限规则:
    → 方案二（完整版）— 规则引擎 + 权限模式
ELSE IF 用户已有权限系统:
    → 方案三（集成版）— 在现有系统上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单权限检查 | 方案一 | ✅ 生产验证 |
| 复杂权限规则 | 方案二 | ✅ 生产验证 |
| 集成现有系统 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的权限系统
- **先问安全要求**：确认安全级别（宽松/严格/自定义）
- **权限规则要明确**：不要有模糊的规则
- **权限检查要记录**：记录每次权限检查的结果
- **权限模式要可配置**：支持多种权限模式
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **最小权限**：默认拒绝，只允许明确授权的操作
2. **权限分离**：读写执行权限分开管理
3. **权限继承**：支持权限继承和覆盖
4. **可审计**：记录所有权限检查
5. **可配置**：权限规则可以动态配置

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |

---

## 安装步骤

### Step 1：定义权限类型

**TypeScript 版：**
```typescript
// permissions/types.ts
type PermissionMode = 'auto' | 'prompt' | 'rule' | 'deny';

interface PermissionRule {
  condition: (input: any, context: any) => boolean;
  action: 'allow' | 'deny' | 'prompt';
  reason?: string;
}

interface PermissionCheck {
  allowed: boolean;
  reason?: string;
  mode: PermissionMode;
}
```

**验证**：定义权限类型，确认类型检查通过。

### Step 2：创建权限检查器

**TypeScript 版：**
```typescript
// permissions/PermissionChecker.ts
class PermissionChecker {
  private rules: PermissionRule[] = [];
  private mode: PermissionMode = 'prompt';
  
  setMode(mode: PermissionMode): void {
    this.mode = mode;
  }
  
  addRule(rule: PermissionRule): void {
    this.rules.push(rule);
  }
  
  check(input: any, context: any): PermissionCheck {
    // 检查规则
    for (const rule of this.rules) {
      if (rule.condition(input, context)) {
        return {
          allowed: rule.action === 'allow',
          reason: rule.reason,
          mode: this.mode
        };
      }
    }
    
    // 默认行为
    return {
      allowed: this.mode === 'auto',
      reason: '无匹配规则',
      mode: this.mode
    };
  }
}
```

**验证**：创建权限检查器，测试权限检查。

### Step 3：实现权限审计

**TypeScript 版：**
```typescript
// permissions/PermissionAuditor.ts
class PermissionAuditor {
  private log: Array<{
    timestamp: Date;
    input: any;
    result: PermissionCheck;
  }> = [];
  
  record(input: any, result: PermissionCheck): void {
    this.log.push({
      timestamp: new Date(),
      input,
      result
    });
  }
  
  getLog(): Array<{
    timestamp: Date;
    input: any;
    result: PermissionCheck;
  }> {
    return [...this.log];
  }
  
  clearLog(): void {
    this.log = [];
  }
}
```

**验证**：创建权限审计器，测试记录功能。

---

## 使用方法

### 创建权限检查器

```typescript
const checker = new PermissionChecker();
checker.setMode('rule');

// 添加规则
checker.addRule({
  condition: (input, ctx) => input.type === 'read',
  action: 'allow',
  reason: '读操作允许'
});

checker.addRule({
  condition: (input, ctx) => input.command.includes('rm -rf'),
  action: 'deny',
  reason: '危险命令禁止'
});
```

### 检查权限

```typescript
const result = checker.check(
  { type: 'read', path: '/tmp' },
  { user: 'admin' }
);

console.log(result);
// { allowed: true, reason: '读操作允许', mode: 'rule' }
```

### 记录审计日志

```typescript
const auditor = new PermissionAuditor();
auditor.record({ type: 'read' }, result);

const log = auditor.getLog();
console.log(log);
```

---

## 目录结构

```
permissions/
├── types.ts             # 类型定义
├── PermissionChecker.ts # 权限检查器
├── PermissionAuditor.ts # 权限审计
└── rules/
    ├── fileRules.ts     # 文件权限规则
    └── commandRules.ts  # 命令权限规则
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 权限被拒绝 | 违反权限规则 | 检查权限规则 |
| 权限检查失败 | 规则配置错误 | 检查规则语法 |
| 审计日志丢失 | 未调用 record | 检查审计代码 |
| 权限模式错误 | 模式设置错误 | 检查 setMode 调用 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| 权限检查 | CheckPermission, HasPermission | 检查 |
| 权限管理 | AddRule, RemoveRule, SetMode | 管理 |
| 权限审计 | RecordAudit, GetAuditLog | 审计 |
