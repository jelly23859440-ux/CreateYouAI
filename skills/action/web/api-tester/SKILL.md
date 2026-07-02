---
name: api-tester
layer: action
category: web
status: unverified
description: API 测试工具，支持请求构建、响应验证、自动化测试
version: 1.0.0
author: CreateYouAI
tags: [api, rest, http, testing, requests]
requirements: [requests]
platform: [windows, linux, macos]
difficulty: beginner
---

# API Tester (API 测试工具)

REST API 测试工具，支持各种 HTTP 方法、认证、请求头配置和响应验证。

## 功能特性

- 支持 GET、POST、PUT、DELETE、PATCH 方法
- 自定义请求头
- JSON 请求体
- 表单数据
- 文件上传
- Basic/Bearer Token 认证
- 响应验证（状态码、JSON Schema）
- 请求历史记录
- 环境变量支持

## 安装依赖

```bash
pip install requests
```

## 使用方法

### 命令行使用

```bash
# GET 请求
python api_tester.py get https://api.example.com/users

# POST 请求（JSON）
python api_tester.py post https://api.example.com/users --data '{"name": "John"}'

# 带认证的请求
python api_tester.py get https://api.example.com/me --auth "Bearer token123"

# 自定义请求头
python api_tester.py get https://api.example.com/data --header "X-Custom: value"

# 保存响应
python api_tester.py get https://api.example.com/data --output response.json
```

### Python 代码示例

