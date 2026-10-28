#!/usr/bin/env python3
"""Compact zelph-node-route/v1 JSON into a dense SQLite sidecar.

The logical v1 relation is preserved. Physical storage changes from repeated
JSON arrays to chunk rows whose sorted membership sets are delta-varint encoded
and zlib compressed.

The source JSON remains the authority for verification. This tool adds no
semantic or external promotion authority.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import os
import sqlite3
import tempfile
import zlib
from pathlib import Path

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
CREATE TABLE node_chunks (
    section TEXT NOT NULL,
    lang TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    member_count INTEGER NOT NULL,
    members_zlib BLOB NOT NULL,
    PRIMARY KEY (section, lang, chunk_index)
) WITHOUT ROWID;
CREATE TABLE name_chunks (
    lang TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    member_count INTEGER NOT NULL,
    names_zlib BLOB NOT NULL,
    PRIMARY KEY (lang, chunk_index)
) WITHOUT ROWID;
"""


class RouteFormatError(ValueError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


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
        if not isinstance(routing.get(section, []), list):
            raise RouteFormatError(f"routing.{section} must be a list")
    return payload


def _put_uvarint(out: bytearray, value: int) -> None:
    if value < 0:
        raise RouteFormatError("route integers must be nonnegative")
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)


def _read_uvarint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset
        shift += 7
        if shift > 63:
            raise RouteFormatError("uvarint exceeds 64 bits")
    raise RouteFormatError("truncated uvarint")


def _encode_nodes(nodes: list[object]) -> tuple[int, bytes]:
    values = sorted({int(node) for node in nodes})
    raw = bytearray()
    previous = 0
    for index, node in enumerate(values):
        delta = node if index == 0 else node - previous
        _put_uvarint(raw, delta)
        previous = node
    return len(values), zlib.compress(bytes(raw), level=9)


def _decode_nodes(blob: bytes, expected_count: int) -> list[int]:
    data = zlib.decompress(blob)
    values: list[int] = []
    offset = 0
    previous = 0
    while offset < len(data):
        delta, offset = _read_uvarint(data, offset)
        value = delta if not values else previous + delta
        values.append(value)
        previous = value
    if len(values) != expected_count:
        raise RouteFormatError(
            f"node member count mismatch: expected {expected_count}, decoded {len(values)}"
        )
    return values


def _encode_names(names: list[object]) -> tuple[int, bytes]:
    values = sorted({str(name) for name in names})
    raw = bytearray()
    for name in values:
        encoded = name.encode("utf-8")
        _put_uvarint(raw, len(encoded))
        raw.extend(encoded)
    return len(values), zlib.compress(bytes(raw), level=9)


def _decode_names(blob: bytes, expected_count: int) -> list[str]:
    data = zlib.decompress(blob)
    values: list[str] = []
    offset = 0
    while offset < len(data):
        length, offset = _read_uvarint(data, offset)
        end = offset + length
        if end > len(data):
            raise RouteFormatError("truncated encoded route name")
        values.append(data[offset:end].decode("utf-8"))
        offset = end
    if len(values) != expected_count:
        raise RouteFormatError(
            f"name member count mismatch: expected {expected_count}, decoded {len(values)}"
        )
    return values


def _node_chunk_rows(payload: dict) -> list[tuple[str, str, int, int, bytes]]:
    rows: list[tuple[str, str, int, int, bytes]] = []
    routing = payload["routing"]
    for section in ("left", "right"):
        for entry in routing.get(section, []):
            count, blob = _encode_nodes(entry.get("nodes", []))
            rows.append((section, "", int(entry["chunkIndex"]), count, blob))
    for entry in routing.get("nameOfNode", []):
        count, blob = _encode_nodes(entry.get("nodes", []))
        rows.append(
            (
                "nameOfNode",
                str(entry.get("lang", "")),
                int(entry["chunkIndex"]),
                count,
                blob,
            )
        )
    rows.sort(key=lambda row: (row[0], row[1], row[2]))
    return rows


def _name_chunk_rows(payload: dict) -> list[tuple[str, int, int, bytes]]:
    rows: list[tuple[str, int, int, bytes]] = []
    for entry in payload["routing"].get("nodeOfName", []):
        count, blob = _encode_names(entry.get("names", []))
        rows.append((str(entry.get("lang", "")), int(entry["chunkIndex"]), count, blob))
    rows.sort(key=lambda row: (row[0], row[1]))
    return rows


def _metadata(payload: dict, source_path: Path) -> list[tuple[str, str]]:
    values = {
        "routeVersion": SQLITE_VERSION,
        "sourceRouteVersion": SOURCE_VERSION,
        "schemaVersion": str(SCHEMA_VERSION),
        "encoding": "sqlite-chunk-zlib-delta-varint",
        "sourceSha256": _digest(source_path),
        "source": _canonical_json(payload.get("source", {})),
    }
    return sorted(values.items())


