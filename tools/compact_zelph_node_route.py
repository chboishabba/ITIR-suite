#!/usr/bin/env python3
"""Compact a chunk-centric zelph-node-route/v1 JSON sidecar into SQLite.

The SQLite projection preserves the exact v1 routing relation while replacing
the full-file JSON scan with keyed lookup tables.

No semantic promotion is performed. The JSON remains the source contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Iterable

SOURCE_VERSION = "zelph-node-route/v1"
SQLITE_VERSION = "zelph-node-route/sqlite-v1"
SCHEMA_VERSION = 1

SCHEMA_SQL = """
PRAGMA page_size=4096;
PRAGMA journal_mode=OFF;
PRAGMA synchronous=OFF;
PRAGMA temp_store=MEMORY;
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
) WITHOUT ROWID;
CREATE TABLE node_routes (
    section TEXT NOT NULL,
    lang TEXT NOT NULL,
    node INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    PRIMARY KEY (section, lang, node, chunk_index)
) WITHOUT ROWID;
CREATE TABLE name_routes (
    lang TEXT NOT NULL,
    name TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    PRIMARY KEY (lang, name, chunk_index)
) WITHOUT ROWID;
CREATE INDEX node_routes_by_node
    ON node_routes(node, section, lang, chunk_index);
