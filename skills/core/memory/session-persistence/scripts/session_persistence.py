"""
会话持久化 - 通用模式

核心功能：
- JSONL 存储（每行一个 JSON 对象）
- 树形结构（id + parentId）
- 分支管理
- 压缩（保留最近 N 条，旧消息生成摘要）
- 会话仓库（多会话管理）

用法：
    from session_persistence import Session, SessionRepo

    repo = SessionRepo(Path("./sessions"))
    session = repo.create()
    session.add_message("user", "hello")
    messages = session.get_messages()
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionEntry:
    """会话条目"""
    id: str
    parent_id: Optional[str]
    type: str  # message / compaction / branch_summary / label / session_info
    role: Optional[str] = None
    content: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


class SessionStorage:
    """会话存储接口 - JSONL 格式"""
    
    def __init__(self, path: Path):
        self.path = path
        self.entries: Dict[str, SessionEntry] = {}
        self.header: Optional[Dict] = None
        self._load()
    
    def _load(self):
        """从 JSONL 文件加载"""
        if not self.path.exists():
            return
        
        with open(self.path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                
                data = json.loads(line)
                
                if i == 0 and data.get("type") == "session":
                    self.header = data
                else:
                    entry = SessionEntry(
                        id=data["id"],
                        parent_id=data.get("parentId"),
                        type=data["type"],
                        role=data.get("role"),
                        content=data.get("content"),
                        timestamp=data.get("timestamp", datetime.now().isoformat()),
                        metadata=data.get("metadata", {})
                    )
                    self.entries[entry.id] = entry
    
    def save(self):
        """保存到 JSONL 文件"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.path, 'w', encoding='utf-8') as f:
            if self.header:
                f.write(json.dumps(self.header, ensure_ascii=False) + '\n')
            
            for entry in self._get_ordered_entries():
                data = {
                    "id": entry.id,
                    "parentId": entry.parent_id,
                    "type": entry.type,
                    "role": entry.role,
                    "content": entry.content,
                    "timestamp": entry.timestamp,
                    "metadata": entry.metadata
                }
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def _get_ordered_entries(self) -> List[SessionEntry]:
        """按 parentId 链深度优先排序"""
        if not self.entries:
            return []
        
        roots = [e for e in self.entries.values() if e.parent_id is None]
        if not roots:
            return list(self.entries.values())
        
        ordered = []
        visited = set()
        
        def dfs(entry_id):
            if entry_id in visited:
                return
            visited.add(entry_id)
            
            entry = self.entries.get(entry_id)
            if entry:
                ordered.append(entry)
            
            children = [e for e in self.entries.values() if e.parent_id == entry_id]
            for child in sorted(children, key=lambda x: x.timestamp):
                dfs(child.id)
        
        for root in roots:
            dfs(root.id)
        
        return ordered
    
    def add(self, entry: SessionEntry):
        """添加条目"""
        self.entries[entry.id] = entry
    
    def get(self, entry_id: str) -> Optional[SessionEntry]:
        """获取条目"""
        return self.entries.get(entry_id)
    
    def get_path_to_root(self, entry_id: str) -> List[SessionEntry]:
        """获取从指定条目到根节点的路径"""
        path = []
        current_id = entry_id
        
        while current_id:
            entry = self.entries.get(current_id)
            if entry:
                path.append(entry)
                current_id = entry.parent_id
            else:
                break
        
        return list(reversed(path))
    
    def get_children(self, entry_id: str) -> List[SessionEntry]:
        """获取子条目"""
        return [e for e in self.entries.values() if e.parent_id == entry_id]
    
    def get_leaf_id(self) -> Optional[str]:
        """获取叶子节点 ID（最新条目）"""
        if not self.entries:
            return None
        
        leaves = []
        for entry in self.entries.values():
            children = self.get_children(entry.id)
            if not children:
                leaves.append(entry)
        
        if not leaves:
            return None
        
        return max(leaves, key=lambda x: x.timestamp).id


