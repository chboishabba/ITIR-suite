from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from dataclasses import dataclass
from typing import Dict, Hashable, List, Optional, Sequence

from .feature_map import build_phi, query_phi
from .monster_lattice import resonance_score_from_hash, hash_file_bytes
from .trace_features import infer_domain_clusters
from .types import AdmissibilityDecision, Query, RetrievalResult, ShardSummary


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    na = sqrt(sum(v * v for v in a.values()))
    nb = sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _shard_domains(
    summaries: Sequence[ShardSummary],
    *,
    k_domains: int,
) -> Dict[str, Hashable]:
    explicit_domains: Dict[str, Hashable] = {}
    windows_for_clustering = []
    for summary in summaries:
        hints = [w.domain_hint for w in summary.trace_windows if w.domain_hint]
        if hints:
            explicit_domains[summary.shard_id] = Counter(hints).most_common(1)[0][0]
        else:
            windows_for_clustering.extend(summary.trace_windows)

    clustered_windows = infer_domain_clusters(windows_for_clustering, k=k_domains) if windows_for_clustering else {}
    shard_domains = dict(explicit_domains)
    for summary in summaries:
        if summary.shard_id in shard_domains:
            continue
        labels = [clustered_windows[w.window_id] for w in summary.trace_windows if w.window_id in clustered_windows]
        if labels:
            shard_domains[summary.shard_id] = Counter(labels).most_common(1)[0][0]
    return shard_domains


def _domain_centroids(
    shard_domains: Dict[str, Hashable],
    shard_vectors: Dict[str, Dict[str, float]],
) -> Dict[Hashable, Dict[str, float]]:
    accum: Dict[Hashable, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    counts: Counter[Hashable] = Counter()
    for shard_id, domain in shard_domains.items():
        counts[domain] += 1
        for key, value in shard_vectors[shard_id].items():
            accum[domain][key] += value
    return {
        domain: {key: value / counts[domain] for key, value in values.items()}
        for domain, values in accum.items()
        if counts[domain]
    }


def _query_domain(
    q_vec: Dict[str, float],
    centroids: Dict[Hashable, Dict[str, float]],
) -> Optional[Hashable]:
    if not centroids:
        return None
    best_domain = None
    best_score = -1.0
    for domain, centroid in centroids.items():
        score = _cosine(q_vec, centroid)
        if score > best_score:
            best_score = score
            best_domain = domain
    return best_domain


def manifold_aware_rank(
    query: Query,
    summaries: Sequence[ShardSummary],
    k_domains: int = 5,
    top_k: Optional[int] = None,
) -> List[RetrievalResult]:
    q_vec = query_phi(query)
    shard_vectors = {summary.shard_id: build_phi(summary).values for summary in summaries}
    shard_domain = _shard_domains(summaries, k_domains=k_domains)
    q_domain = _query_domain(q_vec.values, _domain_centroids(shard_domain, shard_vectors))

    results: List[RetrievalResult] = []
    for s in summaries:
        s_vec = shard_vectors[s.shard_id]
        shard_domain_id = shard_domain.get(s.shard_id)
        if q_domain is None or shard_domain_id is None:
            domain_match = 0.0
        elif shard_domain_id == q_domain:
            domain_match = 1.0
        else:
            domain_match = 0.0

        summary_bytes = ("|".join(sorted(f.fact_id for f in s.facts)) + "|" + s.shard_id).encode("utf-8")
        res = resonance_score_from_hash(hash_file_bytes(summary_bytes))
        spectral_score = _cosine(q_vec.values, s_vec)
        score = 0.65 * spectral_score + 0.15 * domain_match

        reasons = []
        if res.resonance:
            reasons.append("resonance_tiebreak")
        if spectral_score > 0.25:
            reasons.append("spectral_alignment")
        if domain_match == 1.0:
            reasons.append("domain_match")

        results.append(
            RetrievalResult(
                shard_id=s.shard_id,
                score=score,
                spectral_score=spectral_score,
                resonance_strength=res.resonance_strength,
                domain_match=domain_match,
                reasons=reasons,
            )
        )

    results.sort(key=lambda r: (r.score, r.resonance_strength), reverse=True)
    return results[:top_k] if top_k is not None else results


@dataclass
class AdmissibilityPolicy:
    min_score: float = 0.1
    min_spectral_for_non_domain: float = 0.01
    require_structured_alignment: bool = True
    reject_resonance_only: bool = True


def admissibility_filter(
    ranked: Sequence[RetrievalResult],
    policy: Optional[AdmissibilityPolicy] = None,
) -> List[AdmissibilityDecision]:
    active_policy = policy or AdmissibilityPolicy()
    decisions: List[AdmissibilityDecision] = []
    for result in ranked:
        accepted_by: List[str] = []
        blocked_by: List[str] = []

        if result.score >= active_policy.min_score:
            accepted_by.append("score_gate")
        else:
            blocked_by.append("score_below_min")

        structured_alignment = (
            result.domain_match == 1.0
            or result.spectral_score >= active_policy.min_spectral_for_non_domain
        )
        if active_policy.require_structured_alignment:
            if structured_alignment:
                accepted_by.append("structured_alignment")
            else:
                blocked_by.append("no_structured_alignment")

        resonance_only = (
            result.resonance_strength > 0.0
            and result.domain_match == 0.0
            and result.spectral_score < active_policy.min_spectral_for_non_domain
        )
        if active_policy.reject_resonance_only and resonance_only:
            blocked_by.append("resonance_only_signal")

        decisions.append(
            AdmissibilityDecision(
                shard_id=result.shard_id,
                accepted=not blocked_by,
                accepted_by=accepted_by,
                blocked_by=blocked_by,
                result=result,
            )
        )
    return decisions


def manifold_aware_select(
    query: Query,
    summaries: Sequence[ShardSummary],
    *,
    k_domains: int = 5,
    top_k: Optional[int] = None,
    policy: Optional[AdmissibilityPolicy] = None,
) -> List[AdmissibilityDecision]:
    ranked = manifold_aware_rank(query, summaries, k_domains=k_domains, top_k=top_k)
    return admissibility_filter(ranked, policy=policy)
