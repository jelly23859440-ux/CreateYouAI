---
name: mcp-adapter
layer: meta
category: ai-builder
description: >
  将 MCP 工具转换为本地工具，支持工具发现和调用。
  当用户需要连接 MCP 服务器、适配外部工具、构建工具链时触发。
  关键词：MCP、工具适配、工具发现、协议转换、外部工具集成。
---

# MCP 工具适配器

将 Model Context Protocol (MCP) 工具转换为本地可调用的工具接口。

## 功能特性

- 发现 MCP 服务器提供的工具
- 将 MCP 工具转换为本地函数接口
- 支持工具参数验证和类型转换
- 处理异步 MCP 工具调用
- 支持工具列表缓存和刷新
- 错误处理和重试机制
- 工具调用日志记录

## 前置条件

- Python 3.8+
- MCP SDK（mcp 包）
- 网络访问（连接 MCP 服务器）

## 安装步骤

### 安装 MCP SDK

```bash
pip install mcp>=1.0.0
```

### 验证安装

```bash
python -c "import mcp; print(mcp.__version__)"
```

### 可选依赖

```bash
# 用于 HTTP 传输
pip install httpx>=0.25.0

# 用于 WebSocket 传输
pip install websockets>=12.0
```

## 使用方法

### 基础用法：发现和调用 MCP 工具

```python
import asyncio
from typing import Dict, Any, List, Optional

async def discover_mcp_tools(server_url: str) -> List[Dict[str, Any]]:
    """
    发现 MCP 服务器提供的工具
    
    Args:
        server_url: MCP 服务器地址（如 http://localhost:8000）
        
    Returns:
        工具列表
    """
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        raise ImportError("请安装 mcp: pip install mcp>=1.0.0")
    
    # 对于 HTTP 传输，使用 HTTP 客户端
    # 这里演示使用 stdio 传输
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()
            
            # 发现工具
            tools = await session.list_tools()
            
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
                for tool in tools.tools
            ]

# 使用示例
if __name__ == "__main__":
    tools = asyncio.run(discover_mcp_tools("http://localhost:8000"))
    print(f"发现 {len(tools)} 个工具:")
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
```

### 高级用法：完整适配器类

