from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import datetime as dt
import hashlib
import json
import re
import sqlite3

from hermes_codex_plugin.domain.memory.entities import MemoryEntry
from hermes_codex_plugin.domain.memory.redaction import redact


TOKEN_RE = re.compile(r"[\w]{2,}", re.UNICODE)


class SQLiteMemoryRepository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self.connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    scope TEXT NOT NULL DEFAULT 'global',
                    source TEXT NOT NULL DEFAULT '',
                    session_id TEXT NOT NULL DEFAULT '',
                    turn_id TEXT NOT NULL DEFAULT '',
                    cwd TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    fingerprint TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            try:
                conn.execute(
                    """
                    CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts
                    USING fts5(
                        content,
                        kind,
                        scope,
                        source,
                        content='entries',
                        content_rowid='id',
                        tokenize='unicode61'
                    )
                    """
                )
                conn.execute(
                    "INSERT OR REPLACE INTO meta(key, value) VALUES('fts5', '1')"
                )
            except sqlite3.OperationalError:
                conn.execute(
                    "INSERT OR REPLACE INTO meta(key, value) VALUES('fts5', '0')"
                )

    def has_fts(self) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key = 'fts5'").fetchone()
            return row is not None and row["value"] == "1"

    def add_entry(
        self,
        content: str,
        *,
        kind: str = "memory",
        scope: str = "global",
        source: str = "",
        session_id: str = "",
        turn_id: str = "",
        cwd: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        clean_content = redact(content.strip())
        if not clean_content:
            raise ValueError("content must not be empty")
        metadata = metadata or {}
        created_at = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        fingerprint = self._fingerprint(kind, session_id, turn_id, clean_content)
        metadata_json = json.dumps(metadata, ensure_ascii=True, sort_keys=True)
        use_fts = self.has_fts()

        with self.connect() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO entries(
                        kind, scope, source, session_id, turn_id, cwd,
                        content, metadata_json, fingerprint, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        kind,
                        scope,
                        source,
                        session_id,
                        turn_id,
                        cwd,
                        clean_content,
                        metadata_json,
                        fingerprint,
                        created_at,
                    ),
                )
            except sqlite3.IntegrityError:
                row = conn.execute(
                    "SELECT id FROM entries WHERE fingerprint = ?",
                    (fingerprint,),
                ).fetchone()
                if row is None:
                    raise
                return int(row["id"])

            entry_id = int(cursor.lastrowid)
            if use_fts:
                conn.execute(
                    """
                    INSERT INTO entries_fts(rowid, content, kind, scope, source)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (entry_id, clean_content, kind, scope, source),
                )
            return entry_id

    def delete_entry(self, entry_id: int) -> bool:
        with self.connect() as conn:
            row = conn.execute("SELECT id FROM entries WHERE id = ?", (entry_id,)).fetchone()
            if row is None:
                return False
            if self.has_fts():
                conn.execute("DELETE FROM entries_fts WHERE rowid = ?", (entry_id,))
            conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            return True

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        cwd: Optional[str] = None,
        scope: Optional[str] = None,
        kinds: Optional[List[str]] = None,
        exclude_kinds: Optional[List[str]] = None,
    ) -> List[MemoryEntry]:
        tokens = list(tokens_for_query(query))
        if not tokens:
            return []
        if self.has_fts():
            try:
                return self._search_fts(
                    tokens,
                    limit=limit,
                    cwd=cwd,
                    scope=scope,
                    kinds=kinds,
                    exclude_kinds=exclude_kinds,
                )
            except sqlite3.OperationalError:
                pass
        return self._search_like(
            tokens,
            limit=limit,
            cwd=cwd,
            scope=scope,
            kinds=kinds,
            exclude_kinds=exclude_kinds,
        )

    def recent(self, *, limit: int = 20, kind: Optional[str] = None) -> List[MemoryEntry]:
        sql = "SELECT * FROM entries"
        params: List[Any] = []
        if kind:
            sql += " WHERE kind = ?"
            params.append(kind)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [entry_from_row(row) for row in rows]

    def stats(self) -> Dict[str, Any]:
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS c FROM entries").fetchone()["c"]
            by_kind = conn.execute(
                "SELECT kind, COUNT(*) AS c FROM entries GROUP BY kind ORDER BY c DESC"
            ).fetchall()
        return {
            "db_path": str(self.db_path),
            "fts5": self.has_fts(),
            "total_entries": int(total),
            "by_kind": {row["kind"]: int(row["c"]) for row in by_kind},
        }

    def _search_fts(
        self,
        tokens: List[str],
        *,
        limit: int,
        cwd: Optional[str],
        scope: Optional[str],
        kinds: Optional[List[str]],
        exclude_kinds: Optional[List[str]],
    ) -> List[MemoryEntry]:
        match_query = " OR ".join('"{}"'.format(token.replace('"', '""')) for token in tokens)
        filters = ["entries_fts MATCH ?"]
        params: List[Any] = [match_query]
        if cwd:
            filters.append("(e.cwd = ? OR e.cwd = '')")
            params.append(cwd)
        if scope:
            filters.append("e.scope = ?")
            params.append(scope)
        add_kind_filters(filters, params, "e.kind", kinds, exclude_kinds)
        params.append(limit)
        sql = """
            SELECT e.*
            FROM entries_fts
            JOIN entries e ON e.id = entries_fts.rowid
            WHERE {where}
            ORDER BY bm25(entries_fts), e.id DESC
            LIMIT ?
        """.format(where=" AND ".join(filters))
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [entry_from_row(row) for row in rows]

    def _search_like(
        self,
        tokens: List[str],
        *,
        limit: int,
        cwd: Optional[str],
        scope: Optional[str],
        kinds: Optional[List[str]],
        exclude_kinds: Optional[List[str]],
    ) -> List[MemoryEntry]:
        clauses = []
        params: List[Any] = []
        for token in tokens:
            clauses.append("content LIKE ?")
            params.append("%{}%".format(token))
        filters = ["(" + " OR ".join(clauses) + ")"]
        if cwd:
            filters.append("(cwd = ? OR cwd = '')")
            params.append(cwd)
        if scope:
            filters.append("scope = ?")
            params.append(scope)
        add_kind_filters(filters, params, "kind", kinds, exclude_kinds)
        params.append(limit)
        sql = """
            SELECT * FROM entries
            WHERE {where}
            ORDER BY id DESC
            LIMIT ?
        """.format(where=" AND ".join(filters))
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [entry_from_row(row) for row in rows]

    @staticmethod
    def _fingerprint(kind: str, session_id: str, turn_id: str, content: str) -> str:
        identity = "\0".join([kind, session_id, turn_id, content])
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def add_kind_filters(
    filters: List[str],
    params: List[Any],
    column: str,
    kinds: Optional[List[str]],
    exclude_kinds: Optional[List[str]],
) -> None:
    if kinds:
        placeholders = ", ".join("?" for _ in kinds)
        filters.append("{} IN ({})".format(column, placeholders))
        params.extend(kinds)
    if exclude_kinds:
        placeholders = ", ".join("?" for _ in exclude_kinds)
        filters.append("{} NOT IN ({})".format(column, placeholders))
        params.extend(exclude_kinds)


def tokens_for_query(query: str) -> Iterable[str]:
    seen = set()
    for token in TOKEN_RE.findall(query.lower()):
        if token not in seen:
            seen.add(token)
            yield token
        if len(seen) >= 12:
            break


def entry_from_row(row: sqlite3.Row) -> MemoryEntry:
    try:
        metadata = json.loads(row["metadata_json"])
    except json.JSONDecodeError:
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    return MemoryEntry.from_raw(
        id=int(row["id"]),
        kind=row["kind"],
        scope=row["scope"],
        source=row["source"],
        session_id=row["session_id"],
        turn_id=row["turn_id"],
        cwd=row["cwd"],
        content=row["content"],
        metadata=metadata,
        created_at=row["created_at"],
    )
