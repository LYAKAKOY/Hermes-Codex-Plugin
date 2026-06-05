from dataclasses import dataclass
from typing import Optional

from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository
from hermes_codex_plugin.domain.skills.entities import SkillDraft
from hermes_codex_plugin.domain.skills.services import extract_rules, normalize_skill_name


@dataclass(frozen=True)
class ProposeSkill:
    query: str = ""
    name: str = "learned-workflow"
    description: Optional[str] = None
    limit: int = 25


class ProposeSkillHandler:
    def __init__(self, memory_repo: MemoryRepository) -> None:
        self._memory_repo = memory_repo

    def __call__(self, query: ProposeSkill) -> SkillDraft:
        entries = (
            self._memory_repo.search(query.query, limit=query.limit)
            if query.query
            else self._memory_repo.recent(limit=query.limit)
        )
        rules = extract_rules(entries)
        if not rules:
            rules = ["Review local memory before repeating this workflow."]
        description = query.description
        if description is None:
            description = (
                "Use when Codex should apply learned local workflow rules related to {}."
            ).format(query.query or "recent work")
        return SkillDraft.from_raw(
            name=normalize_skill_name(query.name),
            description=description,
            rules=rules[:12],
        )
