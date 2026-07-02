---
name: SSH 远程执行
layer: action
category: device
description: >
  连接远程服务器执行命令，支持密钥认证和密码认证。
  当用户需要远程执行命令、管理服务器、部署应用、检查服务器状态时触发。
  关键词：SSH、远程执行、服务器管理、远程登录、部署、服务器状态。
---

# SSH 远程执行

安全连接远程服务器执行命令，支持密码和密钥认证。

## 能力概览

| 能力 | 说明 |
|------|------|
| 密码认证 | 支持用户名/密码连接 |
| 密钥认证 | 支持 SSH 密钥文件 |
| 命令执行 | 执行远程命令并返回输出 |
| 文件传输 | 支持 SFTP 文件上传下载 |
| 连接池 | 复用连接提高效率 |

## 前置条件

- Python 3.8+
- paramiko 库
- 远程服务器 SSH 服务已开启

## 安装步骤

```bash
pip install paramiko>=3.0.0
```

验证安装：
```bash
python -c "import paramiko; print('paramiko 版本:', paramiko.__version__)"
```

## 使用方法

### 基础 SSH 连接与命令执行

```python
import paramiko
import socket
from typing import Optional, Dict, Tuple

class SSHClient:
    """SSH 客户端"""
    
    def __init__(
        self,
        host: str,
        port: int = 22,
        username: str = "",
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        timeout: int = 10
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.timeout = timeout
        self.client = None
    
    def connect(self) -> bool:
        """建立连接"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": self.timeout
            }
            
            if self.key_filename:
                connect_kwargs["key_filename"] = self.key_filename
            elif self.password:
                connect_kwargs["password"] = self.password
            else:
                raise ValueError("必须提供密码或密钥文件")
            
            self.client.connect(**connect_kwargs)
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            self.client = None
    
    def execute(
        self, 
        command: str, 
        timeout: int = 30
    ) -> Dict[str, any]:
        """
        执行远程命令。
        
        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "exit_code": int
            }
        """
        if not self.client:
            return {
                "success": False,
                "stdout": "",
                "stderr": "未建立连接",
                "exit_code": -1
            }
        
        try:
            stdin, stdout, stderr = self.client.exec_command(
                command, timeout=timeout
            )
            
            exit_code = stdout.channel.recv_exit_status()
            
            return {
                "success": exit_code == 0,
                "stdout": stdout.read().decode('utf-8', errors='replace'),
                "stderr": stderr.read().decode('utf-8', errors='replace'),
                "exit_code": exit_code
            }
        except socket.timeout:
            return {
                "success": False,
                "stdout": "",
                "stderr": "命令执行超时",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

# 使用示例
if __name__ == "__main__":
    with SSHClient(
        host="192.168.1.100",
        username="admin",
        password="your_password"
    ) as ssh:
        result = ssh.execute("uname -a")
        if result["success"]:
            print("系统信息:", result["stdout"])
        else:
            print("执行失败:", result["stderr"])
        
        result = ssh.execute("df -h")
        print("磁盘使用:\n", result["stdout"])
```

### 密钥认证

```python
import os

def create_key_example():
    """密钥认证示例"""
    ssh = SSHClient(
        host="192.168.1.100",
        username="admin",
        key_filename=os.path.expanduser("~/.ssh/id_rsa")
    )
    
    if ssh.connect():
        result = ssh.execute("echo '密钥认证成功'")
        print(result["stdout"])
        ssh.disconnect()

# 使用示例
if __name__ == "__main__":
    create_key_example()
```

### SFTP 文件传输

