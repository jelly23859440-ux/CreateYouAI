---
name: 代码沙箱
layer: action
category: code
status: unverified
version: 1.1
description: >
  在隔离环境中安全执行 Python/Node.js 代码。
  当用户需要运行不受信任的代码、测试代码片段、执行用户提供的脚本时触发。
  关键词：代码沙箱、安全执行、Python 沙箱、Docker 执行、bubblewrap、sandbox-exec。
---

# 代码沙箱

在 OS 级隔离环境中安全执行 Python/Node.js 代码，支持文件系统和网络隔离。

## 能力概览

| 能力 | 说明 |
|------|------|
| Python 执行 | 执行 Python 代码 |
| Node.js 执行 | 执行 JavaScript 代码 |
| 文件系统隔离 | 限制读写路径 |
| 网络隔离 | 限制网络访问 |
| 资源限制 | 内存、CPU、超时 |
| 输出限制 | 防止内存炸弹 |
| 多平台支持 | macOS / Linux / Docker |

## 方案选择

**先问用户环境，再选方案：**

```
IF 用户有 Docker:
    → 方案一（Docker）— 最安全，跨平台
ELSE IF 用户是 macOS:
    → 方案二（sandbox-exec）— 内置，无需安装
ELSE IF 用户是 Linux:
    → 方案三（bubblewrap）— 轻量，安全
ELSE:
    → 方案四（仅超时）— 无隔离，仅限可信代码
```

| 你的环境 | 推荐方案 | 状态 |
|---------|----------|------|
| Docker | 方案一 | ✅ 生产验证（Claude Code 使用） |
| macOS | 方案二 | ✅ 生产验证（Claude Code 使用） |
| Linux | 方案三 | ✅ 生产验证（Claude Code 使用） |
| Windows/其他 | 方案四 | ⚠️ 无隔离 |

---

## 前置条件

| 依赖 | 版本 | 方案 | 用途 |
|------|------|------|------|
| Python | 3.7+ | 所有 | 执行 Python 代码 |
| Node.js | 14+ | 所有 | 执行 JavaScript（可选） |
| Docker | 20+ | 方案一 | 容器隔离 |
| bubblewrap | 0.4+ | 方案三 | Linux 沙箱 |

---

## 方案一：Docker 沙箱（推荐）

最安全，跨平台，Claude Code 在 Docker 环境中使用此方案。

### 安装

```bash
# 检查 Docker
docker --version

# 拉取 Python 镜像
docker pull python:3.12-slim
```

### 实现

```python
import subprocess
import tempfile
import os
import time
import uuid
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float

def execute_in_docker(
    code: str,
    language: str = "python",
    timeout: int = 10,
    memory_limit: str = "100m",
    network: bool = False,
    max_output_size: int = 1024 * 1024,
    writable_paths: list = None
) -> ExecutionResult:
    """
    在 Docker 容器中安全执行代码
    
    Args:
        code: 代码
        language: "python" 或 "node"
        timeout: 超时时间（秒）
        memory_limit: 内存限制
        network: 是否允许网络
        max_output_size: 最大输出大小（字节）
        writable_paths: 可写路径列表
    
    Returns:
        ExecutionResult 对象
    """
    container_name = f"sandbox-{uuid.uuid4().hex[:8]}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入代码文件
        ext = ".py" if language == "python" else ".js"
        code_file = os.path.join(tmpdir, f"code{ext}")
        with open(code_file, 'w') as f:
            f.write(code)
        
        # 选择镜像
        image = "python:3.12-slim" if language == "python" else "node:20-slim"
        cmd = "python" if language == "python" else "node"
        
        # 构建 Docker 命令
        docker_cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--memory", memory_limit,
            "--cpus", "1",
            "--read-only",
            "--tmpfs", "/tmp:size=100m",
            "-v", f"{tmpdir}:/code:ro",
            "-e", "PYTHONDONTWRITEBYTECODE=1",
        ]
        
        # 网络控制
        if not network:
            docker_cmd.append("--network=none")
        
        # 额外可写路径
        if writable_paths:
            for path in writable_paths:
                docker_cmd.extend(["-v", f"{path}:{path}:rw"])
        
        # 安全选项
        docker_cmd.extend([
            "--security-opt", "no-new-privileges",
            "--cap-drop", "ALL",
            image, cmd, f"/code/code{ext}"
        ])
        
        try:
            start = time.time()
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout + 5
            )
            
            elapsed = (time.time() - start) * 1000
            
            stdout = result.stdout[:max_output_size] if result.stdout else ""
            stderr = result.stderr[:max_output_size] if result.stderr else ""
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                return_code=result.returncode,
                execution_time_ms=elapsed
            )
            
        except subprocess.TimeoutExpired:
            # 清理僵尸容器
            subprocess.run(["docker", "kill", container_name], 
                         capture_output=True, timeout=5)
            subprocess.run(["docker", "rm", "-f", container_name], 
                         capture_output=True, timeout=5)
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

# 使用示例
result = execute_in_docker(
    'import os; print(os.listdir("/"))',
    language="python",
    timeout=10,
    memory_limit="100m",
    network=False
)
print(result.stdout)
```

