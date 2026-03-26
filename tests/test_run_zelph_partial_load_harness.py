from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from run_zelph_partial_load_harness import HarnessCase, build_case_matrix, build_fetch_plan, classify_result


def test_classify_result_marks_fallback_case_ok() -> None:
    case = HarnessCase(
        name="manifest_v1_left0",
        command=".load-partial manifest left=0",
        expected_mode="fallback_or_ok",
    )
    output = """
Partial loading from manifest: left chunks=1/18, right chunks=18/18, nameOfNode chunks=8/8, nodeOfName chunks=8/8, skip_payload=false
Shard chunk left/0 failed (...); falling back to sequential bin load
Partial loading: left chunks=1/18, right chunks=18/18, nameOfNode chunks=8/8, nodeOfName chunks=8/8, skip_payload=false
String pool size after partial load: 6632692
WARNING: partial/incomplete graph loaded; reasoning, pruning, cleanup, and destructive edits are blocked.
Time needed for partial loading: 0h0m18.159s
"""
    result = classify_result(Path("/tmp/demo.bin"), case, 0, output, 18.2)
    assert result.ok is True
    assert result.fallback_used is True
    assert result.had_repl_error is False
    assert result.reported_partial_time == "0h0m18.159s"


def test_classify_result_marks_repl_error_not_ok() -> None:
    case = HarnessCase(
        name="manifest_v1_left0",
        command=".load-partial manifest left=0",
        expected_mode="fallback_or_ok",
    )
    output = """
Partial loading from manifest: left chunks=1/18, right chunks=18/18, nameOfNode chunks=8/8, nodeOfName chunks=8/8, skip_payload=false
Error in line ".load-partial manifest left=0": capnp/serialize.c++:201: failed
"""
    result = classify_result(Path("/tmp/demo.bin"), case, 0, output, 1.1)
    assert result.ok is False
    assert result.had_repl_error is True


def test_classify_result_marks_direct_case_ok() -> None:
    case = HarnessCase(
        name="bin_left0",
        command=".load-partial demo.bin left=0 right=none nameOfNode=none nodeOfName=none",
        expected_mode="ok",
    )
    output = """
Partial loading: left chunks=1/18, right chunks=0/18, nameOfNode chunks=0/8, nodeOfName chunks=0/8, skip_payload=false
String pool size after partial load: 0
WARNING: partial/incomplete graph loaded; reasoning, pruning, cleanup, and destructive edits are blocked.
Time needed for partial loading: 0h0m2.490s
"""
    result = classify_result(Path("/tmp/demo.bin"), case, 0, output, 2.5)
    assert result.ok is True
    assert result.fallback_used is False
    assert result.reported_partial_time == "0h0m2.490s"


def test_build_case_matrix_extended_contains_node_and_mixed_cases() -> None:
    cases = build_case_matrix(
        artifact=Path("/tmp/demo.bin"),
        manifest_v1=Path("/tmp/demo-v1.json"),
        manifest_v2=Path("/tmp/demo-v2.json"),
        shard_root=Path("/tmp/demo-shards"),
        include_name_cases=True,
    )
    names = {case.name for case in cases}
    assert "bin_nodeOfName0" in names
    assert "manifest_v1_nodeOfName0" in names
    assert "manifest_v2_nodeOfName0" in names
    assert "bin_left0_nameOfNode0" in names
    assert "manifest_v1_left0_nameOfNode0" in names
    assert "manifest_v2_left0_nameOfNode0" in names


