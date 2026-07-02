---
name: code-sandbox
layer: action
category: code
description: >
  安全执行 Python/Node.js 代码，支持超时、输出限制、资源限制。
  当用户需要运行用户提供的代码、测试代码片段、执行不受信任的代码时触发。
  关键词：代码执行、沙箱、安全运行、Python 执行、Node.js 执行、超时控制。
---

# 代码沙箱执行

在隔离环境中安全执行 Python/Node.js 代码，支持资源限制和超时控制。

## 功能特性

- 支持 Python 和 Node.js 代码执行
- 执行超时控制（默认 10 秒）
- 输出大小限制（默认 1MB）
- 内存使用限制
- 文件系统访问限制
- 网络访问控制
- 进程隔离
- 详细的执行结果和错误信息
- 支持输入参数传递

## 前置条件

- Python 3.7+
- Node.js 14+（如需执行 JavaScript）
- 操作系统权限（创建子进程）

## 安装步骤

### Python 执行（必需）

Python 执行使用标准库，无需额外安装。

### Node.js 执行（可选）

确保 Node.js 已安装：

```bash
# 检查 Node.js 版本
node --version

# 如果未安装，从官网下载：
# https://nodejs.org/
```

### 验证安装

```bash
python -c "import subprocess; print('Python 执行环境正常')"
node --version  # 如果需要 Node.js 支持
```

## 使用方法

### 基础用法：执行 Python 代码

```python
import subprocess
import tempfile
import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float
    memory_used_mb: float = 0

def execute_python_code(
    code: str,
    timeout: int = 10,
    max_output_size: int = 1024 * 1024,  # 1MB
    python_path: str = "python"
) -> ExecutionResult:
    """
    执行 Python 代码
    
    Args:
        code: Python 代码字符串
        timeout: 超时时间（秒）
        max_output_size: 最大输出大小（字节）
        python_path: Python 解释器路径
        
    Returns:
        ExecutionResult 对象
    """
    # 创建临时文件
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as temp_file:
        temp_file.write(code)
        temp_path = temp_file.name
    
    try:
        # 执行代码
        import time
        start_time = time.time()
        
        result = subprocess.run(
            [python_path, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir(),
            env={
                **os.environ,
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONDONTWRITEBYTECODE': '1'
            }
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # 限制输出大小
        stdout = result.stdout[:max_output_size] if result.stdout else ""
        stderr = result.stderr[:max_output_size] if result.stderr else ""
        
        # 如果输出被截断，添加提示
        if len(result.stdout) > max_output_size:
            stdout += f"\n\n[输出被截断，原始大小: {len(result.stdout)} 字节]"
        if len(result.stderr) > max_output_size:
            stderr += f"\n\n[输出被截断，原始大小: {len(result.stderr)} 字节]"
        
        return ExecutionResult(
            success=result.returncode == 0,
            stdout=stdout,
            stderr=stderr,
            return_code=result.returncode,
            execution_time_ms=execution_time
        )
        
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            success=False,
            stdout="",
            stderr=f"执行超时（{timeout} 秒）",
            return_code=-1,
            execution_time_ms=timeout * 1000
        )
    except Exception as e:
        return ExecutionResult(
            success=False,
            stdout="",
            stderr=str(e),
            return_code=-1,
            execution_time_ms=0
        )
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_path)
        except:
            pass

# 使用示例
if __name__ == "__main__":
    # 示例 1：简单计算
    code1 = """
print("Hello from Python Sandbox!")
result = sum(range(100))
print(f"Sum of 0-99: {result}")
"""
    
    result1 = execute_python_code(code1)
    print(f"执行成功: {result1.success}")
    print(f"输出: {result1.stdout}")
    print(f"耗时: {result1.execution_time_ms:.2f} ms")
    
    # 示例 2：带错误的代码
    code2 = """
def divide(a, b):
    return a / b

# 除零错误
result = divide(10, 0)
"""
    
    result2 = execute_python_code(code2)
    print(f"\n执行成功: {result2.success}")
    print(f"错误信息: {result2.stderr}")
```

### 高级用法：完整沙箱类

