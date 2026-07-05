---
name: tool-schema
layer: core
category: reasoning
status: unverified
description: >
  工具参数验证：定义工具 schema 并校验参数。
  关键词：工具、schema、参数、验证。
---

# 工具参数验证

## 功能说明
提供工具 schema 定义和参数验证框架。支持 JSON Schema 格式的工具定义，包括参数类型检查、必填字段验证，以及工具注册和管理功能。可将工具定义转换为 OpenAI 格式以兼容主流 LLM 工具调用接口。

## 使用方法
```python
from tool_schema import ToolSchema

# 创建 schema 管理器
schema = ToolSchema()

# 注册自定义工具
tool_def = {
    "name": "search",
    "label": "搜索工具",
    "description": "执行搜索操作",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "搜索查询"},
            "limit": {"type": "number", "description": "结果数量"}
        },
        "required": ["query"]
    }
}
schema.register_tool(tool_def)

# 验证工具参数
result = schema.validate("search", {"query": "test", "limit": 10})
print(result)  # {'valid': True}

# 获取工具定义
tool = schema.get_tool("search")

# 列出所有工具
tools = schema.list_tools()

# 转换为 OpenAI 格式
openai_tools = schema.to_openai_format()
```

## 依赖
| 依赖 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ |
| dataclasses | 内置 | ✅ |
| typing | 内置 | ✅ |

## 来源
- 原项目：pi-mini
- 来源模块：tool_schema.py
- 核心功能：工具 schema 定义、参数验证、工具管理