def test_build_fetch_plan_for_v1_manifest_uses_http_ranges(tmp_path: Path) -> None:
    manifest_path = tmp_path / "artifact.hf-v1.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifestVersion": "zelph-hf-layout/v1",
                "transport": {"primary": "http-range"},
                "hfObjects": {"bin": {"path": "hf://datasets/acrion/zelph/demo/artifact.bin"}},
                "sections": {
                    "left": {
                        "chunks": [
                            {"chunkIndex": 0, "range": "bytes=128-227"},
                        ]
                    },
                    "right": {"chunks": []},
                    "nameOfNode": {"chunks": []},
                    "nodeOfName": {"chunks": []},
                },
            }
        ),
        encoding="utf-8",
    )
    case = HarnessCase(
        name="manifest_v1_left0",
        command=f".load-partial {manifest_path} left=0 right=none nameOfNode=none nodeOfName=none manifest={manifest_path}",
        expected_mode="fallback_or_ok",
        artifact_kind="manifest",
    )

    plan = build_fetch_plan(case, Path("/tmp/demo.bin"))

    assert plan is not None
    assert plan["transport"] == "http-range"
    assert plan["headerProbeOnly"] is False
    assert plan["fetchRefs"] == [
        {
            "section": "left",
            "chunkIndex": 0,
            "transport": "http-range",
            "objectPath": "hf://datasets/acrion/zelph/demo/artifact.bin",
            "range": "bytes=128-227",
        }
    ]


def test_build_fetch_plan_for_v2_manifest_uses_object_paths(tmp_path: Path) -> None:
    manifest_path = tmp_path / "artifact.hf-v2.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifestVersion": "zelph-hf-layout/v2",
                "transport": {"primary": "hf-object-fetch"},
                "sections": {
                    "left": {"chunks": []},
                    "right": {"chunks": []},
                    "nameOfNode": {
                        "chunks": [
                            {
                                "chunkIndex": 0,
                                "objectPath": "hf://datasets/acrion/zelph/demo/shards/nameOfNode/chunk-000000-en.capnp-packed",
                                "length": 4096,
                                "lang": "en",
                            }
                        ]
                    },
                    "nodeOfName": {"chunks": []},
                },
            }
        ),
        encoding="utf-8",
    )
    case = HarnessCase(
        name="manifest_v2_nameOfNode0",
        command=f".load-partial {manifest_path} left=none right=none nameOfNode=0 nodeOfName=none manifest={manifest_path} shard-root=/tmp/demo-shards",
        expected_mode="fallback_or_ok",
        artifact_kind="manifest",
    )

    plan = build_fetch_plan(case, Path("/tmp/demo.bin"))

    assert plan is not None
    assert plan["transport"] == "hf-object-fetch"
    assert plan["headerProbeOnly"] is False
    assert plan["fetchRefs"] == [
        {
            "section": "nameOfNode",
            "chunkIndex": 0,
            "transport": "hf-object-fetch",
            "objectPath": "hf://datasets/acrion/zelph/demo/shards/nameOfNode/chunk-000000-en.capnp-packed",
            "sizeBytes": 4096,
        }
    ]


def test_build_fetch_plan_surfaces_node_route_index_metadata(tmp_path: Path) -> None:
    manifest_path = tmp_path / "artifact.hf-v2.json"
    manifest_path.write_text(
        json.dumps(
            {
                "manifestVersion": "zelph-hf-layout/v2",
                "transport": {"primary": "hf-object-fetch"},
                "hfObjects": {
                    "nodeRouteIndex": {
                        "path": "hf://datasets/acrion/zelph/demo/artifact.route.json",
                        "role": "node-route-sidecar",
                        "mediaType": "application/json",
                        "sizeBytes": 512,
                    }
                },
                "sections": {
                    "left": {"chunks": []},
                    "right": {"chunks": []},
                    "nameOfNode": {"chunks": []},
                    "nodeOfName": {"chunks": []},
                },
            }
        ),
        encoding="utf-8",
    )
    case = HarnessCase(
        name="manifest_v2_meta_only",
        command=f".load-partial {manifest_path} left=none right=none nameOfNode=none nodeOfName=none manifest={manifest_path}",
        expected_mode="ok",
        artifact_kind="manifest",
    )

    plan = build_fetch_plan(case, Path("/tmp/demo.bin"))

    assert plan is not None
    assert plan["nodeRouteIndex"]["path"] == "hf://datasets/acrion/zelph/demo/artifact.route.json"
