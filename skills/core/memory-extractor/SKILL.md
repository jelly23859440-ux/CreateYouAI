---
name: 记忆提取器
layer: core
category: memory
status: unverified
description: >
  从对话中提取关键信息，支持事实、事件、知识等类型的记忆。
  当用户需要分析对话、提取要点、整理聊天记录、构建知识库时触发。
  关键词：记忆提取、对话分析、信息提取、事实提取、知识整理、聊天记录。
---

# 记忆提取器

从对话或文本中提取结构化的关键信息，支持多种记忆类型。

## 能力概览

| 能力 | 说明 |
|------|------|
| 事实提取 | 提取人名、地点、时间等事实信息 |
| 事件提取 | 识别并结构化事件信息 |
| 知识提取 | 提取概念、关系、定义等知识 |
| 情感分析 | 识别对话中的情感倾向 |
| 实体识别 | 基于规则的命名实体识别 |

## 前置条件

- Python 3.8+
- 基础提取：无第三方依赖
- 高级提取：需要 LLM API（可选）

## 安装步骤

基础版本无额外依赖。如需使用 LLM 增强：

```bash
pip install openai>=1.0.0
```

## 使用方法

### 基础事实提取

```python
import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Fact:
    """事实信息"""
    category: str
    content: str
    confidence: float
    source: str = ""

@dataclass
class Event:
    """事件信息"""
    action: str
    time: Optional[str]
    location: Optional[str]
    participants: List[str]
    details: str

class MemoryExtractor:
    """对话记忆提取器"""
    
    TIME_PATTERNS = [
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
        (r'(\d{1,2})月(\d{1,2})日', lambda m: f"{datetime.now().year}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
        (r'今天|昨日|昨天|前天', lambda m: datetime.now().strftime("%Y-%m-%d")),
        (r'下周[一二三四五六日]', lambda m: m.group()),
    ]
    
    LOCATION_KEYWORDS = ['在', '到', '去', '位于', '地址']
    
    def extract_facts(self, text: str) -> List[Fact]:
        """提取事实信息"""
        facts = []
        
        people = self._extract_people(text)
        for person in people:
            facts.append(Fact("人物", person, 0.9, text))
        
        times = self._extract_times(text)
        for time in times:
            facts.append(Fact("时间", time, 0.85, text))
        
        locations = self._extract_locations(text)
        for loc in locations:
            facts.append(Fact("地点", loc, 0.8, text))
        
        numbers = self._extract_numbers(text)
        for num in numbers:
            facts.append(Fact("数据", num, 0.95, text))
        
        return facts
    
    def extract_events(self, text: str) -> List[Event]:
        """提取事件信息"""
        events = []
        sentences = re.split(r'[。！？.!?]+', text)
        
        for sentence in sentences:
            if any(kw in sentence for kw in ['进行', '完成', '开始', '结束', '参加', '举办']):
                event = Event(
                    action=self._extract_action(sentence),
                    time=self._extract_first_time(sentence),
                    location=self._extract_first_location(sentence),
                    participants=self._extract_participants(sentence),
                    details=sentence.strip()
                )
                events.append(event)
        
        return events
    
    def extract_knowledge(self, text: str) -> List[Dict]:
        """提取知识点"""
        knowledge = []
        
        definitions = re.findall(r'(.+?)是(.+?)[。.]', text)
        for term, definition in definitions:
            knowledge.append({
                "type": "definition",
                "term": term.strip(),
                "definition": definition.strip()
            })
        
        relationships = re.findall(r'(.+?)包括(.+?)[。.]', text)
        for concept, items in relationships:
            knowledge.append({
                "type": "relationship",
                "concept": concept.strip(),
                "items": [i.strip() for i in re.split(r'[,，、和与]', items)]
            })
        
        return knowledge
    
    def _extract_people(self, text: str) -> List[str]:
        """提取人名"""
        patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([\u4e00-\u9fff]{2,4})(?:说|认为|表示|提到|告诉)',
        ]
        people = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            people.extend(matches)
        return list(set(people))
    
    def _extract_times(self, text: str) -> List[str]:
        """提取时间"""
        times = []
        for pattern, formatter in self.TIME_PATTERNS:
            matches = re.finditer(pattern, text)
            for match in matches:
                times.append(formatter(match))
        return list(set(times))
    
    def _extract_locations(self, text: str) -> List[str]:
        """提取地点"""
        locations = []
        for kw in self.LOCATION_KEYWORDS:
            pattern = rf'{kw}([\u4e00-\u9fff\w]{{2,10}}?)(?:[，,。.]|$)'
            matches = re.findall(pattern, text)
            locations.extend(matches)
        return list(set(locations))
    
    def _extract_numbers(self, text: str) -> List[str]:
        """提取数字数据"""
        patterns = [
            r'(\d+(?:\.\d+)?(?:%|元|美元|万|亿))',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
        ]
        numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            numbers.extend(matches)
        return list(set(numbers))
    
    def _extract_action(self, sentence: str) -> str:
        """提取动作"""
        match = re.search(r'(进行|完成|开始|结束|参加|举办)([\u4e00-\u9fff]+)', sentence)
        return match.group(0) if match else sentence[:20]
    
    def _extract_first_time(self, sentence: str) -> Optional[str]:
        """提取第一个时间"""
        for pattern, formatter in self.TIME_PATTERNS:
            match = re.search(pattern, sentence)
            if match:
                return formatter(match)
        return None
    
    def _extract_first_location(self, sentence: str) -> Optional[str]:
        """提取第一个地点"""
        for kw in self.LOCATION_KEYWORDS:
            match = re.search(rf'{kw}([\u4e00-\u9fff\w]{{2,10}})', sentence)
            if match:
                return match.group(1)
        return None
    
    def _extract_participants(self, sentence: str) -> List[str]:
        """提取参与者"""
        return self._extract_people(sentence)

# 使用示例
if __name__ == "__main__":
    extractor = MemoryExtractor()
    
    text = """
    2024年3月15日，张三和李四在北京参加了技术会议。
    会议讨论了人工智能的发展趋势。张三认为深度学习是未来方向。
    本次会议共有50人参加，持续了3天。
    """
    
    print("=== 事实提取 ===")
    facts = extractor.extract_facts(text)
    for fact in facts:
        print(f"  [{fact.category}] {fact.content} (置信度: {fact.confidence})")
    
    print("\n=== 事件提取 ===")
    events = extractor.extract_events(text)
    for event in events:
        print(f"  动作: {event.action}")
        print(f"  时间: {event.time}")
        print(f"  地点: {event.location}")
        print(f"  参与者: {event.participants}")
    
    print("\n=== 知识提取 ===")
    knowledge = extractor.extract_knowledge(text)
    for k in knowledge:
        print(f"  类型: {k['type']}")
        if k['type'] == 'definition':
            print(f"  定义: {k['term']} = {k['definition']}")
```