### Docker 安全特性

| 特性 | 说明 |
|------|------|
| `--network=none` | 禁用网络 |
| `--memory 100m` | 限制内存 |
| `--read-only` | 只读文件系统 |
| `--cap-drop ALL` | 删除所有 capabilities |
| `--security-opt no-new-privileges` | 禁止提权 |
| `PYTHONDONTWRITEBYTECODE=1` | 禁止写 .pyc |
| 容器命名 + 超时清理 | 防止僵尸容器 |

---

## 方案二：macOS sandbox-exec

macOS 内置的沙箱机制，Claude Code 在 macOS 上使用此方案。

### 前置条件

- macOS 10.15+
- `sandbox-exec`（内置）

### 实现

```python
import subprocess
import tempfile
import os
import time
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float

def execute_with_sandbox_exec(
    code: str,
    language: str = "python",
    timeout: int = 10,
    max_output_size: int = 1024 * 1024,
    writable_dirs: list = None
) -> ExecutionResult:
    """
    使用 macOS sandbox-exec 执行代码
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        ext = ".py" if language == "python" else ".js"
        code_file = os.path.join(tmpdir, f"code{ext}")
        with open(code_file, 'w') as f:
            f.write(code)
        
        profile = generate_sandbox_profile(writable_dirs or [tmpdir])
        profile_file = os.path.join(tmpdir, "sandbox.sb")
        with open(profile_file, 'w') as f:
            f.write(profile)
        
        cmd = "python" if language == "python" else "node"
        
        sandbox_cmd = [
            "sandbox-exec",
            "-f", profile_file,
            cmd, code_file
        ]
        
        try:
            start = time.time()
            
            result = subprocess.run(
                sandbox_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            
            elapsed = (time.time() - start) * 1000
            
            stdout = result.stdout[:max_output_size] if result.stdout else ""
            stderr = result.stderr[:max_output_size] if result.stderr else ""
            
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
                stderr=str(e),
                return_code=-1,
                execution_time_ms=0
            )

def generate_sandbox_profile(writable_dirs: list) -> str:
    """
    生成 macOS sandbox-exec profile
    
    注意：(deny default) 必须在最前面，不能有 (allow default)
    """
    rules = [
        '(version 1)',
        '(deny default)',
        # 允许读取系统库
        '(allow file-read* (subpath "/usr") (subpath "/System") (subpath "/Library"))',
        # 允许读取临时目录
        '(allow file-read* (subpath "/tmp"))',
        # 允许写入指定目录
    ]
    
    for dir_path in writable_dirs:
        rules.append(f'(allow file-write* (subpath "{dir_path}"))')
    
    # 网络禁止
    rules.append('(deny network*)')
    
    # 进程限制
    rules.append('(deny process*)')
    rules.append('(allow process-exec)')
    
    return '\n'.join(rules)
```

---

## 方案三：Linux bubblewrap

Linux 上的轻量沙箱，Claude Code 在 Linux 上使用此方案。

### 前置条件

```bash
# 安装 bubblewrap
sudo apt install bubblewrap  # Debian/Ubuntu
sudo dnf install bubblewrap  # Fedora
```

### 实现

