# Contributing

Thank you for improving Hermes Codex Plugin. The project is small on purpose, so contributions
should keep the code inspectable and local-first.

## Development Setup

```bash
cd plugins/hermes-codex-plugin
PYTHONPATH=src python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m compileall -q src tests hooks scripts
```

## Code Style

- Write source, tests, docs, prompts, and policies in English.
- Do not use `from __future__ import annotations`.
- Do not use `print()` in source code.
- Use explicit stdout writing only for required CLI or protocol output.
- Use `loguru` for important errors when available.
- Do not add trivial entity properties that only unwrap value objects.
- Use value objects in domain entities.
- Convert domain entities to DTOs with explicit mapper classes.
- Keep commands and queries in separate packages.
- Put each command or query handler in its own file.
- Do not leave alias or re-export compatibility modules after moving code.

## Testing

Tests should verify behavior and edge cases. Avoid tests that only assert folder structure or source
layout. The current suite uses Python `unittest`.

## Pull Request Checklist

- The test suite passes.
- `compileall` passes.
- New behavior has focused tests.
- Plugin README and root README are updated when user-facing behavior changes.
- No secrets, raw logs, or private chat dumps are committed.
