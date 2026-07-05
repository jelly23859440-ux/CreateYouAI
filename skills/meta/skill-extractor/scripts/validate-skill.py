#!/usr/bin/env python3
"""
Skill 格式验证脚本

验证 SKILL.md 文件是否符合 CreateYouAI 格式标准。
阶段 4 组合验证时调用此脚本。

用法:
    python validate-skill.py <skill-dir>
    python validate-skill.py skills/meta/skill-extractor/
    python validate-skill.py skills/  # 验证目录下所有 skill

检查项:
    1. SKILL.md 文件存在
    2. YAML frontmatter 格式正确
    3. 必需字段完整 (name/layer/category/status/description)
    4. name 符合命名规则 (小写连字符, 1-64 字符)
    5. layer 值合法 (core/action/identity/meta/scenarios)
    6. category 值合法
    7. 正文包含必需章节 (功能说明, 使用方法)
    8. 无个人路径/密钥等敏感信息
"""

import sys
import os
import re
import json
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


# 合法值
VALID_LAYERS = {"core", "action", "identity", "meta", "scenarios"}
VALID_CATEGORIES = {
    "core": {"conversation", "reasoning", "memory"},
    "action": {"code", "tool", "file", "web", "device"},
    "identity": {"personality", "safety", "knowledge"},
    "meta": {"ai-builder", "skill-learn", "contribute"},
    "scenarios": {"coding-ai", "research-ai", "creative-ai", "daily-ai"},
}

# 命名规则: 小写字母+数字+连字符, 1-64字符, 不以连字符开头/结尾, 无连续连字符
NAME_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

# 敏感信息检测
SENSITIVE_PATTERNS = [
    (r'[A-Za-z]:\\Users\\', "个人路径"),
    (r'/home/\w+/', "Linux 个人路径"),
    (r'(?:password|passwd|secret|token|api[_-]?key)\s*[=:]\s*\S+', "疑似密钥/密码"),
    (r'sk-[a-zA-Z0-9]{20,}', "疑似 OpenAI API Key"),
]


class ValidationResult:
    def __init__(self, skill_path):
        self.skill_path = skill_path
        self.errors = []
        self.warnings = []
        self.passed = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def ok(self, msg):
        self.passed.append(msg)

    @property
    def is_valid(self):
        return len(self.errors) == 0

    def report(self):
        status = "PASS" if self.is_valid else "FAIL"
        print(f"\n{'='*60}")
        print(f"  {status}: {self.skill_path}")
        print(f"{'='*60}")

        if self.passed:
            print(f"\n  Passed ({len(self.passed)}):")
            for item in self.passed:
                print(f"    [OK] {item}")

        if self.warnings:
            print(f"\n  Warnings ({len(self.warnings)}):")
            for item in self.warnings:
                print(f"    [WARN] {item}")

        if self.errors:
            print(f"\n  Errors ({len(self.errors)}):")
            for item in self.errors:
                print(f"    [FAIL] {item}")

        print()
        return self.is_valid


