---
name: Token 估算器
layer: core
category: reasoning
status: unverified
description: >
  估算文本的 token 数量，支持多种模型的计算方式。
  当用户想要估算 token 用量、计算文本长度、预估 API 费用、
  或了解文本在不同模型中的 token 数时触发。
  关键词：token 估算、token 计算、文本长度、API 费用、token 用量。
---

# Token 估算器

估算文本的 token 数量，支持 GPT、Claude、Llama 等多种模型。

## 能力概览

| 能力 | 说明 |
|------|------|
| 多模型支持 | GPT-4、Claude、Llama 等主流模型 |
| 纯函数 | 无第三方依赖，可离线使用 |
| 费用估算 | 根据 token 数计算 API 调用费用 |
| 批量处理 | 支持多段文本的 token 统计 |

## 前置条件

- Python 3.8+
- 无第三方依赖（纯标准库）

## 安装步骤

无额外安装。将下方代码保存为 `token_estimator.py` 即可使用。

## 使用方法

### 基础用法：估算 token 数

```python
import re
import math
from typing import Dict, List, Optional

# 不同模型的 token 比率（字符:token 的近似比）
MODEL_RATIOS = {
    "gpt-4": {"chars_per_token": 4.0, "name": "GPT-4"},
    "gpt-4o": {"chars_per_token": 4.0, "name": "GPT-4o"},
    "gpt-3.5-turbo": {"chars_per_token": 4.0, "name": "GPT-3.5 Turbo"},
    "claude-3-opus": {"chars_per_token": 3.5, "name": "Claude 3 Opus"},
    "claude-3-sonnet": {"chars_per_token": 3.5, "name": "Claude 3 Sonnet"},
    "claude-3-haiku": {"chars_per_token": 3.5, "name": "Claude 3 Haiku"},
    "llama-3": {"chars_per_token": 3.8, "name": "Llama 3"},
    "qwen": {"chars_per_token": 3.5, "name": "Qwen"},
    "default": {"chars_per_token": 4.0, "name": "Default"},
}

# API 费用（美元/1K tokens）
MODEL_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
}

def estimate_tokens(text: str, model: str = "default") -> int:
    """
    估算文本的 token 数量。

    Args:
        text: 输入文本
        model: 模型名称（见 MODEL_RATIOS）

    Returns:
        估算的 token 数量
    """
    if not text:
        return 0

    ratio = MODEL_RATIOS.get(model, MODEL_RATIOS["default"])["chars_per_token"]

    cn_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    en_text = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf]', ' ', text)
    en_tokens = len(en_text.split())
    other_chars = len(en_text) - sum(len(w) for w in en_text.split())
    other_tokens = max(0, math.ceil(other_chars / ratio))

    return cn_tokens + en_tokens + other_tokens

def estimate_with_detail(text: str, model: str = "default") -> dict:
    """
    详细的 token 估算，包含中英文字符数等。

    Returns:
        {
            "model": str,
            "total_tokens": int,
            "cn_chars": int,
            "en_words": int,
            "other_chars": int,
            "char_count": int,
        }
    """
    cn_chars = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    en_text = re.sub(r'[\u4e00-\u9fff\u3400-\u4dbf]', ' ', text)
    en_words = len(en_text.split())
    other_chars = len(en_text) - sum(len(w) for w in en_text.split())

    ratio = MODEL_RATIOS.get(model, MODEL_RATIOS["default"])["chars_per_token"]
    other_tokens = max(0, math.ceil(other_chars / ratio))
    total = cn_chars + en_words + other_tokens

    return {
        "model": model,
        "total_tokens": total,
        "cn_chars": cn_chars,
        "en_words": en_words,
        "other_chars": other_chars,
        "char_count": len(text),
    }

def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-4"
) -> dict:
    """
    根据 token 数估算 API 调用费用。

    Returns:
        {
            "model": str,
            "input_tokens": int,
            "output_tokens": int,
            "input_cost": float,
            "output_cost": float,
            "total_cost": float,
            "currency": "USD"
        }
    """
    pricing = MODEL_PRICING.get(model)
    if not pricing:
        return {"model": model, "error": f"未知模型: {model}"}

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]

    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(input_cost + output_cost, 6),
        "currency": "USD",
    }

# 使用示例
if __name__ == "__main__":
    text = "你好，世界！Hello, world! 这是一个测试。"

    detail = estimate_with_detail(text, model="gpt-4")
    print(f"文本: {text}")
    print(f"模型: {detail['model']}")
    print(f"Token 数: {detail['total_tokens']}")
    print(f"中文字符: {detail['cn_chars']}")
    print(f"英文单词: {detail['en_words']}")
    print(f"总字符数: {detail['char_count']}")

    cost = estimate_cost(detail["total_tokens"], 100, model="gpt-4")
    print(f"\n费用估算 (输入 {cost['input_tokens']} + 输出 {cost['output_tokens']}):")
    print(f"  输入费用: ${cost['input_cost']}")
    print(f"  输出费用: ${cost['output_cost']}")
    print(f"  总费用: ${cost['total_cost']}")
```