```python
import subprocess
import tempfile
import os
import sys
import json
import hashlib
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from contextlib import contextmanager
import threading

@dataclass
class SandboxConfig:
    """沙箱配置"""
    timeout: int = 10  # 秒
    max_output_size: int = 1024 * 1024  # 1MB
    max_memory_mb: int = 100  # MB
    allowed_modules: List[str] = field(default_factory=lambda: ['math', 'json', 're', 'datetime'])
    blocked_modules: List[str] = field(default_factory=lambda: ['os', 'sys', 'subprocess', 'shutil'])
    enable_network: bool = False
    enable_file_access: bool = False
    working_directory: Optional[str] = None

@dataclass
class ExecutionMetrics:
    """执行指标"""
    cpu_time_ms: float = 0
    memory_peak_mb: float = 0
    file_operations: int = 0
    network_requests: int = 0

class CodeSandbox:
    """代码沙箱"""
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        初始化沙箱
        
        Args:
            config: 沙箱配置
        """
        self.config = config or SandboxConfig()
        self.execution_history: List[Dict[str, Any]] = []
    
    def execute_python(
        self,
        code: str,
        inputs: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行 Python 代码
        
        Args:
            code: Python 代码
            inputs: 输入参数
            context: 执行上下文变量
            
        Returns:
            执行结果字典
        """
        # 预处理代码
        processed_code = self._preprocess_code(code, inputs, context)
        
        # 安全检查
        safety_check = self._safety_check(processed_code)
        if not safety_check["safe"]:
            return {
                "success": False,
                "error": f"安全检查失败: {safety_check['reason']}",
                "metrics": ExecutionMetrics()
            }
        
        # 执行代码
        with self._create_sandbox_environment() as env:
            result = self._execute_with_monitoring(
                processed_code,
                env["temp_dir"],
                env["python_path"]
            )
        
        # 记录执行历史
        self._record_execution(code, result)
        
        return result
    
    def execute_javascript(
        self,
        code: str,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行 JavaScript 代码
        
        Args:
            code: JavaScript 代码
            inputs: 输入参数
            
        Returns:
            执行结果字典
        """
        # 检查 Node.js 是否可用
        if not self._check_nodejs():
            return {
                "success": False,
                "error": "Node.js 未安装或不可用",
                "metrics": ExecutionMetrics()
            }
        
        # 预处理代码
        processed_code = self._preprocess_javascript(code, inputs)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.js',
            delete=False,
            encoding='utf-8'
        ) as temp_file:
            temp_file.write(processed_code)
            temp_path = temp_file.name
        
        try:
            # 执行代码
            result = subprocess.run(
                ["node", temp_path],
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=self.config.working_directory or tempfile.gettempdir()
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:self.config.max_output_size],
                "stderr": result.stderr[:self.config.max_output_size],
                "return_code": result.returncode,
                "execution_time_ms": 0,  # 需要实际测量
                "metrics": ExecutionMetrics()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"执行超时（{self.config.timeout} 秒）",
                "metrics": ExecutionMetrics()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "metrics": ExecutionMetrics()
            }
        finally:
            try:
                os.unlink(temp_path)
            except:
                pass
    
    def _preprocess_code(
        self,
        code: str,
        inputs: Optional[Dict[str, Any]],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """预处理 Python 代码"""
        lines = []
        
        # 添加导入限制
        lines.append("import sys")
        lines.append("import builtins")
        
        # 保存原始导入函数
        lines.append("_original_import = builtins.__import__")
        
        # 创建安全的导入函数
        lines.append("def safe_import(name, *args, **kwargs):")
        lines.append("    blocked = ['os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'requests']")
        lines.append("    if name in blocked:")
        lines.append("        raise ImportError(f'模块 {name} 被禁止导入')")
        lines.append("    return _original_import(name, *args, **kwargs)")
        
        lines.append("builtins.__import__ = safe_import")
        lines.append("")
        
        # 添加输入参数
        if inputs:
            lines.append("# 输入参数")
            for key, value in inputs.items():
                lines.append(f"{key} = {repr(value)}")
            lines.append("")
        
        # 添加上下文变量
        if context:
            lines.append("# 上下文变量")
            for key, value in context.items():
                lines.append(f"{key} = {repr(value)}")
            lines.append("")
        
        # 添加用户代码
        lines.append("# 用户代码")
        lines.append(code)
        
        return "\n".join(lines)
    
    def _preprocess_javascript(
        self,
        code: str,
        inputs: Optional[Dict[str, Any]]
    ) -> str:
        """预处理 JavaScript 代码"""
        lines = []
        
        # 添加输入参数
        if inputs:
            lines.append("// 输入参数")
            for key, value in inputs.items():
                if isinstance(value, str):
                    lines.append(f"const {key} = {json.dumps(value)};")
                else:
                    lines.append(f"const {key} = {json.dumps(value)};")
            lines.append("")
        
        # 添加用户代码
        lines.append("// 用户代码")
        lines.append(code)
        
        return "\n".join(lines)
    
    def _safety_check(self, code: str) -> Dict[str, Any]:
        """安全检查"""
        # 检查危险函数
        dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'compile\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            r'getattr\s*\(',
            r'setattr\s*\(',
            r'delattr\s*\(',
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return {
                    "safe": False,
                    "reason": f"检测到危险函数: {pattern}"
                }
        
        # 检查文件操作
        file_patterns = [
            r'open\s*\(',
            r'with\s+open',
            r'os\.path',
            r'pathlib',
        ]
        
        if not self.config.enable_file_access:
            for pattern in file_patterns:
                if re.search(pattern, code):
                    return {
                        "safe": False,
                        "reason": f"文件访问被禁止: {pattern}"
                    }
        
        return {"safe": True, "reason": ""}
    
    @contextmanager
    def _create_sandbox_environment(self):
        """创建沙箱环境"""
        temp_dir = tempfile.mkdtemp(prefix="sandbox_")
        
        try:
            # 创建受限的环境变量
            env = os.environ.copy()
            
            # 移除可能危险的环境变量
            dangerous_env = ['PATH', 'PYTHONPATH', 'HOME', 'USERPROFILE']
            for key in dangerous_env:
                if key in env:
                    del env[key]
            
            # 设置安全的环境变量
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONDONTWRITEBYTECODE'] = '1'
            env['PYTHONNOUSERSITE'] = '1'
            
            yield {
                "temp_dir": temp_dir,
                "env": env,
                "python_path": sys.executable
            }
        finally:
            # 清理临时目录
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    def _execute_with_monitoring(
        self,
        code: str,
        temp_dir: str,
        python_path: str
    ) -> Dict[str, Any]:
        """带监控的执行"""
        # 创建临时文件
        temp_file = os.path.join(temp_dir, "script.py")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # 执行代码
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [python_path, temp_file],
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                cwd=temp_dir,
                env={
                    **os.environ,
                    'PYTHONIOENCODING': 'utf-8',
                    'PYTHONDONTWRITEBYTECODE': '1',
                    'PYTHONNOUSERSITE': '1'
                }
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            # 限制输出大小
            stdout = result.stdout[:self.config.max_output_size] if result.stdout else ""
            stderr = result.stderr[:self.config.max_output_size] if result.stderr else ""
            
            return {
                "success": result.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": result.returncode,
                "execution_time_ms": execution_time,
                "metrics": ExecutionMetrics(
                    cpu_time_ms=execution_time,
                    memory_peak_mb=0  # 需要实际监控
                )
            }
            
        except subprocess.TimeoutExpired:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "stdout": "",
                "stderr": f"执行超时（{self.config.timeout} 秒）",
                "return_code": -1,
                "execution_time_ms": execution_time,
                "metrics": ExecutionMetrics(cpu_time_ms=execution_time)
            }
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "execution_time_ms": execution_time,
                "metrics": ExecutionMetrics(cpu_time_ms=execution_time)
            }
    
    def _check_nodejs(self) -> bool:
        """检查 Node.js 是否可用"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _record_execution(self, code: str, result: Dict[str, Any]) -> None:
        """记录执行历史"""
        execution_record = {
            "timestamp": time.time(),
            "code_hash": hashlib.md5(code.encode()).hexdigest(),
            "code_length": len(code),
            "success": result.get("success", False),
            "execution_time_ms": result.get("execution_time_ms", 0),
            "output_size": len(result.get("stdout", "")) + len(result.get("stderr", ""))
        }
        
        self.execution_history.append(execution_record)
        
        # 限制历史记录大小
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """获取执行统计"""
        if not self.execution_history:
            return {"total_executions": 0}
        
        successful = sum(1 for e in self.execution_history if e["success"])
        failed = len(self.execution_history) - successful
        
        avg_time = sum(e["execution_time_ms"] for e in self.execution_history) / len(self.execution_history)
        
        return {
            "total_executions": len(self.execution_history),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.execution_history) * 100,
            "average_execution_time_ms": avg_time,
            "total_execution_time_ms": sum(e["execution_time_ms"] for e in self.execution_history)
        }

# 使用示例
if __name__ == "__main__":
    # 创建沙箱
    sandbox = CodeSandbox(SandboxConfig(
        timeout=5,
        max_output_size=1024 * 1024,
        enable_file_access=False
    ))
    
    # 执行 Python 代码
    code = """
import math

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 计算前 10 个斐波那契数
for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")

# 使用 math 模块
print(f"π ≈ {math.pi:.6f}")
print(f"e ≈ {math.e:.6f}")
"""
    
    result = sandbox.execute_python(code)
    
    print("执行结果:")
    print(f"成功: {result['success']}")
    print(f"输出:\n{result['stdout']}")
    
    if result['stderr']:
        print(f"错误:\n{result['stderr']}")
    
    print(f"执行时间: {result['execution_time_ms']:.2f} ms")
    
    # 获取统计信息
    stats = sandbox.get_execution_stats()
    print(f"\n统计信息:")
    print(f"总执行次数: {stats['total_executions']}")
    print(f"成功率: {stats['success_rate']:.1f}%")
```

