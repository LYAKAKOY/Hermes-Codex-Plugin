from typing import Iterable, List
import re

from hermes_codex_plugin.domain.memory.entities import MemoryEntry


RULE_HINTS = re.compile(
    r"\b(always|prefer|use|run|remember|rule|convention|never|must|should|"
    r"need|needs|required|require|requires)\b",
    re.IGNORECASE,
)


def extract_rules(entries: Iterable[MemoryEntry]) -> List[str]:
    seen = set()
    rules: List[str] = []
    for entry in entries:
        for sentence in split_sentences(entry.body.to_raw()):
            clean = " ".join(sentence.split()).strip(" -")
            if not clean or len(clean) < 12:
                continue
            if clean.endswith("?") or clean.lower().startswith(("should i ", "what ", "how ", "why ")):
                continue
            if not RULE_HINTS.search(clean):
                continue
            key = clean.lower()
            if key in seen:
                continue
            seen.add(key)
            rules.append(clean[:240])
    return rules


def split_sentences(text: str) -> List[str]:
    compact = re.sub(r"\s+", " ", text.strip())
    if not compact:
        return []
    parts = re.split(r"(?<=[.!?])\s+|[\r\n]+", compact)
    return [part.strip() for part in parts if part.strip()]


def normalize_skill_name(name: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", normalized) or "learned-workflow"
