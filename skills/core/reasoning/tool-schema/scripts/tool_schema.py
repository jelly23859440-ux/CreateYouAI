"""
工具参数验证 - 定义工具 schema 并校验参数

核心功能：
- 工具定义（JSON Schema 格式）
- 参数验证
- 工具注册和管理
- 类型检查
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolCall:
    """工具调用"""
    id: str
    name: str
    arguments: Dict


@dataclass
class ToolResult:
    """工具执行结果"""
    content: str
    details: Any = None
    is_error: bool = False
    terminate: bool = False


class ToolSchema:
    """工具 Schema 定义和验证"""
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
    
    def register_tool(self, tool_def: Dict) -> None:
        """注册自定义工具"""
        if "name" not in tool_def:
            raise ValueError("工具定义必须包含 'name' 字段")
        self.tools[tool_def["name"]] = tool_def
    
    def validate(self, tool_name: str, args: Dict) -> Dict:
        """验证工具调用参数"""
        if tool_name not in self.tools:
            return {"valid": False, "error": f"工具不存在: {tool_name}"}
        
        tool = self.tools[tool_name]
        schema = tool.get("parameters", {})
        
        # 检查必填字段
        required = schema.get("required", [])
        for field in required:
            if field not in args:
                return {"valid": False, "error": f"缺少必填参数: {field}"}
        
        # 检查类型
        properties = schema.get("properties", {})
        for key, value in args.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if not self._check_type(value, expected_type):
                    return {"valid": False, "error": f"参数 {key} 类型错误: 期望 {expected_type}"}
        
        return {"valid": True}
    
    def get_tool(self, name: str) -> Optional[Dict]:
        """获取工具定义"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict]:
        """列出所有工具"""
        return list(self.tools.values())
    
    def to_openai_format(self) -> List[Dict]:
        """转换为 OpenAI 工具格式"""
        tools = []
        for tool in self.tools.values():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", {})
                }
            })
        return tools
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查值类型"""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        expected = type_map.get(expected_type)
        if expected is None:
            return True  # 未知类型，跳过检查
        
        return isinstance(value, expected)