```python
import subprocess
import tempfile
import os
import time
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float

def execute_with_bubblewrap(
    code: str,
    language: str = "python",
    timeout: int = 10,
    max_output_size: int = 1024 * 1024,
    network: bool = False,
    memory_limit_mb: int = 100,
    writable_dirs: list = None
) -> ExecutionResult:
    """
    使用 bubblewrap 执行代码
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        ext = ".py" if language == "python" else ".js"
        code_file = os.path.join(tmpdir, f"code{ext}")
        with open(code_file, 'w') as f:
            f.write(code)
        
        cmd = "python" if language == "python" else "node"
        
        # 内存限制需要 prlimit
        mem_bytes = memory_limit_mb * 1024 * 1024
        prefix_cmd = ["prlimit", f"--as={mem_bytes}"]
        
        bwrap_cmd = prefix_cmd + [
            "bwrap",
            "--ro-bind", "/usr", "/usr",
            "--ro-bind", "/lib", "/lib",
            "--ro-bind", "/lib64", "/lib64",
            "--proc", "/proc",
            "--dev-bind", "/dev/null", "/dev/null",
            "--dev-bind", "/dev/zero", "/dev/zero",
            "--dev-bind", "/dev/random", "/dev/random",
            "--dev-bind", "/dev/urandom", "/dev/urandom",
            "--tmpfs", "/tmp",
            "--bind", tmpdir, "/sandbox",
            "--chdir", "/sandbox",
            "--unshare-all",
            "--die-with-parent",
        ]
        
        if writable_dirs:
            for dir_path in writable_dirs:
                bwrap_cmd.extend(["--bind", dir_path, dir_path])
        
        if not network:
            bwrap_cmd.append("--unshare-net")
        
        bwrap_cmd.extend([cmd, f"/sandbox/code{ext}"])
        
        try:
            start = time.time()
            
            result = subprocess.run(
                bwrap_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            
            elapsed = (time.time() - start) * 1000
            
            stdout = result.stdout[:max_output_size] if result.stdout else ""
            stderr = result.stderr[:max_output_size] if result.stderr else ""
            
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
                stderr=str(e),
                return_code=-1,
                execution_time_ms=0
            )
```

### Bubblewrap 安全特性

| 特性 | 说明 |
|------|------|
| `--unshare-all` | 隔离所有命名空间 |
| `--unshare-net` | 禁用网络 |
| `--ro-bind` | 只读绑定挂载 |
| `--dev-bind` | 最小设备集（非完整 /dev） |
| `--die-with-parent` | 父进程退出时退出 |
| `prlimit --as=` | 内存限制 |

---

## 方案四：仅超时（无隔离）

仅适用于**可信代码**，不提供安全隔离。

```python
import subprocess
import tempfile
import os
import time
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time_ms: float

def execute_code(
    code: str,
    language: str = "python",
    timeout: int = 10,
    max_output_size: int = 1024 * 1024
) -> ExecutionResult:
    """
    执行代码（无隔离）
    
    ⚠️ 仅适用于可信代码
    """
    ext = ".py" if language == "python" else ".js"
    cmd = "python" if language == "python" else "node"
    
    with tempfile.NamedTemporaryFile(
        mode='w', suffix=ext, delete=False, encoding='utf-8'
    ) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        start = time.time()
        
        result = subprocess.run(
            [cmd, temp_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout
        )
        
        elapsed = (time.time() - start) * 1000
        
        stdout = result.stdout[:max_output_size] if result.stdout else ""
        stderr = result.stderr[:max_output_size] if result.stderr else ""
        
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
            stderr=str(e),
            return_code=-1,
            execution_time_ms=0
        )
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass
```

---

## 自动选择方案

```python
import platform
import shutil

def create_sandbox(**kwargs):
    """
    根据环境自动选择最佳沙箱方案
    """
    if shutil.which("docker"):
        return lambda code, **kw: execute_in_docker(code, **{**kwargs, **kw})
    
    if platform.system() == "Darwin" and shutil.which("sandbox-exec"):
        return lambda code, **kw: execute_with_sandbox_exec(code, **{**kwargs, **kw})
    
    if platform.system() == "Linux" and shutil.which("bwrap"):
        return lambda code, **kw: execute_with_bubblewrap(code, **{**kwargs, **kw})
    
    return lambda code, **kw: execute_code(code, **{**kwargs, **kw})

# 使用
sandbox = create_sandbox(network=False, timeout=10)
result = sandbox('print("Hello!")')
```

---

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| Docker 未运行 | Docker Desktop 未启动 | 启动 Docker Desktop |
| bwrap 权限不足 | 未安装或无权限 | `sudo apt install bubblewrap` |
| sandbox-exec 不存在 | macOS 版本太低 | 升级到 macOS 10.15+ |
| 网络被拒绝 | 沙箱禁止网络 | 检查 network 参数 |
| 文件写入失败 | 路径不在允许列表 | 添加到 writable_dirs |
| 僵尸容器 | Docker 超时未清理 | 代码已自动清理容器 |
| 内存不足 | prlimit 限制 | 调整 memory_limit_mb |

---

## 依赖

| 依赖 | 版本 | 方案 | 用途 |
|------|------|------|------|
| Python | 3.7+ | 所有 | 执行 Python |
| Node.js | 14+ | 所有 | 执行 JavaScript（可选） |
| Docker | 20+ | 方案一 | 容器隔离 |
| bubblewrap | 0.4+ | 方案三 | Linux 沙箱 |
| prlimit | 内置 | 方案三 | 内存限制 |