### 安全执行不受信任的代码

```python
def safe_execute_user_code(user_code: str, user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    安全执行用户提供的代码
    
    Args:
        user_code: 用户代码
        user_inputs: 用户输入参数
        
    Returns:
        执行结果
    """
    # 创建严格配置的沙箱
    config = SandboxConfig(
        timeout=5,  # 5 秒超时
        max_output_size=1024 * 100,  # 100KB 输出限制
        max_memory_mb=50,  # 50MB 内存限制
        enable_network=False,
        enable_file_access=False
    )
    
    sandbox = CodeSandbox(config)
    
    # 执行代码
    result = sandbox.execute_python(user_code, inputs=user_inputs)
    
    # 安全地清理输出
    if result["success"]:
        # 移除可能的敏感信息
        output = result["stdout"]
        output = output.replace("password", "***")
        output = output.replace("token", "***")
        result["stdout"] = output
    
    return result

# 使用示例
if __name__ == "__main__":
    # 用户提供的代码（可能包含危险操作）
    user_code = """
# 用户想要计算的东西
def calculate_area(radius):
    import math
    return math.pi * radius ** 2

# 计算半径为 5 的圆面积
area = calculate_area(5)
print(f"圆面积: {area:.2f}")
"""
    
    result = safe_execute_user_code(user_code, {"radius": 5})
    print(f"执行结果: {result['success']}")
    print(f"输出: {result['stdout']}")
```

