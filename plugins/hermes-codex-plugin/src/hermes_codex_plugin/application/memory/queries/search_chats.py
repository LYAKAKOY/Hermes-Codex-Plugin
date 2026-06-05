from dataclasses import dataclass
from typing import List

from hermes_codex_plugin.application.memory.dto import MemoryEntryDTO
from hermes_codex_plugin.application.memory.mapper import MemoryEntryMapper
from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository


@dataclass(frozen=True)
class SearchChats:
    query: str
    limit: int = 5


class SearchChatsHandler:
    def __init__(
        self,
        memory_repo: MemoryRepository,
        memory_mapper: MemoryEntryMapper,
    ) -> None:
        self._memory_repo = memory_repo
        self._memory_mapper = memory_mapper

    def __call__(self, query: SearchChats) -> List[MemoryEntryDTO]:
        entries = self._memory_repo.search(query.query, limit=query.limit, cwd=None)
        return [self._memory_mapper.to_dto(entry) for entry in entries]
