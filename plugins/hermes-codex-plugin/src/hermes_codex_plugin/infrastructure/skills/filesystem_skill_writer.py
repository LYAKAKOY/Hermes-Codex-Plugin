from pathlib import Path
from typing import Optional

from hermes_codex_plugin.application.skills.dto import SkillDraftDTO


def write_skill(
    draft: SkillDraftDTO,
    markdown: str,
    *,
    skills_root: Optional[Path] = None,
    overwrite: bool = False,
) -> Path:
    root = skills_root or (Path.home() / ".agents" / "skills")
    skill_dir = root / draft.name
    skill_path = skill_dir / "SKILL.md"
    if skill_path.exists() and not overwrite:
        raise FileExistsError("{} already exists".format(skill_path))
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(markdown, encoding="utf-8")
    return skill_path
