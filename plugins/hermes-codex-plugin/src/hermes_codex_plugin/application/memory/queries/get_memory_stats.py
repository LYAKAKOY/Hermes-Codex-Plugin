from hermes_codex_plugin.application.memory.dto import MemoryStatsDTO
from hermes_codex_plugin.application.memory.mapper import MemoryStatsMapper
from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository


class GetMemoryStatsHandler:
    def __init__(
        self,
        memory_repo: MemoryRepository,
        stats_mapper: MemoryStatsMapper,
    ) -> None:
        self._memory_repo = memory_repo
        self._stats_mapper = stats_mapper

    def __call__(self) -> MemoryStatsDTO:
        return self._stats_mapper.to_dto(self._memory_repo.stats())
