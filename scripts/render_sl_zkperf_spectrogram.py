#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

from itir_jmd_bridge.sl_zkperf import build_zkperf_observation_from_contested_review_db
from itir_jmd_bridge.zkperf_stream import (
    build_zkperf_stream_fixture_from_observations,
    load_zkperf_observations,
    load_zkperf_stream_fixture,
    resolve_zkperf_stream_from_index_ipfs,
    resolve_zkperf_stream_from_index_hf,
)
from itir_jmd_bridge.zkperf_viz import (
    render_zkperf_feature_spectrogram,
    render_zkperf_pca_spectrogram,
    render_zkperf_query_spectrogram,
)


def _load_cluster_summary_builder():
    module_path = ROOT_DIR / "scripts" / "inspect_zkperf_clusters.py"
    spec = importlib.util.spec_from_file_location("inspect_zkperf_clusters", module_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"unable to load cluster inspector module at {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_cluster_summary

_QUERY_PRESETS: dict[str, dict[str, float]] = {
    "semantic-gap": {
        "summary.missing_review_count": 3.0,
        "summary.unresolved_conflict_count": 2.5,
        "summary.contested_affidavit_count": 2.0,
        "summary.covered_count": 1.0,
    },
    "coverage-focus": {
        "summary.covered_count": 3.0,
        "summary.missing_review_count": 1.0,
        "summary.partial_count": 1.0,
    },
    "conflict-pressure": {
        "summary.unresolved_conflict_count": 3.0,
        "summary.contested_affidavit_count": 2.0,
        "summary.support_status.contested": 1.5,
    },
    "trace-motion": {
        "trace.progress_delta_ratio": 3.0,
        "trace.progress_remaining_ratio": 2.0,
        "trace.stage_family.progress": 1.5,
        "trace.message_length_chars": 1.0,
    },
    "runtime-cost": {
        "elapsed_ms": 3.0,
        "max_rss_kb": 2.0,
        "minor_page_faults": 1.5,
        "major_page_faults": 1.0,
    },
}

_QUERY_INTENTS: dict[str, tuple[str, ...]] = {
    "coverage-recovery": ("coverage-focus", "semantic-gap"),
    "conflict-audit": ("conflict-pressure", "semantic-gap"),
    "trace-debug": ("trace-motion", "runtime-cost"),
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Render feature and PCA zkperf spectrograms from a SQLite/read-model run, "
            "observation JSON/NDJSON, a local fixture, or an HF-resolved stream selection."
        )
    )
    parser.add_argument(
        "--list-query-presets",
        action="store_true",
        help="Print available query presets and higher-level intents, then exit.",
    )
    source = parser.add_mutually_exclusive_group(required=False)
    source.add_argument("--db-path", type=Path)
    source.add_argument("--observations", type=Path)
    source.add_argument("--fixture", type=Path)
    source.add_argument("--index-hf-uri")
    source.add_argument("--index-ipfs-uri")
    parser.add_argument("--fixture-seed", type=Path)
    parser.add_argument("--gateway-base-url")

    parser.add_argument("--review-run-id")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--feature-prefix", action="append", dest="feature_prefixes")
    parser.add_argument("--top-k-features", type=int, default=32)
    parser.add_argument("--components", type=int, default=8)
    parser.add_argument("--cluster-k", type=int)
    parser.add_argument("--cluster-report", action="store_true", help="Write cluster drilldown JSON from feature metadata")
    parser.add_argument("--cluster-label", help="Restrict cluster report to one cluster label")
    parser.add_argument("--cluster-largest-only", action="store_true", help="Only include the largest cluster in report")
    parser.add_argument("--cluster-top-metrics", type=int, default=8)
    parser.add_argument("--cluster-select-top-clusters", type=int, default=1)
    parser.add_argument("--cluster-select-top-rows", type=int, default=5)
    parser.add_argument("--cluster-report-output", type=Path)
    parser.add_argument("--selection-fixture-output", type=Path)
    parser.add_argument("--query-observation", type=Path)
    parser.add_argument("--query-metric", action="append", dest="query_metrics", help="Query metric as name=value. Repeatable.")
    parser.add_argument(
        "--query-preset",
        action="append",
        dest="query_presets",
        choices=sorted(_QUERY_PRESETS),
        help="Query preset name. Repeatable.",
    )
    parser.add_argument(
        "--query-intent",
        action="append",
        dest="query_intents",
        choices=sorted(_QUERY_INTENTS),
        help="Higher-level operator intent. Expands to one or more query presets.",
    )
    parser.add_argument("--stream-id")
    parser.add_argument("--stream-revision")
    parser.add_argument("--created-at-utc")
    parser.add_argument("--max-observations-per-window", type=int)
    parser.add_argument("--write-observation", action="store_true")
    parser.add_argument("--write-fixture", action="store_true")
    parser.add_argument("--summary-output", type=Path)

    parser.add_argument("--index-revision")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--window-id")
    parser.add_argument("--sequence-start", type=int)
    parser.add_argument("--sequence-end", type=int)
    parser.add_argument("--select-window-id", action="append", dest="window_ids")
    return parser