### LLM 增强提取

```python
import os
from typing import Optional, Dict, List

def extract_with_llm(
    text: str,
    extraction_type: str = "all",
    api_key: Optional[str] = None
) -> Dict:
    """
    使用 LLM 进行高级记忆提取。
    
    Args:
        text: 输入文本
        extraction_type: 提取类型 (facts/events/knowledge/all)
        api_key: OpenAI API Key
        
    Returns:
        结构化的提取结果
    """
    try:
        import openai
    except ImportError:
        raise ImportError("请安装 openai: pip install openai>=1.0.0")
    
    client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""分析以下文本，提取结构化信息。

文本：
{text[:3000]}

请以 JSON 格式输出：
{{
    "facts": [{{"category": "类别", "content": "内容", "confidence": 0.9}}],
    "events": [{{"action": "动作", "time": "时间", "location": "地点", "participants": ["人物"]}}],
    "knowledge": [{{"type": "定义/关系/因果", "content": "内容"}}],
    "sentiment": "positive/negative/neutral",
    "summary": "一句话总结"
}}"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    import json
    return json.loads(response.choices[0].message.content)

# 使用示例
if __name__ == "__main__":
    text = "用户反馈系统在高峰期响应缓慢，工程师已定位到数据库查询瓶颈，预计下周修复。"
    result = extract_with_llm(text)
    print("情感倾向:", result.get("sentiment"))
    print("总结:", result.get("summary"))
```

### 对话历史分析

```python
def analyze_conversation(messages: List[Dict]) -> Dict:
    """
    分析完整对话历史。
    
    Args:
        messages: [{"role": "user/assistant", "content": "..."}, ...]
        
    Returns:
        对话分析结果
    """
    extractor = MemoryExtractor()
    
    all_text = " ".join(msg["content"] for msg in messages)
    
    user_messages = [m["content"] for m in messages if m["role"] == "user"]
    assistant_messages = [m["content"] for m in messages if m["role"] == "assistant"]
    
    return {
        "total_messages": len(messages),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "facts": [vars(f) for f in extractor.extract_facts(all_text)],
        "events": [vars(e) for e in extractor.extract_events(all_text)],
        "knowledge": extractor.extract_knowledge(all_text),
        "topics": _extract_topics(all_text),
    }

def _extract_topics(text: str) -> List[str]:
    """提取对话主题"""
    from collections import Counter
    words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
    word_freq = Counter(words)
    return [word for word, _ in word_freq.most_common(5)]

# 使用示例
if __name__ == "__main__":
    conversation = [
        {"role": "user", "content": "我昨天在北京参加了技术会议"},
        {"role": "assistant", "content": "会议讨论了什么内容？"},
        {"role": "user", "content": "主要讨论AI发展趋势，张三做了主题演讲"},
    ]
    analysis = analyze_conversation(conversation)
    print("对话主题:", analysis["topics"])
```

## 问题排查

### 问题 1：中文人名提取不准确

**原因**：基于正则的规则有限。

**解决**：使用 LLM 增强提取，或自定义人名模式。

### 问题 2：时间提取遗漏

**原因**：时间表达多样，正则未覆盖。

**解决**：扩展 `TIME_PATTERNS` 列表，添加更多时间模式。

### 问题 3：LLM 提取结果不稳定

**原因**：温度参数过高。

**解决**：设置 `temperature=0.2` 获得更稳定的结构化输出。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| openai | ≥1.0.0 | 可选（LLM 增强） |
| 第三方依赖 | 无 | 基础提取无需额外依赖 |

## Agent 执行规范

### 核心约束
- **先判断文本类型**：对话、文章、新闻等不同类型使用不同策略
- **保留原文引用**：提取结果应可追溯到原文位置
- **置信度标注**：基于规则的提取需标注置信度
