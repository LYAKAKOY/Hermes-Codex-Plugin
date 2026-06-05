from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SkillDraftDTO:
    name: str
    description: str
    rules: List[str]
