from dataclasses import dataclass
from typing import List

from hermes_codex_plugin.domain.skills.value_objects import (
    SkillDescription,
    SkillName,
    SkillRules,
)


@dataclass(frozen=True)
class SkillDraft:
    skill_name: SkillName
    skill_description: SkillDescription
    skill_rules: SkillRules

    @classmethod
    def from_raw(
        cls,
        *,
        name: str,
        description: str,
        rules: List[str],
    ) -> "SkillDraft":
        return cls(
            skill_name=SkillName(name),
            skill_description=SkillDescription(description),
            skill_rules=SkillRules(rules),
        )
