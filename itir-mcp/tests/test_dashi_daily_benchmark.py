from __future__ import annotations

import json
from pathlib import Path

from itir_mcp.dashi_daily_benchmark import (
    build_audit_packet,
    build_renderer_packet,
    compression_metrics,
    convert_chatgpt_exports,
    fact_check_compact_summary,
    main,
    run_dashi_spread_benchmark,
    window_source_rows,
)
from itir_mcp.pnf_spectral_numeric_abi import SCHEMA as SPECTRAL_SCHEMA
from itir_mcp.pnf_spectral_numeric_abi import spectral_parity_hash


def _write_export(path: Path, *, slug: str = "dashi-formal", count: int = 4, long_text: str | None = None) -> Path:
    mapping = {}
    for index in range(count):
        node_id = f"node-{index}"
        text = long_text if index == 1 and long_text is not None else f"Dashi claim {index} has support in the source."
        mapping[node_id] = {
            "id": node_id,
            "parent": None if index == 0 else f"node-{index - 1}",
            "children": [f"node-{index + 1}"] if index + 1 < count else [],
            "message": {
                "id": f"msg-{index}",
                "author": {"role": "user" if index % 2 == 0 else "assistant"},
                "create_time": index,
                "content": {"content_type": "text", "parts": [text]},
            },
        }
    payload = {
        "title": slug,
        "conversation_id": f"conv-{slug}",
        "create_time": 1,
        "mapping": mapping,
    }
    target = path / f"{slug}__fixture.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def _write_spectral_payload(path: Path, *, valid: bool = True) -> Path:
    payload = {
        "schema": SPECTRAL_SCHEMA,
        "graph_version": "graph:test:v1",
        "operator_profile": "spectral-smoke",
        "object_registry": {
            "o0": {"kind": "claim"},
            "o1": {"kind": "claim"},
        },
        "row_map": [
            {"row": 0, "object_id": "o0", "receipt_ids": ["r0"]},
            {"row": 1, "object_id": "o1", "receipt_ids": ["r1"]},
        ],
        "residual_edge_table": [
            {
                "kind": "noTypedMeetEdge",
                "residual_level": "noTypedMeet",
                "source_row": 0,
                "target_row": 1,
                "weight": 3.0,
                "undirected": True,
            },
        ],
        "adjacency": [[0.0, 3.0], [3.0, 0.0]],
        "degree": [3.0, 3.0],
        "laplacian": [[3.0, -3.0], [-3.0, 3.0]],
        "spectral_coordinates": {
            "phi": [
                {"row": 0, "object_id": "o0", "coordinates": [0.0, 1.0]},
                {"row": 1, "object_id": "o1", "coordinates": [1.0, 0.0]},
            ],
            "psi": {
                "probes": [
                    {"probe_id": "p0", "row": 0, "object_id": "o0", "coordinates": [0.0, 1.0], "score": 0.5}
                ]
            },
        },
        "gemv": {
            "z": [1.0, 2.0],
            "A": [[1.0, 0.0], [0.0, 1.0]],
            "b": [0.0, 0.0],
            "row_map": [
                {"row": 0, "object_id": "o0", "receipt_ids": ["r0"]},
                {"row": 1, "object_id": "o1", "receipt_ids": ["r1"]},
            ],
        },
        "receipts": [
            {"receipt_id": "r0", "source": "fixture"},
            {"receipt_id": "r1", "source": "fixture"},
        ],
        "rebuild_witness": {"deterministic_replay": True},
        "authority": {
            "candidate_only": True,
            "truth": False,
            "support": False,
            "admissibility": False,
            "runtime": False,
            "promoted": False,
            "routing": False,
            "vector": False,
        },
    }
    if valid:
        payload["parity_hash"] = spectral_parity_hash(payload)
    else:
        payload["authority"]["truth"] = True
        payload["parity_hash"] = spectral_parity_hash(payload)
    target = path / ("spectral-valid.json" if valid else "spectral-invalid.json")
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def test_chatgpt_mapping_export_converts_deterministically_and_chunks(tmp_path: Path) -> None:
    _write_export(tmp_path, long_text="x" * 13005)
    first = convert_chatgpt_exports(tmp_path, profile=("dashi-formal",))
    second = convert_chatgpt_exports(tmp_path, profile=("dashi-formal",))
    assert first == second
    chunks = [row for row in first if row["node_id"] == "node-1"]
    assert [row["chunk_index"] for row in chunks] == [0, 1, 2]
    assert chunks[0]["conversation_id"] == "conv-dashi-formal"
    assert chunks[0]["source_path"].endswith("dashi-formal__fixture.json")
    assert chunks[0]["role"] == "assistant"


