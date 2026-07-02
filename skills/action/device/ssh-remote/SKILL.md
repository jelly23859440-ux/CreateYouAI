---
name: SSH 远程执行
layer: action
category: device
status: unverified
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
| 批量执行 | 多主机并行执行命令 |

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
import os
from typing import Optional, Dict, Any

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
            
            # 校验密钥文件存在性
            if self.key_filename and not os.path.exists(self.key_filename):
                raise FileNotFoundError(f"密钥文件不存在: {self.key_filename}")
            
            # 空密码视为未提供
            password = self.password if self.password else None
            
            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": self.timeout
            }
            
            if self.key_filename:
                connect_kwargs["key_filename"] = self.key_filename
            elif password:
                connect_kwargs["password"] = password
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
    ) -> Dict[str, Any]:
        """
        执行远程命令
        
        Returns:
            {"success": bool, "stdout": str, "stderr": str, "exit_code": int}
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
    
    def execute_sudo(
        self,
        command: str,
        password: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        执行 sudo 命令（交互式）
        
        Args:
            command: 要执行的命令
            password: sudo 密码
            timeout: 超时时间
        
        注意：密码包含单引号时需转义，生产环境建议使用 pty + stdin.write()
        """
        if not self.client:
            return {
                "success": False,
                "stdout": "",
                "stderr": "未建立连接",
                "exit_code": -1
            }
        
        try:
            # 使用 -S 从 stdin 读取密码
            # 注意：密码包含单引号时需转义，生产环境建议使用 pty + stdin.write()
            stdin, stdout, stderr = self.client.exec_command(
                f"echo '{password}' | sudo -S {command}",
                timeout=timeout
            )
            
            exit_code = stdout.channel.recv_exit_status()
            
            stdout_text = stdout.read().decode('utf-8', errors='replace')
            stderr_text = stderr.read().decode('utf-8', errors='replace')
            
            return {
                "success": exit_code == 0,
                "stdout": stdout_text,
                "stderr": stderr_text,
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
            self.sftp = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
    
    def upload(
        self, 
        local_path: str, 
        remote_path: str
    ) -> Dict[str, Any]:
        """上传文件"""
        try:
            # 先获取文件大小，避免 put 和 getsize 之间的竞态
            file_size = os.path.getsize(local_path)
            self.sftp.put(local_path, remote_path)
            return {
                "success": True,
                "bytes_transferred": file_size,
                "error": None
            }
        except FileNotFoundError as e:
            return {
                "success": False,
                "bytes_transferred": 0,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "bytes_transferred": 0,
                "error": str(e)
            }
    
    def download(
        self, 
        remote_path: str, 
        local_path: str
    ) -> Dict[str, Any]:
        """下载文件"""
        try:
            self.sftp.get(remote_path, local_path)
            file_size = os.path.getsize(local_path)
            return {
                "success": True,
                "bytes_transferred": file_size,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "bytes_transferred": 0,
                "error": str(e)
            }
    
    def list_dir(self, remote_path: str = ".") -> list:
        """列出目录内容"""
        try:
            return self.sftp.listdir(remote_path)
        except Exception as e:
            print(f"列出目录失败: {e}")
            return []


class BatchSSHExecutor:
    """批量 SSH 命令执行器"""
    
    def __init__(self, hosts: list):
        """
        Args:
            hosts: [{"host": "...", "username": "...", "password": "..."}, ...]
        """
        self.hosts = hosts
        # 前置校验：确保每个 host_config 都有 "host" 键
        for i, h in enumerate(self.hosts):
            if "host" not in h:
                raise ValueError(f"第 {i+1} 个 host_config 缺少 'host' 键")
    
    def execute_on_all(
        self, 
        command: str, 
        max_workers: int = 5
    ) -> list:
        """在所有主机上执行命令"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for host_config in self.hosts:
                ssh = SSHClient(**host_config)
                future = executor.submit(self._execute_on_host, ssh, command)
                futures[future] = host_config.get("host", "unknown")
            
            for future in as_completed(futures):
                host = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    result = {
                        "success": False,
                        "stdout": "",
                        "stderr": str(e),
                        "exit_code": -1
                    }
                results.append({
                    "host": host,
                    **result
                })
        
        return results
    
    def _execute_on_host(self, ssh: SSHClient, command: str) -> Dict[str, Any]:
        """在单个主机上执行命令"""
        if ssh.connect():
            try:
                result = ssh.execute(command)
            finally:
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
    # 示例 1：基础连接
    with SSHClient(
        host="192.168.1.100",
        username="admin",
        password="your_password"
    ) as ssh:
        result = ssh.execute("uname -a")
        if result["success"]:
            print("系统信息:", result["stdout"])
    
    # 示例 2：密钥认证
    import os
    ssh = SSHClient(
        host="192.168.1.100",
        username="admin",
        key_filename=os.path.expanduser("~/.ssh/id_rsa")
    )
    if ssh.connect():
        result = ssh.execute("echo '密钥认证成功'")
        print(result["stdout"])
        ssh.disconnect()
    
    # 示例 3：SFTP
    with SSHClient(
        host="192.168.1.100",
        username="admin",
        password="your_password"
    ) as ssh:
        with SFTPClient(ssh) as sftp:
            sftp.upload("local_file.txt", "/tmp/remote_file.txt")
            files = sftp.list_dir("/tmp")
            print("远程 /tmp 目录:", files)
    
    # 示例 4：sudo 执行
    with SSHClient(
        host="192.168.1.100",
        username="admin",
        password="your_password"
    ) as ssh:
        result = ssh.execute_sudo("apt update", password="sudo_password")
        print(result["stdout"])
    
    # 示例 5：批量执行
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

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 连接超时 | 网络不通或 SSH 端口不对 | `ping` 检查网络，`nc -zv host 22` 检查端口 |
| 认证失败 | 密码错误或密钥权限不对 | `chmod 600 ~/.ssh/id_rsa`，`ssh -v user@host` |
| 连接被拒绝 | SSH 服务未启动 | 检查服务器 SSH 服务状态 |
| 权限被拒绝 | 密钥未授权 | 将公钥添加到 `~/.ssh/authorized_keys` |
| 命令执行无输出 | 命令时间过长 | 增加 timeout 参数 |
| 密钥文件不存在 | 路径错误 | 检查 key_filename 路径 |

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| paramiko | ≥3.0.0 | SSH 客户端 |

## Agent 执行规范

- **密码安全**：密码通过环境变量传入，不要硬编码
- **密钥权限**：生产环境使用 `WarningPolicy` 或预加载 `known_hosts`
- **超时设置**：始终设置合理的超时时间
- **连接关闭**：使用后必须关闭连接
- **并发限制**：批量执行时限制并发数，避免触发服务器限制
- **文件校验**：密钥文件使用前检查是否存在
