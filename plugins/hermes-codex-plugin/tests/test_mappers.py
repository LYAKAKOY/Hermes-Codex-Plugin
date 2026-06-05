import unittest

from hermes_codex_plugin.application.memory.mapper import (
    MemoryEntryMapper,
    MemoryStatsMapper,
)
from hermes_codex_plugin.application.skills.mapper import SkillDraftMapper
from hermes_codex_plugin.domain.memory.entities import MemoryEntry
from hermes_codex_plugin.domain.skills.entities import SkillDraft
from hermes_codex_plugin.presentation.skills.formatting import format_skill_draft


class MapperTest(unittest.TestCase):
    def test_memory_entry_mapper_converts_value_objects_to_dto(self) -> None:
        entry = MemoryEntry.from_raw(
            id=1,
            kind="rule",
            scope="project",
            source="test",
            session_id="s1",
            turn_id="t1",
            cwd="/tmp/project",
            content="Always run tests.",
            metadata={"tag": "qa"},
            created_at="2026-06-05T12:00:00Z",
        )

        dto = MemoryEntryMapper().to_dto(entry)

        self.assertEqual(dto.id, 1)
        self.assertEqual(dto.kind, "rule")
        self.assertEqual(dto.scope, "project")
        self.assertEqual(dto.source, "test")
        self.assertEqual(dto.session_id, "s1")
        self.assertEqual(dto.turn_id, "t1")
        self.assertEqual(dto.cwd, "/tmp/project")
        self.assertEqual(dto.content, "Always run tests.")
        self.assertEqual(dto.metadata, {"tag": "qa"})
        self.assertEqual(dto.created_at, "2026-06-05T12:00:00Z")

    def test_memory_stats_mapper_normalizes_missing_values(self) -> None:
        dto = MemoryStatsMapper().to_dto({})

        self.assertEqual(dto.db_path, "")
        self.assertFalse(dto.fts5)
        self.assertEqual(dto.total_entries, 0)
        self.assertEqual(dto.by_kind, {})

    def test_skill_draft_mapper_converts_value_objects_to_dto(self) -> None:
        draft = SkillDraft.from_raw(
            name="review-flow",
            description="Use for review workflows.",
            rules=["Always run tests."],
        )

        dto = SkillDraftMapper().to_dto(draft)

        self.assertEqual(dto.name, "review-flow")
        self.assertEqual(dto.description, "Use for review workflows.")
        self.assertEqual(dto.rules, ["Always run tests."])

    def test_skill_draft_dto_renders_markdown(self) -> None:
        draft = SkillDraft.from_raw(
            name="review-flow",
            description="Use for review workflows.",
            rules=["Always run tests.", "Prefer focused changes."],
        )

        markdown = format_skill_draft(SkillDraftMapper().to_dto(draft))

        self.assertIn("name: review-flow", markdown)
        self.assertIn("description: Use for review workflows.", markdown)
        self.assertIn("- Always run tests.", markdown)
        self.assertIn("- Prefer focused changes.", markdown)


if __name__ == "__main__":
    unittest.main()
