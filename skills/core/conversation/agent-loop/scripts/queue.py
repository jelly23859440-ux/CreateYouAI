"""
代理循环 - 消息队列

提供 PendingMessageQueue，支持 steering（打断）和 follow-up（追加）两种队列模式。
"""

from typing import List, Dict, Optional


class PendingMessageQueue:
    """消息队列"""
    
    def __init__(self, mode: str = "all"):
        """
        Args:
            mode: "all" 保留所有消息，"one-at-a-time" 只保留最新一条
        """
        self.mode = mode
        self.queue: List[Dict] = []
    
    def add(self, message: Dict):
        """添加消息"""
        if self.mode == "one-at-a-time":
            self.queue = [message]  # 只保留最新的一条
        else:
            self.queue.append(message)
    
    def drain(self) -> List[Dict]:
        """取出所有消息并清空队列"""
        messages = self.queue.copy()
        self.queue = []
        return messages
    
    def peek(self) -> Optional[Dict]:
        """查看队列中的第一条消息"""
        return self.queue[0] if self.queue else None
    
    def is_empty(self) -> bool:
        return len(self.queue) == 0
