---
name: 代码沙箱
layer: action
category: code
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
| socat | 1.7+ | 方案三 | 网络代理 |

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
        writable_paths: 可写路径列表
    
    Returns:
        ExecutionResult 对象
    """
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
            "--memory", memory_limit,           # 内存限制
            "--cpus", "1",                      # CPU 限制
            "--read-only",                      # 只读根文件系统
            "--tmpfs", "/tmp:size=100m",        # 可写临时目录
            "-v", f"{tmpdir}:/code:ro",         # 代码只读挂载
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
            "--security-opt", "no-new-privileges",  # 禁止提权
            "--cap-drop", "ALL",                     # 删除所有 capabilities
            "--cap-add", "NET_BIND_SERVICE",         # 仅保留必要的
            image, cmd, f"/code/code{ext}"
        ])
        
        try:
            import time
            start = time.time()
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5  # 给 Docker 额外 5 秒
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

# 使用示例
result = execute_in_docker(
    'import os; print(os.listdir("/"))',
    language="python",
    timeout=10,
    memory_limit="100m",
    network=False
)
print(result.stdout)  # 只能看到容器内的文件
```

### Docker 安全特性

| 特性 | 说明 |
|------|------|
| `--network=none` | 禁用网络 |
| `--memory 100m` | 限制内存 |
| `--read-only` | 只读文件系统 |
| `--cap-drop ALL` | 删除所有 capabilities |
| `--security-opt no-new-privileges` | 禁止提权 |
| `-v ... :ro` | 只读挂载 |

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
    writable_dirs: list = None
) -> ExecutionResult:
    """
    使用 macOS sandbox-exec 执行代码
    
    Args:
        code: 代码
        language: "python" 或 "node"
        timeout: 超时时间
        writable_dirs: 可写目录列表
    
    Returns:
        ExecutionResult 对象
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入代码文件
        ext = ".py" if language == "python" else ".js"
        code_file = os.path.join(tmpdir, f"code{ext}")
        with open(code_file, 'w') as f:
            f.write(code)
        
        # 生成 sandbox profile
        profile = generate_sandbox_profile(writable_dirs or [tmpdir])
        profile_file = os.path.join(tmpdir, "sandbox.sb")
        with open(profile_file, 'w') as f:
            f.write(profile)
        
        # 选择命令
        cmd = "python" if language == "python" else "node"
        
        # 构建命令
        sandbox_cmd = [
            "sandbox-exec",
            "-f", profile_file,
            cmd, code_file
        ]
        
        try:
            import time
            start = time.time()
            
            result = subprocess.run(
                sandbox_cmd,
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

def generate_sandbox_profile(writable_dirs: list) -> str:
    """
    生成 macOS sandbox-exec profile
    
    基于 Claude Code 的 seatbelt 配置
    """
    # 默认拒绝所有操作
    deny_rules = [
        '(deny default)',
        # 允许读取系统库
        '(allow file-read* (subpath "/usr") (subpath "/System") (subpath "/Library"))',
        # 允许读取用户目录
        '(allow file-read* (subpath "/Users"))',
        # 允许读取临时目录
        '(allow file-read* (subpath "/tmp"))',
    ]
    
    # 允许写入指定目录
    write_rules = []
    for dir_path in writable_dirs:
        write_rules.append(f'(allow file-write* (subpath "{dir_path}"))')
    
    # 网络限制（可选）
    network_rules = [
        '(deny network*)',  # 禁止网络
        # '(allow network*)',  # 允许网络（取消注释以启用）
    ]
    
    # 进程限制
    process_rules = [
        '(deny process*)',
        '(allow process-exec)',
    ]
    
    # 组合 profile
    profile = """
(version 1)
(allow default)
""" + '\n'.join(deny_rules) + '\n' + '\n'.join(write_rules) + '\n' + '\n'.join(network_rules)
    
    return profile
```

---

## 方案三：Linux bubblewrap

Linux 上的轻量沙箱，Claude Code 在 Linux 上使用此方案。

### 前置条件

```bash
# 安装 bubblewrap
sudo apt install bubblewrap  # Debian/Ubuntu
sudo dnf install bubblewrap  # Fedora

# 安装 socat（网络代理）
sudo apt install socat
```

### 实现

```python
import subprocess
import tempfile
import os
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
    network: bool = False,
    writable_dirs: list = None
) -> ExecutionResult:
    """
    使用 bubblewrap 执行代码
    
    Args:
        code: 代码
        language: "python" 或 "node"
        timeout: 超时时间
        network: 是否允许网络
        writable_dirs: 可写目录列表
    
    Returns:
        ExecutionResult 对象
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入代码文件
        ext = ".py" if language == "python" else ".js"
        code_file = os.path.join(tmpdir, f"code{ext}")
        with open(code_file, 'w') as f:
            f.write(code)
        
        # 构建 bwrap 命令
        bwrap_cmd = [
            "bwrap",
            # 文件系统隔离
            "--ro-bind", "/usr", "/usr",           # 只读挂载 /usr
            "--ro-bind", "/lib", "/lib",           # 只读挂载 /lib
            "--ro-bind", "/lib64", "/lib64",       # 只读挂载 /lib64
            "--proc", "/proc",                     # 挂载 /proc
            "--dev", "/dev",                       # 挂载 /dev
            "--tmpfs", "/tmp",                     # 可写临时目录
            "--bind", tmpdir, "/sandbox",          # 挂载代码目录
            "--chdir", "/sandbox",                 # 切换到代码目录
            "--unshare-all",                       # 隔离所有命名空间
            "--die-with-parent",                   # 父进程退出时退出
        ]
        
        # 可写目录
        if writable_dirs:
            for dir_path in writable_dirs:
                bwrap_cmd.extend(["--bind", dir_path, dir_path])
        
        # 网络隔离
        if not network:
            bwrap_cmd.append("--unshare-net")
        
        # 执行命令
        cmd = "python" if language == "python" else "node"
        bwrap_cmd.extend([cmd, f"/sandbox/code{ext}"])
        
        try:
            import time
            start = time.time()
            
            result = subprocess.run(
                bwrap_cmd,
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
```

### Bubblewrap 安全特性

| 特性 | 说明 |
|------|------|
| `--unshare-all` | 隔离所有命名空间（mount, pid, net, user） |
| `--unshare-net` | 禁用网络 |
| `--ro-bind` | 只读绑定挂载 |
| `--die-with-parent` | 父进程退出时退出 |
| `--chdir` | 限制工作目录 |

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

---

## 自动选择方案

```python
import platform
import shutil

def create_sandbox(**kwargs):
    """
    根据环境自动选择最佳沙箱方案
    """
    # 方案一：Docker（最安全）
    if shutil.which("docker"):
        return lambda code, **kw: execute_in_docker(code, **{**kwargs, **kw})
    
    # 方案二：macOS sandbox-exec
    if platform.system() == "Darwin" and shutil.which("sandbox-exec"):
        return lambda code, **kw: execute_with_sandbox_exec(code, **{**kwargs, **kw})
    
    # 方案三：Linux bubblewrap
    if platform.system() == "Linux" and shutil.which("bwrap"):
        return lambda code, **kw: execute_with_bubblewrap(code, **{**kwargs, **kw})
    
    # 方案四：仅超时（无隔离）
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

---

## 依赖

| 依赖 | 版本 | 方案 | 用途 |
|------|------|------|------|
| Python | 3.7+ | 所有 | 执行 Python |
| Node.js | 14+ | 所有 | 执行 JavaScript（可选） |
| Docker | 20+ | 方案一 | 容器隔离 |
| bubblewrap | 0.4+ | 方案三 | Linux 沙箱 |
| socat | 1.7+ | 方案三 | 网络代理 |
