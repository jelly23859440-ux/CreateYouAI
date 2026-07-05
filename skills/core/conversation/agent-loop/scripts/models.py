"""
代理循环 - 数据模型

提供 AgentMessage、AgentState、ExecutionMode 等基础数据结构。
"""

from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ExecutionMode(Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


@dataclass
class AgentMessage:
    """代理消息"""
    role: str  # user / assistant / tool
    content: str = ""
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class AgentState:
    """代理状态"""
    system_prompt: str = ""
    model: str = "openai/gpt-4"
    messages: List[AgentMessage] = field(default_factory=list)
    is_streaming: bool = False
    streaming_message: Optional[AgentMessage] = None
    pending_tool_calls: set = field(default_factory=set)
    error_message: Optional[str] = None