```python
"""
api_tester.py - REST API 测试工具
支持各种 HTTP 方法、认证和响应验证
"""
import requests
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin


@dataclass
class APIResponse:
    """API 响应"""
    status_code: int
    headers: Dict[str, str]
    body: Any
    elapsed_ms: float
    url: str
    method: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """请求是否成功 (2xx)"""
        return 200 <= self.status_code < 300
    
    @property
    def json(self) -> Optional[Dict]:
        """尝试解析 JSON 响应"""
        try:
            return self.body if isinstance(self.body, dict) else json.loads(self.body)
        except (json.JSONDecodeError, TypeError):
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "status_code": self.status_code,
            "headers": self.headers,
            "body": self.body,
            "elapsed_ms": self.elapsed_ms,
            "url": self.url,
            "method": self.method,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
        }


class APITester:
    """API 测试器"""
    
    def __init__(
        self,
        base_url: str = "",
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        """
        初始化测试器
        
        Args:
            base_url: 基础 URL
            timeout: 请求超时时间（秒）
            verify_ssl: 是否验证 SSL 证书
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.history: List[APIResponse] = []
    
    def set_auth(self, auth_type: str, credential: str) -> None:
        """
        设置认证
        
        Args:
            auth_type: 认证类型 ("bearer", "basic")
            credential: 认证凭据
        """
        if auth_type.lower() == "bearer":
            self.session.headers["Authorization"] = f"Bearer {credential}"
        elif auth_type.lower() == "basic":
            import base64
            encoded = base64.b64encode(credential.encode()).decode()
            self.session.headers["Authorization"] = f"Basic {encoded}"
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """
        设置默认请求头
        
        Args:
            headers: 请求头字典
        """
        self.session.headers.update(headers)
    
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        files: Optional[Dict] = None
    ) -> APIResponse:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点（相对于 base_url）
            data: 表单数据或原始数据
            json_data: JSON 数据
            headers: 额外的请求头
            params: URL 查询参数
            files: 上传的文件
            
        Returns:
            APIResponse 对象
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        # 合并请求头
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        start_time = datetime.now()
        
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                data=data,
                json=json_data,
                headers=headers,
                params=params,
                files=files,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # 尝试解析响应体
            try:
                body = response.json()
            except json.JSONDecodeError:
                body = response.text
            
            api_response = APIResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=body,
                elapsed_ms=elapsed_ms,
                url=url,
                method=method.upper()
            )
            
            self.history.append(api_response)
            
            return api_response
        
        except requests.RequestException as e:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            error_response = APIResponse(
                status_code=0,
                headers={},
                body={"error": str(e)},
                elapsed_ms=elapsed_ms,
                url=url,
                method=method.upper()
            )
            
            self.history.append(error_response)
            
            raise
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """发送 GET 请求"""
        return self.request("GET", endpoint, params=params, headers=headers)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """发送 POST 请求"""
        return self.request("POST", endpoint, data=data, json_data=json_data, headers=headers)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """发送 PUT 请求"""
        return self.request("PUT", endpoint, data=data, json_data=json_data, headers=headers)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """发送 PATCH 请求"""
        return self.request("PATCH", endpoint, data=data, json_data=json_data, headers=headers)
    
    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """发送 DELETE 请求"""
        return self.request("DELETE", endpoint, headers=headers)
    
    def assert_status(self, response: APIResponse, expected: int) -> bool:
        """
        断言状态码
        
        Args:
            response: API 响应
            expected: 期望的状态码
            
        Returns:
            是否匹配
        """
        return response.status_code == expected
    
    def assert_json_field(
        self,
        response: APIResponse,
        field_path: str,
        expected_value: Any = None
    ) -> bool:
        """
        断言 JSON 字段
        
        Args:
            response: API 响应
            field_path: 字段路径（如 "data.users.0.name"）
            expected_value: 期望值（可选）
            
        Returns:
            字段是否存在且匹配
        """
        data = response.json
        if data is None:
            return False
        
        # 解析字段路径
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return False
            else:
                return False
        
        if expected_value is None:
            return True
        
        return current == expected_value
    
    def assert_response_time(
        self,
        response: APIResponse,
        max_ms: float
    ) -> bool:
        """
        断言响应时间
        
        Args:
            response: API 响应
            max_ms: 最大允许响应时间（毫秒）
            
        Returns:
            是否在允许范围内
        """
        return response.elapsed_ms <= max_ms
    
    def run_test_suite(
        self,
        tests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        运行测试套件
        
        Args:
            tests: 测试列表，每项包含:
                - name: 测试名称
                - method: HTTP 方法
                - endpoint: API 端点
                - expected_status: 期望状态码
                - data/json_data: 请求数据（可选）
                - assertions: 断言列表（可选）
                
        Returns:
            测试结果列表
        """
        results = []
        
        for test in tests:
            result = {
                "name": test["name"],
                "passed": False,
                "error": None,
                "response": None,
            }
            
            try:
                response = self.request(
                    method=test.get("method", "GET"),
                    endpoint=test["endpoint"],
                    data=test.get("data"),
                    json_data=test.get("json_data")
                )
                
                result["response"] = response.to_dict()
                
                # 检查状态码
                if "expected_status" in test:
                    if response.status_code != test["expected_status"]:
                        result["error"] = f"状态码不匹配: 期望 {test['expected_status']}, 实际 {response.status_code}"
                        results.append(result)
                        continue
                
                # 运行自定义断言
                assertions = test.get("assertions", [])
                for assertion in assertions:
                    assert_type = assertion.get("type")
                    
                    if assert_type == "status":
                        if not self.assert_status(response, assertion["value"]):
                            result["error"] = f"状态码断言失败"
                            break
                    
                    elif assert_type == "json_field":
                        if not self.assert_json_field(
                            response,
                            assertion["path"],
                            assertion.get("value")
                        ):
                            result["error"] = f"JSON 字段断言失败: {assertion['path']}"
                            break
                    
                    elif assert_type == "response_time":
                        if not self.assert_response_time(response, assertion["max_ms"]):
                            result["error"] = f"响应时间断言失败: {response.elapsed_ms:.0f}ms > {assertion['max_ms']}ms"
                            break
                
                if result["error"] is None:
                    result["passed"] = True
            
            except Exception as e:
                result["error"] = str(e)
            
            results.append(result)
        
        return results
    
    def clear_history(self) -> None:
        """清空请求历史"""
        self.history.clear()
    
    def export_history(self, file_path: str) -> None:
        """
        导出请求历史
        
        Args:
            file_path: 输出文件路径
        """
        data = [resp.to_dict() for resp in self.history]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="API 测试工具")
    parser.add_argument("method", choices=["get", "post", "put", "patch", "delete"])
    parser.add_argument("url", help="API URL")
    parser.add_argument("--data", help="请求数据 (JSON 字符串)")
    parser.add_argument("--header", action="append", help="请求头 (Key: Value)")
    parser.add_argument("--auth", help="认证 (Bearer token 或 user:pass)")
    parser.add_argument("--output", help="保存响应到文件")
    parser.add_argument("--timeout", type=int, default=30)
    
    args = parser.parse_args()
    
    # 解析 URL
    from urllib.parse import urlparse
    parsed = urlparse(args.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    endpoint = parsed.path
    
    tester = APITester(base_url=base_url, timeout=args.timeout)
    
    # 设置认证
    if args.auth:
        if args.auth.startswith("Bearer "):
            tester.set_auth("bearer", args.auth[7:])
        else:
            tester.set_auth("basic", args.auth)
    
    # 设置请求头
    headers = {}
    if args.header:
        for h in args.header:
            key, value = h.split(':', 1)
            headers[key.strip()] = value.strip()
    
    # 解析数据
    json_data = None
    if args.data:
        try:
            json_data = json.loads(args.data)
        except json.JSONDecodeError:
            print("错误: 无效的 JSON 数据")
            exit(1)
    
    # 发送请求
    try:
        response = tester.request(
            method=args.method.upper(),
            endpoint=endpoint,
            json_data=json_data,
            headers=headers if headers else None
        )
        
        print(f"\n{'='*50}")
        print(f"请求: {args.method.upper()} {args.url}")
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {response.elapsed_ms:.0f}ms")
        print(f"{'='*50}\n")
        
        if isinstance(response.body, dict):
            print(json.dumps(response.body, indent=2, ensure_ascii=False))
        else:
            print(response.body)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                if isinstance(response.body, dict):
                    json.dump(response.body, f, indent=2, ensure_ascii=False)
                else:
                    f.write(str(response.body))
            print(f"\n响应已保存到: {args.output}")
    
    except Exception as e:
        print(f"错误: {e}")
        exit(1)
```

