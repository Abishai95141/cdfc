"""P5-B1 — open or create the run store, and record the schema digest inside it.

**The database file is an artifact, not a cache.** It is hashed and named in the run manifest, so
a reviewer can re-open the exact rows a number was computed from. That is why the schema's own
digest is written into it: a run must be able to say what shape it was produced under.
"""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Final

SCHEMA: Final[Path] = Path(__file__).resolve().parent / "schema.sql"


def schema_sha256() -> str:
    return hashlib.sha256(SCHEMA.read_bytes()).hexdigest()


def open_db(path: Path) -> sqlite3.Connection:
    """Create the store if absent, apply the schema, and record its digest."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.execute(
        "INSERT INTO meta(key, value) VALUES('schema_sha256', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (schema_sha256(),),
    )
    conn.commit()
    return conn


def digest_of(path: Path) -> str:
    """The store's own digest, for the manifest. A file nobody can hash is not an artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
