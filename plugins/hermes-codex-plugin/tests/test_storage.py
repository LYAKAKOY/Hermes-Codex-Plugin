from pathlib import Path
import tempfile
import unittest

from hermes_codex_plugin.infrastructure.persistence.sqlite_memory_repository import (
    SQLiteMemoryRepository,
)


class SQLiteMemoryRepositoryTest(unittest.TestCase):
    def test_add_and_search_with_full_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            entry_id = store.add_entry(
                "Always run unit tests before shipping Python changes.",
                kind="rule",
                scope="project",
            )

            results = store.search("unit tests python", limit=5)

            self.assertEqual(results[0].entry_id.to_raw(), entry_id)
            self.assertIn("unit tests", results[0].body.to_raw())
            self.assertEqual(store.stats()["total_entries"], 1)

    def test_delete_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            entry_id = store.add_entry("Remember this temporary fact.")

            self.assertTrue(store.delete_entry(entry_id))
            self.assertFalse(store.search("temporary fact"))

    def test_search_can_filter_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            rule_id = store.add_entry("Project convention: use DDD.", kind="project_rule")
            store.add_entry("User asked about DDD.", kind="prompt")

            results = store.search("DDD", kinds=["project_rule"])

            self.assertEqual([entry.entry_id.to_raw() for entry in results], [rule_id])

    def test_duplicate_entry_returns_existing_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")

            first_id = store.add_entry("Remember this once.", kind="memory")
            second_id = store.add_entry("Remember this once.", kind="memory")

            self.assertEqual(first_id, second_id)
            self.assertEqual(store.stats()["total_entries"], 1)

    def test_redacts_obvious_secrets_before_storage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")

            store.add_entry("token=super-secret-value", kind="memory")
            results = store.search("REDACTED")

            self.assertEqual(results[0].body.to_raw(), "[REDACTED]")
            self.assertFalse(store.search("super-secret-value"))

    def test_empty_content_and_empty_query_are_ignored_safely(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")

            with self.assertRaises(ValueError):
                store.add_entry("   ")

            self.assertEqual(store.search("   "), [])

    def test_search_can_exclude_kinds_and_filter_by_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            same_cwd_id = store.add_entry(
                "HCP_CWD_FILTER same project.",
                kind="memory",
                cwd="/tmp/current",
            )
            global_id = store.add_entry(
                "HCP_CWD_FILTER global memory.",
                kind="rule",
                cwd="",
            )
            store.add_entry(
                "HCP_CWD_FILTER other project.",
                kind="memory",
                cwd="/tmp/other",
            )

            results = store.search(
                "HCP_CWD_FILTER",
                cwd="/tmp/current",
                exclude_kinds=["rule"],
            )

            ids = [entry.entry_id.to_raw() for entry in results]

            self.assertEqual(ids, [same_cwd_id])
            self.assertNotIn(global_id, ids)

    def test_like_search_fallback_finds_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")
            entry_id = store.add_entry("HCP_LIKE_FALLBACK works.", kind="memory")
            store.has_fts = lambda: False

            results = store.search("HCP_LIKE_FALLBACK")

            self.assertEqual([entry.entry_id.to_raw() for entry in results], [entry_id])

    def test_delete_missing_entry_returns_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = SQLiteMemoryRepository(Path(tmp) / "memory.sqlite3")

            self.assertFalse(store.delete_entry(999))


if __name__ == "__main__":
    unittest.main()
