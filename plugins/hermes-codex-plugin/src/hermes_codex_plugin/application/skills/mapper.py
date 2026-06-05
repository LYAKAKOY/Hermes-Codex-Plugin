from hermes_codex_plugin.application.skills.dto import SkillDraftDTO
from hermes_codex_plugin.domain.skills.entities import SkillDraft


class SkillDraftMapper:
    def to_dto(self, draft: SkillDraft) -> SkillDraftDTO:
        return SkillDraftDTO(
            name=draft.skill_name.to_raw(),
            description=draft.skill_description.to_raw(),
            rules=list(draft.skill_rules.to_raw()),
        )
