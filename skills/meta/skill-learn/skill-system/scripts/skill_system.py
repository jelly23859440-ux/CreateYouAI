"""
技能系统 - 精简版（去除业务逻辑，保留通用模式）

核心功能：
- SKILL.md 解析（YAML frontmatter + markdown body）
- 多位置发现（用户级 > 项目级 > 显式路径）
- 名称冲突处理（先加载优先）
- 渐进加载（只在 prompt 中放描述，内容按需加载）
- 验证规则（name: 小写 a-z 0-9-，最长 64 字符）
"""

import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class Skill:
    """技能定义"""
    name: str
    description: str
    content: str
    file_path: str
    disable_model_invocation: bool = False
    source: str = ""  # user/project/path


@dataclass
class SkillDiagnostic:
    """技能诊断信息"""
    code: str  # file_info_failed, list_failed, read_failed, parse_failed, invalid_metadata, collision
    message: str
    path: str
    severity: str = "warning"  # warning/error


class SkillSystem:
    """技能系统 - 管理技能的加载、发现、验证"""

    NAME_REGEX = re.compile(r'^[a-z0-9-]+$')
    MAX_NAME_LENGTH = 64
    MAX_DESCRIPTION_LENGTH = 1024

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.diagnostics: List[SkillDiagnostic] = []

    def load_skill(self, skill_path: Path) -> Optional[Skill]:
        """加载单个 SKILL.md"""
        if not skill_path.exists():
            return None

        content = skill_path.read_text(encoding='utf-8')
        frontmatter, body = self._parse_frontmatter(content)

        name = frontmatter.get('name', skill_path.parent.name)
        description = frontmatter.get('description', '')

        if not self._validate_name(name):
            return None

        if not description:
            return None

        return Skill(
            name=name,
            description=description[:self.MAX_DESCRIPTION_LENGTH],
            content=body,
            file_path=str(skill_path),
            disable_model_invocation=frontmatter.get('disable-model-invocation', False)
        )

    def load_directory(self, dir_path: Path, source: str = "project") -> List[Skill]:
        """递归加载目录下的所有技能"""
        loaded = []

        if not dir_path.exists():
            return loaded

        skill_md = dir_path / "SKILL.md"
        if skill_md.exists():
            skill = self.load_skill(skill_md)
            if skill:
                skill.source = source
                self.skills[skill.name] = skill
                loaded.append(skill)
            return loaded

        for item in sorted(dir_path.iterdir()):
            if item.name.startswith('.') or item.name == 'node_modules':
                continue

            if item.is_dir():
                loaded.extend(self.load_directory(item, source))
            elif item.suffix == '.md':
                skill = self.load_skill(item)
                if skill:
                    skill.source = source
                    if skill.name not in self.skills:
                        self.skills[skill.name] = skill
                        loaded.append(skill)

        return loaded

    def load_from_hierarchy(self, project_root: Path, explicit_paths: List[Path] = None) -> List[Skill]:
        """从层级结构加载（用户级 > 项目级 > 显式路径）"""
        all_skills = []

        user_skills_dir = Path.home() / ".pi" / "skills"
        all_skills.extend(self.load_directory(user_skills_dir, "user"))

        project_skills_dir = project_root / ".pi" / "skills"
        all_skills.extend(self.load_directory(project_skills_dir, "project"))

        if explicit_paths:
            for path in explicit_paths:
                all_skills.extend(self.load_directory(path, "path"))

        return all_skills

    def format_for_prompt(self) -> str:
        """格式化为 system prompt 中的可用技能列表"""
        lines = ["<available_skills>"]

        for name, skill in self.skills.items():
            if skill.disable_model_invocation:
                continue

            lines.append("  <skill>")
            lines.append(f"    <name>{skill.name}</name>")
            lines.append(f"    <description>{skill.description}</description>")
            lines.append(f"    <location>{skill.file_path}</location>")
            lines.append("  </skill>")

        lines.append("</available_skills>")
        return "\n".join(lines)

    def format_invocation(self, skill: Skill, additional_instructions: str = None) -> str:
        """格式化技能调用（加载完整内容）"""
        lines = [
            f'<skill name="{skill.name}" location="{skill.file_path}">',
            f"References are relative to {Path(skill.file_path).parent}",
            "",
            skill.content,
        ]

        if additional_instructions:
            lines.extend(["", additional_instructions])

        lines.append("</skill>")
        return "\n".join(lines)

    def _parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """解析 YAML frontmatter"""
        if not content.startswith('---'):
            return {}, content

        end = content.find('\n---', 3)
        if end == -1:
            return {}, content

        yaml_str = content[3:end].strip()
        body = content[end + 4:].strip()

        try:
            frontmatter = yaml.safe_load(yaml_str)
            return frontmatter or {}, body
        except yaml.YAMLError:
            return {}, content

    def _validate_name(self, name: str) -> bool:
        """验证技能名称"""
        if len(name) > self.MAX_NAME_LENGTH:
            return False
        if not self.NAME_REGEX.match(name):
            return False
        if name.startswith('-') or name.endswith('-'):
            return False
        if '--' in name:
            return False
        return True
