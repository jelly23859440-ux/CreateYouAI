---
name: 记忆系统设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建分层记忆系统。
  当用户想要实现记忆存储、记忆检索、记忆整理时触发。
  关键词：记忆系统、memory、热层、温层、冷层、记忆检索。
---

# 记忆系统设计

教 AI 如何设计和构建分层记忆系统，让 Agent 能记住和检索信息。

## 能力概览

| 能力 | 说明 |
|------|------|
| 分层存储 | 热层（活跃）→ 温层（近期）→ 冷层（归档） |
| 记忆检索 | 基于相关性、时间、标签检索 |
| 记忆整理 | 自动归档、去重、合并 |
| 记忆提取 | 从对话中自动提取关键信息 |
| 记忆关联 | 建立记忆之间的关联关系 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单记忆:
    → 方案一（轻量版）— 单层存储 + 关键词检索
ELSE IF 用户需要分层记忆:
    → 方案二（完整版）— 热/温/冷三层 + 向量检索
ELSE IF 用户已有数据库:
    → 方案三（集成版）— 在现有数据库上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单记忆 | 方案一 | ✅ 生产验证 |
| 分层记忆 | 方案二 | ✅ 生产验证 |
| 集成现有数据库 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的记忆系统
- **先问数据类型**：确认要存储什么类型的数据（对话、知识、事件）
- **每个记忆单元要结构化**：不要存储原始文本，要提取关键信息
- **记忆检索要高效**：不要每次都扫描全部记忆
- **记忆整理要定期**：不要让记忆无限增长
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **分层存储**：根据活跃度分层，提高检索效率
2. **结构化**：记忆单元要有明确的结构（类型、标签、时间、内容）
3. **可检索**：支持多种检索方式（关键词、向量、时间范围）
4. **可整理**：支持自动归档、去重、合并
5. **可扩展**：支持添加新的记忆类型和检索方式

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |
| SQLite/PostgreSQL | - | 存储（可选） |

### Python 版 ⚠️ 社区贡献，待验证

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行时 |
| SQLite/PostgreSQL | - | 存储（可选） |

---

## 安装步骤

### Step 1：定义记忆结构

**TypeScript 版：**
```typescript
// memory/types.ts
interface Memory {
  id: string;
  type: 'fact' | 'opinion' | 'event' | 'knowledge';
  content: string;
  tags: string[];
  confidence: number;  // 0-1
  createdAt: Date;
  updatedAt: Date;
  accessCount: number;
  lastAccessedAt: Date;
}

interface MemoryQuery {
  type?: string;
  tags?: string[];
  keywords?: string;
  timeRange?: { start: Date; end: Date };
  limit?: number;
}
```

**验证**：定义一个简单的记忆结构，确认类型检查通过。

### Step 2：创建分层存储

**TypeScript 版：**
```typescript
// memory/MemoryStore.ts
class MemoryStore {
  private hot: Memory[] = [];   // 热层：最近访问
  private warm: Memory[] = [];  // 温层：近期记忆
  private cold: Memory[] = [];  // 冷层：归档记忆
  
  async add(memory: Memory): Promise<void> {
    this.hot.push(memory);
    this.trimHotLayer();
  }
  
  async query(query: MemoryQuery): Promise<Memory[]> {
    // 先查热层
    let results = this.searchLayer(this.hot, query);
    
    // 如果结果不够，查温层
    if (results.length < (query.limit || 10)) {
      results = results.concat(this.searchLayer(this.warm, query));
    }
    
    // 如果还不够，查冷层
    if (results.length < (query.limit || 10)) {
      results = results.concat(this.searchLayer(this.cold, query));
    }
    
    return results.slice(0, query.limit || 10);
  }
  
  private searchLayer(layer: Memory[], query: MemoryQuery): Memory[] {
    return layer.filter(memory => {
      if (query.type && memory.type !== query.type) return false;
      if (query.tags && !query.tags.some(tag => memory.tags.includes(tag))) return false;
      if (query.keywords && !memory.content.includes(query.keywords)) return false;
      return true;
    });
  }
  
  private trimHotLayer(): void {
    // 热层最多 100 条
    if (this.hot.length > 100) {
      const moved = this.hot.splice(0, 50);
      this.warm = moved.concat(this.warm);
    }
  }
}
```

