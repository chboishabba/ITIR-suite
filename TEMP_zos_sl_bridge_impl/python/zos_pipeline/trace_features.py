from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from typing import Dict, Iterable, List, Tuple

from .types import FeatureVector, TraceEvent, TraceWindow


def build_trace_window(window_id: str, shard_id: str, events: List[TraceEvent], domain_hint: str | None = None) -> TraceWindow:
    return TraceWindow(window_id=window_id, shard_id=shard_id, events=events, domain_hint=domain_hint)


def trace_window_vector(window: TraceWindow) -> Dict[str, float]:
    event_count = max(1, len(window.events))
    stage_counts = Counter(e.stage for e in window.events)
    op_counts = Counter(e.op for e in window.events)
    inv_counts = Counter(inv for e in window.events for inv in e.invariants)
    loop_counts = Counter(e.loop for e in window.events if e.loop is not None)

    reg_sums: Dict[str, float] = defaultdict(float)
    reg_sq_sums: Dict[str, float] = defaultdict(float)
    for event in window.events:
        for k, v in event.regs.items():
            reg_sums[k] += float(v)
            reg_sq_sums[k] += float(v) * float(v)

    vec: Dict[str, float] = {
        "event_count": float(event_count),
        "stage_cardinality": float(len(stage_counts)),
        "op_cardinality": float(len(op_counts)),
        "inv_cardinality": float(len(inv_counts)),
        "loop_cardinality": float(len(loop_counts)),
    }

    for stage, c in stage_counts.items():
        vec[f"stage::{stage}"] = c / event_count
    for op, c in op_counts.items():
        vec[f"op::{op}"] = c / event_count
    for inv, c in inv_counts.items():
        vec[f"inv::{inv}"] = c / event_count
    for loop, c in loop_counts.items():
        vec[f"loop::{loop}"] = c / event_count

    for reg, total in reg_sums.items():
        mean = total / event_count
        var = max(0.0, reg_sq_sums[reg] / event_count - mean * mean)
        vec[f"reg_mean::{reg}"] = mean
        vec[f"reg_std::{reg}"] = sqrt(var)

    return vec


def aggregate_shard_vector(windows: Iterable[TraceWindow]) -> Dict[str, float]:
    agg: Dict[str, float] = defaultdict(float)
    n = 0
    for w in windows:
        n += 1
        vec = trace_window_vector(w)
        for k, v in vec.items():
            agg[k] += v
    if n == 0:
        return {}
    return {k: v / n for k, v in agg.items()}


def _vector_to_dense(vectors: List[Dict[str, float]]) -> Tuple[List[str], List[List[float]]]:
    keys = sorted({k for vec in vectors for k in vec.keys()})
    dense = [[vec.get(k, 0.0) for k in keys] for vec in vectors]
    return keys, dense


def _kmeans(dense: List[List[float]], k: int = 5, steps: int = 20) -> List[int]:
    if not dense:
        return []
    k = max(1, min(k, len(dense)))
    centers = [row[:] for row in dense[:k]]
    labels = [0] * len(dense)

    def dist2(a: List[float], b: List[float]) -> float:
        return sum((x - y) ** 2 for x, y in zip(a, b))

    for _ in range(steps):
        for i, row in enumerate(dense):
            labels[i] = min(range(k), key=lambda c: dist2(row, centers[c]))
        new_centers = [[0.0] * len(dense[0]) for _ in range(k)]
        counts = [0] * k
        for label, row in zip(labels, dense):
            counts[label] += 1
            for j, v in enumerate(row):
                new_centers[label][j] += v
        for c in range(k):
            if counts[c]:
                centers[c] = [v / counts[c] for v in new_centers[c]]
    return labels


def infer_domain_clusters(windows: List[TraceWindow], k: int = 5) -> Dict[str, int]:
    vectors = [trace_window_vector(w) for w in windows]
    _, dense = _vector_to_dense(vectors)
    labels = _kmeans(dense, k=k)
    return {w.window_id: label for w, label in zip(windows, labels)}
