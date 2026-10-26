"""Local referee receipt storage. This module is not an MCP write surface."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from .frontier_reference_validation import FORMAL, formal_receipt_resolver

SCHEMA = """
CREATE TABLE IF NOT EXISTS formal_referee_receipts (
 repo TEXT NOT NULL, sha TEXT NOT NULL, path TEXT NOT NULL,
 canonical_thread_id TEXT NOT NULL, receipt_json TEXT NOT NULL,
 PRIMARY KEY (repo, sha, path, canonical_thread_id)
)
"""


class LocalRefereeReceiptStore:
    """Instantiate only in the trusted local referee process."""

    def __init__(self, db_path: Path) -> None:
        self.path = Path(db_path)

    def record_from_referee(
        self, repo: str, sha: str, path: str, canonical_thread_id: str,
        receipt: Mapping[str, Any], *,
        referee_verified: bool,
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
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(SCHEMA)
            db.execute(
                "INSERT OR IGNORE INTO formal_referee_receipts VALUES (?,?,?,?,?)",
                (repo, sha, path, canonical_thread_id, encoded),
            )
            row = db.execute(
                "SELECT receipt_json FROM formal_referee_receipts "
                "WHERE repo=? AND sha=? AND path=? AND canonical_thread_id=?",
                (repo, sha, path, canonical_thread_id),
            ).fetchone()
        return row is not None and row[0] == encoded

    def read(
        self, repo: str, sha: str, path: str, canonical_thread_id: str,
    ) -> dict[str, Any] | None:
        if not self.path.is_file():
            return None
        with sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True) as db:
            row = db.execute(
                "SELECT receipt_json FROM formal_referee_receipts "
                "WHERE repo=? AND sha=? AND path=? AND canonical_thread_id=?",
                (repo, sha, path, canonical_thread_id),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def resolver(self):
        return formal_receipt_resolver(self.read)
