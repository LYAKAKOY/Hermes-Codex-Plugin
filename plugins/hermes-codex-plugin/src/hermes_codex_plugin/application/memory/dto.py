from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class MemoryEntryDTO:
    id: int
    kind: str
    scope: str
    source: str
    session_id: str
    turn_id: str
    cwd: str
    content: str
    metadata: Dict[str, Any]
    created_at: str


@dataclass(frozen=True)
class MemoryStatsDTO:
    db_path: str
    fts5: bool
    total_entries: int
    by_kind: Dict[str, int]