```python
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import inspect

@dataclass
class MCPTool:
    """MCP 工具描述"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server_url: str
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ToolCallResult:
    """工具调用结果"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0
    tool_name: str = ""

class MCPAdapter:
    """MCP 工具适配器"""
    
    def __init__(self, cache_dir: str = ".mcp_cache"):
        """
        初始化适配器
        
        Args:
            cache_dir: 工具缓存目录
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.tools: Dict[str, MCPTool] = {}
        self.logger = logging.getLogger(__name__)
        self._sessions: Dict[str, Any] = {}
    
    async def connect_server(self, server_url: str, transport: str = "http") -> bool:
        """
        连接到 MCP 服务器
        
        Args:
            server_url: 服务器地址
            transport: 传输类型（http, stdio, websocket）
            
        Returns:
            是否连接成功
        """
        try:
            if transport == "http":
                return await self._connect_http(server_url)
            elif transport == "stdio":
                return await self._connect_stdio(server_url)
            elif transport == "websocket":
                return await self._connect_websocket(server_url)
            else:
                self.logger.error(f"不支持的传输类型: {transport}")
                return False
        except Exception as e:
            self.logger.error(f"连接失败: {e}")
            return False
    
    async def _connect_http(self, server_url: str) -> bool:
        """HTTP 传输连接"""
        try:
            import httpx
        except ImportError:
            raise ImportError("请安装 httpx: pip install httpx>=0.25.0")
        
        async with httpx.AsyncClient() as client:
            # 发现工具
            response = await client.get(f"{server_url}/tools")
            if response.status_code == 200:
                tools_data = response.json()
                for tool_data in tools_data.get("tools", []):
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        parameters=tool_data.get("parameters", {}),
                        server_url=server_url
                    )
                    self.tools[tool.name] = tool
                
                self._cache_tools(server_url)
                return True
        return False
    
    async def _connect_stdio(self, command: str) -> bool:
        """Stdio 传输连接"""
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            
            # 解析命令
            parts = command.split()
            server_params = StdioServerParameters(
                command=parts[0],
                args=parts[1:] if len(parts) > 1 else [],
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    
                    for tool in tools.tools:
                        mcp_tool = MCPTool(
                            name=tool.name,
                            description=tool.description or "",
                            parameters=tool.inputSchema or {},
                            server_url=command
                        )
                        self.tools[tool.name] = mcp_tool
                    
                    self._cache_tools(command)
                    return True
        except Exception as e:
            self.logger.error(f"Stdio 连接失败: {e}")
            return False
    
    async def _connect_websocket(self, server_url: str) -> bool:
        """WebSocket 传输连接"""
        try:
            import websockets
            import json
            
            async with websockets.connect(server_url) as websocket:
                # 发送发现请求
                await websocket.send(json.dumps({"type": "discover"}))
                response = await websocket.recv()
                data = json.loads(response)
                
                for tool_data in data.get("tools", []):
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data.get("description", ""),
                        parameters=tool_data.get("parameters", {}),
                        server_url=server_url
                    )
                    self.tools[tool.name] = tool
                
                self._cache_tools(server_url)
                return True
        except Exception as e:
            self.logger.error(f"WebSocket 连接失败: {e}")
            return False
    
    def list_tools(self) -> List[MCPTool]:
        """列出所有已发现的工具"""
        return list(self.tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """获取指定工具"""
        return self.tools.get(tool_name)
    
    async def call_tool(self, tool_name: str, **kwargs) -> ToolCallResult:
        """
        调用 MCP 工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
            
        Returns:
            调用结果
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolCallResult(
                success=False,
                error=f"工具未找到: {tool_name}",
                tool_name=tool_name
            )
        
        start_time = datetime.now()
        
        try:
            # 根据服务器类型选择调用方式
            if tool.server_url.startswith("http"):
                result = await self._call_http(tool, kwargs)
            elif "stdio" in tool.server_url:
                result = await self._call_stdio(tool, kwargs)
            else:
                result = await self._call_websocket(tool, kwargs)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return ToolCallResult(
                success=True,
                result=result,
                duration_ms=duration,
                tool_name=tool_name
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolCallResult(
                success=False,
                error=str(e),
                duration_ms=duration,
                tool_name=tool_name
            )
    
    async def _call_http(self, tool: MCPTool, params: Dict[str, Any]) -> Any:
        """通过 HTTP 调用工具"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{tool.server_url}/tools/{tool.name}/call",
                json={"parameters": params}
            )
            
            if response.status_code == 200:
                return response.json().get("result")
            else:
                raise Exception(f"HTTP 错误: {response.status_code}")
    
    async def _call_stdio(self, tool: MCPTool, params: Dict[str, Any]) -> Any:
        """通过 Stdio 调用工具"""
        # 简化实现，实际需要管理会话
        raise NotImplementedError("Stdio 调用需要完整的会话管理")
    
    async def _call_websocket(self, tool: MCPTool, params: Dict[str, Any]) -> Any:
        """通过 WebSocket 调用工具"""
        import websockets
        import json
        
        async with websockets.connect(tool.server_url) as websocket:
            await websocket.send(json.dumps({
                "type": "call",
                "tool": tool.name,
                "parameters": params
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get("success"):
                return data.get("result")
            else:
                raise Exception(data.get("error", "调用失败"))
    
    def _cache_tools(self, server_url: str) -> None:
        """缓存工具列表"""
        cache_file = self.cache_dir / f"{hash(server_url)}.json"
        tools_data = [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "server_url": tool.server_url,
                "last_updated": tool.last_updated.isoformat()
            }
            for tool in self.tools.values()
            if tool.server_url == server_url
        ]
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(tools_data, f, ensure_ascii=False, indent=2)
    
    def load_cached_tools(self, server_url: str) -> bool:
        """从缓存加载工具"""
        cache_file = self.cache_dir / f"{hash(server_url)}.json"
        
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                tools_data = json.load(f)
            
            for tool_data in tools_data:
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    parameters=tool_data.get("parameters", {}),
                    server_url=tool_data.get("server_url", server_url),
                    last_updated=datetime.fromisoformat(tool_data.get("last_updated", datetime.now().isoformat()))
                )
                self.tools[tool.name] = tool
            
            return True
        except Exception as e:
            self.logger.error(f"加载缓存失败: {e}")
            return False
    
    def wrap_as_local_function(self, tool_name: str) -> Optional[Callable]:
        """
        将 MCP 工具包装为本地函数
        
        Args:
            tool_name: 工具名称
            
        Returns:
            可调用的函数
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        
        async def tool_function(**kwargs):
            result = await self.call_tool(tool_name, **kwargs)
            if result.success:
                return result.result
            else:
                raise Exception(result.error)
        
        # 设置函数签名
        tool_function.__name__ = tool_name
        tool_function.__doc__ = tool.description
        tool_function.__annotations__ = self._generate_annotations(tool.parameters)
        
        return tool_function
    
    def _generate_annotations(self, parameters: Dict[str, Any]) -> Dict[str, type]:
        """根据参数 schema 生成类型注解"""
        annotations = {}
        
        for param_name, param_info in parameters.items():
            param_type = param_info.get("type", "string")
            
            if param_type == "string":
                annotations[param_name] = str
            elif param_type == "integer":
                annotations[param_name] = int
            elif param_type == "number":
                annotations[param_name] = float
            elif param_type == "boolean":
                annotations[param_name] = bool
            elif param_type == "array":
                annotations[param_name] = list
            elif param_type == "object":
                annotations[param_name] = dict
            else:
                annotations[param_name] = Any
        
        return annotations
    
    def create_tool_wrapper(self, tool_name: str, validator: Optional[Callable] = None) -> Callable:
        """
        创建带验证的工具包装器
        
        Args:
            tool_name: 工具名称
            validator: 参数验证函数
            
        Returns:
            包装后的函数
        """
        original_func = self.wrap_as_local_function(tool_name)
        if not original_func:
            raise ValueError(f"工具未找到: {tool_name}")
        
        async def validated_wrapper(**kwargs):
            # 参数验证
            if validator:
                validation_result = validator(kwargs)
                if not validation_result.get("valid", True):
                    raise ValueError(f"参数验证失败: {validation_result.get('error')}")
            
            return await original_func(**kwargs)
        
        validated_wrapper.__name__ = f"validated_{tool_name}"
        validated_wrapper.__doc__ = f"经过验证的 {tool_name} 包装器"
        
        return validated_wrapper

# 使用示例
if __name__ == "__main__":
    async def main():
        # 创建适配器
        adapter = MCPAdapter()
        
        # 连接到 MCP 服务器（示例）
        # connected = await adapter.connect_server("http://localhost:8000")
        
        # 模拟已发现的工具
        adapter.tools["example_tool"] = MCPTool(
            name="example_tool",
            description="示例工具",
            parameters={"input": {"type": "string", "description": "输入参数"}},
            server_url="http://localhost:8000"
        )
        
        # 列出工具
        tools = adapter.list_tools()
        print(f"可用工具: {[t.name for t in tools]}")
        
        # 包装为本地函数
        local_func = adapter.wrap_as_local_function("example_tool")
        if local_func:
            print(f"本地函数: {local_func.__name__}")
            print(f"函数文档: {local_func.__doc__}")
    
    asyncio.run(main())
```

