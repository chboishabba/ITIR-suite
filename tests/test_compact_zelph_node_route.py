from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_tool():
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "tools" / "compact_zelph_node_route.py"
    spec = importlib.util.spec_from_file_location("compact_zelph_node_route", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _route_fixture(path: Path) -> None:
    payload = {
        "routeVersion": "zelph-node-route/v1",
        "source": {
            "binPath": "/data/demo.bin",
            "binSizeBytes": 4096,
            "headerLengthBytes": 128,
            "leftChunkCount": 2,
            "rightChunkCount": 1,
            "nameOfNodeChunkCount": 2,
            "nodeOfNameChunkCount": 2,
        },
        "routing": {
            "left": [
                {"chunkIndex": 0, "which": "left", "entryCount": 3, "nodes": [42, 7, 42]},
                {"chunkIndex": 1, "which": "left", "entryCount": 1, "nodes": [42]},
            ],
            "right": [
                {"chunkIndex": 2, "which": "right", "entryCount": 2, "nodes": [99, 42]},
            ],
            "nameOfNode": [
                {"lang": "en", "chunkIndex": 3, "entryCount": 2, "nodes": [42, 7]},
                {"lang": "wikidata", "chunkIndex": 4, "entryCount": 1, "nodes": [42]},
            ],
            "nodeOfName": [
                {
                    "lang": "en",
                    "chunkIndex": 5,
                    "entryCount": 3,
                    "names": ["Douglas Adams", "Alice", "Alice"],
                },
                {
                    "lang": "wikidata",
                    "chunkIndex": 6,
                    "entryCount": 1,
                    "names": ["Douglas Adams"],
                },
            ],
        },
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_compact_route_roundtrip_and_keyed_lookup(tmp_path: Path) -> None:
    tool = _load_tool()
    source = tmp_path / "route.json"
    compact = tmp_path / "route.sqlite"
    _route_fixture(source)

    stats = tool.compact(source, compact)
    verified = tool.verify(source, compact)

    assert stats["routeVersion"] == "zelph-node-route/sqlite-v1"
    assert stats["sourceRouteVersion"] == "zelph-node-route/v1"
    assert stats["encoding"] == "sqlite-chunk-zlib-delta-varint"
    assert stats["nodeChunkRows"] == 5
    assert stats["nameChunkRows"] == 2
    assert stats["nodeMemberships"] == 8
    assert stats["nameMemberships"] == 3
    assert verified == {
        "integrityCheck": "ok",
        "nodeChunksMatch": True,
        "nameChunksMatch": True,
        "sourceDigestMatch": True,
        "nodeChunkRows": 5,
        "nameChunkRows": 2,
        "ok": True,
    }

    assert tool.lookup_node(compact, 42, section="left") == [
        {"section": "left", "lang": "", "chunkIndex": 0},
        {"section": "left", "lang": "", "chunkIndex": 1},
    ]
    assert tool.lookup_node(compact, 42, section="nameOfNode", lang="en") == [
        {"section": "nameOfNode", "lang": "en", "chunkIndex": 3}
    ]
    assert tool.lookup_name(compact, "Douglas Adams", "en") == [5]
    assert tool.lookup_name(compact, "Douglas Adams", "wikidata") == [6]


def test_compact_route_is_byte_deterministic(tmp_path: Path) -> None:
    tool = _load_tool()
    source = tmp_path / "route.json"
    first = tmp_path / "first.sqlite"
    second = tmp_path / "second.sqlite"
    _route_fixture(source)

    first_stats = tool.compact(source, first)
    second_stats = tool.compact(source, second)

    assert first.read_bytes() == second.read_bytes()
    assert first_stats["outputSha256"] == second_stats["outputSha256"]


def test_compact_route_is_materially_denser_for_large_numeric_membership(tmp_path: Path) -> None:
    tool = _load_tool()
    source = tmp_path / "large.route.json"
    compact = tmp_path / "large.route.sqlite"

    chunks = []
    for chunk_index in range(8):
        start = chunk_index * 5000
        nodes = list(range(start, start + 5000))
        chunks.append(
            {
                "chunkIndex": chunk_index,
                "which": "left",
                "entryCount": len(nodes),
                "nodes": nodes,
            }
        )
    source.write_text(
        json.dumps(
            {
                "routeVersion": "zelph-node-route/v1",
                "source": {"binPath": "/data/large.bin"},
                "routing": {
                    "left": chunks,
                    "right": [],
                    "nameOfNode": [],
                    "nodeOfName": [],
                },
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )

    stats = tool.compact(source, compact)
    assert tool.verify(source, compact)["ok"] is True
    assert stats["outputBytes"] < stats["sourceBytes"] // 2


def test_compact_route_rejects_non_v1_source(tmp_path: Path) -> None:
    tool = _load_tool()
    source = tmp_path / "route.json"
    source.write_text(
        json.dumps({"routeVersion": "zelph-node-route/v2", "routing": {}}),
        encoding="utf-8",
    )

    try:
        tool.compact(source, tmp_path / "route.sqlite")
    except tool.RouteFormatError as exc:
        assert "expected routeVersion='zelph-node-route/v1'" in str(exc)
    else:
        raise AssertionError("non-v1 route source must fail closed")


def test_verify_detects_source_drift(tmp_path: Path) -> None:
    tool = _load_tool()
    source = tmp_path / "route.json"
    compact = tmp_path / "route.sqlite"
    _route_fixture(source)
    tool.compact(source, compact)

    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["routing"]["left"][0]["nodes"].append(123456)
    source.write_text(json.dumps(payload), encoding="utf-8")

    result = tool.verify(source, compact)
    assert result["ok"] is False
    assert result["nodeChunksMatch"] is False
    assert result["sourceDigestMatch"] is False
