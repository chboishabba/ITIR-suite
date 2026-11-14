#!/usr/bin/env python3
"""Batch migration of conversation messages from SQLite into TrueNAS PostgreSQL corpus spine.

Enforces:
  1. PostgreSQL (sensiblaw_sparse_ready_20260818) is the sole and only canonical database.
  2. Full 5-stage content-addressable relational hierarchy:
     binary_content -> canonical_content -> document -> span -> chat_archive_message
  3. Idempotent ON CONFLICT DO NOTHING everywhere.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import sqlite3
import sys
import time
from typing import Sequence

import psycopg

DEFAULT_PG_URL = "postgresql://admin:admin@truenas.local:5432/sensiblaw_sparse_ready_20260818"
DEFAULT_SQLITE_PATH = Path.home() / "chat_archive.sqlite"


def migrate_messages(
    *,
    sqlite_path: Path = DEFAULT_SQLITE_PATH,
    pg_url: str = DEFAULT_PG_URL,
    limit: int | None = None,
    batch_size: int = 1000,
    prefix_filter: str | None = None,
) -> dict[str, int]:
    if not sqlite_path.is_file():
        raise FileNotFoundError(f"SQLite archive not found at {sqlite_path}")

    print(f"Connecting to SQLite: {sqlite_path}")
    conn_sq = sqlite3.connect(sqlite_path)
    cur_sq = conn_sq.cursor()

    query = """
        SELECT message_id, canonical_thread_id, role, text, title, ts,
               node_id, parent_node_id, branch_membership, citation_token,
               filename, mime_type, asset_pointer, source_scope
        FROM messages
        WHERE canonical_thread_id IS NOT NULL 
          AND text IS NOT NULL 
          AND length(trim(text)) > 0
    """
    params: list[object] = []
    if prefix_filter:
        query += " AND canonical_thread_id LIKE ?"
        params.append(f"{prefix_filter}%")
    query += " ORDER BY ts ASC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cur_sq.execute(query, params)

    print(f"Connecting to PostgreSQL: {pg_url.split('@')[-1]}")
    conn_pg = psycopg.connect(pg_url)

    total_migrated = 0
    start_time = time.time()

    while True:
        batch = cur_sq.fetchmany(batch_size)
        if not batch:
            break

        binary_rows = []
        canonical_rows = []
        doc_rows = []
        span_rows = []
        msg_rows = []

        for r in batch:
            (
                msg_id, thread_id, role, text, title, ts,
                node_id, parent_node_id, branch, citation,
                fn, mime, asset, scope
            ) = r
            if not text or len(text.strip()) == 0:
                continue

            raw_bytes = text.encode("utf-8")
            sha = sha256(raw_bytes).hexdigest()
            sha_bytes = bytes.fromhex(sha)

            source_content_ref = f"source-content:{sha}"
            canonical_ref = f"canonical-content:{sha}:media-normalization:utf8:v0_1"
            doc_ref = f"document:{sha}"
            span_ref = f"mention:document:{sha}:0:{len(text)}"

            node_str = node_id or msg_id
            msg_ref = f"message:{thread_id}:{node_str}"
            conv_ref = f"conversation:{thread_id}"
            node_ref = f"node:{node_str}"
            parent_ref = f"node:{parent_node_id}" if parent_node_id else None

            role_norm = (role or "user").lower()
            if role_norm not in {"user", "assistant", "tool", "system"}:
                role_norm = "user"

            # 1. binary_content
            binary_rows.append((
                source_content_ref, sha_bytes, "text/plain", None, raw_bytes, len(raw_bytes)
            ))
            # 2. canonical_content
            canonical_rows.append((
                canonical_ref, sha_bytes, "utf-8", "media-normalization:utf8:v0_1", None, raw_bytes, len(raw_bytes)
            ))
            # 3. document
            doc_rows.append((
                doc_ref, source_content_ref, canonical_ref, "text/plain",
                "media:utf8-text:v0_1", "media-normalization:utf8:v0_1",
                "compiler-context:local-only:v0_1", sha_bytes
            ))
            # 4. span
            span_rows.append((
                span_ref, doc_ref, 0, len(text), 0, 1, "full_message"
            ))
            # 5. chat_archive_message
            msg_rows.append((
                msg_ref, conv_ref, node_ref, parent_ref,
                branch or "active", ts or "1970-01-01T00:00:00Z",
                role_norm, title or "Untitled", "message",
                scope or "archive", text, mime or "text/plain",
                doc_ref, f"source:sha256:{sha}", span_ref
            ))

        with conn_pg.transaction():
            with conn_pg.cursor() as cur_pg:
                cur_pg.executemany("""
                    INSERT INTO corpus.binary_content
                    (content_ref, content_sha256, media_type, compression_ref, payload, uncompressed_byte_length)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (content_ref) DO NOTHING
                """, binary_rows)

                cur_pg.executemany("""
                    INSERT INTO corpus.canonical_content
                    (canonical_ref, content_sha256, encoding_ref, normalization_ref, compression_ref, payload, uncompressed_byte_length)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (canonical_ref) DO NOTHING
                """, canonical_rows)

                cur_pg.executemany("""
                    INSERT INTO corpus.document
                    (document_ref, source_content_ref, canonical_ref, media_type,
                     adapter_ref, adapter_version, compiler_context_ref, document_sha256)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (document_ref) DO NOTHING
                """, doc_rows)

                cur_pg.executemany("""
                    INSERT INTO corpus.span
                    (span_ref, document_ref, start_char, end_char, start_token, end_token, span_type_ref)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (span_ref) DO NOTHING
                """, span_rows)

                cur_pg.executemany("""
                    INSERT INTO corpus.chat_archive_message
                    (message_ref, conversation_ref, node_ref, parent_node_ref,
                     branch_membership_ref, message_time_ref, role_ref, thread_title,
                     content_kind_ref, source_scope, body_storage_ref, mime_type,
                     document_ref, source_revision_ref, full_message_span_ref,
                     identity_verified, candidate_only, creates_semantic_authority,
                     applicability_promoted, claim_truth_promoted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            true, true, false, false, false)
                    ON CONFLICT (message_ref) DO NOTHING
                """, msg_rows)

        total_migrated += len(batch)
        elapsed = time.time() - start_time
        rate = total_migrated / elapsed if elapsed > 0 else 0
        print(f"Migrated {total_migrated} messages ({rate:.1f} msgs/sec)...", flush=True)

    print(f"\nMigration complete: {total_migrated} messages processed in {time.time() - start_time:.2f}s.")
    return {"total_migrated": total_migrated}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate messages from SQLite to PostgreSQL spine")
    parser.add_argument("--sqlite-path", type=Path, default=DEFAULT_SQLITE_PATH)
    parser.add_argument("--pg-url", type=str, default=DEFAULT_PG_URL)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--prefix-filter", type=str, default=None, help="e.g. 6a for the 6a* tranche")
    args = parser.parse_args()

    migrate_messages(
        sqlite_path=args.sqlite_path,
        pg_url=args.pg_url,
        limit=args.limit,
        batch_size=args.batch_size,
        prefix_filter=args.prefix_filter,
    )