```python
class SFTPClient:
    """SFTP 文件传输客户端"""
    
    def __init__(self, ssh_client: SSHClient):
        self.ssh = ssh_client
        self.sftp = None
    
    def connect(self):
        """建立 SFTP 连接"""
        if self.ssh.client:
            self.sftp = self.ssh.client.open_sftp()
    
    def disconnect(self):
        """关闭 SFTP 连接"""
        if self.sftp:
            self.sftp.close()
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        """上传文件"""
        try:
            self.sftp.put(local_path, remote_path)
            return True
        except Exception as e:
            print(f"上传失败: {e}")
            return False
    
    def download(self, remote_path: str, local_path: str) -> bool:
        """下载文件"""
        try:
            self.sftp.get(remote_path, local_path)
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            return False
    
    def list_dir(self, remote_path: str = ".") -> list:
        """列出目录内容"""
        try:
            return self.sftp.listdir(remote_path)
        except Exception as e:
            print(f"列出目录失败: {e}")
            return []

# 使用示例
if __name__ == "__main__":
    ssh = SSHClient(
        host="192.168.1.100",
        username="admin",
        password="your_password"
    )
    
    if ssh.connect():
        sftp = SFTPClient(ssh)
        sftp.connect()
        
        sftp.upload("local_file.txt", "/tmp/remote_file.txt")
        
        files = sftp.list_dir("/tmp")
        print("远程 /tmp 目录:", files)
        
        sftp.disconnect()
        ssh.disconnect()
```

### 批量命令执行

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

class BatchSSHExecutor:
    """批量 SSH 命令执行器"""
    
    def __init__(self, hosts: List[Dict]):
        """
        Args:
            hosts: [{"host": "...", "username": "...", "password": "..."}, ...]
        """
        self.hosts = hosts
    
    def execute_on_all(
        self, 
        command: str, 
        max_workers: int = 5
    ) -> List[Dict]:
        """在所有主机上执行命令"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for host_config in self.hosts:
                ssh = SSHClient(**host_config)
                future = executor.submit(self._execute_on_host, ssh, command)
                futures[future] = host_config["host"]
            
            for future in as_completed(futures):
                host = futures[future]
                result = future.result()
                results.append({
                    "host": host,
                    **result
                })
        
        return results
    
    def _execute_on_host(self, ssh: SSHClient, command: str) -> Dict:
        """在单个主机上执行命令"""
        if ssh.connect():
            result = ssh.execute(command)
            ssh.disconnect()
            return result
        return {
            "success": False,
            "stdout": "",
            "stderr": "连接失败",
            "exit_code": -1
        }

# 使用示例
if __name__ == "__main__":
    hosts = [
        {"host": "192.168.1.101", "username": "admin", "password": "pass1"},
        {"host": "192.168.1.102", "username": "admin", "password": "pass2"},
    ]
    
    batch = BatchSSHExecutor(hosts)
    results = batch.execute_on_all("uptime")
    
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"{status} {r['host']}: {r['stdout'].strip()}")
```

### 服务器状态检查

```python
def get_server_status(ssh: SSHClient) -> Dict:
    """获取服务器综合状态"""
    commands = {
        "system": "uname -a",
        "uptime": "uptime",
        "cpu": "lscpu | grep 'Model name' || cat /proc/cpuinfo | grep 'model name' | head -1",
        "memory": "free -h | grep Mem",
        "disk": "df -h / | tail -1",
        "load": "cat /proc/loadavg",
    }
    
    status = {}
    for key, cmd in commands.items():
        result = ssh.execute(cmd)
        if result["success"]:
            status[key] = result["stdout"].strip()
    
    return status

# 使用示例
if __name__ == "__main__":
    with SSHClient("192.168.1.100", "admin", password="pass") as ssh:
        status = get_server_status(ssh)
        for key, value in status.items():
            print(f"{key}: {value}")
```

## 问题排查

### 问题 1：连接超时

**原因**：网络不通或 SSH 端口不对。

**解决**：
```bash
# 检查网络连通性
ping 192.168.1.100

# 检查 SSH 端口
nc -zv 192.168.1.100 22
```

### 问题 2：认证失败

**原因**：密码错误或密钥权限不对。

**解决**：
```bash
# 检查密钥权限（Linux/Mac）
chmod 600 ~/.ssh/id_rsa

# 测试 SSH 连接
ssh -v user@host
```

### 问题 3：命令执行无输出

**原因**：命令执行时间过长或产生大量输出。

**解决**：增大 timeout 参数，或使用异步执行。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| paramiko | ≥3.0.0 | 必需 |

## Agent 执行规范

### 核心约束
- **密钥安全**：不要在代码中硬编码密码
- **超时设置**：始终设置合理的超时时间
- **错误处理**：捕获并处理所有连接异常
- **连接关闭**：使用后必须关闭连接