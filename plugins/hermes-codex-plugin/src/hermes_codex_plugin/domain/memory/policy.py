GLOBAL_MEMORY_POLICY = (
    "Hermes Codex Plugin global memory policy: local memory is a standing source of "
    "user preferences, project conventions, architectural rules, prior decisions, and "
    "workflow rules. For every user request, before assuming missing context or asking "
    "the user to repeat a rule, check whether the needed context is already present in "
    "the current prompt/thread. If it is not, consult Hermes Codex Plugin memory first. "
    "If MCP tools are callable, call `hermes_codex_search_chats` to search across "
    "previous chats/sessions, or `hermes_codex_search` for a narrower memory search. "
    "Use skills for reusable procedures and chat memory for facts, prior decisions, and "
    "context from earlier conversations. If MCP tools are not callable, apply the durable "
    "memory entries injected by this hook. If memory has no relevant result, continue with "
    "the normal Codex workflow: inspect the repository, reason from the current context, "
    "and ask the user only when the missing information cannot be discovered. Do not wait "
    "for the user to explicitly ask you to search memory."
)


def search_hint_context(query: str) -> str:
    compact_query = " ".join(query.split())[:400]
    return (
        "Hermes Codex Plugin search hint: use this user request as the primary memory "
        "query: `{}`. Prefer exact terms from the request, then add project-specific "
        "terms only if the current context provides them. Do not use hardcoded domain "
        "keywords unless they appear in the request or recalled memory."
    ).format(compact_query)


def global_memory_policy_context() -> str:
    return GLOBAL_MEMORY_POLICY
