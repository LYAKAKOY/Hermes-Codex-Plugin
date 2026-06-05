from typing import Iterable, List

from hermes_codex_plugin.domain.memory.entities import MemoryEntry
from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository


DURABLE_KINDS = ["project_rule", "user_rule", "rule", "memory"]
RECALL_KINDS = ["project_rule", "user_rule", "rule", "memory", "assistant", "transcript"]


class MemoryRecallService:
    def __init__(self, memory_repo: MemoryRepository) -> None:
        self._memory_repo = memory_repo

    def recall(self, query: str, *, limit: int, cwd: str) -> List[MemoryEntry]:
        same_cwd_durable = self._memory_repo.search(
            query,
            limit=max(limit, 8),
            cwd=cwd,
            kinds=DURABLE_KINDS,
        )
        cross_cwd_durable = self._memory_repo.search(
            query,
            limit=max(limit, 8),
            cwd=None,
            kinds=DURABLE_KINDS,
        )
        same_cwd_supplemental = self._memory_repo.search(
            query,
            limit=limit,
            cwd=cwd,
            kinds=RECALL_KINDS,
        )
        cross_cwd_supplemental = self._memory_repo.search(
            query,
            limit=limit,
            cwd=None,
            kinds=RECALL_KINDS,
        )
        return dedupe_entries(
            same_cwd_durable
            + cross_cwd_durable
            + same_cwd_supplemental
            + cross_cwd_supplemental
        )[:limit]

    def recent_durable(self, *, limit: int) -> List[MemoryEntry]:
        entries: List[MemoryEntry] = []
        for kind in DURABLE_KINDS:
            entries.extend(self._memory_repo.recent(limit=limit, kind=kind))
        entries.sort(key=lambda entry: entry.entry_id.to_raw(), reverse=True)
        return entries[:limit]


def dedupe_entries(entries: Iterable[MemoryEntry]) -> List[MemoryEntry]:
    seen = set()
    unique: List[MemoryEntry] = []
    for entry in entries:
        entry_id = entry.entry_id.to_raw()
        if entry_id in seen:
            continue
        seen.add(entry_id)
        unique.append(entry)
    return unique
