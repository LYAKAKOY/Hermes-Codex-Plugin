from typing import List

from hermes_codex_plugin.domain.common.value_objects import ValueObject


class SkillName(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value.strip():
            raise ValueError("skill name must not be empty")


class SkillDescription(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        if not self.value.strip():
            raise ValueError("skill description must not be empty")


class SkillRules(ValueObject[List[str]]):
    value: List[str]

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("skill rules must not be empty")
        if not all(isinstance(rule, str) and rule.strip() for rule in self.value):
            raise ValueError("skill rules must be non-empty strings")
