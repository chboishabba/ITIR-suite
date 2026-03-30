
from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

FeatureMap = Mapping[str, float]


# ============================================================
# Core contracts
# ============================================================

@dataclass(frozen=True)
class PhiBundle:
    """
    Structured feature split.

    grounded:
        Truth-bearing structured features derived from SL facts.
        Examples:
            pred::complaint
            role::tenant
            argval::issue::mould
            qual::jurisdiction::vic

    domain:
        Real manifold/domain features used for graph geometry and spectral reranking.
        These must come from actual shard evidence or a real query-domain projection.
        Examples:
            dom::housing_complaints
            motif::tenancy
            trace::cluster_3
            hecke::T_47

    experimental:
        Non-authoritative heuristics only. Never used for admissibility.
        Examples:
            resonance
            ann sketch
            latent prior
    """
    grounded: Dict[str, float] = field(default_factory=dict)
    domain: Dict[str, float] = field(default_factory=dict)
    experimental: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class QueryBundle:
    text: str
    phi: PhiBundle


@dataclass(frozen=True)
class ShardCandidate:
    shard_id: str
    phi: PhiBundle
    provenance_ok: bool = True
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalConfig:
    # Grounded retrieval gate
    min_grounded_overlap: int = 1
    min_grounded_similarity: float = 0.01

    # Candidate generation
    shortlist_k: int = 25

    # Spectral rerank
    graph_top_k: int = 8
    graph_sigma: float = 0.35
    ppr_alpha: float = 0.15
    ppr_steps: int = 30
    spectral_weight: float = 0.30

    # Optional experimental tiebreak (never part of core score)
    resonance_tiebreak_weight: float = 0.02

    # Numerical stability
    eps: float = 1e-12


@dataclass(frozen=True)
class RetrievalScore:
    shard_id: str
    admissible: bool
    grounded_similarity: float
    grounded_overlap: int
    spectral_score: float
    resonance_score: float
    total_score: float
    reasons: Tuple[str, ...]
    metadata: Mapping[str, object] = field(default_factory=dict)


# ============================================================
# Sparse helpers
# ============================================================

def _dot(a: FeatureMap, b: FeatureMap) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(v * b.get(k, 0.0) for k, v in a.items())


def _norm(a: FeatureMap) -> float:
    return sqrt(sum(v * v for v in a.values()))


def cosine_similarity(a: FeatureMap, b: FeatureMap, eps: float = 1e-12) -> float:
    na = _norm(a)
    nb = _norm(b)
    if na <= eps or nb <= eps:
        return 0.0
    return _dot(a, b) / max(na * nb, eps)


def overlap_count(a: FeatureMap, b: FeatureMap) -> int:
    if len(a) > len(b):
        a, b = b, a
    return sum(1 for k in a if k in b)


# ============================================================
# Governance
# ============================================================

def admissible_grounded(
    query: QueryBundle,
    shard: ShardCandidate,
    cfg: RetrievalConfig,
) -> Tuple[bool, float, int, List[str]]:
    sim = cosine_similarity(query.phi.grounded, shard.phi.grounded, cfg.eps)
    ov = overlap_count(query.phi.grounded, shard.phi.grounded)

    reasons: List[str] = []

    if not shard.provenance_ok:
        reasons.append("rejected:no_provenance")
        return False, sim, ov, reasons

    if ov < cfg.min_grounded_overlap:
        reasons.append(f"rejected:overlap<{cfg.min_grounded_overlap}")
        return False, sim, ov, reasons

    if sim < cfg.min_grounded_similarity:
        reasons.append(f"rejected:similarity<{cfg.min_grounded_similarity}")
        return False, sim, ov, reasons

    reasons.append("accepted:grounded")
    return True, sim, ov, reasons


# ============================================================
# Spectral manifold reranking
# ============================================================

@dataclass
class _Node:
    shard: ShardCandidate
    grounded_similarity: float
    grounded_overlap: int


def _rbf_affinity(a: FeatureMap, b: FeatureMap, sigma: float, eps: float) -> float:
    """
    Use cosine distance on real domain vectors.
    If either side has no domain vector, affinity is zero.
    """
    sim = cosine_similarity(a, b, eps)
    if sim <= eps:
        return 0.0
    # Convert cosine similarity in [0,1-ish] to distance-like quantity.
    dist = max(0.0, 1.0 - sim)
    return pow(2.718281828459045, -(dist * dist) / max(2.0 * sigma * sigma, eps))


def _build_knn_graph(nodes: Sequence[_Node], cfg: RetrievalConfig) -> List[List[Tuple[int, float]]]:
    n = len(nodes)
    graph: List[List[Tuple[int, float]]] = [[] for _ in range(n)]
    if n == 0:
        return graph

    for i in range(n):
        scored: List[Tuple[int, float]] = []
        a = nodes[i].shard.phi.domain
        if not a:
            continue
        for j in range(n):
            if i == j:
                continue
            b = nodes[j].shard.phi.domain
            if not b:
                continue
            w = _rbf_affinity(a, b, cfg.graph_sigma, cfg.eps)
            if w > 0.0:
                scored.append((j, w))
        scored.sort(key=lambda x: x[1], reverse=True)
        graph[i] = scored[: cfg.graph_top_k]
    return graph


