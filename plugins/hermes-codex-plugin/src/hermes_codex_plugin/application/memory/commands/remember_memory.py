from dataclasses import dataclass, field
from typing import Any, Dict

from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository


@dataclass(frozen=True)
class RememberMemory:
    content: str
    kind: str = "memory"
    scope: str = "global"
    source: str = "application"
    session_id: str = ""
    turn_id: str = ""
    cwd: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class RememberMemoryHandler:
    def __init__(self, memory_repo: MemoryRepository) -> None:
        self._memory_repo = memory_repo

    def __call__(self, command: RememberMemory) -> int:
        return self._memory_repo.add_entry(
            command.content,
            kind=command.kind,
            scope=command.scope,
            source=command.source,
            session_id=command.session_id,
            turn_id=command.turn_id,
            cwd=command.cwd,
            metadata=command.metadata,
        )