def _normalize_hf_resolved_payload(payload: dict[str, Any]) -> dict[str, Any]:
    windows = []
    for row in payload.get("windows", []):
        if not isinstance(row, dict):
            continue
        window_meta = row.get("window")
        payload_info = row.get("payload")
        if not isinstance(window_meta, dict) or not isinstance(payload_info, dict):
            continue
        payload_json = payload_info.get("json")
        if not isinstance(payload_json, dict):
            continue
        windows.append(
            {
                "windowId": window_meta.get("windowId"),
                "sequence": window_meta.get("sequence"),
                "payload": payload_json,
            }
        )
    return {
        "contractVersion": "zkperf-stream/v1",
        "streamId": payload.get("streamId"),
        "streamRevision": payload.get("streamRevision"),
        "streamKind": "zkperf-observation-stream",
        "windowingMode": "resolved-selection",
        "windows": windows,
    }


def _build_fixture_from_args(args: argparse.Namespace, output_dir: Path) -> tuple[str, dict[str, Any], dict[str, str]]:
    written_paths: dict[str, str] = {}

    if args.db_path is not None:
        observation = build_zkperf_observation_from_contested_review_db(
            args.db_path,
            review_run_id=args.review_run_id,
        )
        if args.write_observation:
            observation_path = output_dir / "observation.json"
            observation_path.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            written_paths["observationPath"] = str(observation_path.resolve())
        fixture = build_zkperf_stream_fixture_from_observations(
            [observation],
            stream_id=args.stream_id,
            stream_revision=args.stream_revision,
            created_at_utc=args.created_at_utc,
            max_observations_per_window=args.max_observations_per_window,
        )
        return "db", fixture, written_paths

    if args.observations is not None:
        observations = load_zkperf_observations(args.observations)
        fixture = build_zkperf_stream_fixture_from_observations(
            observations,
            stream_id=args.stream_id,
            stream_revision=args.stream_revision,
            created_at_utc=args.created_at_utc,
            max_observations_per_window=args.max_observations_per_window,
        )
        return "observations", fixture, written_paths

    if args.fixture is not None and args.index_hf_uri is None and args.index_ipfs_uri is None:
        return "fixture", load_zkperf_stream_fixture(args.fixture), written_paths

    selection_requested = any(
        value is not None and value is not False and value != []
        for value in (
            args.window_id,
            args.sequence_start,
            args.sequence_end,
            args.window_ids,
            args.stream_revision,
        )
    )
    if args.index_hf_uri is not None:
        resolved = resolve_zkperf_stream_from_index_hf(
            fixture_path=args.fixture_seed,
            index_hf_uri=str(args.index_hf_uri),
            index_revision=args.index_revision,
            latest=bool(args.latest or not selection_requested),
            stream_revision=args.stream_revision,
            window_id=args.window_id,
            sequence_start=args.sequence_start,
            sequence_end=args.sequence_end,
            window_ids=args.window_ids,
        )
        input_mode = "hf_index"
    else:
        resolved = resolve_zkperf_stream_from_index_ipfs(
            fixture_path=args.fixture_seed,
            index_ipfs_uri=str(args.index_ipfs_uri),
            gateway_base_url=args.gateway_base_url,
            latest=bool(args.latest or not selection_requested),
            stream_revision=args.stream_revision,
            window_id=args.window_id,
            sequence_start=args.sequence_start,
            sequence_end=args.sequence_end,
            window_ids=args.window_ids,
        )
        input_mode = "ipfs_index"
    fixture = _normalize_hf_resolved_payload(resolved)
    if args.write_fixture:
        resolved_path = output_dir / "resolved-fixture.json"
        resolved_path.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written_paths["resolvedFixturePath"] = str(resolved_path.resolve())
    return input_mode, fixture, written_paths


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.list_query_presets:
        print(json.dumps(_query_catalog(), indent=2, sort_keys=True))
        return 0
    if args.output_dir is None:
        raise SystemExit("--output-dir is required unless --list-query-presets is used")
    if not any(
        value is not None
        for value in (args.db_path, args.observations, args.fixture, args.index_hf_uri, args.index_ipfs_uri)
    ):
        raise SystemExit("one input source is required unless --list-query-presets is used")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if (args.index_hf_uri or args.index_ipfs_uri) and args.fixture_seed is None:
        raise SystemExit("--index-hf-uri/--index-ipfs-uri requires --fixture-seed as the local stream-manifest seed")

    input_mode, fixture, written_paths = _build_fixture_from_args(args, output_dir)

    if args.write_fixture and input_mode != "hf_index":
        fixture_path = output_dir / "fixture.json"
        fixture_path.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written_paths["fixturePath"] = str(fixture_path.resolve())

    feature_png = output_dir / "zkperf-feature-spectrogram.png"
    feature_meta = output_dir / "zkperf-feature-spectrogram.json"
    pca_png = output_dir / "zkperf-pca-spectrogram.png"
    pca_meta = output_dir / "zkperf-pca-spectrogram.json"
    query_png = output_dir / "zkperf-query-spectrogram.png"
    query_meta = output_dir / "zkperf-query-spectrogram.json"

    feature_payload = render_zkperf_feature_spectrogram(
        fixture,
        output_path=feature_png,
        metadata_path=feature_meta,
        top_k_features=args.top_k_features,
        feature_prefixes=list(args.feature_prefixes) if args.feature_prefixes else None,
        cluster_k=args.cluster_k,
    )
    pca_payload = render_zkperf_pca_spectrogram(
        fixture,
        output_path=pca_png,
        metadata_path=pca_meta,
        top_k_features=args.top_k_features,
        components=args.components,
        feature_prefixes=list(args.feature_prefixes) if args.feature_prefixes else None,
        cluster_k=args.cluster_k,
    )
    query_payload = None
    query_preset_names = list(args.query_presets or [])
    query_intents = list(args.query_intents or [])
    for intent_name in query_intents:
        query_preset_names.extend(_QUERY_INTENTS[intent_name])
    query_preset_metrics = _expand_query_presets(query_preset_names)
    query_metrics = _parse_query_metrics(args.query_metrics)
    query_observation = _load_query_observation(args.query_observation)
    combined_query_metrics = dict(query_preset_metrics)
    combined_query_metrics.update(query_metrics)
    if combined_query_metrics or query_observation is not None:
        query_payload = render_zkperf_query_spectrogram(
            fixture,
            output_path=query_png,
            metadata_path=query_meta,
            query_metrics=combined_query_metrics or None,
            query_observation=query_observation,
            feature_prefixes=list(args.feature_prefixes) if args.feature_prefixes else None,
        )
        if query_preset_names:
            query_payload["queryPresetNames"] = query_preset_names
            query_payload["queryPresetMetrics"] = query_preset_metrics
        if query_intents:
            query_payload["queryIntentNames"] = query_intents
            if "metadataPath" in query_payload:
                Path(query_payload["metadataPath"]).write_text(
                    json.dumps(query_payload, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

    summary = {
        "inputMode": input_mode,
        "outputDir": str(output_dir),
        "featureSpectrogram": feature_payload,
        "pcaSpectrogram": pca_payload,
        **written_paths,
    }
    if query_payload is not None:
        summary["querySpectrogram"] = query_payload

    if args.cluster_report:
        if not isinstance(feature_payload, dict) or "clusterLabels" not in feature_payload:
            raise SystemExit("--cluster-report requires --cluster-k with at least two clusters in feature spectrogram output")
        build_cluster_summary = _load_cluster_summary_builder()
        cluster_summary = build_cluster_summary(
            feature_payload,
            fixture=fixture,
            query_metadata=query_payload,
            top_metrics=args.cluster_top_metrics,
            include_rows=True,
            include_all_clusters=not args.cluster_largest_only,
            cluster_filter=args.cluster_label,
            select_top_clusters=args.cluster_select_top_clusters,
            select_top_rows=args.cluster_select_top_rows,
        )
        cluster_report_path = args.cluster_report_output or (output_dir / "zkperf-cluster-report.json")
        cluster_report_path.parent.mkdir(parents=True, exist_ok=True)
        cluster_report_path.write_text(json.dumps(cluster_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary["clusterReportPath"] = str(cluster_report_path.resolve())
        summary["clusterReport"] = cluster_summary
        selection_fixture_path = args.selection_fixture_output
        if selection_fixture_path is None and isinstance(cluster_summary.get("selection"), dict):
            selection_fixture_path = output_dir / "zkperf-selection-fixture.json"
        if selection_fixture_path is not None and isinstance(cluster_summary.get("selection"), dict):
            selected_fixture = {
                "contractVersion": fixture.get("contractVersion", "zkperf-stream/v1"),
                "streamId": fixture.get("streamId"),
                "streamRevision": fixture.get("streamRevision"),
                "streamKind": fixture.get("streamKind", "zkperf-observation-stream"),
                "windowingMode": "cluster-selection",
                "selectionMode": "query_alignment",
                "windows": [],
            }
            wanted = {
                row.get("rowLabel")
                for row in cluster_summary["selection"].get("recommendedRows", [])
                if isinstance(row, dict) and isinstance(row.get("rowLabel"), str)
            }
            for window in fixture.get("windows", []):
                if not isinstance(window, dict):
                    continue
                payload = window.get("payload")
                observations = payload.get("observations") if isinstance(payload, dict) else None
                window_id = window.get("windowId")
                if not isinstance(window_id, str) or not isinstance(observations, list):
                    continue
                kept = []
                sequence = int(window.get("sequence") or 0)
                for index, observation in enumerate(observations, start=1):
                    row_label = f"{sequence:04d}:{window_id}:{index}"
                    if row_label in wanted and isinstance(observation, dict):
                        kept.append(observation)
                if kept:
                    selected_fixture["windows"].append(
                        {
                            "windowId": window_id,
                            "sequence": window.get("sequence"),
                            "payload": {"observations": kept},
                        }
                    )
            selection_fixture_path.parent.mkdir(parents=True, exist_ok=True)
            selection_fixture_path.write_text(
                json.dumps(selected_fixture, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            summary["selectionFixturePath"] = str(selection_fixture_path.resolve())

    if args.summary_output is not None:
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        args.summary_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary["summaryOutput"] = str(args.summary_output.resolve())
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _expand_query_presets(items: list[str] | None) -> dict[str, float]:
    expanded: dict[str, float] = {}
    for item in items or []:
        preset = _QUERY_PRESETS.get(item)
        if preset is None:
            raise SystemExit(f"unknown --query-preset {item!r}")
        for metric_name, metric_value in preset.items():
            expanded[metric_name] = expanded.get(metric_name, 0.0) + float(metric_value)
    return expanded


def _query_catalog() -> dict[str, Any]:
    return {
        "queryIntents": {name: list(presets) for name, presets in sorted(_QUERY_INTENTS.items())},
        "queryPresets": {name: metrics for name, metrics in sorted(_QUERY_PRESETS.items())},
    }


def _parse_query_metrics(items: list[str] | None) -> dict[str, float]:
    parsed: dict[str, float] = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"invalid --query-metric {item!r}; expected name=value")
        name, value_text = item.split("=", 1)
        try:
            value = float(value_text)
        except ValueError as exc:
            raise SystemExit(f"invalid numeric value in --query-metric {item!r}") from exc
        parsed[name] = value
    return parsed


def _load_query_observation(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("--query-observation must be a JSON object")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