### 创建自定义 MCP 服务器

```python
"""
简单的 MCP 服务器示例
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent

# 创建服务器
server = Server("example-server")

@server.list_tools()
async def list_tools():
    """列出可用工具"""
    return [
        Tool(
            name="hello_world",
            description="返回问候语",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "要问候的名字"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="calculate",
            description="执行简单计算",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式"
                    }
                },
                "required": ["expression"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """调用工具"""
    if name == "hello_world":
        return [TextContent(type="text", text=f"Hello, {arguments['name']}!")]
    elif name == "calculate":
        try:
            result = eval(arguments["expression"])  # 注意：生产环境应使用安全解析
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            return [TextContent(type="text", text=f"计算错误: {e}")]
    else:
        raise ValueError(f"未知工具: {name}")

# 启动服务器
if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())
```

## 问题排查

### 问题 1：连接超时

**症状**：无法连接到 MCP 服务器。

**原因**：
- 服务器未启动
- 网络问题
- 防火墙阻止

**解决方案**：
```python
# 1. 检查服务器是否运行
import httpx
try:
    response = httpx.get("http://localhost:8000/health", timeout=5)
    print(f"服务器状态: {response.status_code}")
except httpx.ConnectError:
    print("服务器未运行")

# 2. 增加超时时间
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.get("http://localhost:8000/tools")

# 3. 检查防火墙设置
# Windows: netsh advfirewall firewall add rule name="MCP" dir=in action=allow protocol=TCP localport=8000
```

