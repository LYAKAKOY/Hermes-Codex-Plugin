from pathlib import Path
from typing import Any, Dict
import json
import sys

from hermes_codex_plugin.application.memory.commands.remember_memory import (
    RememberMemory,
    RememberMemoryHandler,
)
from hermes_codex_plugin.application.memory.mapper import MemoryEntryMapper
from hermes_codex_plugin.application.memory.recall import MemoryRecallService, dedupe_entries
from hermes_codex_plugin.domain.memory.interfaces.repository import MemoryRepository
from hermes_codex_plugin.domain.memory.policy import (
    global_memory_policy_context,
    search_hint_context,
)
from hermes_codex_plugin.infrastructure.config import load_settings
from hermes_codex_plugin.infrastructure.logging import logger
from hermes_codex_plugin.infrastructure.persistence.sqlite_memory_repository import (
    SQLiteMemoryRepository,
)
from hermes_codex_plugin.presentation.formatting import format_entries


def main(expected_event: str) -> None:
    try:
        event = read_event()
        result = handle_event(event, expected_event=expected_event)
        if result is not None:
            write_stdout(json.dumps(result, ensure_ascii=True))
    except Exception as exc:
        logger.exception("Hermes Codex Plugin hook failed")
        payload = {
            "continue": True,
            "systemMessage": "Hermes Codex Plugin hook failed: {}".format(exc),
        }
        write_stdout(json.dumps(payload, ensure_ascii=True))


def write_stdout(message: str) -> None:
    sys.stdout.write(message)
    if not message.endswith("\n"):
        sys.stdout.write("\n")


def read_event() -> Dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        return {}
    return payload


def handle_event(event: Dict[str, Any], *, expected_event: str) -> Dict[str, Any]:
    settings = load_settings()
    if settings.disabled:
        return {"continue": True}

    memory_repo = SQLiteMemoryRepository(settings.db_path)
    name = event.get("hook_event_name") or expected_event
    if expected_event == "SessionStart":
        return handle_session_start(memory_repo, event, name, settings.recall_chars)
    if expected_event == "UserPromptSubmit":
        return handle_user_prompt_submit(
            memory_repo,
            event,
            name,
            settings.recall_limit,
            settings.recall_chars,
        )
    if expected_event == "Stop":
        return handle_stop(memory_repo, event, settings.capture_assistant)
    if expected_event == "PreCompact":
        return handle_pre_compact(memory_repo, event, settings.max_capture_chars)
    return {"continue": True}


def handle_session_start(
    memory_repo: MemoryRepository,
    event: Dict[str, Any],
    hook_name: str,
    max_chars: int,
) -> Dict[str, Any]:
    del event
    recent = memory_repo.recent(limit=5)
    if not recent:
        return {"continue": True}
    memory_mapper = MemoryEntryMapper()
    context = format_entries(
        [memory_mapper.to_dto(entry) for entry in recent],
        max_chars=max_chars,
    )
    return additional_context(hook_name, context)


def handle_user_prompt_submit(
    memory_repo: MemoryRepository,
    event: Dict[str, Any],
    hook_name: str,
    limit: int,
    max_chars: int,
) -> Dict[str, Any]:
    prompt = str(event.get("prompt") or "").strip()
    session_id = str(event.get("session_id") or "")
    turn_id = str(event.get("turn_id") or "")
    cwd = str(event.get("cwd") or "")

    if not prompt:
        return {"continue": True}

    recall_service = MemoryRecallService(memory_repo)
    matches = recall_service.recall(prompt, limit=limit, cwd=cwd)
    standing = recall_service.recent_durable(limit=3)
    memory_mapper = MemoryEntryMapper()

    remember = RememberMemoryHandler(memory_repo)
    remember(
        RememberMemory(
            prompt,
            kind="prompt",
            scope="session",
            source="UserPromptSubmit",
            session_id=session_id,
            turn_id=turn_id,
            cwd=cwd,
            metadata={"hook_event_name": hook_name},
        )
    )

    context_parts = [global_memory_policy_context(), search_hint_context(prompt)]
    recalled = dedupe_entries(standing + matches)
    if recalled:
        context_parts.append(
            format_entries(
                [memory_mapper.to_dto(entry) for entry in recalled],
                max_chars=max_chars,
                heading=(
                    "Hermes Codex Plugin durable/relevant memory. Prefer user_rule, "
                    "project_rule, rule, and memory entries over transient prompt/assistant "
                    "history."
                ),
            )
        )
    return additional_context(hook_name, "\n\n".join(context_parts))


def handle_stop(
    memory_repo: MemoryRepository,
    event: Dict[str, Any],
    capture_assistant: bool,
) -> Dict[str, Any]:
    if not capture_assistant:
        return {"continue": True}
    message = str(event.get("last_assistant_message") or "").strip()
    if message:
        remember = RememberMemoryHandler(memory_repo)
        remember(
            RememberMemory(
                message,
                kind="assistant",
                scope="session",
                source="Stop",
                session_id=str(event.get("session_id") or ""),
                turn_id=str(event.get("turn_id") or ""),
                cwd=str(event.get("cwd") or ""),
                metadata={"hook_event_name": event.get("hook_event_name") or "Stop"},
            )
        )
    return {"continue": True}


def handle_pre_compact(
    memory_repo: MemoryRepository,
    event: Dict[str, Any],
    max_capture_chars: int,
) -> Dict[str, Any]:
    transcript_path = event.get("transcript_path")
    if not transcript_path:
        return {"continue": True}
    path = Path(str(transcript_path)).expanduser()
    if not path.is_file():
        return {"continue": True}
    content = path.read_text(encoding="utf-8", errors="replace")
    if len(content) > max_capture_chars:
        content = content[-max_capture_chars:]
    if content.strip():
        remember = RememberMemoryHandler(memory_repo)
        remember(
            RememberMemory(
                content,
                kind="transcript",
                scope="session",
                source=str(path),
                session_id=str(event.get("session_id") or ""),
                turn_id=str(event.get("turn_id") or ""),
                cwd=str(event.get("cwd") or ""),
                metadata={
                    "hook_event_name": event.get("hook_event_name") or "PreCompact",
                    "trigger": event.get("trigger"),
                },
            )
        )
    return {"continue": True}


def additional_context(hook_name: str, context: str) -> Dict[str, Any]:
    return {
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": hook_name,
            "additionalContext": context,
        },
    }