def test_windowing_is_stable_and_respects_caps(tmp_path: Path) -> None:
    _write_export(tmp_path, count=80)
    rows = convert_chatgpt_exports(tmp_path, profile=("dashi-formal",))
    windowed = window_source_rows(rows, per_thread_cap=30, total_cap=25)
    assert len(windowed) == 25
    assert windowed == window_source_rows(rows, per_thread_cap=30, total_cap=25)
    assert windowed[0]["turn_index"] == 0
    assert any(row["turn_index"] > 30 for row in windowed)


def test_renderer_packet_is_compact_and_excludes_raw_text_and_refs(tmp_path: Path) -> None:
    _write_export(tmp_path, count=12)
    rows = window_source_rows(convert_chatgpt_exports(tmp_path, profile=("dashi-formal",)))
    audit = build_audit_packet(rows, date="2026-06-18")
    renderer = build_renderer_packet(audit)
    assert len(json.dumps(renderer)) < len(json.dumps(audit))
    rendered = json.dumps(renderer)
    assert "source_rows" not in renderer
    assert "weak_surfaces" not in renderer
    assert "conflict_surfaces" not in renderer
    assert "receipt_ids" not in rendered
    assert "span_refs" not in rendered
    assert "source_path" not in rendered
    assert "node_id" not in rendered
    assert renderer["facts"]
    assert {"fact_id", "normal_form", "rendered_fact", "fibre_id", "residual_status", "citations", "authority_label"} <= set(
        renderer["facts"][0]
    )
    assert "predicates" not in renderer


def test_compression_metrics_are_emitted(tmp_path: Path) -> None:
    _write_export(tmp_path, count=3)
    rows = convert_chatgpt_exports(tmp_path, profile=("dashi-formal",))
    audit = build_audit_packet(rows, date="2026-06-18")
    renderer = build_renderer_packet(audit)
    metrics = compression_metrics(
        raw_text="\n".join(row["text"] for row in rows),
        source_rows=rows,
        audit_packet=audit,
        renderer_packet=renderer,
        rendered_summary=audit["compact_summary"],
    )
    assert metrics["raw_text_bytes"] > 0
    assert metrics["renderer_packet_bytes"] > 0
    assert "renderer_to_raw_ratio" in metrics


def test_fact_check_reports_unavailable_without_sensiblaw() -> None:
    result = fact_check_compact_summary("- Dashi claim [S1]", [], sensiblaw_available=False)
    assert result["status"] == "unavailable"
    assert result["claims"][0]["classification"] == "UNAVAILABLE"


def test_fact_check_fixture_classifications() -> None:
    surfaces = [
        {"surface_id": "S1", "citation_marker": "[S1]", "text": "Dashi has a kernel operator."},
        {"surface_id": "S2", "citation_marker": "[S2]", "text": "The compact packet preserves citations and predicates."},
        {"surface_id": "S3", "citation_marker": "[S3]", "text": "The ABI is not promoted."},
        {"surface_id": "S4", "citation_marker": "[S4]", "text": "Unrelated material."},
    ]
    summary = "\n".join(
        [
            "- Dashi has a kernel operator. [S1]",
            "- The compact packet preserves citations. [S2]",
            "- The ABI is promoted. [S3]",
            "- A theorem about bananas holds. [S4]",
        ]
    )
    result = fact_check_compact_summary(summary, surfaces, sensiblaw_available=True)
    classes = [claim["classification"] for claim in result["claims"]]
    assert classes == ["EXACT", "PARTIAL", "CONTRADICTION", "NO_TYPED_MEET"]
    assert all(claim["receipt_ids"] == [] for claim in result["claims"])


