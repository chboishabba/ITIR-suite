"""Source-bound formal referee receipts; PostgreSQL is the sole runtime database."""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Mapping

from .frontier_reference_validation import FORMAL, formal_receipt_resolver
from .pg_semantic_spine import _default_connect

SCHEMA = """
CREATE SCHEMA IF NOT EXISTS formal;
CREATE TABLE IF NOT EXISTS formal.referee_receipt (
    repo text NOT NULL,
    sha text NOT NULL,
    path text NOT NULL,
    canonical_thread_id text NOT NULL,
    receipt_json jsonb NOT NULL,
    PRIMARY KEY (repo, sha, path, canonical_thread_id)
);
"""

class PostgresRefereeReceiptStore:
    """Only the independent trusted referee may call record_from_referee.

    The application has no fallback to SQLite. Database roles should grant
    INSERT only to the referee identity and SELECT to the consumer identity.
    """

    def __init__(self, database_url: str | None = None, *, connect: Callable | None = None):
        self.database_url = database_url
        self.connect = connect or _default_connect

    def _connection(self):
        return self.connect(self.database_url or os.environ.get("DATABASE_URL") or None)

    def record_from_referee(
        self, repo: str, sha: str, path: str, canonical_thread_id: str,
        receipt: Mapping[str, Any], *, referee_verified: bool,
    ) -> bool:
        if referee_verified is not True:
            return False
        if FORMAL.fullmatch(f"{repo}@{sha}:{path}") is None or ".." in path.split("/"):
            return False
        if not canonical_thread_id:
            return False
        if not formal_receipt_resolver(lambda *_: receipt)(
            repo, sha, path, canonical_thread_id
        ):
            return False
        encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
        with self._connection() as db:
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO formal.referee_receipt "
                    "(repo,sha,path,canonical_thread_id,receipt_json) "
                    "VALUES (%s,%s,%s,%s,%s::jsonb) ON CONFLICT DO NOTHING",
                    (repo, sha, path, canonical_thread_id, encoded),
                )
                cur.execute(
                    "SELECT receipt_json FROM formal.referee_receipt "
                    "WHERE repo=%s AND sha=%s AND path=%s AND canonical_thread_id=%s",
                    (repo, sha, path, canonical_thread_id),
                )
                row = cur.fetchone()
        if row is None:
            return False
        stored = row[0]
        if isinstance(stored, str):
            stored = json.loads(stored)
        return stored == json.loads(encoded)

    def read(self, repo: str, sha: str, path: str, canonical_thread_id: str) -> dict[str, Any] | None:
        with self._connection() as db:
            with db.cursor() as cur:
                cur.execute(
                    "SELECT receipt_json FROM formal.referee_receipt "
                    "WHERE repo=%s AND sha=%s AND path=%s AND canonical_thread_id=%s",
                    (repo, sha, path, canonical_thread_id),
                )
                row = cur.fetchone()
        if row is None:
            return None
        value = row[0]
        return json.loads(value) if isinstance(value, str) else dict(value)

    def resolver(self):
        return formal_receipt_resolver(self.read)


def default_receipt_store():
    """No legacy SQLite path accepted, even if supplied in the environment."""
    if os.environ.get("ITIR_FORMAL_RECEIPT_DB"):
        raise ValueError("ITIR_FORMAL_RECEIPT_DB is retired; use PostgreSQL DATABASE_URL")
    return PostgresRefereeReceiptStore()
