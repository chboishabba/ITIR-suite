#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


def _cluster_sort_key(value: Any) -> tuple[int, str]:
    try:
        return (0, f"{int(value):020d}")
    except (TypeError, ValueError):
        return (1, str(value))


def _normalize_label(value: Any) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


_ROW_LABEL_RE = re.compile(r"^\d+:(?P<window>[^:]+):(?P<ordinal>\d+)$")


def _parse_row_label(value: str) -> tuple[str, int] | None:
    match = _ROW_LABEL_RE.match(value)
    if match is None:
        return None
    try:
        ordinal = int(match.group("ordinal"))
    except ValueError:
        return None
    return (match.group("window"), ordinal)


def _load_observations_from_fixture(fixture: dict[str, Any]) -> dict[str, dict[str, float]]:
    by_row: dict[str, dict[str, float]] = {}
    for window in fixture.get("windows", []):
        if not isinstance(window, dict):
            continue
        window_id = window.get("windowId")
        payload = window.get("payload")
        if not isinstance(window_id, str) or not isinstance(payload, dict):
            continue
        observations = payload.get("observations")
        if not isinstance(observations, list):
            continue
        for index, observation in enumerate(observations, start=1):
            if not isinstance(observation, dict):
                continue
            metrics = observation.get("metrics")
            if not isinstance(metrics, list):
                continue
            values: dict[str, float] = {}
            for metric_row in metrics:
                if not isinstance(metric_row, dict):
                    continue
                name = metric_row.get("metric")
                value = metric_row.get("value")
                if not isinstance(name, str):
                    continue
                if isinstance(value, (int, float)):
                    values[name] = float(value)
            if not values:
                continue
            row_label = f"{window_id}:{index}"
            by_row[row_label] = values
    return by_row


def _summarize_cluster_metrics(
    row_labels: list[str],
    metrics_by_row: dict[str, dict[str, float]],
    *,
    top_metrics: int,
) -> tuple[dict[str, float], dict[str, Any]]:
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    matched_rows = 0
    for row in row_labels:
        parsed = _parse_row_label(row)
        if parsed is None:
            continue
        lookup_key = f"{parsed[0]}:{parsed[1]}"
        metric_map = metrics_by_row.get(lookup_key)
        if metric_map is None:
            continue
        matched_rows += 1
        for name, value in metric_map.items():
            totals[name] = totals.get(name, 0.0) + value
            counts[name] = counts.get(name, 0) + 1

    if matched_rows == 0:
        return {}, {"matchedRowCount": 0}

    averages = {name: totals[name] / counts[name] for name in totals}
    ranked = sorted(averages.items(), key=lambda item: (-abs(item[1]), item[0]))
    top = {name: value for name, value in ranked[: max(1, top_metrics)]}
    signal: dict[str, Any] = {"matchedRowCount": matched_rows}
    if "semantic_gap_score" in averages:
        signal["semanticGapScoreAvg"] = averages["semantic_gap_score"]
    if "elapsed_ms" in averages:
        signal["elapsedMsAvg"] = averages["elapsed_ms"]
    signal["dominantStageFamilies"] = _top_prefixed_metric_counts(averages, "trace.stage_family.", top_n=3)
    signal["dominantDomainRoles"] = _top_prefixed_metric_counts(averages, "trace.domain_role.", top_n=4)
    signal["dominantDomainSignals"] = _top_prefixed_metric_counts(averages, "trace.domain_signal.", top_n=4)
    return top, signal


def _top_prefixed_metric_counts(values: dict[str, float], prefix: str, *, top_n: int) -> dict[str, float]:
    subset = {
        key[len(prefix) :]: value
        for key, value in values.items()
        if key.startswith(prefix) and isinstance(value, (int, float))
    }
    ranked = sorted(subset.items(), key=lambda item: (-abs(item[1]), item[0]))
    return {key: value for key, value in ranked[: max(1, top_n)]}


def _build_query_score_map(query_metadata: dict[str, Any] | None) -> dict[str, float]:
    if not isinstance(query_metadata, dict):
        return {}
    row_labels = query_metadata.get("rowLabels")
    scores = query_metadata.get("scores")
    if not isinstance(row_labels, list) or not isinstance(scores, list) or len(row_labels) != len(scores):
        return {}
    result: dict[str, float] = {}
    for row_label, score in zip(row_labels, scores):
        if isinstance(row_label, str) and isinstance(score, (int, float)):
            result[row_label] = float(score)
    return result


