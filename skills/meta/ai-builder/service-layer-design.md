---
name: 服务层设计
layer: meta
category: ai-builder
description: >
  教 AI 如何设计和构建服务层架构。
  当用户想要实现服务注册、服务调用、服务集成时触发。
  关键词：服务层、service layer、服务注册、服务调用。
---

# 服务层设计

教 AI 如何设计和构建服务层架构，让 Agent 能调用外部服务。

## 能力概览

| 能力 | 说明 |
|------|------|
| 服务注册 | 注册可用的服务 |
| 服务调用 | 调用服务提供的功能 |
| 服务发现 | 自动发现可用的服务 |
| 服务监控 | 监控服务状态 |
| 服务容错 | 处理服务故障 |

## 构建方案选择

**先问用户需求，再选方案：**

```
IF 用户需要简单服务调用:
    → 方案一（轻量版）— HTTP 客户端 + 服务注册
ELSE IF 用户需要微服务架构:
    → 方案二（完整版）— 服务发现 + 负载均衡 + 熔断器
ELSE IF 用户已有服务框架:
    → 方案三（集成版）— 在现有框架上扩展
```

| 你的需求 | 推荐方案 | 状态 |
|---------|----------|------|
| 简单服务调用 | 方案一 | ✅ 生产验证 |
| 微服务架构 | 方案二 | ⚠️ 社区贡献，待验证 |
| 集成现有框架 | 方案三 | ⚠️ 社区贡献，待验证 |

---

## Agent 执行规范

### 核心约束

- **先问用户需求**：了解用户要做什么类型的服务层
- **先问服务类型**：确认服务是 HTTP、gRPC 还是消息队列
- **服务要有文档**：每个服务都要有 API 文档
- **服务要可监控**：监控服务状态和性能
- **服务要可容错**：处理服务故障
- **不要猜测需求**：让用户告诉你具体需要什么功能

### 设计原则

1. **服务自治**：每个服务独立部署和扩展
2. **服务发现**：支持自动发现可用的服务
3. **服务容错**：处理服务故障和超时
4. **服务监控**：监控服务状态和性能
5. **服务安全**：支持认证和授权

---

## 前置条件

### TypeScript 版

| 依赖 | 版本 | 用途 |
|------|------|------|
| TypeScript | 5.0+ | 类型安全 |
| Node.js | 18+ | 运行时 |
| axios | 1.6+ | HTTP 客户端（可选） |

---

## 安装步骤

### Step 1：定义服务接口

**TypeScript 版：**
```typescript
// services/types.ts
interface Service {
  name: string;
  baseUrl: string;
  endpoints: ServiceEndpoint[];
}

interface ServiceEndpoint {
  name: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
}

interface ServiceCall {
  service: string;
  endpoint: string;
  params?: any;
  data?: any;
}
```

**验证**：定义服务接口，确认类型检查通过。

### Step 2：创建服务注册表

**TypeScript 版：**
```typescript
// services/ServiceRegistry.ts
class ServiceRegistry {
  private services: Map<string, Service> = new Map();
  
  register(service: Service): void {
    this.services.set(service.name, service);
  }
  
  get(name: string): Service | undefined {
    return this.services.get(name);
  }
  
  getAll(): Service[] {
    return Array.from(this.services.values());
  }
  
  discover(): Service[] {
    // 实现服务发现逻辑
    return this.getAll();
  }
}
```

**验证**：创建服务注册表，注册和获取服务。

### Step 3：实现服务客户端

**TypeScript 版：**
```typescript
// services/ServiceClient.ts
import axios from 'axios';

class ServiceClient {
  constructor(private registry: ServiceRegistry) {}
  
  async call(call: ServiceCall): Promise<any> {
    const service = this.registry.get(call.service);
    if (!service) {
      throw new Error(`服务 ${call.service} 未找到`);
    }
    
    const endpoint = service.endpoints.find(e => e.name === call.endpoint);
    if (!endpoint) {
      throw new Error(`端点 ${call.endpoint} 未找到`);
    }
    
    const url = `${service.baseUrl}${endpoint.path}`;
    
    try {
      const response = await axios({
        method: endpoint.method,
        url,
        params: call.params,
        data: call.data,
      });
      
      return response.data;
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      throw new Error(`服务调用失败: ${msg}`);
    }
  }
}
```

**验证**：创建服务客户端，测试服务调用。

### Step 4：添加服务监控

**TypeScript 版：**
```typescript
// services/ServiceMonitor.ts
class ServiceMonitor {
  private metrics: Map<string, {
    calls: number;
    errors: number;
    totalTime: number;
  }> = new Map();
  
  record(service: string, duration: number, error?: Error): void {
    if (!this.metrics.has(service)) {
      this.metrics.set(service, { calls: 0, errors: 0, totalTime: 0 });
    }
    
    const metric = this.metrics.get(service)!;
    metric.calls++;
    metric.totalTime += duration;
    
    if (error) {
      metric.errors++;
    }
  }
  
  getMetrics(service: string): {
    calls: number;
    errors: number;
    avgTime: number;
  } | undefined {
    const metric = this.metrics.get(service);
    if (!metric) return undefined;
    
    return {
      calls: metric.calls,
      errors: metric.errors,
      avgTime: metric.totalTime / metric.calls,
    };
  }
}
```

**验证**：创建服务监控器，测试监控功能。

---

## 使用方法

### 注册服务

```typescript
const registry = new ServiceRegistry();

registry.register({
  name: 'user-service',
  baseUrl: 'https://api.example.com/users',
  endpoints: [
    {
      name: 'get-user',
      method: 'GET',
      path: '/:id',
      description: '获取用户信息'
    },
    {
      name: 'create-user',
      method: 'POST',
      path: '/',
      description: '创建用户'
    }
  ]
});
```

### 调用服务

```typescript
const client = new ServiceClient(registry);

const user = await client.call({
  service: 'user-service',
  endpoint: 'get-user',
  params: { id: '123' }
});

console.log(user);
```

### 监控服务

```typescript
const monitor = new ServiceMonitor();

const start = Date.now();
try {
  await client.call({ service: 'user-service', endpoint: 'get-user' });
  monitor.record('user-service', Date.now() - start);
} catch (error) {
  monitor.record('user-service', Date.now() - start, error);
}

const metrics = monitor.getMetrics('user-service');
console.log(metrics);
```

---

## 目录结构

```
services/
├── types.ts             # 类型定义
├── ServiceRegistry.ts   # 服务注册表
├── ServiceClient.ts     # 服务客户端
├── ServiceMonitor.ts    # 服务监控
└── services/
    ├── UserService.ts   # 用户服务
    └── OrderService.ts  # 订单服务
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 服务未找到 | 服务未注册 | 检查服务注册 |
| 服务调用失败 | 网络问题 | 检查网络连接 |
| 服务超时 | 服务响应慢 | 增加超时时间 |
| 服务错误 | 服务实现问题 | 检查服务实现 |

---

## 工具分类

| 类别 | 工具示例 | 说明 |
|------|----------|------|
| 服务管理 | RegisterService, UnregisterService | 生命周期 |
| 服务调用 | CallService, InvokeService | 调用 |
| 服务发现 | DiscoverServices, FindService | 发现 |
| 服务监控 | GetMetrics, HealthCheck | 监控 |
