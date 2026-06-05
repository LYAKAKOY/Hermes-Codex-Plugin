---
name: hermes-codex-plugin
description: Use when a task may depend on prior user preferences, project conventions, architectural rules, workflow decisions, previous Codex work, full-text memory search, durable rule saving, or skill drafting/updating through Hermes Codex Plugin.
---

# Hermes Codex Plugin

Use the bundled MCP tools to inspect and manage local memory. Treat memory as a standing source of
user preferences, project conventions, architectural rules, and workflow decisions. Prefer this
skill when the current context does not already contain the rules needed to answer or edit safely,
not only when the user explicitly says to search memory.

## Workflow

1. Search first with `hermes_codex_search_chats` when prior context from earlier chats may matter.
2. Use `hermes_codex_search` for narrower local memory search when a project directory filter is useful.
3. Save durable facts with `hermes_codex_remember`.
4. Use `hermes_codex_propose_skill` to draft a skill from repeated rules.
5. Only write a skill with `hermes_codex_write_skill` when the user clearly wants it.

## Rules

- Keep memories compact and actionable.
- Do not save secrets, credentials, raw logs, or huge code blocks.
- Treat skill drafts as proposals that need review before use.
- Prefer project-scoped memories for repository conventions and user-scoped memories for stable personal preferences.
