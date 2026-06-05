from typing import Any, Dict

from hermes_codex_plugin.application.memory.dto import MemoryEntryDTO, MemoryStatsDTO
from hermes_codex_plugin.domain.memory.entities import MemoryEntry


class MemoryEntryMapper:
    def to_dto(self, entry: MemoryEntry) -> MemoryEntryDTO:
        return MemoryEntryDTO(
            id=entry.entry_id.to_raw(),
            kind=entry.memory_kind.to_raw(),
            scope=entry.memory_scope.to_raw(),
            source=entry.memory_source.to_raw(),
            session_id=entry.session.to_raw(),
            turn_id=entry.turn.to_raw(),
            cwd=entry.current_working_directory.to_raw(),
            content=entry.body.to_raw(),
            metadata=entry.meta.to_raw(),
            created_at=entry.created_time.to_raw(),
        )


class MemoryStatsMapper:
    def to_dto(self, stats: Dict[str, Any]) -> MemoryStatsDTO:
        return MemoryStatsDTO(
            db_path=str(stats.get("db_path") or ""),
            fts5=bool(stats.get("fts5")),
            total_entries=int(stats.get("total_entries") or 0),
            by_kind=dict(stats.get("by_kind") or {}),
        )