def test_benchmark_emits_variants_and_diagnostic_abis(tmp_path: Path) -> None:
    _write_export(tmp_path, count=10)
    result = run_dashi_spread_benchmark(tmp_path, date="2026-06-18", profile=("dashi-formal",), min_source_units=1)
    assert set(result["variants"]) == {"A_raw_dashi", "B_full_audit_packet", "C_renderer_packet"}
    assert result["compression_scoreboard"]["renderer_packet_bytes"] < result["compression_scoreboard"]["full_audit_packet_bytes"]
    assert result["fact_check"]["marker"] != "not_run_v0_marker_surface_coverage"
    assert result["abi_statuses"]["numeric_abi_smoke"]["diagnostic_only"] is True
    assert result["abi_statuses"]["spectral_numeric_abi_smoke"]["status"] == "SKIPPED"
    assert result["abi_statuses"]["spectral_numeric_abi_smoke"]["reason"] == "spectral payload not supplied"


def test_spectral_payload_status_is_pass_for_valid_payload(tmp_path: Path) -> None:
    _write_export(tmp_path, count=10)
    payload_path = _write_spectral_payload(tmp_path, valid=True)
    result = run_dashi_spread_benchmark(
        tmp_path,
        date="2026-06-18",
        profile=("dashi-formal",),
        min_source_units=1,
        spectral_payload_path=payload_path,
    )
    spectral = result["abi_statuses"]["spectral_numeric_abi_smoke"]
    assert spectral["status"] == "PASS"
    assert spectral["source"] == "file"
    assert spectral["candidate_only"] is True
    assert spectral["diagnostic_only"] is True
    assert spectral["rows"] == 2
    assert spectral["parity_hash"]


def test_spectral_payload_status_fails_closed_for_invalid_payload(tmp_path: Path) -> None:
    _write_export(tmp_path, count=10)
    payload_path = _write_spectral_payload(tmp_path, valid=False)
    result = run_dashi_spread_benchmark(
        tmp_path,
        date="2026-06-18",
        profile=("dashi-formal",),
        min_source_units=1,
        spectral_payload_path=payload_path,
    )
    spectral = result["abi_statuses"]["spectral_numeric_abi_smoke"]
    assert spectral["status"] == "FAIL"
    assert spectral["diagnostic_only"] is True
    assert spectral["reason"] == "spectral payload invalid"
    assert spectral["diagnostics"]["source"] == "file"
    assert spectral["diagnostics"]["payload_path"] == str(payload_path)
    assert "authority.truth" in spectral["diagnostics"]["error"]


def test_spectral_payload_status_is_pass_for_direct_payload(tmp_path: Path) -> None:
    _write_export(tmp_path, count=10)
    payload_path = _write_spectral_payload(tmp_path, valid=True)
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    result = run_dashi_spread_benchmark(
        tmp_path,
        date="2026-06-18",
        profile=("dashi-formal",),
        min_source_units=1,
        spectral_payload=payload,
    )
    spectral = result["abi_statuses"]["spectral_numeric_abi_smoke"]
    assert spectral["status"] == "PASS"
    assert spectral["source"] == "candidate_payloads"


def test_cli_emits_json_and_respects_spectral_payload(tmp_path: Path, capsys) -> None:
    _write_export(tmp_path, count=10)
    payload_path = _write_spectral_payload(tmp_path, valid=True)
    exit_code = main(
        [
            "--export-dir",
            str(tmp_path),
            "--date",
            "2026-06-18",
            "--profile",
            "dashi-formal",
            "--min-source-units",
            "1",
            "--spectral-payload",
            str(payload_path),
        ]
    )
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert exit_code == 0
    assert result["abi_statuses"]["spectral_numeric_abi_smoke"]["status"] == "PASS"
