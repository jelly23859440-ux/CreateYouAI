---
name: llm-provider
layer: core
category: reasoning
status: unverified
description: >
  统一 LLM 接口：调用多家提供商。
  关键词：LLM、API、模型、提供商。
---

# 统一 LLM 接口

## 功能说明
提供统一的LLM调用接口，支持OpenAI、Anthropic、Google Gemini、Ollama、DeepSeek等多种提供商，支持同步和流式调用，支持工具调用和认证管理。

## 使用方法
```python
from llm_provider import LLMProvider, Message

# 初始化提供商
provider = LLMProvider()

# 同步调用
response = provider.complete(
    model="openai/gpt-4",
    messages=[{"role": "user", "content": "你好，请介绍一下自己"}]
)
print(response.content)

# 流式调用
for chunk in provider.stream(
    model="ollama/llama2",
    messages=[{"role": "user", "content": "讲个故事"}]
):
    if chunk["type"] == "text_delta":
        print(chunk["content"], end="", flush=True)

# 带工具调用
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名"}
                },
                "required": ["location"]
            }
        }
    }
]

response = provider.complete(
    model="openai/gpt-4",
    messages=[{"role": "user", "content": "北京今天天气怎么样？"}],
    tools=tools
)
```

## 依赖
| 依赖 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ |
| openai | 最新版 | 可选（OpenAI/DeepSeek） |
| anthropic | 最新版 | 可选（Anthropic） |
| google-generativeai | 最新版 | 可选（Google Gemini） |
| requests | 最新版 | ✅（Ollama） |

## 来源
- 原项目：pi-mini
- 来源模块：llm_provider.py