### 问题 2：工具未发现

**症状**：连接成功但工具列表为空。

**原因**：
- 服务器未正确注册工具
- 协议版本不兼容

**解决方案**：
```python
# 1. 检查服务器日志
# 2. 验证工具注册
@server.list_tools()
async def list_tools():
    tools = [
        Tool(
            name="my_tool",
            description="我的工具",
            inputSchema={...}
        )
    ]
    print(f"注册了 {len(tools)} 个工具")  # 调试输出
    return tools

# 3. 使用正确的协议版本
# pip install mcp>=1.0.0
```

### 问题 3：工具调用失败

**症状**：调用工具时返回错误。

**解决方案**：
```python
# 1. 验证参数
def validate_params(params: dict, schema: dict) -> bool:
    required = schema.get("required", [])
    for field in required:
        if field not in params:
            return False
    return True

# 2. 检查参数类型
def check_types(params: dict, schema: dict) -> bool:
    properties = schema.get("properties", {})
    for key, value in params.items():
        if key in properties:
            expected_type = properties[key].get("type")
            if expected_type == "string" and not isinstance(value, str):
                return False
            elif expected_type == "integer" and not isinstance(value, int):
                return False
    return True

# 3. 添加详细错误处理
try:
    result = await adapter.call_tool("tool_name", **params)
    if not result.success:
        print(f"调用失败: {result.error}")
except Exception as e:
    print(f"异常: {e}")
```

### 问题 4：性能问题

**症状**：工具调用响应慢。

**解决方案**：
```python
# 1. 使用缓存
adapter.load_cached_tools("http://localhost:8000")

# 2. 并发调用
async def batch_call(adapter: MCPAdapter, tool_name: str, params_list: list):
    tasks = [adapter.call_tool(tool_name, **params) for params in params_list]
    return await asyncio.gather(*tasks)

# 3. 连接池
import httpx
async with httpx.AsyncClient(
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=5
    )
) as client:
    # 使用连接池
    pass
```

## 依赖

| 依赖 | 版本 | 类型 | 说明 |
|------|------|------|------|
| Python | 3.8+ | 必需 | 运行环境 |
| mcp | ≥1.0.0 | 必需 | MCP 协议 SDK |
| httpx | ≥0.25.0 | 可选 | HTTP 传输支持 |
| websockets | ≥12.0 | 可选 | WebSocket 传输支持 |

## Agent 执行规范

### 核心约束
- **安全调用**：不执行任意代码，仅调用注册的工具
- **超时控制**：所有网络调用设置超时（默认 30 秒）
- **错误处理**：捕获所有异常，提供清晰的错误信息
- **日志记录**：记录所有工具调用和结果

### 最佳实践
- 优先使用 HTTP 传输（最稳定）
- 缓存工具列表以减少发现开销
- 为工具调用添加重试机制（指数退避）
- 定期刷新工具列表以获取最新状态
- 在生产环境中禁用 `eval()` 等危险函数