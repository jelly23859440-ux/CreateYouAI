---
name: extension-system
layer: meta
category: ai-builder
status: unverified
description: >
  扩展系统：注册/注销工具、事件发射。
  关键词：扩展、插件、工具注册、事件。
---

# 扩展系统

## 功能说明

扩展系统提供事件驱动架构，支持：
- **事件订阅与发射**：通过装饰器 `on()` 订阅事件，`emit()` 触发事件
- **工具注册**：动态注册自定义工具，定义参数和执行逻辑
- **命令注册**：注册自定义命令及处理器
- **执行钩子**：在工具执行前后添加拦截器，支持前置阻止

## 使用方法

```python
from extension_system import ExtensionSystem

# 初始化扩展系统
ext = ExtensionSystem()

# 订阅事件
@ext.on("session_start")
def on_session_start(data):
    print("会话开始")

# 注册工具
ext.register_tool({
    "name": "my_tool",
    "description": "自定义工具",
    "parameters": {"type": "object", "properties": {}},
    "execute": lambda params: {"result": "done"}
})

# 执行工具（带钩子）
result = ext.execute_tool("my_tool", {})

# 触发事件
ext.emit("tool_call", {"tool": "my_tool"})
```

## 依赖

| 依赖 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ |

## 来源

- 原项目：pi-mini
- 来源模块：extension_system.py