def _build_cluster_selection(
    ordered_clusters: list[dict[str, Any]],
    query_scores: dict[str, float],
    *,
    top_clusters: int,
    top_rows: int,
) -> dict[str, Any] | None:
    if not query_scores:
        return None

    ranked_clusters: list[dict[str, Any]] = []
    for cluster in ordered_clusters:
        row_labels = cluster.get("rows")
        if not isinstance(row_labels, list):
            row_labels = []
            first_row = cluster.get("firstRow")
            last_row = cluster.get("lastRow")
            if isinstance(first_row, str):
                row_labels.append(first_row)
            if isinstance(last_row, str) and last_row != first_row:
                row_labels.append(last_row)
        scored_rows = [
            {"rowLabel": row_label, "score": query_scores[row_label]}
            for row_label in row_labels
            if row_label in query_scores
        ]
        if not scored_rows:
            continue
        scored_rows.sort(key=lambda row: (-row["score"], row["rowLabel"]))
        avg_score = sum(row["score"] for row in scored_rows) / len(scored_rows)
        ranked_clusters.append(
            {
                "label": cluster["label"],
                "count": cluster["count"],
                "avgQueryScore": avg_score,
                "maxQueryScore": scored_rows[0]["score"],
                "topRows": scored_rows[: max(1, top_rows)],
            }
        )

    if not ranked_clusters:
        return None

    ranked_clusters.sort(key=lambda row: (-row["avgQueryScore"], -row["maxQueryScore"], row["label"]))
    selected_clusters = ranked_clusters[: max(1, top_clusters)]
    selected_rows: list[dict[str, Any]] = []
    for cluster in selected_clusters:
        selected_rows.extend(cluster["topRows"])
    selected_rows.sort(key=lambda row: (-row["score"], row["rowLabel"]))

    return {
        "mode": "query_alignment",
        "recommendedClusterLabels": [row["label"] for row in selected_clusters],
        "recommendedRows": selected_rows[: max(1, top_rows)],
        "clusterRanking": selected_clusters,
    }


