---
name: Cron 表达式解析器
layer: core
category: reasoning
status: unverified
description: >
  解析标准 cron 表达式，计算下次执行时间。
  当用户想要设置定时任务、解析 cron 表达式、查看定时计划、
  或验证 cron 表达式是否正确时触发。
  关键词：cron、定时任务、定时执行、schedule、cron 表达式、下次执行时间。
---

# Cron 表达式解析器

解析标准 5 字段 cron 表达式，计算下次执行时间，支持通配符、步骤、范围、列表。

## 能力概览

| 能力 | 说明 |
|------|------|
| 表达式解析 | 分/时/日/月/周 五字段解析 |
| 下次执行 | 计算从给定时间起的下 N 次执行时间 |
| 通配符支持 | `*`、`,`、`-`、`/` 全支持 |
| 校验 | 检查表达式是否合法 |

## 前置条件

- Python 3.8+
- 无第三方依赖（纯标准库）

## 安装步骤

无额外安装。将下方代码保存为 `cron_parser.py` 即可使用。

## 使用方法

### 基础用法：解析并计算下次执行

```python
from datetime import datetime, timedelta
from typing import List, Optional

class CronParser:
    """标准 cron 表达式解析器（5 字段格式：分 时 日 月 周）"""

    FIELD_RANGES = {
        "minute": (0, 59),
        "hour": (0, 23),
        "day": (1, 31),
        "month": (1, 12),
        "weekday": (0, 7),
    }

    def __init__(self, expression: str):
        self.expression = expression.strip()
        self.fields = self.expression.split()
        if len(self.fields) != 5:
            raise ValueError(f"需要 5 个字段，得到 {len(self.fields)} 个: {self.expression}")
        self.parsed = {}
        field_names = ["minute", "hour", "day", "month", "weekday"]
        for name, value in zip(field_names, self.fields):
            self.parsed[name] = self._parse_field(name, value)

    def _parse_field(self, name: str, value: str) -> set:
        lo, hi = self.FIELD_RANGES[name]
        result = set()

        for part in value.split(","):
            result |= self._parse_part(part, lo, hi)

        return result

    def _parse_part(self, part: str, lo: int, hi: int) -> set:
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            if step <= 0:
                raise ValueError(f"步长必须大于 0: {part}")
            if base == "*":
                return set(range(lo, hi + 1, step))
            else:
                start, end = self._parse_range(base, lo, hi)
                return set(range(start, end + 1, step))
        elif "-" in part:
            start, end = self._parse_range(part, lo, hi)
            return set(range(start, end + 1))
        elif part == "*":
            return set(range(lo, hi + 1))
        else:
            val = int(part)
            if not (lo <= val <= hi):
                raise ValueError(f"值 {val} 超出范围 [{lo}-{hi}]")
            return {val}

    def _parse_range(self, part: str, lo: int, hi: int) -> tuple:
        start_str, end_str = part.split("-", 1)
        start, end = int(start_str), int(end_str)
        if not (lo <= start <= hi and lo <= end <= hi):
            raise ValueError(f"范围 {part} 超出有效范围 [{lo}-{hi}]")
        return start, end

    def matches(self, dt: datetime) -> bool:
        """检查给定时间是否匹配此 cron 表达式"""
        if dt.minute not in self.parsed["minute"]:
            return False
        if dt.hour not in self.parsed["hour"]:
            return False
        if dt.month not in self.parsed["month"]:
            return False

        weekday = dt.weekday()
        if weekday == 6:
            weekday = 0
        else:
            weekday += 1

        if "day" in self.fields and "weekday" in self.fields:
            day_match = dt.day in self.parsed["day"]
            weekday_match = weekday in self.parsed["weekday"]
            return day_match and weekday_match
        elif "day" in self.fields and self.fields[2] != "*":
            return dt.day in self.parsed["day"]
        elif "weekday" in self.fields and self.fields[4] != "*":
            return weekday in self.parsed["weekday"]

        return True

    def next_run(self, after: Optional[datetime] = None, count: int = 1) -> List[datetime]:
        """计算从 after 时间起的下 N 次执行时间"""
        if after is None:
            after = datetime.now()

        results = []
        current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
        max_iterations = 366 * 24 * 60

        for _ in range(max_iterations):
            if self.matches(current):
                results.append(current)
                if len(results) >= count:
                    break
            current += timedelta(minutes=1)

        return results

    def describe(self) -> str:
        """生成人类可读的描述"""
        parts = []
        f = self.fields

        if f[0] == "*":
            parts.append("每分钟")
        elif "/" in f[0]:
            step = f[0].split("/")[1]
            parts.append(f"每 {step} 分钟")
        else:
            parts.append(f"在第 {f[0]} 分钟")

        if f[1] == "*":
            parts.append("每小时")
        elif "/" in f[1]:
            step = f[1].split("/")[1]
            parts.append(f"每 {step} 小时")
        else:
            parts.append(f"在 {f[1]} 时")

        if f[2] == "*" and f[4] == "*":
            parts.append("每天")
        elif f[4] != "*":
            weekday_names = {0: "日", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}
            if "," in f[4]:
                days = [weekday_names.get(int(d), d) for d in f[4].split(",")]
                parts.append(f"每周 {'/'.join(days)}")
            else:
                parts.append(f"周{'日一二三四五六七'[int(f[4])]}" if f[4].isdigit() else f"周 {f[4]}")

        if f[3] != "*":
            parts.append(f"在 {f[3]} 月")

        return "，".join(parts)

# 使用示例
if __name__ == "__main__":
    cron = CronParser("*/5 * * * *")
    print(f"表达式: {cron.expression}")
    print(f"描述: {cron.describe()}")
    print(f"\n下次执行:")
    for t in cron.next_run(count=5):
        print(f"  {t.strftime('%Y-%m-%d %H:%M')}")

    print(f"\n匹配测试:")
    test_time = datetime(2025, 7, 1, 10, 15)
    print(f"  {test_time}: {'匹配' if cron.matches(test_time) else '不匹配'}")
```