def _row_normalize(graph: Sequence[Sequence[Tuple[int, float]]], eps: float) -> List[List[Tuple[int, float]]]:
    out: List[List[Tuple[int, float]]] = []
    for nbrs in graph:
        z = sum(w for _, w in nbrs)
        if z <= eps:
            out.append([])
        else:
            out.append([(j, w / z) for j, w in nbrs])
    return out


def _seed_vector(query: QueryBundle, nodes: Sequence[_Node], cfg: RetrievalConfig) -> List[float]:
    """
    Seed personalized PageRank using query<->domain similarity * grounded score.
    This keeps spectral propagation anchored in grounded retrieval.
    """
    seeds: List[float] = []
    for node in nodes:
        domain_sim = cosine_similarity(query.phi.domain, node.shard.phi.domain, cfg.eps)
        seed = max(0.0, node.grounded_similarity) * max(0.0, domain_sim)
        seeds.append(seed)

    z = sum(seeds)
    if z <= cfg.eps:
        # Fall back to grounded-only seed if domain is unknown/empty.
        seeds = [max(0.0, node.grounded_similarity) for node in nodes]
        z = sum(seeds)

    if z <= cfg.eps:
        return [0.0 for _ in nodes]

    return [s / z for s in seeds]


def _personalized_pagerank(
    graph: Sequence[Sequence[Tuple[int, float]]],
    seed: Sequence[float],
    cfg: RetrievalConfig,
) -> List[float]:
    """
    Standard PPR on a row-normalized KNN graph.

    r_{t+1} = alpha * seed + (1-alpha) * P^T r_t
    """
    n = len(graph)
    if n == 0:
        return []

    g = _row_normalize(graph, cfg.eps)
    r = list(seed)

    for _ in range(cfg.ppr_steps):
        new_r = [cfg.ppr_alpha * s for s in seed]
        for i, nbrs in enumerate(g):
            if not nbrs:
                continue
            mass = (1.0 - cfg.ppr_alpha) * r[i]
            for j, w in nbrs:
                new_r[j] += mass * w
        r = new_r

    return r


def _resonance_tiebreak(query: QueryBundle, shard: ShardCandidate) -> float:
    q = query.phi.experimental.get("resonance")
    s = shard.phi.experimental.get("resonance")
    if q is None or s is None:
        return 0.0
    qf = float(q)
    sf = float(s)
    return max(0.0, 1.0 - abs(qf - sf))


# ============================================================
# Public API
# ============================================================

def score_candidates(
    query: QueryBundle,
    shards: Sequence[ShardCandidate],
    cfg: Optional[RetrievalConfig] = None,
) -> List[RetrievalScore]:
    cfg = cfg or RetrievalConfig()

    # 1. Grounded gate first.
    prelim: List[_Node] = []
    rejected: List[RetrievalScore] = []

    for shard in shards:
        ok, sim, ov, reasons = admissible_grounded(query, shard, cfg)
        if ok:
            prelim.append(_Node(shard=shard, grounded_similarity=sim, grounded_overlap=ov))
        else:
            rejected.append(
                RetrievalScore(
                    shard_id=shard.shard_id,
                    admissible=False,
                    grounded_similarity=sim,
                    grounded_overlap=ov,
                    spectral_score=0.0,
                    resonance_score=0.0,
                    total_score=float("-inf"),
                    reasons=tuple(reasons),
                    metadata=shard.metadata,
                )
            )

    prelim.sort(key=lambda n: (n.grounded_similarity, n.grounded_overlap), reverse=True)
    shortlist = prelim[: cfg.shortlist_k]

    if not shortlist:
        return rejected

    # 2. Build real domain graph over shortlist only.
    graph = _build_knn_graph(shortlist, cfg)
    seed = _seed_vector(query, shortlist, cfg)
    spectral = _personalized_pagerank(graph, seed, cfg)

    # 3. Final rerank = grounded primary + spectral secondary.
    #    Resonance is tiebreak-only and never part of the core score.
    out: List[RetrievalScore] = []
    for idx, node in enumerate(shortlist):
        resonance = cfg.resonance_tiebreak_weight * _resonance_tiebreak(query, node.shard)
        spectral_score = cfg.spectral_weight * spectral[idx]
        total = node.grounded_similarity + spectral_score

        reasons = ["accepted:grounded"]
        if node.shard.phi.domain and query.phi.domain:
            reasons.append("domain:spectral")
        else:
            reasons.append("domain:unknown")
        if resonance > 0.0:
            reasons.append("resonance:tiebreak")

        out.append(
            RetrievalScore(
                shard_id=node.shard.shard_id,
                admissible=True,
                grounded_similarity=node.grounded_similarity,
                grounded_overlap=node.grounded_overlap,
                spectral_score=spectral_score,
                resonance_score=resonance,
                total_score=total,
                reasons=tuple(reasons),
                metadata=node.shard.metadata,
            )
        )

    out.sort(
        key=lambda s: (
            s.total_score,
            s.grounded_similarity,
            s.grounded_overlap,
            s.spectral_score,
            s.resonance_score,
        ),
        reverse=True,
    )

    return out + rejected


def top_k(
    query: QueryBundle,
    shards: Sequence[ShardCandidate],
    k: int = 10,
    cfg: Optional[RetrievalConfig] = None,
) -> List[RetrievalScore]:
    ranked = score_candidates(query, shards, cfg=cfg)
    admissible = [r for r in ranked if r.admissible]
    return admissible[:k]
