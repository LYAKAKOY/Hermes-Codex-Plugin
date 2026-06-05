from dataclasses import dataclass
from typing import Any, Dict

from hermes_codex_plugin.domain.common.value_objects import ValueObject


class MemoryEntryId(ValueObject[int]):
    value: int

    def _validate(self) -> None:
        if self.value < 1:
            raise ValueError("memory entry id must be positive")


class MemoryKind(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value.strip():
            raise ValueError("memory kind must not be empty")


class MemoryScope(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value.strip():
            raise ValueError("memory scope must not be empty")


class MemorySource(ValueObject[str]):
    value: str


class MemorySessionId(ValueObject[str]):
    value: str


class MemoryTurnId(ValueObject[str]):
    value: str


class MemoryCwd(ValueObject[str]):
    value: str


class MemoryContent(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value.strip():
            raise ValueError("memory content must not be empty")


@dataclass(frozen=True)
class MemoryMetadata(ValueObject[Dict[str, Any]]):
    value: Dict[str, Any]

    def _validate(self) -> None:
        if not isinstance(self.value, dict):
            raise ValueError("memory metadata must be a dict")


class MemoryCreatedAt(ValueObject[str]):
    value: str