class Session:
    """会话管理"""
    
    def __init__(self, path: Path):
        self.path = path
        self.storage = SessionStorage(path)
        
        if not self.storage.header:
            self.storage.header = {
                "type": "session",
                "version": 1,
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat()
            }
    
    def add_message(self, role: str, content: str, parent_id: str = None) -> SessionEntry:
        """添加消息"""
        if parent_id is None:
            parent_id = self.storage.get_leaf_id()
        
        entry = SessionEntry(
            id=str(uuid.uuid4()),
            parent_id=parent_id,
            type="message",
            role=role,
            content=content
        )
        
        self.storage.add(entry)
        self.storage.save()
        return entry
    
    def branch(self, from_id: str) -> str:
        """从指定条目创建分支，返回新分支的叶子 ID"""
        entry = SessionEntry(
            id=str(uuid.uuid4()),
            parent_id=from_id,
            type="branch_summary",
            content="分支点"
        )
        self.storage.add(entry)
        self.storage.save()
        return entry.id
    
    def navigate(self, target_id: str) -> List[SessionEntry]:
        """导航到指定条目，返回路径"""
        return self.storage.get_path_to_root(target_id)
    
    def get_messages(self) -> List[Dict]:
        """获取当前分支的所有消息"""
        leaf_id = self.storage.get_leaf_id()
        if not leaf_id:
            return []
        
        path = self.storage.get_path_to_root(leaf_id)
        messages = []
        
        for entry in path:
            if entry.type == "message":
                msg = {"role": entry.role, "content": entry.content}
                messages.append(msg)
        
        return messages
    
    def compact(self, keep_recent: int = 20):
        """压缩会话，保留最近 N 条消息"""
        messages = self.get_messages()
        if len(messages) <= keep_recent:
            return
        
        recent = messages[-keep_recent:]
        old = messages[:-keep_recent]
        summary = self._summarize(old)
        
        leaf_id = self.storage.get_leaf_id()
        entry = SessionEntry(
            id=str(uuid.uuid4()),
            parent_id=leaf_id,
            type="compaction",
            content=summary,
            metadata={"kept_recent": keep_recent}
        )
        self.storage.add(entry)
        self.storage.save()
    
    def _summarize(self, messages: List[Dict]) -> str:
        """生成消息摘要 - 可重写以使用 LLM"""
        user_msgs = [m for m in messages if m.get("role") == "user"]
        if not user_msgs:
            return "之前的对话"
        
        topics = []
        for msg in user_msgs[:5]:
            content = msg.get("content", "")[:50]
            topics.append(content)
        
        return f"之前的对话主题：{'、'.join(topics)}"
    
    def list_entries(self) -> List[SessionEntry]:
        """列出所有条目"""
        return self.storage._get_ordered_entries()
    
    def delete(self):
        """删除会话文件"""
        if self.path.exists():
            self.path.unlink()


class SessionRepo:
    """会话仓库 - 管理多个会话"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.root_path.mkdir(parents=True, exist_ok=True)
    
    def create(self, group: str = "default") -> Session:
        """创建新会话"""
        group_dir = self.root_path / group
        group_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{session_id}.jsonl"
        
        session_path = group_dir / filename
        return Session(session_path)
    
    def open(self, session_path: Path) -> Session:
        """打开已有会话"""
        return Session(session_path)
    
    def list(self, group: str = None) -> List[Path]:
        """列出会话"""
        if group:
            group_dir = self.root_path / group
            if group_dir.exists():
                return sorted(group_dir.glob("*.jsonl"))
            return []
        
        sessions = []
        for group_dir in self.root_path.iterdir():
            if group_dir.is_dir():
                sessions.extend(sorted(group_dir.glob("*.jsonl")))
        return sessions
    
    def delete(self, session_path: Path):
        """删除会话"""
        if session_path.exists():
            session_path.unlink()