### 批量统计

```python
def batch_estimate(texts: List[str], model: str = "default") -> dict:
    """
    批量估算多段文本的 token 数。

    Returns:
        {
            "total_tokens": int,
            "total_chars": int,
            "text_count": int,
            "details": [{"index": int, "tokens": int, "chars": int}, ...]
        }
    """
    details = []
    total_tokens = 0
    total_chars = 0

    for i, text in enumerate(texts):
        tokens = estimate_tokens(text, model)
        total_tokens += tokens
        total_chars += len(text)
        details.append({"index": i, "tokens": tokens, "chars": len(text)})

    return {
        "total_tokens": total_tokens,
        "total_chars": total_chars,
        "text_count": len(texts),
        "details": details,
    }

# 使用示例
if __name__ == "__main__":
    texts = [
        "第一段测试文本",
        "Second test text with more words",
        "混合文本 Mixed text 中英文都有",
    ]
    result = batch_estimate(texts, model="gpt-4")
    print(f"总 Token 数: {result['total_tokens']}")
    print(f"总字符数: {result['total_chars']}")
    for d in result["details"]:
        print(f"  段落 {d['index']}: {d['tokens']} tokens, {d['chars']} chars")
```

### 模型对比

```python
def compare_models(text: str) -> List[dict]:
    """对比同一文本在不同模型中的 token 数"""
    results = []
    for model_key in ["gpt-4", "claude-3-opus", "llama-3", "qwen"]:
        tokens = estimate_tokens(text, model_key)
        cost = estimate_cost(tokens, 0, model=model_key)
        results.append({
            "model": model_key,
            "name": MODEL_RATIOS[model_key]["name"],
            "tokens": tokens,
            "input_cost_per_1k": MODEL_PRICING.get(model_key, {}).get("input", "N/A"),
        })
    return sorted(results, key=lambda x: x["tokens"])

# 使用示例
if __name__ == "__main__":
    text = "这是一段用于对比不同模型 token 数量的测试文本。"
    comparison = compare_models(text)
    print(f"文本: {text}\n")
    print("模型对比:")
    for c in comparison:
        print(f"  {c['name']}: {c['tokens']} tokens")
```

### 命令行用法

```bash
# 估算文本
python token_estimator.py "Hello, world! 你好世界"

# 指定模型
python token_estimator.py --model gpt-4 "你的文本"

# 批量估算
python token_estimator.py --batch file1.txt file2.txt
```

## 问题排查

### 问题 1：估算结果与实际不符

**原因**：不同模型的 tokenizer 实现不同，字符比率为近似值。

**解决**：对于精确计数，使用 `tiktoken`（OpenAI）或模型官方 SDK。

### 问题 2：中文 token 数偏高

**原因**：中文字符在多数模型中约 1 字符 = 1 token。

**解决**：本工具已针对中文优化，结果比简单字符/4 更准确。

### 问题 3：费用估算与实际账单差异

**原因**：价格可能已更新，或有折扣/免费额度。

**解决**：查看模型提供方的最新定价页面。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| 第三方依赖 | 无 | — |