def _build_selected_fixture(
    fixture: dict[str, Any],
    recommended_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    selected_labels = {
        row.get("rowLabel")
        for row in recommended_rows
        if isinstance(row, dict) and isinstance(row.get("rowLabel"), str)
    }
    windows_out: list[dict[str, Any]] = []
    for window in fixture.get("windows", []):
        if not isinstance(window, dict):
            continue
        window_id = window.get("windowId")
        payload = window.get("payload")
        observations = payload.get("observations") if isinstance(payload, dict) else None
        if not isinstance(window_id, str) or not isinstance(observations, list):
            continue
        kept: list[dict[str, Any]] = []
        for index, observation in enumerate(observations, start=1):
            row_label = f"{window.get('sequence', 0):04d}:{window_id}:{index}"
            if row_label in selected_labels and isinstance(observation, dict):
                kept.append(observation)
        if kept:
            windows_out.append(
                {
                    "windowId": window_id,
                    "sequence": window.get("sequence"),
                    "payload": {"observations": kept},
                }
            )
    return {
        "contractVersion": fixture.get("contractVersion", "zkperf-stream/v1"),
        "streamId": fixture.get("streamId"),
        "streamRevision": fixture.get("streamRevision"),
        "streamKind": fixture.get("streamKind", "zkperf-observation-stream"),
        "windowingMode": "cluster-selection",
        "selectionMode": "query_alignment",
        "windows": windows_out,
    }


def build_cluster_summary(
    metadata: dict[str, Any],
    *,
    fixture: dict[str, Any] | None = None,
    query_metadata: dict[str, Any] | None = None,
    top_metrics: int = 8,
    include_rows: bool = True,
    include_all_clusters: bool = True,
    cluster_filter: str | None = None,
    select_top_clusters: int = 1,
    select_top_rows: int = 5,
) -> dict[str, Any]:
    row_labels = metadata.get("rowLabels")
    cluster_labels = metadata.get("clusterLabels")
    cluster_counts = metadata.get("clusterCounts")
    if not isinstance(row_labels, list) or not isinstance(cluster_labels, list):
        raise ValueError("metadata must include rowLabels and clusterLabels")
    if len(row_labels) != len(cluster_labels):
        raise ValueError("rowLabels and clusterLabels must have the same length")

    clusters: dict[str, dict[str, Any]] = {}
    for row_label, cluster_label in zip(row_labels, cluster_labels):
        label = _normalize_label(cluster_label)
        cluster = clusters.setdefault(
            label,
            {
                "label": label,
                "count": 0,
                "rows": [] if include_rows else None,
                "firstRow": None,
                "lastRow": None,
            },
        )
        row_text = str(row_label)
        cluster["count"] += 1
        if include_rows:
            cluster["rows"].append(row_text)
        if cluster["firstRow"] is None:
            cluster["firstRow"] = row_text
        cluster["lastRow"] = row_text

    ordered_clusters = [clusters[key] for key in sorted(clusters.keys(), key=_cluster_sort_key)]
    if cluster_filter is not None:
        ordered_clusters = [cluster for cluster in ordered_clusters if cluster["label"] == cluster_filter]
    elif not include_all_clusters and ordered_clusters:
        ordered_clusters = [max(ordered_clusters, key=lambda cluster: cluster["count"])]

    metrics_by_row = _load_observations_from_fixture(fixture) if isinstance(fixture, dict) else {}
    for cluster in ordered_clusters:
        row_values: list[str]
        if include_rows and isinstance(cluster.get("rows"), list):
            row_values = cluster["rows"]
        else:
            first_row = cluster.get("firstRow")
            last_row = cluster.get("lastRow")
            row_values = []
            if isinstance(first_row, str):
                row_values.append(first_row)
            if isinstance(last_row, str) and last_row != first_row:
                row_values.append(last_row)
        if metrics_by_row:
            top, signal = _summarize_cluster_metrics(row_values, metrics_by_row, top_metrics=top_metrics)
            cluster["topMetrics"] = top
            cluster["signals"] = signal
        cluster["windowCounts"] = _cluster_window_counts(row_values)
        cluster["retrievalCandidates"] = _cluster_retrieval_candidates(row_values, metrics_by_row)

    summary: dict[str, Any] = {
        "streamId": metadata.get("streamId"),
        "streamRevision": metadata.get("streamRevision"),
        "rowCount": len(row_labels),
        "clusterCount": len(ordered_clusters),
        "clusters": ordered_clusters,
    }
    if isinstance(cluster_counts, dict):
        summary["clusterCounts"] = {
            _normalize_label(key): value
            for key, value in sorted(cluster_counts.items(), key=lambda item: _cluster_sort_key(item[0]))
        }
    else:
        summary["clusterCounts"] = {cluster["label"]: cluster["count"] for cluster in ordered_clusters}
    selection = _build_cluster_selection(
        ordered_clusters,
        _build_query_score_map(query_metadata),
        top_clusters=select_top_clusters,
        top_rows=select_top_rows,
    )
    if selection is not None:
        summary["selection"] = selection
    return summary


def _cluster_window_counts(row_values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in row_values:
        parsed = _parse_row_label(row)
        if parsed is None:
            continue
        window_id, _ = parsed
        counts[window_id] = counts.get(window_id, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _cluster_retrieval_candidates(row_values: list[str], metrics_by_row: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in row_values:
        parsed = _parse_row_label(row)
        if parsed is None:
            continue
        lookup_key = f"{parsed[0]}:{parsed[1]}"
        metric_map = metrics_by_row.get(lookup_key, {})
        score = 0.0
        if "semantic_gap_score" in metric_map:
            score += float(metric_map["semantic_gap_score"])
        score += float(metric_map.get("trace.progress_delta_ratio", 0.0))
        score += float(metric_map.get("summary.covered_count", 0.0))
        score -= float(metric_map.get("summary.missing_review_count", 0.0))
        candidates.append(
            {
                "rowLabel": row,
                "windowId": parsed[0],
                "ordinal": parsed[1],
                "priorityScore": round(score, 6),
            }
        )
    candidates.sort(key=lambda item: (-item["priorityScore"], item["rowLabel"]))
    return candidates[:5]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect clustering metadata from a zkperf spectrogram renderer output.")
    parser.add_argument("--input", type=Path, required=True, help="Path to renderer metadata JSON")
    parser.add_argument("--fixture", type=Path, help="Optional stream fixture JSON to compute per-cluster metric summaries")
    parser.add_argument("--query-metadata", type=Path, help="Optional query spectrogram metadata JSON for query-aware cluster selection")
    parser.add_argument("--cluster", help="Inspect only one cluster label")
    parser.add_argument("--largest-only", action="store_true", help="Inspect only the largest cluster")
    parser.add_argument("--top-metrics", type=int, default=8, help="Number of top averaged metrics to include per cluster")
    parser.add_argument("--select-top-clusters", type=int, default=1, help="How many query-ranked clusters to recommend")
    parser.add_argument("--select-top-rows", type=int, default=5, help="How many query-ranked rows to recommend")
    parser.add_argument("--selection-fixture-output", type=Path, help="Optional path to write a fixture containing only recommended rows")
    parser.add_argument("--hide-rows", action="store_true", help="Suppress full row listing in output")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit JSON instead of human-readable text")
    args = parser.parse_args(argv)

    metadata = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise SystemExit("metadata input must be a JSON object")
    fixture = None
    if args.fixture is not None:
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
        if not isinstance(fixture, dict):
            raise SystemExit("fixture input must be a JSON object")
    query_metadata = None
    if args.query_metadata is not None:
        query_metadata = json.loads(args.query_metadata.read_text(encoding="utf-8"))
        if not isinstance(query_metadata, dict):
            raise SystemExit("query metadata input must be a JSON object")

    summary = build_cluster_summary(
        metadata,
        fixture=fixture,
        query_metadata=query_metadata,
        top_metrics=args.top_metrics,
        include_rows=not args.hide_rows,
        include_all_clusters=not args.largest_only,
        cluster_filter=args.cluster,
        select_top_clusters=args.select_top_clusters,
        select_top_rows=args.select_top_rows,
    )
    if args.selection_fixture_output is not None:
        if not isinstance(fixture, dict):
            raise SystemExit("--selection-fixture-output requires --fixture")
        selection = summary.get("selection")
        if not isinstance(selection, dict):
            raise SystemExit("--selection-fixture-output requires query-aware selection data")
        recommended_rows = selection.get("recommendedRows")
        if not isinstance(recommended_rows, list) or not recommended_rows:
            raise SystemExit("--selection-fixture-output found no recommended rows to materialize")
        selected_fixture = _build_selected_fixture(fixture, recommended_rows)
        args.selection_fixture_output.parent.mkdir(parents=True, exist_ok=True)
        args.selection_fixture_output.write_text(
            json.dumps(selected_fixture, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summary["selectionFixturePath"] = str(args.selection_fixture_output.resolve())
    if args.json_output:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    print(f"stream_id: {summary['streamId']}")
    print(f"stream_revision: {summary['streamRevision']}")
    print(f"row_count: {summary['rowCount']}")
    print(f"cluster_count: {summary['clusterCount']}")
    print("cluster_counts:")
    for label, count in sorted(summary["clusterCounts"].items(), key=lambda item: _cluster_sort_key(item[0])):
        print(f"  {label}: {count}")
    print("clusters:")
    for cluster in summary["clusters"]:
        print(
            f"  cluster {cluster['label']}: count={cluster['count']} "
            f"first={cluster['firstRow']} last={cluster['lastRow']}"
        )
        top_metrics = cluster.get("topMetrics")
        if isinstance(top_metrics, dict) and top_metrics:
            print("    top_metrics:")
            for name, value in top_metrics.items():
                print(f"      {name}: {value}")
        signals = cluster.get("signals")
        if isinstance(signals, dict) and signals:
            print("    signals:")
            for key, value in signals.items():
                print(f"      {key}: {value}")
        window_counts = cluster.get("windowCounts")
        if isinstance(window_counts, dict) and window_counts:
            print("    window_counts:")
            for key, value in window_counts.items():
                print(f"      {key}: {value}")
        retrieval_candidates = cluster.get("retrievalCandidates")
        if isinstance(retrieval_candidates, list) and retrieval_candidates:
            print("    retrieval_candidates:")
            for candidate in retrieval_candidates:
                if isinstance(candidate, dict):
                    print(
                        "      - "
                        f"{candidate.get('rowLabel')} "
                        f"(window={candidate.get('windowId')}, score={candidate.get('priorityScore')})"
                    )
        rows = cluster.get("rows")
        if isinstance(rows, list):
            print("    rows:")
            for row in rows:
                print(f"      - {row}")
    selection = summary.get("selection")
    if isinstance(selection, dict):
        print("selection:")
        labels = selection.get("recommendedClusterLabels")
        if isinstance(labels, list):
            print(f"  recommended_clusters: {', '.join(str(label) for label in labels)}")
        rows = selection.get("recommendedRows")
        if isinstance(rows, list):
            print("  recommended_rows:")
            for row in rows:
                if isinstance(row, dict):
                    print(f"    - {row.get('rowLabel')}: {row.get('score')}")
    if "selectionFixturePath" in summary:
        print(f"selection_fixture: {summary['selectionFixturePath']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