def compact(source_path: Path, output_path: Path) -> dict:
    payload = _load_v1(source_path)
    node_rows = _node_chunk_rows(payload)
    name_rows = _name_chunk_rows(payload)

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
                "INSERT INTO node_chunks(section, lang, chunk_index, member_count, members_zlib) "
                "VALUES (?, ?, ?, ?, ?)",
                node_rows,
            )
            connection.executemany(
                "INSERT INTO name_chunks(lang, chunk_index, member_count, names_zlib) "
                "VALUES (?, ?, ?, ?)",
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

    node_memberships = sum(row[3] for row in node_rows)
    name_memberships = sum(row[2] for row in name_rows)
    source_bytes = source_path.stat().st_size
    output_bytes = output_path.stat().st_size
    return {
        "routeVersion": SQLITE_VERSION,
        "sourceRouteVersion": SOURCE_VERSION,
        "encoding": "sqlite-chunk-zlib-delta-varint",
        "nodeChunkRows": len(node_rows),
        "nameChunkRows": len(name_rows),
        "nodeMemberships": node_memberships,
        "nameMemberships": name_memberships,
        "sourceBytes": source_bytes,
        "outputBytes": output_bytes,
        "outputToSourceRatio": output_bytes / source_bytes if source_bytes else 0.0,
        "sourceSha256": _digest(source_path),
        "outputSha256": _digest(output_path),
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


def lookup_node(
    path: Path,
    node: int,
    section: str | None = None,
    lang: str | None = None,
) -> list[dict]:
    connection = _open_checked(path)
    try:
        query = (
            "SELECT section, lang, chunk_index, member_count, members_zlib "
            "FROM node_chunks WHERE 1=1"
        )
        params: list[object] = []
        if section is not None:
            query += " AND section = ?"
            params.append(section)
        if lang is not None:
            query += " AND lang = ?"
            params.append(lang)
        query += " ORDER BY section, lang, chunk_index"

        matches: list[dict] = []
        for selected_section, selected_lang, chunk, count, blob in connection.execute(
            query, params
        ):
            values = _decode_nodes(blob, count)
            position = bisect.bisect_left(values, node)
            if position < len(values) and values[position] == node:
                matches.append(
                    {
                        "section": selected_section,
                        "lang": selected_lang,
                        "chunkIndex": chunk,
                    }
                )
        return matches
    finally:
        connection.close()


def lookup_name(path: Path, name: str, lang: str) -> list[int]:
    connection = _open_checked(path)
    try:
        matches: list[int] = []
        for chunk, count, blob in connection.execute(
            "SELECT chunk_index, member_count, names_zlib FROM name_chunks "
            "WHERE lang = ? ORDER BY chunk_index",
            (lang,),
        ):
            values = _decode_names(blob, count)
            position = bisect.bisect_left(values, name)
            if position < len(values) and values[position] == name:
                matches.append(chunk)
        return matches
    finally:
        connection.close()


def _expected_node_chunks(payload: dict) -> list[tuple[str, str, int, list[int]]]:
    expected: list[tuple[str, str, int, list[int]]] = []
    for section in ("left", "right"):
        for entry in payload["routing"].get(section, []):
            expected.append(
                (
                    section,
                    "",
                    int(entry["chunkIndex"]),
                    sorted({int(node) for node in entry.get("nodes", [])}),
                )
            )
    for entry in payload["routing"].get("nameOfNode", []):
        expected.append(
            (
                "nameOfNode",
                str(entry.get("lang", "")),
                int(entry["chunkIndex"]),
                sorted({int(node) for node in entry.get("nodes", [])}),
            )
        )
    return sorted(expected, key=lambda row: (row[0], row[1], row[2]))


def _expected_name_chunks(payload: dict) -> list[tuple[str, int, list[str]]]:
    expected = [
        (
            str(entry.get("lang", "")),
            int(entry["chunkIndex"]),
            sorted({str(name) for name in entry.get("names", [])}),
        )
        for entry in payload["routing"].get("nodeOfName", [])
    ]
    return sorted(expected, key=lambda row: (row[0], row[1]))


def verify(source_path: Path, sqlite_path: Path) -> dict:
    payload = _load_v1(source_path)
    expected_nodes = _expected_node_chunks(payload)
    expected_names = _expected_name_chunks(payload)
    connection = _open_checked(sqlite_path)
    try:
        actual_nodes = [
            (section, lang, chunk, _decode_nodes(blob, count))
            for section, lang, chunk, count, blob in connection.execute(
                "SELECT section, lang, chunk_index, member_count, members_zlib "
                "FROM node_chunks ORDER BY section, lang, chunk_index"
            )
        ]
        actual_names = [
            (lang, chunk, _decode_names(blob, count))
            for lang, chunk, count, blob in connection.execute(
                "SELECT lang, chunk_index, member_count, names_zlib "
                "FROM name_chunks ORDER BY lang, chunk_index"
            )
        ]
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        connection.close()

    source_sha = _digest(source_path)
    result = {
        "integrityCheck": integrity,
        "nodeChunksMatch": actual_nodes == expected_nodes,
        "nameChunksMatch": actual_names == expected_names,
        "sourceDigestMatch": metadata.get("sourceSha256") == source_sha,
        "nodeChunkRows": len(actual_nodes),
        "nameChunkRows": len(actual_names),
    }
    result["ok"] = (
        result["integrityCheck"] == "ok"
        and result["nodeChunksMatch"]
        and result["nameChunksMatch"]
        and result["sourceDigestMatch"]
    )
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compact zelph-node-route/v1 JSON into a dense SQLite sidecar."
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
