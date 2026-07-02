---
name: 文本摘要生成器
layer: core
category: memory
description: >
  对长文本生成摘要，支持抽取式和生成式两种摘要方式。
  当用户需要总结文章、提取要点、压缩文本、生成摘要时触发。
  关键词：摘要、总结、提取要点、压缩文本、文本总结、文章摘要。
---

# 文本摘要生成器

对长文本生成简洁准确的摘要，支持抽取式和生成式两种方式。

## 能力概览

| 能力 | 说明 |
|------|------|
| 抽取式摘要 | 从原文中抽取关键句子组成摘要 |
| 生成式摘要 | 基于 LLM 生成全新的摘要文本 |
| 多语言支持 | 中文、英文等多语言文本处理 |
| 长文本处理 | 支持超长文本的分段摘要 |
| 关键词提取 | 自动提取文本核心关键词 |

## 前置条件

- Python 3.8+
- 抽取式摘要：无第三方依赖
- 生成式摘要：需要 LLM API（OpenAI/Anthropic/本地模型）

## 安装步骤

### 方案一：抽取式摘要（无需额外依赖）

直接将代码保存为 `text_summarizer.py` 即可使用。

### 方案二：生成式摘要（需要 LLM API）

```bash
pip install openai>=1.0.0
```

验证安装：
```bash
python -c "import openai; print('OpenAI SDK 版本:', openai.__version__)"
```

## 使用方法

### 抽取式摘要：基于 TextRank 算法

```python
import re
import math
from collections import Counter
from typing import List, Tuple

def extractive_summary(text: str, num_sentences: int = 3) -> str:
    """
    抽取式摘要：从原文中抽取最重要的句子。
    
    Args:
        text: 输入文本
        num_sentences: 返回的句子数量
        
    Returns:
        摘要文本
    """
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return text
    
    sentence_scores = {}
    word_freq = get_word_frequencies(text)
    
    for i, sentence in enumerate(sentences):
        score = calculate_sentence_score(sentence, word_freq, i, len(sentences))
        sentence_scores[i] = score
    
    top_indices = sorted(
        sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    )
    
    return ' '.join(sentences[i] for i in top_indices)

def split_sentences(text: str) -> List[str]:
    """分割文本为句子"""
    pattern = r'[。！？.!?；;]+'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if len(s.strip()) > 2]

def get_word_frequencies(text: str) -> dict:
    """计算词频"""
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text.lower())
    return dict(Counter(words))

def calculate_sentence_score(
    sentence: str, 
    word_freq: dict, 
    position: int, 
    total: int
) -> float:
    """计算句子重要性得分"""
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', sentence.lower())
    if not words:
        return 0.0
    
    freq_score = sum(word_freq.get(w, 0) for w in words) / len(words)
    position_score = 1.0 - abs(position - total / 2) / (total / 2 + 1)
    
    return freq_score * 0.7 + position_score * 0.3

# 使用示例
if __name__ == "__main__":
    text = """
    人工智能正在改变我们的生活方式。从智能手机到自动驾驶汽车，AI技术已经渗透到各个领域。
    机器学习作为AI的核心技术，让计算机能够从数据中学习并做出决策。
    深度学习则进一步推动了图像识别、自然语言处理等领域的突破。
    然而，AI的发展也带来了隐私、就业等方面的挑战。
    我们需要在享受AI便利的同时，认真思考如何应对其带来的社会影响。
    """
    summary = extractive_summary(text, num_sentences=2)
    print("抽取式摘要：", summary)
```

### 生成式摘要：基于 LLM API

```python
import os
from typing import Optional

def generate_summary(
    text: str,
    max_length: int = 200,
    language: str = "zh",
    api_key: Optional[str] = None
) -> str:
    """
    生成式摘要：使用 LLM 生成全新的摘要。
    
    Args:
        text: 输入文本
        max_length: 摘要最大长度（字符数）
        language: 语言（zh/en）
        api_key: OpenAI API Key（或设置 OPENAI_API_KEY 环境变量）
        
    Returns:
        生成的摘要文本
    """
    try:
        import openai
    except ImportError:
        raise ImportError("请安装 openai: pip install openai>=1.0.0")
    
    client = openai.OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
    
    lang_prompt = "用中文" if language == "zh" else "in English"
    prompt = f"""请对以下文本生成一段简洁的摘要，控制在{max_length}字以内。
    
文本内容：
{text[:4000]}

要求：
1. 保留核心观点和关键信息
2. 语言流畅自然
3. 不超过{max_length}字

请直接输出摘要内容，不要加前缀："""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()

# 使用示例
if __name__ == "__main__":
    text = "你的长文本内容..."
    summary = generate_summary(text, max_length=150)
    print("生成式摘要：", summary)
```

### 关键词提取

```python
def extract_keywords(text: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """
    提取文本关键词。
    
    Args:
        text: 输入文本
        top_k: 返回的关键词数量
        
    Returns:
        [(关键词, 重要性得分), ...]
    """
    word_freq = get_word_frequencies(text)
    total = sum(word_freq.values())
    
    if total == 0:
        return []
    
    scored_words = [
        (word, count / total) 
        for word, count in word_freq.items()
        if len(word) > 1
    ]
    
    return sorted(scored_words, key=lambda x: x[1], reverse=True)[:top_k]

# 使用示例
if __name__ == "__main__":
    text = "机器学习是人工智能的重要分支，深度学习是机器学习的子集..."
    keywords = extract_keywords(text, top_k=3)
    print("关键词：", [(w, f"{s:.3f}") for w, s in keywords])
```

### 命令行用法

```bash
# 抽取式摘要
python text_summarizer.py --method extractive --sentences 3 input.txt

# 生成式摘要
python text_summarizer.py --method generative --max-length 200 input.txt

# 提取关键词
python text_summarizer.py --keywords --top-k 5 input.txt
```

## 问题排查

### 问题 1：抽取式摘要质量不佳

**原因**：文本过短或句子结构复杂。

**解决**：确保文本至少有5个句子；对于短文本，直接返回原文。

### 问题 2：生成式摘要 API 调用失败

**原因**：API Key 未设置或无效。

**解决**：
```bash
export OPENAI_API_KEY="your-api-key"
python -c "import openai; print(openai.OpenAI().models.list())"
```

### 问题 3：中文分句不准确

**原因**：正则表达式未覆盖所有标点。

**解决**：已内置支持中文标点（。！？；），如需扩展可修改 `split_sentences` 函数。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| openai | ≥1.0.0 | 可选（生成式摘要） |
| 第三方依赖 | 无 | 抽取式摘要无需额外依赖 |

## Agent 执行规范

### 核心约束
- **先判断文本长度**：短文本直接返回，无需摘要
- **选择合适方法**：无 API 时使用抽取式，有 API 时可选生成式
- **验证输出**：摘要应保留原文核心信息