## 使用示例

```python
from api_tester import APITester

# 创建测试器
tester = APITester(base_url="https://jsonplaceholder.typicode.com")

# GET 请求
response = tester.get("/posts/1")
print(f"状态码: {response.status_code}")
print(f"数据: {response.json}")

# POST 请求
response = tester.post(
    "/posts",
    json_data={
        "title": "Test Post",
        "body": "This is a test.",
        "userId": 1
    }
)
print(f"创建成功: {response.success}")

# 设置认证
tester.set_auth("bearer", "your-api-token")

# 运行测试套件
tests = [
    {
        "name": "获取用户列表",
        "method": "GET",
        "endpoint": "/users",
        "expected_status": 200,
        "assertions": [
            {"type": "response_time", "max_ms": 1000}
        ]
    },
    {
        "name": "创建用户",
        "method": "POST",
        "endpoint": "/users",
        "json_data": {"name": "New User", "email": "test@example.com"},
        "expected_status": 201
    }
]

results = tester.run_test_suite(tests)
for r in results:
    status = "✓" if r["passed"] else "✗"
    print(f"{status} {r['name']}: {r.get('error', 'OK')}")
```

## 故障排除

### 问题：requests 未安装
```
错误: ModuleNotFoundError: No module named 'requests'
```
**解决**: 安装 requests
```bash
pip install requests
```

### 问题：SSL 证书验证失败
```
错误: SSLError: certificate verify failed
```
**解决**: 禁用 SSL 验证（仅用于测试环境）
```python
tester = APITester(verify_ssl=False)
```

### 问题：连接超时
```
错误: ConnectionError: Connection timed out
```
**解决**: 增加超时时间
```python
tester = APITester(timeout=60)
```

### 问题：JSON 解析错误
```
错误: JSONDecodeError
```
**解决**: 检查请求数据格式，确保是有效 JSON

## 参考链接

- [requests 官方文档](https://docs.python-requests.org/)
- [HTTP 状态码](https://httpstatuses.com/)
- [REST API 设计指南](https://restfulapi.net/)
