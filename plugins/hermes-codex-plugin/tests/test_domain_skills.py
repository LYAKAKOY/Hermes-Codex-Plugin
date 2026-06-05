import unittest

from hermes_codex_plugin.domain.skills.entities import SkillDraft
from hermes_codex_plugin.domain.skills.services import (
    extract_rules,
    normalize_skill_name,
    split_sentences,
)
from hermes_codex_plugin.domain.skills.value_objects import (
    SkillDescription,
    SkillName,
    SkillRules,
)
from hermes_codex_plugin.domain.memory.entities import MemoryEntry


class SkillDomainTest(unittest.TestCase):
    def test_skill_draft_uses_value_object_fields(self) -> None:
        draft = SkillDraft.from_raw(
            name="review-flow",
            description="Use for review workflows.",
            rules=["Always run tests.", "Prefer focused changes."],
        )

        self.assertEqual(draft.skill_name, SkillName("review-flow"))
        self.assertEqual(draft.skill_description, SkillDescription("Use for review workflows."))
        self.assertEqual(
            draft.skill_rules,
            SkillRules(["Always run tests.", "Prefer focused changes."]),
        )

    def test_skill_value_objects_reject_empty_values(self) -> None:
        invalid_cases = [
            (SkillName, ""),
            (SkillDescription, " "),
            (SkillRules, []),
            (SkillRules, [""]),
        ]

        for value_object, value in invalid_cases:
            with self.subTest(value_object=value_object.__name__):
                with self.assertRaises(ValueError):
                    value_object(value)

    def test_extract_rules_keeps_only_actionable_unique_sentences(self) -> None:
        entries = [
            MemoryEntry.from_raw(
                id=1,
                kind="rule",
                scope="global",
                source="test",
                session_id="",
                turn_id="",
                cwd="",
                content=(
                    "Always run pytest before release. "
                    "Always run pytest before release. "
                    "What should I do next? Random observation."
                ),
                metadata={},
                created_at="2026-06-05T12:00:00Z",
            ),
            MemoryEntry.from_raw(
                id=2,
                kind="rule",
                scope="global",
                source="test",
                session_id="",
                turn_id="",
                cwd="",
                content="Must check edge cases.",
                metadata={},
                created_at="2026-06-05T12:01:00Z",
            ),
        ]

        rules = extract_rules(entries)

        self.assertEqual(
            rules,
            [
                "Always run pytest before release.",
                "Must check edge cases.",
            ],
        )

    def test_sentence_split_and_skill_name_normalization_handle_noise(self) -> None:
        self.assertEqual(split_sentences("A rule.\n\nAnother rule!"), ["A rule.", "Another rule!"])
        self.assertEqual(normalize_skill_name("  Review Flow!!  "), "review-flow")
        self.assertEqual(normalize_skill_name("!!!"), "learned-workflow")


if __name__ == "__main__":
    unittest.main()