### 常用 cron 表达式速查

| 表达式 | 含义 |
|--------|------|
| `* * * * *` | 每分钟 |
| `0 * * * *` | 每小时整点 |
| `0 0 * * *` | 每天午夜 |
| `0 9 * * 1-5` | 工作日上午 9 点 |
| `*/5 * * * *` | 每 5 分钟 |
| `0 0 1 * *` | 每月 1 日午夜 |
| `30 8 * * 1` | 每周一 8:30 |
| `0 */2 * * *` | 每 2 小时 |

### 批量验证

```python
def validate_cron_expressions(expressions: List[str]) -> List[dict]:
    """批量验证 cron 表达式"""
    results = []
    for expr in expressions:
        try:
            cron = CronParser(expr)
            results.append({
                "expression": expr,
                "valid": True,
                "description": cron.describe(),
                "next_run": cron.next_run(count=1)[0].isoformat(),
            })
        except Exception as e:
            results.append({
                "expression": expr,
                "valid": False,
                "error": str(e),
            })
    return results

# 使用示例
if __name__ == "__main__":
    exprs = ["*/5 * * * *", "0 9 * * 1-5", "60 * * * *", "0 0 1 * *"]
    results = validate_cron_expressions(exprs)
    for r in results:
        if r["valid"]:
            print(f"✓ {r['expression']}: {r['description']}")
        else:
            print(f"✗ {r['expression']}: {r['error']}")
```

## 问题排查

### 问题 1：`ValueError: 需要 5 个字段`

**原因**：cron 表达式字段数不对。

**解决**：标准 cron 需要 5 个字段（分 时 日 月 周），检查是否多写了秒字段。

### 问题 2：计算下次执行返回空列表

**原因**：表达式不匹配任何时间（如日期+星期矛盾）。

**解决**：检查日期和星期字段是否冲突。例如 `0 0 31 2 *`（2 月 31 日）无效。

### 问题 3：`ValueError: 值 XX 超出范围`

**原因**：字段值超出有效范围。

**解决**：检查各字段范围：分(0-59)、时(0-23)、日(1-31)、月(1-12)、周(0-7)。

### 问题 4：性能问题（计算太慢）

**原因**：表达式过于稀疏（如 `0 0 1 1 *`），需要遍历大量时间。

**解决**：增加 `max_iterations` 上限，或优化跳过逻辑（先跳到匹配的月/日）。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| 第三方依赖 | 无 | — |
