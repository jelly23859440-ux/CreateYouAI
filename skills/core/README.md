# Core Skills / 核心能力层

Agent 的"大脑"——没有这些，Agent 不成立。

## Skills

| Skill | 依赖 | 说明 |
|-------|------|------|
| [cron-scheduler](cron-scheduler/SKILL.md) | 无 | Cron 表达式解析 + 下次执行时间计算 |
| [token-estimator](token-estimator/SKILL.md) | 无 | Token 数量估算（支持多种模型） |
| [text-summarizer](text-summarizer/SKILL.md) | 无 / LLM API | 文本摘要生成（抽取式 + 生成式） |
| [memory-extractor](memory-extractor/SKILL.md) | 无 / LLM API | 从对话中提取关键信息 |
| [db-query](db-query/SKILL.md) | sqlite3（内置） | SQLite/PostgreSQL 数据库查询 |

## 零依赖 Skill

以下 Skill 无需安装额外依赖，直接可用：

- **cron-scheduler** — 纯 Python 实现，支持通配符、步骤、范围
- **token-estimator** — 纯数学计算，支持 Claude/GPT/Llama 等模型
- **db-query** — 使用 Python 内置 sqlite3 模块

## 可选 LLM 增强

以下 Skill 支持 LLM API 增强，但基础功能不需要：

- **text-summarizer** — 抽取式摘要无需 LLM，生成式摘要需要
- **memory-extractor** — 基础提取无需 LLM，高级提取需要
