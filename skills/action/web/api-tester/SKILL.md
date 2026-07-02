---
name: API 测试工具
layer: action
category: web
status: unverified
description: API 测试工具，支持请求构建、响应验证、自动化测试
version: 1.1
requirements:
  - name: requests
    version: ">=2.28"
    required: true
---

# API 测试工具

REST API 测试工具，支持各种 HTTP 方法、认证、请求头配置和响应验证。

## 功能特性

- 支持 GET、POST、PUT、DELETE、PATCH 方法
- 自定义请求头
- JSON 请求体
- 表单数据
- 文件上传
- Basic/Bearer Token 认证
- 响应验证（状态码、JSON 字段）
- 请求历史记录

## 安装依赖

```bash
pip install requests
```

## 使用方法

### Python 代码示例

```python
import requests
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth


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
    def parsed_json(self) -> Optional[Dict]:
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
        # 清除之前的认证配置
        self.session.auth = None
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]
        
        if auth_type.lower() == "bearer":
            self.session.headers["Authorization"] = f"Bearer {credential}"
        elif auth_type.lower() == "basic":
            if ":" in credential:
                username, password = credential.split(":", 1)
            else:
                username, password = credential, ""
            self.session.auth = HTTPBasicAuth(username, password)
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """设置默认请求头"""
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
        """发送 HTTP 请求"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
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
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict] = None
    ) -> APIResponse:
        """发送 POST 请求"""
        return self.request("POST", endpoint, data=data, json_data=json_data, headers=headers, files=files)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict] = None
    ) -> APIResponse:
        """发送 PUT 请求"""
        return self.request("PUT", endpoint, data=data, json_data=json_data, headers=headers, files=files)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Union[Dict, str]] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict] = None
    ) -> APIResponse:
        """发送 PATCH 请求"""
        return self.request("PATCH", endpoint, data=data, json_data=json_data, headers=headers, files=files)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """发送 DELETE 请求"""
        return self.request("DELETE", endpoint, params=params, headers=headers)
    
    def assert_status(self, response: APIResponse, expected: int) -> bool:
        """断言状态码"""
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
            field_path: 字段路径（如 "data.users.0.name"，支持负数索引如 "-1"）
            expected_value: 期望值（可选）
        
        Returns:
            字段是否存在且匹配
        """
        data = response.parsed_json
        if data is None:
            return False
        
        # 解析字段路径
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, list):
                # 支持负数索引（如 "-1" 表示最后一个元素）
                if part.lstrip('-').isdigit():
                    index = int(part)
                    if -len(current) <= index < len(current):
                        current = current[index]
                    else:
                        return False
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
        """断言响应时间"""
        return response.elapsed_ms <= max_ms
    
    def run_test_suite(
        self,
        tests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        运行测试套件
        
        Args:
            tests: 测试列表
            
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
        """导出请求历史"""
        data = [resp.to_dict() for resp in self.history]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)


# 命令行入口
if __name__ == "__main__":
    import argparse
    from urllib.parse import urlparse, parse_qs
    
    parser = argparse.ArgumentParser(description="API 测试工具")
    parser.add_argument("method", choices=["get", "post", "put", "patch", "delete"])
    parser.add_argument("url", help="API URL")
    parser.add_argument("--data", help="请求数据 (JSON 字符串)")
    parser.add_argument("--header", action="append", help="请求头 (Key: Value)")
    parser.add_argument("--auth", help="认证 (Bearer token 或 user:pass)")
    parser.add_argument("--output", help="保存响应到文件")
    parser.add_argument("--timeout", type=int, default=30)
    
    args = parser.parse_args()
    
    # 解析 URL（保留查询参数）
    parsed = urlparse(args.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    endpoint = parsed.path
    query_params = parse_qs(parsed.query)
    # 将查询参数展平为单值
    params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
    
    tester = APITester(base_url=base_url, timeout=args.timeout)
    
    # 设置认证
    if args.auth:
        if args.auth.startswith("Bearer "):
            tester.set_auth("bearer", args.auth[7:])
        elif ":" in args.auth:
            tester.set_auth("basic", args.auth)
        else:
            print("错误: 认证格式不正确，使用 'Bearer token' 或 'user:pass'")
            exit(1)
    
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
            headers=headers if headers else None,
            params=params if params else None
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

tester = APITester(base_url="https://jsonplaceholder.typicode.com")

# GET 请求
response = tester.get("/posts/1")
print(f"状态码: {response.status_code}")
print(f"数据: {response.parsed_json}")

# POST 请求
response = tester.post(
    "/posts",
    json_data={"title": "Test", "body": "Test body", "userId": 1}
)
print(f"创建成功: {response.success}")

# 文件上传
response = tester.post(
    "/upload",
    files={"file": open("photo.jpg", "rb")}
)

# Basic 认证
tester.set_auth("basic", "user:pass")

# 运行测试套件
tests = [
    {"name": "获取列表", "method": "GET", "endpoint": "/posts", "expected_status": 200},
    {"name": "创建", "method": "POST", "endpoint": "/posts", "json_data": {"title": "Test"}, "expected_status": 201},
]
results = tester.run_test_suite(tests)
for r in results:
    print(f"{'✓' if r['passed'] else '✗'} {r['name']}: {r.get('error', 'OK')}")
```

## 命令行用法

```bash
# GET 请求
python api_tester.py get https://api.example.com/users

# POST JSON
python api_tester.py post https://api.example.com/users --data '{"name": "John"}'

# 带查询参数
python api_tester.py get "https://api.example.com/users?id=1&name=test"

# Bearer 认证
python api_tester.py get https://api.example.com/me --auth "Bearer token123"

# Basic 认证
python api_tester.py get https://api.example.com/me --auth "user:pass"

# 自定义请求头
python api_tester.py get https://api.example.com/data --header "X-Custom: value"
```

## 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| requests 未安装 | 未安装依赖 | `pip install requests` |
| SSL 证书验证失败 | 自签名证书 | `APITester(verify_ssl=False)` |
| 连接超时 | 网络问题 | 增加 `timeout` 参数 |
| JSON 解析错误 | 请求数据格式错误 | 检查 JSON 格式 |
| 认证失败 | 格式错误 | 使用 `Bearer token` 或 `user:pass` |

## 依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| requests | ≥2.28 | HTTP 客户端 |
