from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class Query:
    query_id: str
    text: str
    selectors: Dict[str, str] = field(default_factory=dict)
    predicate_hints: List[str] = field(default_factory=list)
    role_hints: Dict[str, str] = field(default_factory=dict)


@dataclass
class FactRecord:
    fact_id: str
    predicate: str
    arguments: Dict[str, Any]
    qualifiers: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    shard_id: Optional[str] = None


@dataclass
class TraceEvent:
    t: int
    stage: str
    op: str
    regs: Dict[str, float] = field(default_factory=dict)
    invariants: List[str] = field(default_factory=list)
    loop: Optional[str] = None
    doc_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceWindow:
    window_id: str
    shard_id: str
    events: List[TraceEvent]
    domain_hint: Optional[str] = None


@dataclass
class ShardSummary:
    shard_id: str
    facts: List[FactRecord]
    trace_windows: List[TraceWindow]
    sink_refs: Dict[str, str] = field(default_factory=dict)
    manifest_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResonanceScore:
    hash_u64: int
    o71: int
    o59: int
    o47: int
    offset_primary: int
    offset_secondary: int
    dist_primary: int
    dist_secondary: int
    resonance_strength: float
    resonance: bool


@dataclass
class FeatureVector:
    shard_id: Optional[str]
    values: Dict[str, float]
    domain_id: Optional[int] = None


@dataclass
class RetrievalResult:
    shard_id: str
    score: float
    spectral_score: float
    resonance_strength: float
    domain_match: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class AdmissibilityDecision:
    shard_id: str
    accepted: bool
    accepted_by: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)
    result: Optional[RetrievalResult] = None
