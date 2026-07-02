---
name: 代码执行器
layer: action
category: code
description: >
  执行 Python/Node.js 代码，支持超时和输出限制。
  当用户需要运行代码片段、测试代码、执行脚本时触发。
  关键词：代码执行、Python 执行、Node.js 执行、超时控制。
---

# 代码执行器

执行 Python/Node.js 代码，支持超时和输出限制。

> **⚠️ 安全声明**：本工具仅提供超时和输出限制，**不提供安全隔离**。
> 执行不受信任的代码必须使用 Docker 容器（见下方）。

## 能力概览

| 能力 | 说明 |
|------|------|
| Python 执行 | 执行 Python 代码 |
| Node.js 执行 | 执行 JavaScript 代码 |
| 超时控制 | 防止无限循环 |
| 输出限制 | 截断过长输出 |
| 执行记录 | 记录执行历史 |

## 前置条件

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.7+ | 执行 Python 代码 |
| Node.js | 14+ | 执行 JavaScript 代码（可选） |

## 验证安装

```bash
python --version
node --version  # 可选
```

---

## 安全警告

**本工具不能防止以下攻击：**

```python
# 这些都能绕过黑名单检查
getattr(__builtins__, 'eval')('import os; os.system("rm -rf /")')
import importlib; importlib.import_module('os')
__builtins__.__import__('os')
compile('import os', '<string>', 'exec')
```

**如果需要执行不受信任的代码，必须使用 Docker：**

```bash
docker run --rm --network=none --memory=100m --read-only \
  -v /tmp/code:/code python:3.12-slim python /code/script.py
```

---

## 使用方法

### 基础用法

```python
import subprocess
import tempfile
import os
import time
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float

def execute_python(
    code: str,
    timeout: int = 10,
    max_output_size: int = 1024 * 1024,
    python_path: str = "python"
) -> ExecutionResult:
    """
    执行 Python 代码
    
    Args:
        code: Python 代码
        timeout: 超时时间（秒）
        max_output_size: 最大输出大小（字节）
        python_path: Python 解释器路径
    
    Returns:
        ExecutionResult 对象
    """
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False, encoding='utf-8'
    ) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        start = time.time()
        
        result = subprocess.run(
            [python_path, temp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tempfile.gettempdir()
        )
        
        elapsed = (time.time() - start) * 1000
        
        stdout = result.stdout[:max_output_size] if result.stdout else ""
        stderr = result.stderr[:max_output_size] if result.stderr else ""
        
        if result.stdout and len(result.stdout) > max_output_size:
            stdout += f"\n[输出被截断，原始大小: {len(result.stdout)} 字节]"
        
        return ExecutionResult(
            success=result.returncode == 0,
            stdout=stdout,
            stderr=stderr,
            return_code=result.returncode,
            execution_time_ms=elapsed
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
            stderr=str(e) if isinstance(e, Exception) else String(e),
            return_code=-1,
            execution_time_ms=0
        )
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

def execute_javascript(
    code: str,
    timeout: int = 10,
    max_output_size: int = 1024 * 1024
) -> ExecutionResult:
    """执行 JavaScript 代码"""
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.js', delete=False, encoding='utf-8'
    ) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        start = time.time()
        
        result = subprocess.run(
            ["node", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        elapsed = (time.time() - start) * 1000
        
        return ExecutionResult(
            success=result.returncode == 0,
            stdout=result.stdout[:max_output_size] if result.stdout else "",
            stderr=result.stderr[:max_output_size] if result.stderr else "",
            return_code=result.returncode,
            execution_time_ms=elapsed
        )
        
    except FileNotFoundError:
        return ExecutionResult(
            success=False,
            stdout="",
            stderr="Node.js 未安装",
            return_code=-1,
            execution_time_ms=0
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
            stderr=str(e) if isinstance(e, Exception) else String(e),
            return_code=-1,
            execution_time_ms=0
        )
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass
```

### 使用示例

```python
# 执行 Python
result = execute_python('print("Hello!")')
print(result.stdout)  # Hello!

# 带超时
result = execute_python('import time; time.sleep(20)', timeout=5)
print(result.success)  # False
print(result.stderr)   # 执行超时（5 秒）

# 执行 JavaScript
result = execute_javascript('console.log("Hello from Node!")')
print(result.stdout)  # Hello from Node!
```

---

## 安全执行（Docker）

如果需要执行不受信任的代码，使用 Docker 隔离：

```python
import subprocess
import tempfile
import os

def execute_in_docker(
    code: str,
    language: str = "python",
    timeout: int = 10,
    memory_limit: str = "100m"
) -> ExecutionResult:
    """
    在 Docker 容器中安全执行代码
    
    Args:
        code: 代码
        language: "python" 或 "node"
        timeout: 超时时间
        memory_limit: 内存限制
    
    Returns:
        ExecutionResult 对象
    """
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入代码文件
        ext = ".py" if language == "python" else ".js"
        code_file = os.path.join(tmpdir, f"code{ext}")
        with open(code_file, 'w') as f:
            f.write(code)
        
        # 选择镜像
        image = "python:3.12-slim" if language == "python" else "node:20-slim"
        cmd = "python" if language == "python" else "node"
        
        # Docker 命令
        docker_cmd = [
            "docker", "run", "--rm",
            "--network=none",           # 禁用网络
            f"--memory={memory_limit}", # 限制内存
            "--read-only",              # 只读文件系统
            "-v", f"{tmpdir}:/code:ro", # 挂载代码目录（只读）
            image, cmd, f"/code/code{ext}"
        ]
        
        try:
            start = time.time()
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            elapsed = (time.time() - start) * 1000
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time_ms=elapsed
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
                stderr=str(e) if isinstance(e, Exception) else String(e),
                return_code=-1,
                execution_time_ms=0
            )

# 安全执行用户代码
result = execute_in_docker(
    user_code,
    language="python",
    timeout=10,
    memory_limit="100m"
)
```

### Docker 安全特性

| 特性 | 说明 |
|------|------|
| `--network=none` | 禁用网络访问 |
| `--memory=100m` | 限制内存 100MB |
| `--read-only` | 只读文件系统 |
| `-v ... :ro` | 代码目录只读挂载 |
| `--rm` | 容器执行后自动删除 |

---

## 目录结构

```
code-executor/
├── SKILL.md          # 本文件
└── scripts/
    └── executor.py   # 可选：独立执行脚本
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 执行超时 | 代码有无限循环 | 检查代码逻辑，增加 timeout |
| Node.js 未安装 | 系统没有 Node.js | 安装 Node.js 或只用 Python |
| Docker 执行失败 | Docker 未运行 | 启动 Docker Desktop |
| 输出被截断 | 输出超过限制 | 增加 max_output_size |

---

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.7+ | 执行 Python 代码 |
| Node.js | 14+ | 执行 JavaScript（可选） |
| Docker | 20+ | 安全执行（可选） |
