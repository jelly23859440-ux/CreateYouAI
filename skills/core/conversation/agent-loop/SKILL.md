---
name: agent-loop
layer: core
category: conversation
status: unverified
description: >
  代理循环：有状态对话、工具执行循环。
  关键词：代理、循环、对话、工具执行。
---

# 代理循环

## 功能说明

代理循环（Agent Loop）是有状态对话系统的核心引擎，管理以下流程：

1. **有状态对话** — 维护完整的消息历史，支持多轮对话
2. **工具执行循环** — LLM 返回工具调用时，执行工具并将结果反馈给 LLM，直到返回纯文本响应
3. **消息队列** — 支持中途注入（steering）和后续追加（follow-up）两种消息队列模式
4. **事件系统** — 在关键节点（agent_start, turn_start, tool_execution, turn_end, agent_end）触发事件
5. **钩子机制** — 提供 before_tool_call / after_tool_call 钩子，用于安全检查和结果后处理

## 使用方法

```python
from agent_loop import AgentLoop, AgentMessage

# 1. 定义工具
tools = [
    {
        "name": "search",
        "description": "搜索文档",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"}
            },
            "required": ["query"]
        }
    }
]

# 2. 创建代理循环
agent = AgentLoop(
    llm_provider=your_llm_client,
    tools=tools,
    system_prompt="你是一个助手。",
    model="gpt-4",
    max_iterations=20
)

# 3. 注册工具执行器
@agent.tool("search")
def search_tool(args):
    # 实现搜索逻辑
    return {"content": f"搜索结果: {args['query']}"}

# 4. 订阅事件
@agent.on("tool_execution_start")
def on_tool_start(data):
    print(f"执行工具: {data['tool_name']}")

# 5. 开始对话
response = agent.prompt("帮我搜索 Python 教程")
print(response.content)

# 6. 中途注入消息（打断当前轮次）
agent.steer("先停下来，我有个问题")

# 7. 追加后续消息（当前轮次结束后执行）
agent.follow_up("然后帮我总结一下")

# 8. 重置状态
agent.reset()
```

## 依赖

| 依赖 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ |
| dataclasses | 内置 | ✅ |

## 架构设计

```
┌─────────────────────────────────────────────────┐
│                   AgentLoop                      │
├─────────────────────────────────────────────────┤
│  prompt(user_input) → _run_loop()               │
│  ┌───────────────────────────────────────────┐  │
│  │  while iterations < max:                  │  │
│  │    1. drain steering_queue                │  │
│  │    2. call LLM                            │  │
│  │    3. if tool_calls → execute → append    │  │
│  │    4. else → return final response        │  │
│  └───────────────────────────────────────────┘  │
│  drain follow_up_queue → recursive call          │
└─────────────────────────────────────────────────┘
```

## 来源

- 原项目：pi-mini
- 来源模块：agent_loop.py
