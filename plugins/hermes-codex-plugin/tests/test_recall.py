from pathlib import Path
import tempfile
import unittest

from hermes_codex_plugin.application.memory.recall import MemoryRecallService
from hermes_codex_plugin.infrastructure.persistence.sqlite_memory_repository import (
    SQLiteMemoryRepository,
)


class MemoryRecallServiceTest(unittest.TestCase):
    def test_recall_includes_same_cwd_global_and_cross_chat_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            same_cwd_id = store.add_entry(
                "Rule: HCP_RECALL_SAME_CWD should be used.",
                kind="rule",
                cwd="/tmp/current",
            )
            global_id = store.add_entry(
                "Memory: HCP_RECALL_GLOBAL should be used.",
                kind="memory",
            )
            cross_chat_id = store.add_entry(
                "Assistant note: HCP_RECALL_CROSS_CHAT should be used.",
                kind="assistant",
                session_id="old-chat",
                cwd="/tmp/other",
            )

            results = MemoryRecallService(store).recall(
                "HCP_RECALL_SAME_CWD HCP_RECALL_GLOBAL HCP_RECALL_CROSS_CHAT",
                limit=10,
                cwd="/tmp/current",
            )

            self.assertEqual(
                {entry.entry_id.to_raw() for entry in results},
                {same_cwd_id, global_id, cross_chat_id},
            )

    def test_recent_durable_ignores_transient_prompt_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            prompt_id = store.add_entry("Prompt history should not be standing memory.", kind="prompt")
            rule_id = store.add_entry("Always keep durable rules.", kind="user_rule")

            results = MemoryRecallService(store).recent_durable(limit=5)
            ids = [entry.entry_id.to_raw() for entry in results]

            self.assertIn(rule_id, ids)
            self.assertNotIn(prompt_id, ids)

    def test_recall_deduplicates_entries_found_by_multiple_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            entry_id = store.add_entry(
                "Rule: HCP_DEDUPE should only appear once.",
                kind="rule",
                cwd="/tmp/current",
            )

            results = MemoryRecallService(store).recall(
                "HCP_DEDUPE",
                limit=10,
                cwd="/tmp/current",
            )

            ids = [entry.entry_id.to_raw() for entry in results]

            self.assertEqual(ids.count(entry_id), 1)


if __name__ == "__main__":
    unittest.main()
