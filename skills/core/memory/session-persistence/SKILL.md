---
name: session-persistence
layer: core
category: memory
status: unverified
description: >
  会话持久化：会话创建、消息保存、压缩。
  关键词：会话、持久化、存储、压缩。
---

# 会话持久化

## 功能说明

会话持久化模块提供基于 JSONL 的会话存储能力：

- **JSONL 存储**：每条记录一行 JSON，支持流式写入和断点续传
- **树形结构**：通过 `id + parentId` 实现条目的父子关系，支持多分支
- **分支管理**：从任意节点创建分支，支持导航和路径追踪
- **压缩**：保留最近 N 条消息，旧消息生成摘要
- **会话仓库**：管理多个会话文件，支持按工作目录分组

## 使用方法

### 基本用法

```python
from pathlib import Path
from session_persistence import Session, SessionRepo

# 创建会话仓库
repo = SessionRepo(Path("./sessions"))

# 创建新会话
session = repo.create()

# 添加消息
session.add_message("user", "你好")
session.add_message("assistant", "你好！有什么可以帮你的？")

# 获取所有消息
messages = session.get_messages()
```

### 分支管理

```python
# 获取当前叶子节点
leaf_id = session.storage.get_leaf_id()

# 从该节点创建分支
branch_id = session.branch(leaf_id)

# 在分支上添加消息
session.add_message("user", "换个话题", parent_id=branch_id)
```

### 压缩会话

```python
# 保留最近 10 条，旧消息生成摘要
session.compact(keep_recent=10)
```

### 自定义压缩摘要

```python
# 继承 Session 并重写 _summarize
class CustomSession(Session):
    def _summarize(self, messages: list) -> str:
        # 使用 LLM 生成摘要
        return llm_summarize(messages)
```

## 核心 API

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `Session(path)` | path: Path | Session | 创建会话实例 |
| `session.add_message(role, content, parent_id?)` | role: str, content: str | SessionEntry | 添加消息 |
| `session.get_messages()` | - | List[Dict] | 获取当前分支所有消息 |
| `session.branch(from_id)` | from_id: str | str | 创建分支，返回新分支 ID |
| `session.compact(keep_recent?)` | keep_recent: int = 20 | None | 压缩会话 |
| `session.navigate(target_id)` | target_id: str | List[SessionEntry] | 导航到指定条目 |
| `SessionRepo(root_path)` | root_path: Path | SessionRepo | 创建会话仓库 |
| `repo.create(cwd?)` | cwd: str | Session | 创建新会话 |
| `repo.open(path)` | path: Path | Session | 打开已有会话 |
| `repo.list(cwd?)` | cwd: str | List[Path] | 列出会话 |

## JSONL 文件格式

```jsonl
{"type":"session","version":3,"id":"abc-123","timestamp":"2026-01-01T00:00:00"}
{"id":"msg-1","parentId":null,"type":"message","role":"user","content":"你好","timestamp":"..."}
{"id":"msg-2","parentId":"msg-1","type":"message","role":"assistant","content":"你好！","timestamp":"..."}
```

## 依赖

| 依赖 | 版本 | 必需 |
|------|------|------|
| Python | 3.8+ | ✅ |

标准库依赖（无需安装）：json, uuid, pathlib, dataclasses

## 来源
- 原项目：pi-mini
- 来源模块：session_persistence.py
- 设计参考：Pi agent 的 session.ts + jsonl-storage.ts
