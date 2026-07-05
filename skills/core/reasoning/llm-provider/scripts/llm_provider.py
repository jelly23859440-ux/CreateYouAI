"""
统一 LLM 接口 - 支持多家提供商

核心功能：
- 统一调用多个 LLM 提供商
- 流式响应
- 工具调用
- 认证管理
"""

import os
import json
from typing import List, Dict, Optional, Generator, Any
from dataclasses import dataclass, field


@dataclass
class Message:
    """消息定义"""
    role: str  # user / assistant / system / tool
    content: str = ""
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    parameters: Dict  # JSON Schema


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    tool_calls: Optional[List[Dict]] = None
    usage: Optional[Dict] = None
    finish_reason: Optional[str] = None


class LLMProvider:
    """统一 LLM 提供商"""
    
    def __init__(self):
        self.providers = {
            "openai": self._call_openai,
            "anthropic": self._call_anthropic,
            "google": self._call_google,
            "ollama": self._call_ollama,
            "deepseek": self._call_deepseek,
        }
    
    def complete(self, model: str, messages: List[Dict], **kwargs) -> LLMResponse:
        """同步调用"""
        provider, model_name = self._parse_model(model)
        
        if provider not in self.providers:
            return LLMResponse(
                content="",
                model=model,
                usage={"error": f"不支持的提供商: {provider}"}
            )
        
        try:
            return self.providers[provider](model_name, messages, **kwargs)
        except Exception as e:
            return LLMResponse(
                content="",
                model=model,
                usage={"error": str(e)}
            )
    
    def stream(self, model: str, messages: List[Dict], **kwargs) -> Generator[Dict, None, None]:
        """流式调用"""
        provider, model_name = self._parse_model(model)
        
        if provider == "openai":
            yield from self._stream_openai(model_name, messages, **kwargs)
        elif provider == "ollama":
            yield from self._stream_ollama(model_name, messages, **kwargs)
        else:
            # 非流式提供商，一次性返回
            response = self.complete(model, messages, **kwargs)
            yield {"type": "text_delta", "content": response.content}
            yield {"type": "done", "content": response.content}
    
    def _parse_model(self, model: str) -> tuple:
        """解析模型字符串 'openai/gpt-4' -> ('openai', 'gpt-4')"""
        parts = model.split("/", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return "openai", model
    
    def _call_openai(self, model: str, messages: List[Dict], **kwargs) -> LLMResponse:
        """调用 OpenAI"""
        from openai import OpenAI
        client = OpenAI()
        
        # 构建参数
        params = {
            "model": model,
            "messages": messages,
        }
        
        if "tools" in kwargs:
            params["tools"] = kwargs["tools"]
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        
        response = client.chat.completions.create(**params)
        
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            tool_calls=response.choices[0].message.tool_calls,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason
        )
    
    def _call_anthropic(self, model: str, messages: List[Dict], **kwargs) -> LLMResponse:
        """调用 Anthropic"""
        from anthropic import Anthropic
        client = Anthropic()
        
        # 分离系统消息
        system_msg = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        params = {
            "model": model,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": user_messages,
        }
        
        if system_msg:
            params["system"] = system_msg
        
        response = client.messages.create(**params)
        
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        )
    
    def _call_google(self, model: str, messages: List[Dict], **kwargs) -> LLMResponse:
        """调用 Google Gemini"""
        import google.generativeai as genai
        
        genai.configure()
        model_instance = genai.GenerativeModel(model)
        
        # 转换消息格式
        history = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            role = "model" if msg["role"] == "assistant" else "user"
            history.append({"role": role, "parts": [msg["content"]]})
        
        response = model_instance.generate_content(history)
        
        return LLMResponse(
            content=response.text,
            model=model,
            usage={
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }
        )
    
    def _call_ollama(self, model: str, messages: List[Dict], **kwargs) -> LLMResponse:
        """调用 Ollama"""
        import requests
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            }
        )
        
        data = response.json()
        
        return LLMResponse(
            content=data["message"]["content"],
            model=model,
            usage={
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
            }
        )
    
    def _call_deepseek(self, model: str, messages: List[Dict], **kwargs) -> LLMResponse:
        """调用 DeepSeek（使用 OpenAI 兼容接口）"""
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )
    
    def _stream_openai(self, model: str, messages: List[Dict], **kwargs) -> Generator[Dict, None, None]:
        """流式调用 OpenAI"""
        from openai import OpenAI
        client = OpenAI()
        
        params = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        if "tools" in kwargs:
            params["tools"] = kwargs["tools"]
        
        stream = client.chat.completions.create(**params)
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield {"type": "text_delta", "content": chunk.choices[0].delta.content}
            if chunk.choices[0].delta.tool_calls:
                yield {"type": "tool_call_delta", "tool_calls": chunk.choices[0].delta.tool_calls}
        
        yield {"type": "done", "content": ""}
    
    def _stream_ollama(self, model: str, messages: List[Dict], **kwargs) -> Generator[Dict, None, None]:
        """流式调用 Ollama"""
        import requests
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": True
            },
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "message" in data:
                    yield {"type": "text_delta", "content": data["message"]["content"]}
                if data.get("done"):
                    yield {"type": "done", "content": ""}