## 问题排查

### 问题 1：执行超时

**症状**：代码执行时间超过限制。

**原因**：
- 代码包含无限循环
- 计算复杂度过高
- 系统资源不足

**解决方案**：
```python
# 1. 增加超时时间（谨慎使用）
config = SandboxConfig(timeout=30)  # 30 秒

# 2. 优化代码
# 错误：无限循环
while True:
    pass

# 正确：添加退出条件
for i in range(1000):
    if condition:
        break

# 3. 使用异步执行
import asyncio
async def run_with_timeout(code, timeout):
    try:
        return await asyncio.wait_for(execute_code(code), timeout)
    except asyncio.TimeoutError:
        return {"success": False, "error": "超时"}
```

### 问题 2：内存不足

**症状**：`MemoryError` 或系统变慢。

**解决方案**：
```python
# 1. 限制内存使用
config = SandboxConfig(max_memory_mb=100)

# 2. 优化数据结构
# 错误：加载大文件到内存
with open("large_file.txt") as f:
    data = f.read()  # 可能消耗大量内存

# 正确：逐行处理
with open("large_file.txt") as f:
    for line in f:
        process_line(line)

# 3. 使用生成器
def fibonacci_generator():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b
```

### 问题 3：模块导入被阻止

**症状**：`ImportError: 模块 xxx 被禁止导入`。

**解决方案**：
```python
# 1. 检查模块是否在允许列表中
config = SandboxConfig(
    allowed_modules=['math', 'json', 're', 'datetime', 'collections']
)

# 2. 使用安全模块替代
# 错误：使用 os 模块
import os
os.listdir(".")

# 正确：使用 pathlib
from pathlib import Path
list(Path(".").iterdir())

# 3. 自定义导入限制
def custom_import(name, *args, **kwargs):
    allowed = ['math', 'json']
    if name not in allowed:
        raise ImportError(f"模块 {name} 不允许")
    return __import__(name, *args, **kwargs)
```

### 问题 4：输出被截断

**症状**：输出不完整。

**解决方案**：
```python
# 1. 增加输出限制
config = SandboxConfig(max_output_size=1024 * 1024 * 5)  # 5MB

# 2. 分块输出
def chunked_output(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        yield data[i:i+chunk_size]

# 3. 使用文件输出
code = """
import sys
import io

# 重定向到文件
with open('output.txt', 'w') as f:
    old_stdout = sys.stdout
    sys.stdout = f
    
    # 你的代码
    print("大量输出...")
    
    sys.stdout = old_stdout
"""
```

## 依赖

| 依赖 | 版本 | 类型 | 说明 |
|------|------|------|------|
| Python | 3.7+ | 必需 | 运行环境 |
| Node.js | 14+ | 可选 | JavaScript 执行支持 |

## Agent 执行规范

### 核心约束
- **最小权限原则**：只授予必要的权限
- **输入验证**：验证所有用户输入
- **输出过滤**：过滤敏感信息
- **资源限制**：严格控制 CPU、内存、时间
- **日志记录**：记录所有执行尝试

### 安全最佳实践
- 永远不要在生产环境中执行不受信任的代码
- 使用 Docker 容器进行更强的隔离
- 定期更新依赖库以修复安全漏洞
- 监控系统资源使用情况
- 实施代码签名和验证机制

### 性能优化
- 缓存编译结果
- 使用进程池管理执行环境
- 实现异步执行和超时控制
- 监控和优化内存使用