"""


class RouteFormatError(ValueError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _source_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_v1(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("routeVersion") != SOURCE_VERSION:
        raise RouteFormatError(
            f"expected routeVersion={SOURCE_VERSION!r}, got {payload.get('routeVersion')!r}"
        )
    routing = payload.get("routing")
    if not isinstance(routing, dict):
        raise RouteFormatError("routing must be an object")
    for section in ("left", "right", "nameOfNode", "nodeOfName"):
        value = routing.get(section, [])
        if not isinstance(value, list):
            raise RouteFormatError(f"routing.{section} must be a list")
    return payload


def _node_rows(payload: dict) -> list[tuple[str, str, int, int]]:
    rows: set[tuple[str, str, int, int]] = set()
    routing = payload["routing"]

    for section in ("left", "right"):
        for entry in routing.get(section, []):
            chunk = int(entry["chunkIndex"])
            for node in entry.get("nodes", []):
                rows.add((section, "", int(node), chunk))

    for entry in routing.get("nameOfNode", []):
        chunk = int(entry["chunkIndex"])
        lang = str(entry.get("lang", ""))
        for node in entry.get("nodes", []):
            rows.add(("nameOfNode", lang, int(node), chunk))

    return sorted(rows)


def _name_rows(payload: dict) -> list[tuple[str, str, int]]:
    rows: set[tuple[str, str, int]] = set()
    for entry in payload["routing"].get("nodeOfName", []):
        chunk = int(entry["chunkIndex"])
        lang = str(entry.get("lang", ""))
        for name in entry.get("names", []):
            rows.add((lang, str(name), chunk))
    return sorted(rows)


def _metadata(payload: dict, source_path: Path) -> list[tuple[str, str]]:
    source = payload.get("source", {})
    values = {
        "routeVersion": SQLITE_VERSION,
        "sourceRouteVersion": SOURCE_VERSION,
        "schemaVersion": str(SCHEMA_VERSION),
        "sourceSha256": _source_digest(source_path),
        "source": _canonical_json(source),
    }
    return sorted(values.items())


def compact(source_path: Path, output_path: Path) -> dict:
    payload = _load_v1(source_path)
    node_rows = _node_rows(payload)
    name_rows = _name_rows(payload)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=output_path.name + ".",
        suffix=".tmp",
        dir=output_path.parent,
    )
    os.close(fd)
    temp_path = Path(temp_name)

    try:
        connection = sqlite3.connect(temp_path)
        try:
            connection.executescript(SCHEMA_SQL)
            connection.executemany(
                "INSERT INTO metadata(key, value) VALUES (?, ?)",
                _metadata(payload, source_path),
            )
            connection.executemany(
                "INSERT INTO node_routes(section, lang, node, chunk_index) VALUES (?, ?, ?, ?)",
                node_rows,
            )
            connection.executemany(
                "INSERT INTO name_routes(lang, name, chunk_index) VALUES (?, ?, ?)",
                name_rows,
            )
            connection.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            connection.commit()
            connection.execute("VACUUM")
            connection.commit()
        finally:
            connection.close()

        os.replace(temp_path, output_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    output_bytes = output_path.stat().st_size
    source_bytes = source_path.stat().st_size
    return {
        "routeVersion": SQLITE_VERSION,
        "sourceRouteVersion": SOURCE_VERSION,
        "nodeRouteRows": len(node_rows),
        "nameRouteRows": len(name_rows),
        "sourceBytes": source_bytes,
        "outputBytes": output_bytes,
        "outputToSourceRatio": output_bytes / source_bytes if source_bytes else 0.0,
        "sourceSha256": _source_digest(source_path),
        "outputSha256": _source_digest(output_path),
    }


def _open_checked(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    metadata = dict(connection.execute("SELECT key, value FROM metadata"))
    if metadata.get("routeVersion") != SQLITE_VERSION:
        connection.close()
        raise RouteFormatError(
            f"expected SQLite routeVersion={SQLITE_VERSION!r}, got {metadata.get('routeVersion')!r}"
        )
    if int(metadata.get("schemaVersion", "0")) != SCHEMA_VERSION:
        connection.close()
        raise RouteFormatError("unsupported SQLite route schema version")
    return connection


def lookup_node(path: Path, node: int, section: str | None = None, lang: str | None = None) -> list[dict]:
    connection = _open_checked(path)
    try:
        query = "SELECT section, lang, chunk_index FROM node_routes WHERE node = ?"
        params: list[object] = [node]
        if section is not None:
            query += " AND section = ?"
            params.append(section)
        if lang is not None:
            query += " AND lang = ?"
            params.append(lang)
        query += " ORDER BY section, lang, chunk_index"
        return [
            {"section": row[0], "lang": row[1], "chunkIndex": row[2]}
            for row in connection.execute(query, params)
        ]
    finally:
        connection.close()


def lookup_name(path: Path, name: str, lang: str) -> list[int]:
    connection = _open_checked(path)
    try:
        return [
            row[0]
            for row in connection.execute(
                "SELECT chunk_index FROM name_routes WHERE lang = ? AND name = ? ORDER BY chunk_index",
                (lang, name),
            )
        ]
    finally:
        connection.close()


def verify(source_path: Path, sqlite_path: Path) -> dict:
    payload = _load_v1(source_path)
    expected_nodes = _node_rows(payload)
    expected_names = _name_rows(payload)
    connection = _open_checked(sqlite_path)
    try:
        actual_nodes = list(
            connection.execute(
                "SELECT section, lang, node, chunk_index FROM node_routes "
                "ORDER BY section, lang, node, chunk_index"
            )
        )
        actual_names = list(
            connection.execute(
                "SELECT lang, name, chunk_index FROM name_routes "
                "ORDER BY lang, name, chunk_index"
            )
        )
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        connection.close()

    source_sha = _source_digest(source_path)
    ok = (
        actual_nodes == expected_nodes
        and actual_names == expected_names
        and metadata.get("sourceSha256") == source_sha
        and integrity == "ok"
    )
    return {
        "ok": ok,
        "integrityCheck": integrity,
        "nodeRoutesMatch": actual_nodes == expected_nodes,
        "nameRoutesMatch": actual_names == expected_names,
        "sourceDigestMatch": metadata.get("sourceSha256") == source_sha,
        "nodeRouteRows": len(actual_nodes),
        "nameRouteRows": len(actual_names),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compact zelph-node-route/v1 JSON into a keyed SQLite sidecar."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("source_json", type=Path)
    build.add_argument("output_sqlite", type=Path)

    check = sub.add_parser("verify")
    check.add_argument("source_json", type=Path)
    check.add_argument("route_sqlite", type=Path)

    node = sub.add_parser("lookup-node")
    node.add_argument("route_sqlite", type=Path)
    node.add_argument("node", type=int)
    node.add_argument("--section")
    node.add_argument("--lang")

    name = sub.add_parser("lookup-name")
    name.add_argument("route_sqlite", type=Path)
    name.add_argument("name")
    name.add_argument("--lang", required=True)

    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "build":
        result = compact(args.source_json, args.output_sqlite)
    elif args.command == "verify":
        result = verify(args.source_json, args.route_sqlite)
        if not result["ok"]:
            print(_canonical_json(result))
            return 2
    elif args.command == "lookup-node":
        result = lookup_node(args.route_sqlite, args.node, args.section, args.lang)
    else:
        result = lookup_name(args.route_sqlite, args.name, args.lang)

    print(_canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
