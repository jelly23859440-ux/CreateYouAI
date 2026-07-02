---
name: 数据库查询助手
layer: core
category: memory
status: unverified
description: >
  连接 SQLite/PostgreSQL 数据库，执行查询并格式化结果。
  当用户需要查询数据库、分析数据、执行 SQL、查看表结构时触发。
  关键词：数据库查询、SQL、SQLite、PostgreSQL、数据分析、查询数据。
---

# 数据库查询助手

连接 SQLite/PostgreSQL 数据库，执行安全查询并格式化输出结果。

## 能力概览

| 能力 | 说明 |
|------|------|
| 多数据库支持 | SQLite（内置）、PostgreSQL |
| 安全查询 | 参数化查询防 SQL 注入 |
| 结果格式化 | 表格、JSON、CSV 多种输出 |
| 表结构探索 | 查看表、列、索引信息 |
| 查询历史 | 记录并复用历史查询 |

## 前置条件

- Python 3.8+
- SQLite：Python 内置，无需额外安装
- PostgreSQL：需要 psycopg2

## 安装步骤

### SQLite（无需安装）

SQLite 是 Python 内置模块，直接使用。

### PostgreSQL 支持

```bash
pip install psycopg2-binary>=2.9.0
```

验证安装：
```bash
python -c "import psycopg2; print('psycopg2 版本:', psycopg2.__version__)"
```

## 使用方法

### SQLite 基础操作

```python
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """建立连接"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self
    
    def disconnect(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    @contextmanager
    def cursor(self):
        """获取游标的上下文管理器"""
        if not self.conn:
            self.connect()
        cur = self.conn.cursor()
        try:
            yield cur
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        finally:
            cur.close()
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询并返回结果"""
        with self.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            return []
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """批量执行"""
        with self.cursor() as cur:
            cur.executemany(query, params_list)
            return cur.rowcount
    
    def get_tables(self) -> List[str]:
        """获取所有表名"""
        result = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row['name'] for row in result]
    
    def get_table_info(self, table: str) -> List[Dict]:
        """获取表结构"""
        return self.execute(f"PRAGMA table_info({table})")
    
    def get_row_count(self, table: str) -> int:
        """获取表行数"""
        result = self.execute(f"SELECT COUNT(*) as count FROM {table}")
        return result[0]['count'] if result else 0

# 使用示例
if __name__ == "__main__":
    db = DatabaseManager("example.db")
    
    with db.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute(
            "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)",
            ("张三", "zhangsan@example.com")
        )
        cur.execute(
            "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)",
            ("李四", "lisi@example.com")
        )
    
    print("表列表:", db.get_tables())
    print("users 表结构:")
    for col in db.get_table_info("users"):
        print(f"  {col['name']}: {col['type']}")
    
    print("\n用户列表:")
    users = db.execute("SELECT * FROM users")
    for user in users:
        print(f"  {user['name']} ({user['email']})")
    
    db.disconnect()
```

### 安全查询执行

```python
import re
from datetime import datetime

class SafeQueryExecutor:
    """安全查询执行器"""
    
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE',
        'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
    ]
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.history = []
    
    def is_select_query(self, query: str) -> bool:
        """检查是否为 SELECT 查询"""
        normalized = query.strip().upper()
        return normalized.startswith('SELECT') or normalized.startswith('WITH')
    
    def is_dangerous(self, query: str) -> bool:
        """检查是否为危险操作"""
        normalized = query.upper()
        return any(kw in normalized for kw in self.DANGEROUS_KEYWORDS)
    
    def validate_query(self, query: str) -> tuple[bool, str]:
        """验证查询安全性"""
        if self.is_dangerous(query):
            return False, "包含危险关键字，拒绝执行"
        
        if not self.is_select_query(query):
            return False, "仅支持 SELECT 查询"
        
        if ';' in query.rstrip().rstrip(';'):
            return False, "不支持多语句执行"
        
        return True, "验证通过"
    
    def execute_safe(
        self, 
        query: str, 
        params: tuple = (),
        max_rows: int = 1000
    ) -> Dict[str, Any]:
        """
        安全执行查询。
        
        Returns:
            {
                "success": bool,
                "data": List[Dict],
                "row_count": int,
                "message": str,
                "query": str,
                "timestamp": str
            }
        """
        valid, msg = self.validate_query(query)
        if not valid:
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "message": msg,
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            limited_query = f"{query.rstrip().rstrip(';')} LIMIT {max_rows}"
            data = self.db.execute(limited_query, params)
            
            self.history.append({
                "query": query,
                "params": params,
                "row_count": len(data),
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "message": f"查询成功，返回 {len(data)} 行",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "message": f"查询错误: {str(e)}",
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

# 使用示例
if __name__ == "__main__":
    db = DatabaseManager("example.db")
    executor = SafeQueryExecutor(db)
    
    result = executor.execute_safe("SELECT * FROM users WHERE name = ?", ("张三",))
    
    if result["success"]:
        print(f"查询成功: {result['message']}")
        for row in result["data"]:
            print(f"  {row}")
    else:
        print(f"查询失败: {result['message']}")
    
    dangerous = executor.execute_safe("DROP TABLE users")
    print(f"\n危险查询: {dangerous['message']}")
```

