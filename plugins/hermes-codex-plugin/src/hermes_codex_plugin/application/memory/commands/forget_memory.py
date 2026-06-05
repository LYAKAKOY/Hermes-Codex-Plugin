from dataclasses import dataclass

from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository


@dataclass(frozen=True)
class ForgetMemory:
    entry_id: int


class ForgetMemoryHandler:
    def __init__(self, memory_repo: MemoryRepository) -> None:
        self._memory_repo = memory_repo

    def __call__(self, command: ForgetMemory) -> bool:
        return self._memory_repo.delete_entry(command.entry_id)
