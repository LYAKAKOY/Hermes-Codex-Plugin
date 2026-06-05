from dataclasses import dataclass
from typing import List, Optional

from hermes_codex_plugin.application.memory.dto import MemoryEntryDTO
from hermes_codex_plugin.application.memory.mapper import MemoryEntryMapper
from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository


@dataclass(frozen=True)
class SearchMemory:
    query: str
    limit: int = 5
    cwd: Optional[str] = None
    scope: Optional[str] = None
    kinds: Optional[List[str]] = None
    exclude_kinds: Optional[List[str]] = None


class SearchMemoryHandler:
    def __init__(
        self,
        memory_repo: MemoryRepository,
        memory_mapper: MemoryEntryMapper,
    ) -> None:
        self._memory_repo = memory_repo
        self._memory_mapper = memory_mapper

    def __call__(self, query: SearchMemory) -> List[MemoryEntryDTO]:
        entries = self._memory_repo.search(
            query.query,
            limit=query.limit,
            cwd=query.cwd,
            scope=query.scope,
            kinds=query.kinds,
            exclude_kinds=query.exclude_kinds,
        )
        return [self._memory_mapper.to_dto(entry) for entry in entries]
