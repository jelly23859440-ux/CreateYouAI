"""
代理循环 - 核心引擎

提供 AgentLoop，管理有状态对话和工具执行循环。
不包含内置工具实现，通过 registry 注册自定义工具。
"""

import json
from typing import List, Dict, Callable, Any, Optional

from .models import AgentMessage, AgentState
from .queue import PendingMessageQueue


class AgentLoop:
    """代理循环 - 管理有状态对话和工具执行"""
    
    def __init__(
        self,
        llm_provider,
        tools: List[Dict],
        system_prompt: str = "",
        model: str = "openai/gpt-4",
        max_iterations: int = 20,
        before_tool_call: Callable = None,
        after_tool_call: Callable = None,
    ):
        """
        Args:
            llm_provider: LLM 提供者，需实现 complete(model, messages, tools) 方法
            tools: 工具定义列表 [{"name": ..., "description": ..., "parameters": ...}]
            system_prompt: 系统提示词
            model: 模型名称
            max_iterations: 最大循环次数
            before_tool_call: 工具执行前钩子 (name, args) -> {"block": bool, "reason": str}
            after_tool_call: 工具执行后钩子 (name, args, result) -> result
        """
        self.llm = llm_provider
        self.tools = tools
        self.state = AgentState(
            system_prompt=system_prompt,
            model=model
        )
        self.max_iterations = max_iterations
        self.before_tool_call = before_tool_call
        self.after_tool_call = after_tool_call
        
        # 消息队列
        self.steering_queue = PendingMessageQueue("one-at-a-time")
        self.follow_up_queue = PendingMessageQueue("all")
        
        # 事件处理器
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # 工具注册表
        self._tool_registry: Dict[str, Callable] = {}
    
    def tool(self, name: str):
        """工具注册装饰器"""
        def decorator(func):
            self._tool_registry[name] = func
            return func
        return decorator
    
    def on(self, event_name: str):
        """事件订阅装饰器"""
        def decorator(handler):
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(handler)
            return handler
        return decorator
    
    def emit(self, event_name: str, data: Any = None):
        """触发事件"""
        for handler in self.event_handlers.get(event_name, []):
            try:
                handler(data or {})
            except Exception as e:
                print(f"事件处理错误: {e}")
    
    def prompt(self, user_input: str) -> AgentMessage:
        """用户输入 -> 代理响应"""
        self.state.messages.append(AgentMessage(role="user", content=user_input))
        return self._run_loop()
    
    def continue_conversation(self) -> AgentMessage:
        """继续对话（不添加新用户消息）"""
        return self._run_loop()
    
    def steer(self, message: str):
        """中途注入消息（打断当前轮次）"""
        self.steering_queue.add({
            "role": "user",
            "content": message
        })
    
    def follow_up(self, message: str):
        """后续消息（当前轮次结束后执行）"""
        self.follow_up_queue.add({
            "role": "user",
            "content": message
        })
    
    def abort(self):
        """中止当前轮次"""
        self.state.error_message = "用户中止"
    
    def reset(self):
        """重置状态"""
        self.state = AgentState(
            system_prompt=self.state.system_prompt,
            model=self.state.model
        )
        self.steering_queue = PendingMessageQueue("one-at-a-time")
        self.follow_up_queue = PendingMessageQueue("all")
    
    def _run_loop(self) -> AgentMessage:
        """运行代理循环"""
        self.emit("agent_start")
        
        iterations = 0
        while iterations < self.max_iterations:
            if self.state.error_message:
                break
            
            # 注入 steering 消息
            steering_msgs = self.steering_queue.drain()
            for msg in steering_msgs:
                self.state.messages.append(AgentMessage(**msg))
            
            # 调用 LLM
            self.emit("turn_start")
            response = self._call_llm()
            
            if response.tool_calls:
                assistant_msg = AgentMessage(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=response.tool_calls
                )
                self.state.messages.append(assistant_msg)
                
                for tool_call in response.tool_calls:
                    result = self._execute_tool_call(tool_call)
                    self.state.messages.append(result)
                
                self.emit("turn_end")
                iterations += 1
            else:
                assistant_msg = AgentMessage(
                    role="assistant",
                    content=response.content
                )
                self.state.messages.append(assistant_msg)
                self.emit("turn_end")
                break
        
        # 检查 follow-up 消息
        follow_up_msgs = self.follow_up_queue.drain()
        if follow_up_msgs:
            for msg in follow_up_msgs:
                self.state.messages.append(AgentMessage(**msg))
            return self._run_loop()
        
        self.emit("agent_end")
        return self.state.messages[-1]
    
    def _call_llm(self):
        """调用 LLM"""
        messages = []
        
        if self.state.system_prompt:
            messages.append({"role": "system", "content": self.state.system_prompt})
        
        for msg in self.state.messages:
            msg_dict = {"role": msg.role, "content": msg.content}
            if msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            if msg.name:
                msg_dict["name"] = msg.name
            messages.append(msg_dict)
        
        tools = self._convert_tools_to_openai_format()
        
        return self.llm.complete(self.state.model, messages, tools=tools)
    
    def _convert_tools_to_openai_format(self) -> List[Dict]:
        """转换工具为 OpenAI 格式"""
        tools = []
        for tool in self.tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
        return tools
    
    def _execute_tool_call(self, tool_call: Dict) -> AgentMessage:
        """执行工具调用"""
        call_id = tool_call["id"]
        call_name = tool_call["function"]["name"]
        call_args = json.loads(tool_call["function"]["arguments"])
        
        self.emit("tool_execution_start", {"tool_name": call_name, "args": call_args})
        
        # 执行前钩子
        if self.before_tool_call:
            hook_result = self.before_tool_call(call_name, call_args)
            if hook_result and hook_result.get("block"):
                return AgentMessage(
                    role="tool",
                    content=f"被阻止: {hook_result.get('reason', '未知原因')}",
                    tool_call_id=call_id,
                    name=call_name
                )
        
        # 执行工具（从注册表查找）
        try:
            result = self._execute_tool(call_name, call_args)
        except Exception as e:
            result = {"content": str(e), "isError": True}
        
        # 执行后钩子
        if self.after_tool_call:
            result = self.after_tool_call(call_name, call_args, result)
        
        self.emit("tool_execution_end", {"tool_name": call_name, "result": result})
        
        return AgentMessage(
            role="tool",
            content=result.get("content", ""),
            tool_call_id=call_id,
            name=call_name
        )
    
    def _execute_tool(self, name: str, args: Dict) -> Dict:
        """执行工具（从注册表查找）"""
        if name in self._tool_registry:
            return self._tool_registry[name](args)
        return {"content": f"未知工具: {name}", "isError": True}