**验证**：创建记忆存储实例，添加和查询记忆。

### Step 3：实现记忆检索

**TypeScript 版：**
```typescript
// memory/MemoryRetriever.ts
class MemoryRetriever {
  constructor(private store: MemoryStore) {}
  
  async retrieve(query: string, limit: number = 5): Promise<Memory[]> {
    // 1. 关键词检索
    const keywordResults = await this.store.query({
      keywords: query,
      limit: limit * 2
    });
    
    // 2. 按相关性排序
    const ranked = this.rankByRelevance(keywordResults, query);
    
    // 3. 返回 top N
    return ranked.slice(0, limit);
  }
  
  private rankByRelevance(memories: Memory[], query: string): Memory[] {
    return memories.sort((a, b) => {
      // 简单的相关性评分
      const scoreA = this.calculateScore(a, query);
      const scoreB = this.calculateScore(b, query);
      return scoreB - scoreA;
    });
  }
  
  private calculateScore(memory: Memory, query: string): number {
    let score = 0;
    
    // 关键词匹配
    if (memory.content.includes(query)) score += 10;
    
    // 标签匹配
    if (memory.tags.some(tag => query.includes(tag))) score += 5;
    
    // 时间衰减
    const daysSinceAccess = (Date.now() - memory.lastAccessedAt.getTime()) / (1000 * 60 * 60 * 24);
    score -= daysSinceAccess * 0.1;
    
    // 访问频率
    score += memory.accessCount * 0.5;
    
    return score;
  }
}
```

**验证**：创建记忆检索器，测试检索功能。

### Step 4：添加记忆整理

**TypeScript 版：**
```typescript
// memory/MemoryOrganizer.ts
class MemoryOrganizer {
  constructor(private store: MemoryStore) {}
  
  async organize(): Promise<void> {
    // 1. 去重
    await this.deduplicate();
    
    // 2. 合并相似记忆
    await this.mergeSimilar();
    
    // 3. 归档旧记忆
    await this.archiveOld();
  }
  
  private async deduplicate(): Promise<void> {
    // 实现去重逻辑
  }
  
  private async mergeSimilar(): Promise<void> {
    // 实现合并逻辑
  }
  
  private async archiveOld(): Promise<void> {
    // 将超过 30 天未访问的记忆移到冷层
  }
}
```

**验证**：创建记忆整理器，测试整理功能。

---

## 使用方法

### 添加记忆

```typescript
const store = new MemoryStore();

await store.add({
  id: '1',
  type: 'fact',
  content: 'TypeScript 是 JavaScript 的超集',
  tags: ['typescript', 'javascript'],
  confidence: 0.9,
  createdAt: new Date(),
  updatedAt: new Date(),
  accessCount: 0,
  lastAccessedAt: new Date()
});
```

### 检索记忆

```typescript
const retriever = new MemoryRetriever(store);

const results = await retriever.retrieve('TypeScript', 5);
console.log(results);
```

### 整理记忆

```typescript
const organizer = new MemoryOrganizer(store);

await organizer.organize();
```

---

## 目录结构

```
memory/
├── types.ts           # 类型定义
├── MemoryStore.ts     # 分层存储
├── MemoryRetriever.ts # 记忆检索
├── MemoryOrganizer.ts # 记忆整理
└── extractors/
    ├── FactExtractor.ts
    ├── EventExtractor.ts
    └── KnowledgeExtractor.ts
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 记忆未保存 | 存储空间不足 | 检查存储配置 |
| 检索结果不相关 | 相关性算法问题 | 调整评分权重 |
| 检索速度慢 | 未建立索引 | 添加索引或使用向量数据库 |
| 记忆重复 | 去重逻辑问题 | 检查 deduplicate 实现 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| 记忆管理 | AddMemory, UpdateMemory, DeleteMemory | CRUD 操作 |
| 记忆检索 | SearchMemory, GetMemory, QueryMemory | 检索 |
| 记忆整理 | OrganizeMemory, DeduplicateMemory, ArchiveMemory | 整理 |
| 记忆提取 | ExtractFacts, ExtractEvents, ExtractKnowledge | 提取 |
