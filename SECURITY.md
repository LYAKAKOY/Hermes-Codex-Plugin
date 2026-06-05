# Security Policy

Hermes Codex Plugin stores local memory and should be treated as a local data tool.

## Reporting Issues

Please report security issues privately to the maintainers before opening a public issue.

## Data Handling

- Memory is stored locally in SQLite.
- No embeddings are generated.
- No remote service is required for storage or search.
- Obvious secrets are redacted before storage with deterministic patterns.

## Known Limits

Redaction is not a complete data loss prevention system. Users should avoid saving credentials,
tokens, private logs, or sensitive personal data.