def parse_frontmatter(content):
    """解析 YAML frontmatter"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None, None

    yaml_text = match.group(1)
    body = content[match.end():]

    try:
        data = yaml.safe_load(yaml_text)
        return data, body
    except yaml.YAMLError as e:
        return {"_error": str(e)}, None


def find_skill_dirs(path):
    """找到所有包含 SKILL.md 的目录"""
    path = Path(path)
    if path.is_file() and path.name == "SKILL.md":
        return [path.parent]
    if path.is_dir():
        return sorted(set(p.parent for p in path.rglob("SKILL.md")))
    return []


def validate_skill(skill_dir):
    """验证单个 skill 目录"""
    result = ValidationResult(str(skill_dir))
    skill_md = skill_dir / "SKILL.md"

    # 1. 文件存在
    if not skill_md.exists():
        result.error("SKILL.md 文件不存在")
        return result
    result.ok("SKILL.md 文件存在")

    content = skill_md.read_text(encoding="utf-8")

    # 2. frontmatter 解析
    frontmatter, body = parse_frontmatter(content)
    if frontmatter is None:
        result.error("缺少 YAML frontmatter (--- ... ---)")
        return result

    if "_error" in frontmatter:
        result.error(f"YAML 解析错误: {frontmatter['_error']}")
        return result
    result.ok("YAML frontmatter 格式正确")

    # 3. 必需字段
    required_fields = ["name", "layer", "category", "status", "description"]
    for field in required_fields:
        if field not in frontmatter:
            result.error(f"缺少必需字段: {field}")
        elif not frontmatter[field]:
            result.error(f"字段为空: {field}")
        else:
            result.ok(f"字段完整: {field}")

    # 4. name 命名规则
    name = frontmatter.get("name", "")
    if name:
        if len(name) > 64:
            result.error(f"name 超过 64 字符 (当前 {len(name)})")
        elif not NAME_PATTERN.match(name):
            result.error(f"name 不符合命名规则 (小写字母+数字+连字符): '{name}'")
        else:
            result.ok(f"name 命名合规: {name}")

    # 5. layer 合法性
    layer = frontmatter.get("layer", "")
    if layer and layer not in VALID_LAYERS:
        result.error(f"layer 值非法: '{layer}' (合法值: {', '.join(sorted(VALID_LAYERS))})")
    elif layer:
        result.ok(f"layer 合法: {layer}")

    # 6. category 合法性
    category = frontmatter.get("category", "")
    if layer and category:
        valid_cats = VALID_CATEGORIES.get(layer, set())
        if category not in valid_cats:
            result.error(
                f"category '{category}' 不属于 layer '{layer}' "
                f"(合法值: {', '.join(sorted(valid_cats))})"
            )
        else:
            result.ok(f"category 合法: {layer}/{category}")

    # 7. status 合法性
    status = frontmatter.get("status", "")
    if status and status not in ("unverified", "verified"):
        result.error(f"status 值非法: '{status}' (合法值: unverified, verified)")
    elif status:
        result.ok(f"status 合法: {status}")

    # 8. description 内容
    desc = frontmatter.get("description", "")
    if desc:
        if "关键词" not in str(desc):
            result.warn("description 中未找到'关键词'，建议添加触发关键词")
        else:
            result.ok("description 包含关键词")

    # 9. 正文必需章节
    if body:
        if not re.search(r'^#+\s*功能说明', body, re.MULTILINE):
            result.warn("正文缺少 '功能说明' 章节")
        else:
            result.ok("正文包含 '功能说明'")

        if not re.search(r'^#+\s*使用方法', body, re.MULTILINE):
            result.warn("正文缺少 '使用方法' 章节")
        else:
            result.ok("正文包含 '使用方法'")

    # 10. 敏感信息检测
    for pattern, desc in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            result.error(f"检测到敏感信息 ({desc}): {matches[0]}")

    # 11. 目录结构检查
    scripts_dir = skill_dir / "scripts"
    references_dir = skill_dir / "references"
    if scripts_dir.exists():
        result.ok(f"scripts/ 目录存在 ({len(list(scripts_dir.iterdir()))} 个文件)")
    if references_dir.exists():
        result.ok(f"references/ 目录存在 ({len(list(references_dir.iterdir()))} 个文件)")

    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python validate-skill.py <skill-dir>")
        print("     python validate-skill.py skills/meta/skill-extractor/")
        print("     python validate-skill.py skills/  # 验证所有 skill")
        sys.exit(1)

    target = sys.argv[1]
    skill_dirs = find_skill_dirs(target)

    if not skill_dirs:
        print(f"未找到 SKILL.md 文件: {target}")
        sys.exit(1)

    print(f"找到 {len(skill_dirs)} 个 skill 待验证")

    all_valid = True
    results = []
    for skill_dir in skill_dirs:
        result = validate_skill(skill_dir)
        results.append(result)
        if not result.is_valid:
            all_valid = False

    # 汇总
    print(f"\n{'='*60}")
    print(f"  验证汇总: {len(results)} 个 skill")
    print(f"  通过: {sum(1 for r in results if r.is_valid)} | 失败: {sum(1 for r in results if not r.is_valid)}")
    print(f"{'='*60}\n")

    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
