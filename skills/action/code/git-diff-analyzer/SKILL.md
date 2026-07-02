---
name: Git Diff 分析器
layer: action
category: code
description: >
  读取 git diff 输出，分析代码变更，生成结构化的变更报告。
  当用户想要查看代码变更、分析提交历史、生成变更报告、
  按作者或时间筛选改动时触发。
  关键词：git diff、代码变更、变更报告、提交历史、代码审查、code review。
---

# Git Diff 分析器

解析 `git diff` 输出，生成结构化变更报告，支持多维度筛选。

## 能力概览

| 能力 | 说明 |
|------|------|
| 变更分析 | 解析 unified diff，提取文件级/行级变更 |
| 报告生成 | 输出 JSON/Markdown 格式的变更摘要 |
| 多维筛选 | 按文件名、作者、时间范围过滤 |
| 统计汇总 | 新增/删除/修改行数统计 |

## 前置条件

- Git 已安装并在 PATH 中
- Python 3.8+

## 安装步骤

无需额外安装，使用 Python 标准库即可。

验证 Git 可用：

```bash
git --version
```

验证 Python 可用：

```bash
python --version
```

## 使用方法

### 方法 1：分析当前未提交的变更

```python
import subprocess
import re
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class FileChange:
    filename: str
    additions: int = 0
    deletions: int = 0
    status: str = "modified"  # added, deleted, modified, renamed

@dataclass
class DiffReport:
    total_additions: int = 0
    total_deletions: int = 0
    files: List[FileChange] = field(default_factory=list)

def get_diff(repo_path: str = ".") -> str:
    """获取当前工作区的 diff 输出"""
    result = subprocess.run(
        ["git", "diff"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result.stdout

def get_staged_diff(repo_path: str = ".") -> str:
    """获取已暂存的 diff 输出"""
    result = subprocess.run(
        ["git", "diff", "--cached"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_diff(diff_text: str) -> DiffReport:
    """解析 unified diff 输出"""
    report = DiffReport()
    current_file = None

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            if match:
                current_file = FileChange(filename=match.group(1))
                report.files.append(current_file)

        elif line.startswith("+") and not line.startswith("+++"):
            if current_file:
                current_file.additions += 1
                report.total_additions += 1

        elif line.startswith("-") and not line.startswith("---"):
            if current_file:
                current_file.deletions += 1
                report.total_deletions += 1

    return report

def get_file_status(filename: str, repo_path: str = ".") -> str:
    """获取文件状态（added/deleted/modified）"""
    result = subprocess.run(
        ["git", "status", "--porcelain", filename],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    if result.stdout.startswith("A"):
        return "added"
    elif result.stdout.startswith("D"):
        return "deleted"
    elif result.stdout.startswith("R"):
        return "renamed"
    return "modified"

def analyze(repo_path: str = ".") -> DiffReport:
    """主分析函数"""
    diff_text = get_diff(repo_path)
    if not diff_text:
        diff_text = get_staged_diff(repo_path)

    report = parse_diff(diff_text)

    for file_change in report.files:
        file_change.status = get_file_status(file_change.filename, repo_path)

    return report

def to_json(report: DiffReport) -> dict:
    """转换为 JSON 格式"""
    return {
        "summary": {
            "total_files": len(report.files),
            "total_additions": report.total_additions,
            "total_deletions": report.total_deletions,
        },
        "files": [
            {
                "filename": f.filename,
                "additions": f.additions,
                "deletions": f.deletions,
                "status": f.status,
            }
            for f in report.files
        ],
    }

def to_markdown(report: DiffReport) -> str:
    """转换为 Markdown 报告"""
    lines = [
        "# Git Diff 变更报告\n",
        f"**文件数**: {len(report.files)}",
        f"**新增行数**: +{report.total_additions}",
        f"**删除行数**: -{report.total_deletions}\n",
        "## 文件变更明细\n",
        "| 文件 | 状态 | 新增 | 删除 |",
        "|------|------|------|------|",
    ]
    for f in report.files:
        lines.append(
            f"| `{f.filename}` | {f.status} | +{f.additions} | -{f.deletions} |"
        )
    return "\n".join(lines)

# 使用示例
if __name__ == "__main__":
    report = analyze(".")
    print(to_markdown(report))
```

### 方法 2：按作者筛选提交

```python
import subprocess
import json
from datetime import datetime

def get_commits_by_author(
    author: str,
    repo_path: str = ".",
    since: str = None,
    until: str = None
) -> list:
    """按作者和时间范围查询提交"""
    cmd = ["git", "log", f"--author={author}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]
    if since:
        cmd.append(f"--since={since}")
    if until:
        cmd.append(f"--until={until}")

    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|")
        if len(parts) == 5:
            commits.append({
                "hash": parts[0],
                "author_name": parts[1],
                "author_email": parts[2],
                "date": parts[3],
                "message": parts[4],
            })
    return commits

def get_commit_diff_stats(commit_hash: str, repo_path: str = ".") -> dict:
    """获取单个提交的统计信息"""
    result = subprocess.run(
        ["git", "diff", "--stat", f"{commit_hash}~1", commit_hash],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    return {"hash": commit_hash, "stat": result.stdout}

# 使用示例
if __name__ == "__main__":
    commits = get_commits_by_author(
        "张三",
        since="2025-01-01",
        until="2025-12-31"
    )
    for c in commits:
        print(f"{c['date']} - {c['message']} ({c['hash'][:8]})")
```

### 命令行用法

```bash
# 分析当前变更
python git_diff_analyzer.py

# 分析特定仓库
python git_diff_analyzer.py --repo /path/to/repo

# 按作者筛选
python git_diff_analyzer.py --author "张三" --since 2025-01-01

# 输出 JSON
python git_diff_analyzer.py --format json
```

## 问题排查

### 问题 1：`git: command not found`

**原因**：Git 未安装或未加入 PATH。

**解决**：安装 Git 并确保 `git --version` 能正常输出。

### 问题 2：`fatal: not a git repository`

**原因**：当前目录不是 Git 仓库。

**解决**：切换到 Git 仓库目录，或用 `--repo` 参数指定路径。

### 问题 3：空 diff 输出

**原因**：工作区没有未提交的变更。

**解决**：使用 `--staged` 参数分析已暂存的变更，或先 `git add` 文件。

## 依赖

| 依赖 | 版本 | 类型 |
|------|------|------|
| Python | 3.8+ | 必需 |
| Git | 2.0+ | 必需 |
