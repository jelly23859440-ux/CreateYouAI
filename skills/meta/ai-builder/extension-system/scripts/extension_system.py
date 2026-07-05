from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolDefinition:
    name: str
    label: str
    description: str
    parameters: Dict
    execute: Callable
    execution_mode: str = "sequential"


@dataclass
class CommandDefinition:
    name: str
    description: str
    handler: Callable


class ExtensionSystem:
    EVENT_TYPES = [
        "session_start", "session_end",
        "before_agent_start", "agent_start", "agent_end",
        "turn_start", "turn_end",
        "tool_call", "tool_result", "tool_execution_end",
        "input", "context", "before_provider_request",
    ]

    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.tools: Dict[str, ToolDefinition] = {}
        self.commands: Dict[str, CommandDefinition] = {}
        self.before_hooks: List[Callable] = []
        self.after_hooks: List[Callable] = []

    def on(self, event_name: str):
        def decorator(handler):
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(handler)
            return handler
        return decorator

    def emit(self, event_name: str, event_data: Any = None) -> List[Any]:
        results = []
        for handler in self.event_handlers.get(event_name, []):
            try:
                result = handler(event_data or {})
                results.append({"handler": handler.__name__, "result": result})
            except Exception as e:
                results.append({"handler": handler.__name__, "error": str(e)})
        return results

    def register_tool(self, tool_def: Dict) -> None:
        tool = ToolDefinition(
            name=tool_def["name"],
            label=tool_def.get("label", tool_def["name"]),
            description=tool_def["description"],
            parameters=tool_def["parameters"],
            execute=tool_def["execute"],
            execution_mode=tool_def.get("execution_mode", "sequential")
        )
        self.tools[tool.name] = tool

    def register_command(self, name: str, options: Dict) -> None:
        self.commands[name] = CommandDefinition(
            name=name,
            description=options["description"],
            handler=options["handler"]
        )

    def add_before_hook(self, hook: Callable) -> None:
        self.before_hooks.append(hook)

    def add_after_hook(self, hook: Callable) -> None:
        self.after_hooks.append(hook)

    def execute_tool(self, tool_name: str, params: Dict) -> Dict:
        for hook in self.before_hooks:
            result = hook(tool_name, params)
            if result and result.get("block"):
                return {"content": f"被阻止: {result.get('reason', '未知原因')}", "isError": True}

        if tool_name not in self.tools:
            return {"content": f"工具不存在: {tool_name}", "isError": True}

        tool = self.tools[tool_name]
        try:
            result = tool.execute(params)
        except Exception as e:
            result = {"content": str(e), "isError": True}

        for hook in self.after_hooks:
            result = hook(tool_name, params, result)

        return result

    def list_events(self) -> Dict[str, List[str]]:
        return {
            event: [h.__name__ for h in handlers]
            for event, handlers in self.event_handlers.items()
        }