### 结果格式化

```python
import csv
import json
from io import StringIO

class ResultFormatter:
    """查询结果格式化器"""
    
    @staticmethod
    def to_table(data: List[Dict], max_col_width: int = 30) -> str:
        """格式化为 ASCII 表格"""
        if not data:
            return "(无数据)"
        
        columns = list(data[0].keys())
        
        col_widths = {}
        for col in columns:
            max_width = max(len(str(col)), max(len(str(row.get(col, ''))) for row in data))
            col_widths[col] = min(max_width, max_col_width)
        
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        separator = "-+-".join("-" * col_widths[col] for col in columns)
        
        lines = [header, separator]
        for row in data:
            line = " | ".join(
                str(row.get(col, ''))[:max_col_width].ljust(col_widths[col])
                for col in columns
            )
            lines.append(line)
        
        return "\n".join(lines)
    
    @staticmethod
    def to_json(data: List[Dict], indent: int = 2) -> str:
        """格式化为 JSON"""
        return json.dumps(data, ensure_ascii=False, indent=indent, default=str)
    
    @staticmethod
    def to_csv_string(data: List[Dict]) -> str:
        """格式化为 CSV 字符串"""
        if not data:
            return ""
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    @staticmethod
    def to_markdown(data: List[Dict]) -> str:
        """格式化为 Markdown 表格"""
        if not data:
            return "(无数据)"
        
        columns = list(data[0].keys())
        
        header = "| " + " | ".join(columns) + " |"
        separator = "| " + " | ".join("---" for _ in columns) + " |"
        
        rows = []
        for row in data:
            row_str = "| " + " | ".join(str(row.get(col, '')) for col in columns) + " |"
            rows.append(row_str)
        
        return "\n".join([header, separator] + rows)

# 使用示例
if __name__ == "__main__":
    data = [
        {"id": 1, "name": "张三", "age": 25},
        {"id": 2, "name": "李四", "age": 30},
    ]
    
    formatter = ResultFormatter()
    
    print("=== ASCII 表格 ===")
    print(formatter.to_table(data))
    
    print("\n=== Markdown 表格 ===")
    print(formatter.to_markdown(data))
    
    print("\n=== JSON ===")
    print(formatter.to_json(data))
```

### PostgreSQL 支持

```python
import os

class PostgreSQLManager(DatabaseManager):
    """PostgreSQL 数据库管理器"""
    
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError("请安装 psycopg2: pip install psycopg2-binary")
        
        self.conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        self.conn.cursor_factory = psycopg2.extras.RealDictCursor
    
    def connect(self):
        return self
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
    
    def execute(self, query: str, params: tuple = ()) -> List[Dict]:
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return [dict(row) for row in cur.fetchall()]
            self.conn.commit()
            return []

# 使用示例
if __name__ == "__main__":
    db = PostgreSQLManager(
        host=os.environ.get("PG_HOST", "localhost"),
        port=int(os.environ.get("PG_PORT", 5432)),
        database=os.environ.get("PG_DB", "mydb"),
        user=os.environ.get("PG_USER", "postgres"),
        password=os.environ.get("PG_PASS", "")
    )
    
    tables = db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    )
    print("PostgreSQL 表:", [t['table_name'] for t in tables])
```

### 命令行用法

```bash
# 查询 SQLite 数据库
python db_query.py --db mydb.sqlite "SELECT * FROM users"

# 查看表结构
python db_query.py --db mydb.sqlite --tables

# 导出为 CSV
python db_query.py --db mydb.sqlite --format csv "SELECT * FROM users" > users.csv

# PostgreSQL 查询
python db_query.py --db postgresql://user:pass@host:5432/mydb "SELECT COUNT(*) FROM orders"
```

## 问题排查

### 问题 1：SQLite 数据库锁定

**原因**：多进程同时写入。

**解决**：使用 WAL 模式或添加超时：
```python
sqlite3.connect("db.sqlite", timeout=10)
```

### 问题 2：PostgreSQL 连接失败

**原因**：网络、认证或配置错误。

**解决**：
```bash
# 检查连接参数
psql -h host -p 5432 -U user -d dbname
```

### 问题 3：查询结果为空

**原因**：表不存在或查询条件不匹配。

**解决**：先执行 `--tables` 查看表，再用 `SELECT COUNT(*)` 验证数据。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| sqlite3 | 内置 | SQLite 必需 |
| psycopg2-binary | ≥2.9.0 | PostgreSQL 可选 |

## Agent 执行规范

### 核心约束
- **仅执行 SELECT**：禁止执行修改数据的语句
- **参数化查询**：始终使用参数占位符，禁止字符串拼接
- **限制结果集**：默认限制 1000 行，防止内存溢出
- **记录查询历史**：便于审计和复用
