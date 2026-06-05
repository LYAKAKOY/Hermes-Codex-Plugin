from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, final

from hermes_codex_plugin.domain.memory.entities import MemoryEntry


@final
class MemoryRepository(Protocol):
    db_path: Path

    def add_entry(
        self,
        content: str,
        *,
        kind: str = "memory",
        scope: str = "global",
        source: str = "",
        session_id: str = "",
        turn_id: str = "",
        cwd: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int: ...

    def delete_entry(self, entry_id: int) -> bool: ...

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        cwd: Optional[str] = None,
        scope: Optional[str] = None,
        kinds: Optional[List[str]] = None,
        exclude_kinds: Optional[List[str]] = None,
    ) -> List[MemoryEntry]: ...

    def recent(
        self,
        *,
        limit: int = 20,
        kind: Optional[str] = None,
    ) -> List[MemoryEntry]: ...

    def stats(self) -> Dict[str, Any]: ...
