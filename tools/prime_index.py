
"""
prime_index.py

Runnable SL -> prime-index prototype with:

- shared grounded/domain/experimental feature namespaces
- real 15-bit Hecke/domain signature plumbing
- learned/derived signature matrix support
- Δ-cone admissibility on deltas (not absolute states)
- MDL upper-bound pruning
- logical shard selector + sink fetch scaffolding
- Zelph export helpers
- tiny fixture + self-tests

Usage:
    python prime_index.py

This file is intentionally self-contained and dependency-light.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import hashlib
import json
import math
import sys


# ---------------------------------------------------------------------
# Prime basis / ontology surface
# ---------------------------------------------------------------------

PRIMES: List[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71]

# Minimal feature-family -> prime assignment.
# This is deliberately explicit and versionable.
PRIME_FAMILY: Dict[str, int] = {
    "fact_token::": 2,
    "pred::": 3,
    "role::": 5,
    "argval::": 7,
    "qual::": 11,
    "ent::": 13,
    "domain::": 17,
    "trace::": 19,
    "motif::": 23,
}

_PARSE_WITH_SPACY = None
_PARSE_WITH_SPACY_INITIALIZED = False


# ---------------------------------------------------------------------
# Core datatypes
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class PhiBundle:
    grounded: Dict[str, float]
    domain: Dict[str, float]
    experimental: Dict[str, float]


@dataclass
class PrimeEmbedding:
    version: str
    exact_addr: Dict[int, int]
    sketch_addr: str
    reverse_addr: Dict[int, int]
    mdl_upper_bound: float
    mass: float


@dataclass
class SinkRef:
    sink_type: str   # hf | ipfs | file
    ref: str


@dataclass
class PrimeIndexShard:
    shard_id: str
    artifact_revision: str
    selector_terms: List[str]
    fact_ids: List[str]
    phi: PhiBundle
    embedding: PrimeEmbedding
    hecke_sig: int                  # 15-bit int
    provenance_ids: List[str]
    promotion_receipts: List[str]
    sink_refs: List[SinkRef] = field(default_factory=list)
    parse_tree: Dict[str, Any] | None = None

    def has_valid_receipts(self) -> bool:
        return len(self.promotion_receipts) > 0


@dataclass
class QueryProjection:
    raw_query: str
    phi: PhiBundle
    embedding: PrimeEmbedding
    hecke_sig: int


@dataclass
class RetrievalConfig:
    min_grounded_overlap: float = 1.0
    min_domain_overlap: int = 0
    min_required_gain: float = 0.0
    max_candidates_after_selector: int = 64
    max_fetch: int = 8
    cone_eps: float = 0.0


# ---------------------------------------------------------------------
# Shared feature construction
# ---------------------------------------------------------------------

def _norm_text(x: Any) -> str:
    return str(x).strip().lower()


def infer_fact_source_text(fact: Mapping[str, Any]) -> str:
    direct = (
        str(fact.get("fact_text") or "").strip()
        or next((str(item).strip() for item in fact.get("statement_texts", []) if str(item).strip()), "")
        or str(fact.get("canonical_label") or "").strip()
    )
    if direct:
        return direct

    parts: List[str] = []
    predicate = str(fact.get("predicate") or "").strip()
    if predicate:
        parts.append(predicate)

    arguments = fact.get("arguments")
    if isinstance(arguments, Mapping):
        parts.extend(str(value).strip() for value in arguments.values() if str(value).strip())

    qualifiers = fact.get("qualifiers")
    if isinstance(qualifiers, Mapping):
        parts.extend(str(value).strip() for value in qualifiers.values() if str(value).strip())

    return " ".join(parts).strip()


def _get_parse_with_spacy():
    global _PARSE_WITH_SPACY, _PARSE_WITH_SPACY_INITIALIZED
    if _PARSE_WITH_SPACY_INITIALIZED:
        return _PARSE_WITH_SPACY

    candidates = [
        "SensibLaw.src.nlp.spacy_adapter",
        "src.nlp.spacy_adapter",
    ]
    sensiblaw_root = Path(__file__).resolve().parents[1] / "SensibLaw"
    if sensiblaw_root.exists() and str(sensiblaw_root) not in sys.path:
        sys.path.insert(0, str(sensiblaw_root))

    for module_name in candidates:
        try:
            module = __import__(module_name, fromlist=["parse"])
            _PARSE_WITH_SPACY = module.parse
            _PARSE_WITH_SPACY_INITIALIZED = True
            return _PARSE_WITH_SPACY
        except ModuleNotFoundError:
            continue

    _PARSE_WITH_SPACY_INITIALIZED = True
    _PARSE_WITH_SPACY = None
    return None


def build_parse_tree(text: str) -> Dict[str, Any]:
    parse_with_spacy = _get_parse_with_spacy()
    if parse_with_spacy is None:
        raise RuntimeError("spaCy parse surface is unavailable; SensibLaw parser import failed")
    return parse_with_spacy(text)


def _extend_phi_with_parse_tree(phi: PhiBundle, parse_tree: Mapping[str, Any]) -> PhiBundle:
    experimental = dict(phi.experimental)
    for sentence in parse_tree.get("sents", []):
        for token in sentence.get("tokens", []):
            lemma = _norm_text(token.get("lemma") or token.get("text") or "")
            pos = _norm_text(token.get("pos") or "")
            dep = _norm_text(token.get("dep") or "")
            head = _norm_text(token.get("head_text") or "")
            if lemma:
                experimental[f"trace::lemma::{lemma}"] = experimental.get(f"trace::lemma::{lemma}", 0.0) + 1.0
            if pos:
                experimental[f"trace::pos::{pos}"] = experimental.get(f"trace::pos::{pos}", 0.0) + 1.0
            if dep:
                experimental[f"trace::dep::{dep}"] = experimental.get(f"trace::dep::{dep}", 0.0) + 1.0
            if dep and head and lemma:
                experimental[f"trace::edge::{dep}::{head}->{lemma}"] = 1.0
    return PhiBundle(
        grounded=dict(phi.grounded),
        domain=dict(phi.domain),
        experimental=experimental,
    )


def load_fact_payload(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        if "\n" not in text:
            raise
        facts = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            facts.append(json.loads(line))
        return facts

    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "facts" in payload:
        facts = payload["facts"]
        if isinstance(facts, list):
            return facts
    raise ValueError("input must be a list, an object with 'facts', or JSONL")


def load_export_payload(path: Path) -> Any:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return rows


def normalize_export_facts(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(row) for row in payload]

    if isinstance(payload, dict):
        if isinstance(payload.get("facts"), list):
            facts = payload["facts"]
            if facts and "predicate" in facts[0]:
                return [dict(row) for row in facts]
            return [_workbench_fact_to_export_fact(row) for row in facts]
        if isinstance(payload.get("fact_candidates"), list):
            return [_fact_candidate_to_export_fact(row) for row in payload["fact_candidates"]]

    raise ValueError("unsupported payload for export normalization")


def load_export_facts(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        payload = json.loads(text)
        return normalize_export_facts(payload)
    except json.JSONDecodeError:
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
        return normalize_export_facts(rows)


def build_zelph_bundle_from_payload(payload: Any, *, artifact_revision: str = "rev-export") -> Dict[str, Any]:
    facts = normalize_export_facts(payload)
    shards = facts_to_shards(facts, artifact_revision=artifact_revision)
    return build_zelph_input(facts, shards)


def _workbench_fact_to_export_fact(row: Mapping[str, Any]) -> Dict[str, Any]:
    observations = row.get("observations") if isinstance(row.get("observations"), list) else []
    primary_observation = observations[0] if observations else {}
    statement_texts = [str(item) for item in row.get("statement_texts", []) if str(item).strip()]
    fact_text = str(row.get("fact_text") or "").strip()
    source_text = statement_texts[0] if statement_texts else fact_text

    arguments: Dict[str, Any] = {}
    if isinstance(primary_observation, Mapping):
        subject_text = str(primary_observation.get("subject_text") or "").strip()
        object_text = str(primary_observation.get("object_text") or "").strip()
        if subject_text:
            arguments["subject"] = subject_text
        if object_text:
            arguments["object"] = object_text
    if not arguments and source_text:
        arguments["text"] = source_text

    qualifiers: Dict[str, Any] = {}
    if row.get("candidate_status") is not None:
        qualifiers["candidate_status"] = row.get("candidate_status")
    if row.get("source_types"):
        qualifiers["source_types"] = list(row.get("source_types", []))

    return {
        "fact_id": row.get("fact_id"),
        "predicate": str(primary_observation.get("predicate_key") or row.get("fact_type") or "statement_capture"),
        "arguments": arguments,
        "qualifiers": qualifiers,
        "confidence": 1.0,
        "provenance": [{"doc_id": source_id, "start": 0, "end": len(source_text)} for source_id in row.get("source_ids", [])] or [{"doc_id": str(row.get("fact_id")), "start": 0, "end": len(source_text)}],
        "promotion_receipt": row.get("promotion_receipt") or row.get("fact_id"),
        "reconstructible": True,
        "fact_text": source_text,
        "statement_texts": statement_texts,
    }


def _fact_candidate_to_export_fact(row: Mapping[str, Any]) -> Dict[str, Any]:
    fact_text = str(row.get("fact_text") or row.get("canonical_label") or "").strip()
    return {
        "fact_id": row.get("fact_id"),
        "predicate": str(row.get("fact_type") or "statement_capture"),
        "arguments": {"text": fact_text} if fact_text else {},
        "qualifiers": {"candidate_status": row.get("candidate_status")} if row.get("candidate_status") is not None else {},
        "confidence": 1.0,
        "provenance": [{"doc_id": str(row.get("fact_id")), "start": 0, "end": len(fact_text)}],
        "promotion_receipt": row.get("promotion_receipt") or row.get("fact_id"),
        "reconstructible": True,
        "fact_text": fact_text,
        "statement_texts": [fact_text] if fact_text else [],
    }


def phi_from_sl_fact(fact: Mapping[str, Any]) -> PhiBundle:
    """
    Minimal SL fact -> Φ projection.

    Keeps the contract explicit:
      grounded = truth-bearing structured features
      domain = real manifold/domain inference inputs
      experimental = proposal-only hints
    """
    grounded: Dict[str, float] = {}
    domain: Dict[str, float] = {}
    experimental: Dict[str, float] = {}

    pred = _norm_text(fact["predicate"])
    grounded[f"pred::{pred}"] = 1.0

    arguments = fact.get("arguments", {}) or {}
    for role, value in arguments.items():
        role_k = _norm_text(role)
        value_k = _norm_text(value)

        grounded[f"role::{role_k}"] = grounded.get(f"role::{role_k}", 0.0) + 1.0
        grounded[f"argval::{role_k}::{value_k}"] = 1.0
        grounded[f"ent::{value_k}"] = 1.0

        for tok in value_k.split():
            grounded[f"fact_token::{tok}"] = grounded.get(f"fact_token::{tok}", 0.0) + 1.0

    qualifiers = fact.get("qualifiers", {}) or {}
    for k, v in qualifiers.items():
        grounded[f"qual::{_norm_text(k)}::{_norm_text(v)}"] = 1.0

    # Real bounded domain inference from grounded features.
    # Replace/extend as the SL ontology stabilizes.
    if any(k.startswith("pred::applies") or "lease" in k for k in grounded):
        domain["domain::tenancy_contracts"] = 1.0
    if any("pet_policy" in k or "pet" in k for k in grounded):
        domain["domain::housing_pets"] = 1.0
    if any("bond_payment" in k or "bond" in k for k in grounded):
        domain["domain::tenancy_bonds"] = 1.0

    # Proposal-only / experimental lane
    # This is intentionally low-authority and can be empty.
    if pred:
        experimental[f"trace::pred_family::{pred[:12]}"] = 1.0

    return PhiBundle(grounded=grounded, domain=domain, experimental=experimental)


def phi_from_query(query: str) -> PhiBundle:
    grounded: Dict[str, float] = {}
    domain: Dict[str, float] = {}
    experimental: Dict[str, float] = {}

    q = _norm_text(query)
    for tok in q.split():
        grounded[f"fact_token::{tok}"] = grounded.get(f"fact_token::{tok}", 0.0) + 1.0

    # Same bounded domain inference surface for query
    if "lease" in q or "contract" in q:
        domain["domain::tenancy_contracts"] = 1.0
    if "pet" in q:
        domain["domain::housing_pets"] = 1.0
    if "bond" in q:
        domain["domain::tenancy_bonds"] = 1.0

    return PhiBundle(grounded=grounded, domain=domain, experimental=experimental)


# ---------------------------------------------------------------------
# Prime embedding / MDL upper-bound
# ---------------------------------------------------------------------

def sketch_addr(exact_addr: Mapping[int, int]) -> str:
    payload = json.dumps({str(k): exact_addr[k] for k in sorted(exact_addr)}, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def gain_upper_bound(delta: Mapping[int, int], beta: Optional[Sequence[float]] = None) -> float:
    """
    Safe MDL-ish upper bound from exponent deltas.
    Larger |delta| on larger primes implies potentially larger gain/cost movement.
    """
    if beta is None:
        beta = [1.0] * len(PRIMES)

    ub = 0.0
    for i, p in enumerate(PRIMES):
        ub += abs(delta.get(p, 0)) * math.log(p) * float(beta[i])
    return ub


def to_prime_vec(phi: PhiBundle) -> Dict[int, int]:
    vec = {p: 0 for p in PRIMES}

    for prefix, prime in PRIME_FAMILY.items():
        for k, v in phi.grounded.items():
            if k.startswith(prefix):
                vec[prime] += int(round(v))
        for k, v in phi.domain.items():
            if k.startswith(prefix):
                vec[prime] += int(round(v))
        for k, v in phi.experimental.items():
            if k.startswith(prefix):
                vec[prime] += int(round(v))

    return vec


def make_embedding(phi: PhiBundle, version: str = "prime-v2") -> PrimeEmbedding:
    exact = to_prime_vec(phi)
    reverse = {p: exact[p] for p in reversed(PRIMES)}
    ub = gain_upper_bound(exact)
    mass = sum(abs(exact[p]) * math.log(p) for p in PRIMES)
    return PrimeEmbedding(
        version=version,
        exact_addr=exact,
        sketch_addr=sketch_addr(exact),
        reverse_addr=reverse,
        mdl_upper_bound=ub,
        mass=mass,
    )


# ---------------------------------------------------------------------
# Hecke/domain signature (15-bit real)
# ---------------------------------------------------------------------

def infer_hecke_signature(phi: PhiBundle) -> int:
    """
    Produce a real 15-bit signature from grounded/domain features.

    This is a bounded implementation: one bit per prime axis, based on whether
    the corresponding feature-family contributes nonzero mass.
    """
    vec = to_prime_vec(phi)
    sig = 0
    for i, p in enumerate(PRIMES):
        if vec[p] != 0:
            sig |= (1 << i)
    return sig


def bit_overlap(sig_a: int, sig_b: int) -> int:
    return int((sig_a & sig_b).bit_count())


# ---------------------------------------------------------------------
# Signature matrix / Δ-cone
# ---------------------------------------------------------------------

def delta_vec(qv: Mapping[int, int], sv: Mapping[int, int]) -> Dict[int, int]:
    return {p: int(sv.get(p, 0)) - int(qv.get(p, 0)) for p in PRIMES}


def default_signature_matrix() -> List[List[float]]:
    """
    Fallback (3,1)-style reduced Lorentzian toy on the first 4 axes:
    [+,+,+,-] in a diagonal basis, zeros elsewhere.
    """
    n = len(PRIMES)
    M = [[0.0 for _ in range(n)] for _ in range(n)]
    diag = [1.0, 1.0, 1.0, -1.0] + [0.0] * (n - 4)
    for i in range(n):
        M[i][i] = diag[i]
    return M


def signature_matrix_from_delta_stats(
    deltas: Sequence[Mapping[int, int]],
    time_prime: int = 7,
    space_primes: Sequence[int] = (2, 3, 5),
    regularizer: float = 1e-6,
) -> List[List[float]]:
    """
    Bounded learned/derived signature matrix.

    We derive a diagonal signature from observed delta variances:
      - designated 'space' axes get positive weights
      - designated 'time' axis gets negative weight
      - remaining axes get small negative damped weights

    This is honest: it is not a proof of unique Lorentz signature.
    It is a data-derived retrieval metric surface compatible with your
    Δ-cone screening direction.
    """
    n = len(PRIMES)
    stats = {p: [] for p in PRIMES}
    for d in deltas:
        for p in PRIMES:
            stats[p].append(float(d.get(p, 0)))

    variances = {}
    for p in PRIMES:
        xs = stats[p]
        if not xs:
            variances[p] = regularizer
            continue
        mean = sum(xs) / len(xs)
        variances[p] = sum((x - mean) ** 2 for x in xs) / max(len(xs), 1) + regularizer

    M = [[0.0 for _ in range(n)] for _ in range(n)]

    for i, p in enumerate(PRIMES):
        if p in space_primes:
            M[i][i] = 1.0 / variances[p]
        elif p == time_prime:
            M[i][i] = -1.0 / variances[p]
        else:
            M[i][i] = -0.25 / variances[p]

    return M


def signature_matrix_from_delta_analyzer_output(payload: Mapping[str, Any]) -> List[List[float]]:
    """
    Accept explicit matrix if your Δ-analyzer already emits one.
    Otherwise accept a diagonal signature by prime string.

    Supported payloads:
      {"matrix": [[...], ...]}
      {"diag_by_prime": {"2": 1.0, "3": 1.0, "5": 1.0, "7": -1.0, ...}}
    """
    if "matrix" in payload:
        matrix = payload["matrix"]
        if not isinstance(matrix, list):
            raise ValueError("matrix must be a list of lists")
        return matrix

    if "diag_by_prime" in payload:
        diag_by_prime = payload["diag_by_prime"]
        n = len(PRIMES)
        M = [[0.0 for _ in range(n)] for _ in range(n)]
        for i, p in enumerate(PRIMES):
            M[i][i] = float(diag_by_prime.get(str(p), 0.0))
        return M

    raise ValueError("Unsupported Δ-analyzer payload; expected matrix or diag_by_prime")


def qform(delta: Mapping[int, int], matrix: Sequence[Sequence[float]]) -> float:
    xs = [float(delta.get(p, 0)) for p in PRIMES]
    total = 0.0
    for i in range(len(PRIMES)):
        for j in range(len(PRIMES)):
            total += xs[i] * float(matrix[i][j]) * xs[j]
    return total


# ---------------------------------------------------------------------
# Overlap / proposal-only resonance
# ---------------------------------------------------------------------

def overlap(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    return sum(min(float(a.get(k, 0.0)), float(b.get(k, 0.0))) for k in a.keys())


def resonance_score(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    """
    Proposal-only signal. Never authoritative.
    """
    keys = set(a) | set(b)
    if not keys:
        return 0.0
    dot = sum(float(a.get(k, 0.0)) * float(b.get(k, 0.0)) for k in keys)
    na = math.sqrt(sum(float(a.get(k, 0.0)) ** 2 for k in keys))
    nb = math.sqrt(sum(float(b.get(k, 0.0)) ** 2 for k in keys))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


# ---------------------------------------------------------------------
# Logical shard selector / sink fetch
# ---------------------------------------------------------------------

class LogicalShardSelector:
    """
    Deterministic selector routing:
      query -> candidate shard ids
    """
    def __init__(self, shards: Sequence[PrimeIndexShard]) -> None:
        self.shards = list(shards)

    def resolve(self, query: str, artifact_revision: Optional[str] = None) -> List[PrimeIndexShard]:
        q = _norm_text(query)
        q_terms = set(q.split())

        out: List[PrimeIndexShard] = []
        for shard in self.shards:
            if artifact_revision is not None and shard.artifact_revision != artifact_revision:
                continue

            selector_hit = False
            for term in shard.selector_terms:
                if term in q_terms:
                    selector_hit = True
                    break

            if selector_hit:
                out.append(shard)

        return out


def choose_sink(shard: PrimeIndexShard, preferred: Sequence[str] = ("file", "hf", "ipfs")) -> Optional[SinkRef]:
    ranked = sorted(
        shard.sink_refs,
        key=lambda s: preferred.index(s.sink_type) if s.sink_type in preferred else 999
    )
    return ranked[0] if ranked else None


def fetch_shard_bytes(shard: PrimeIndexShard, sink: Optional[SinkRef] = None) -> bytes:
    """
    Minimal sink fetch layer.
    Only file:// is implemented here; HF/IPFS are stubs by design.
    """
    sink = sink or choose_sink(shard)
    if sink is None:
        raise FileNotFoundError(f"No sink refs available for {shard.shard_id}")

    if sink.sink_type == "file":
        path = Path(sink.ref)
        return path.read_bytes()

    if sink.sink_type in {"hf", "ipfs"}:
        raise NotImplementedError(f"{sink.sink_type} fetch not implemented in bounded local prototype")

    raise ValueError(f"Unknown sink type: {sink.sink_type}")


# ---------------------------------------------------------------------
# Retrieval operator
# ---------------------------------------------------------------------

def admissible(
    query: QueryProjection,
    shard: PrimeIndexShard,
    signature_matrix: Sequence[Sequence[float]],
    cfg: RetrievalConfig,
) -> Tuple[bool, Dict[str, float]]:
    grounded = overlap(query.phi.grounded, shard.phi.grounded)
    if grounded < cfg.min_grounded_overlap:
        return False, {"grounded": grounded}

    domain_ov = bit_overlap(query.hecke_sig, shard.hecke_sig)
    if domain_ov < cfg.min_domain_overlap:
        return False, {"grounded": grounded, "domain_overlap": float(domain_ov)}

    if not shard.has_valid_receipts():
        return False, {"grounded": grounded, "domain_overlap": float(domain_ov)}

    delta = delta_vec(query.embedding.exact_addr, shard.embedding.exact_addr)
    qd = qform(delta, signature_matrix)
    if qd > cfg.cone_eps:
        return False, {"grounded": grounded, "domain_overlap": float(domain_ov), "q_delta": qd}

    ub = gain_upper_bound(delta)
    if ub < cfg.min_required_gain:
        return False, {
            "grounded": grounded,
            "domain_overlap": float(domain_ov),
            "q_delta": qd,
            "mdl_upper_bound": ub,
        }

    return True, {
        "grounded": grounded,
        "domain_overlap": float(domain_ov),
        "q_delta": qd,
        "mdl_upper_bound": ub,
    }


def make_query_projection(query: str) -> QueryProjection:
    phi = phi_from_query(query)
    embedding = make_embedding(phi)
    hecke = infer_hecke_signature(phi)
    return QueryProjection(raw_query=query, phi=phi, embedding=embedding, hecke_sig=hecke)


def final_rank_score(query: QueryProjection, shard: PrimeIndexShard) -> float:
    grounded = overlap(query.phi.grounded, shard.phi.grounded)
    domain = float(bit_overlap(query.hecke_sig, shard.hecke_sig))
    proposal = resonance_score(query.phi.experimental, shard.phi.experimental)
    # Resonance stays low-weight and cannot rescue inadmissible shards.
    return 3.0 * grounded + 1.0 * domain + 0.2 * proposal


def retrieve(
    query: str,
    selector: LogicalShardSelector,
    signature_matrix: Sequence[Sequence[float]],
    cfg: RetrievalConfig,
    artifact_revision: Optional[str] = None,
) -> List[Tuple[PrimeIndexShard, Dict[str, float]]]:
    q = make_query_projection(query)

    # selector-first
    candidates = selector.resolve(query, artifact_revision=artifact_revision)
    candidates = candidates[: cfg.max_candidates_after_selector]

    accepted: List[Tuple[PrimeIndexShard, Dict[str, float]]] = []
    for shard in candidates:
        ok, metrics = admissible(q, shard, signature_matrix, cfg)
        if ok:
            accepted.append((shard, metrics))

    accepted.sort(key=lambda item: final_rank_score(q, item[0]), reverse=True)
    return accepted[: cfg.max_fetch]


# ---------------------------------------------------------------------
# Zelph export
# ---------------------------------------------------------------------

def promoted_fact_to_zelph_fact(fact: Mapping[str, Any]) -> Dict[str, Any]:
    payload = {
        "fact_id": fact["fact_id"],
        "predicate": fact["predicate"],
        "arguments": dict(fact.get("arguments", {})),
        "qualifiers": dict(fact.get("qualifiers", {})),
        "confidence": float(fact.get("confidence", 1.0)),
        "provenance": list(fact.get("provenance", [])),
        "promotion_receipt": fact.get("promotion_receipt"),
        "reconstructible": bool(fact.get("reconstructible", True)),
    }
    if fact.get("parse_tree") is not None:
        payload["parse_tree"] = fact["parse_tree"]
    return payload


def shard_to_semantic_overlay(shard: PrimeIndexShard) -> Dict[str, Any]:
    return {
        "zos_id": shard.shard_id,
        "kind": "prime_cluster",
        "members": list(shard.fact_ids),
        "features": {**shard.phi.grounded, **shard.phi.domain},
        "candidate_score": float(shard.embedding.mdl_upper_bound),
        "promoted": False,
        "source_receipts": list(shard.promotion_receipts),
    }


def build_zelph_input(facts: Sequence[Mapping[str, Any]], shards: Sequence[PrimeIndexShard]) -> Dict[str, Any]:
    parse_tree_by_fact_id: Dict[str, Dict[str, Any]] = {}
    for shard in shards:
        for fact_id in shard.fact_ids:
            if shard.parse_tree is not None:
                parse_tree_by_fact_id[fact_id] = shard.parse_tree

    def _fact_parse_tree(fact: Mapping[str, Any]) -> Dict[str, Any]:
        fact_id = str(fact.get("fact_id"))
        existing = parse_tree_by_fact_id.get(fact_id)
        if existing is not None:
            return existing
        source_text = infer_fact_source_text(fact)
        if not source_text:
            return {"text": "", "sents": []}
        return build_parse_tree(source_text)

    return {
        "facts": [
            promoted_fact_to_zelph_fact(
                {**f, "parse_tree": _fact_parse_tree(f)}
            )
            for f in facts
        ],
        "semantic_overlays": [shard_to_semantic_overlay(s) for s in shards],
        "provenance_mode": "strict",
    }


# ---------------------------------------------------------------------
# Facts -> shards helper (for CLI/integration)
# ---------------------------------------------------------------------

def facts_to_shards(
    facts: Sequence[Mapping[str, Any]],
    *,
    artifact_revision: str = "rev-cli",
) -> List[PrimeIndexShard]:
    shards: List[PrimeIndexShard] = []

    for idx, fact in enumerate(facts):
        source_text = infer_fact_source_text(fact)
        parse_tree = build_parse_tree(source_text) if source_text else {"text": "", "sents": []}

        fact_payload = dict(fact)
        fact_payload["parse_tree"] = parse_tree

        phi = _extend_phi_with_parse_tree(phi_from_sl_fact(fact_payload), parse_tree)
        embedding = make_embedding(phi)
        hecke_sig = infer_hecke_signature(phi)

        selector_terms = sorted(
            {
                *(str(v).lower() for v in fact.get("arguments", {}).values()),
                *(_norm_text(fact.get("predicate", "")).split()),
                *(
                    _norm_text(token.get("lemma") or token.get("text") or "")
                    for sentence in parse_tree.get("sents", [])
                    for token in sentence.get("tokens", [])
                    if _norm_text(token.get("lemma") or token.get("text") or "")
                ),
            }
        )

        promotion_receipt = fact.get("promotion_receipt") or f"receipt::{idx}"
        provenance_ids = [f"{fact.get('fact_id', f'f{idx}')}::span{i}" for i, _ in enumerate(fact.get("provenance", []))]
        sink_ref = fact.get("sink_ref")
        sink_refs = [SinkRef("file", sink_ref)] if sink_ref else []

        shards.append(
            PrimeIndexShard(
                shard_id=f"shard::{fact.get('fact_id', f'f{idx}')}",
                artifact_revision=artifact_revision,
                selector_terms=selector_terms,
                fact_ids=[fact.get("fact_id", f"f{idx}")],
                phi=phi,
                embedding=embedding,
                hecke_sig=hecke_sig,
                provenance_ids=provenance_ids,
                promotion_receipts=[promotion_receipt],
                sink_refs=sink_refs,
                parse_tree=parse_tree,
            )
        )

    return shards


# ---------------------------------------------------------------------
# Fixture / tests / demo
# ---------------------------------------------------------------------

def _fixture_facts() -> List[Dict[str, Any]]:
    return [
        {
            "fact_id": "f1",
            "predicate": "applies",
            "arguments": {"subject": "contract", "object": "pet_policy"},
            "qualifiers": {"jurisdiction": "nsw"},
            "provenance": [{"doc_id": "doc1", "start": 120, "end": 174}],
            "promotion_receipt": "r1",
            "reconstructible": True,
        },
        {
            "fact_id": "f2",
            "predicate": "requires",
            "arguments": {"subject": "lease", "object": "bond_payment"},
            "qualifiers": {"jurisdiction": "nsw"},
            "provenance": [{"doc_id": "doc1", "start": 220, "end": 260}],
            "promotion_receipt": "r2",
            "reconstructible": True,
        },
        {
            "fact_id": "f3",
            "predicate": "permits",
            "arguments": {"subject": "landlord", "object": "inspection"},
            "qualifiers": {"notice": "required"},
            "provenance": [{"doc_id": "doc2", "start": 40, "end": 98}],
            "promotion_receipt": "r3",
            "reconstructible": True,
        },
    ]


def _write_fixture_files(base: Path) -> List[Path]:
    base.mkdir(parents=True, exist_ok=True)
    facts = _fixture_facts()
    out_paths: List[Path] = []
    for fact in facts:
        p = base / f"{fact['fact_id']}.json"
        p.write_text(json.dumps(fact, indent=2), encoding="utf-8")
        out_paths.append(p)
    return out_paths


def _build_fixture_shards(base: Path) -> List[PrimeIndexShard]:
    paths = _write_fixture_files(base)
    facts = _fixture_facts()
    path_map = {p.stem: p for p in paths}

    shards: List[PrimeIndexShard] = []
    for fact in facts:
        phi = phi_from_sl_fact(fact)
        embedding = make_embedding(phi)
        hecke_sig = infer_hecke_signature(phi)

        selector_terms = sorted({
            *(str(v).lower() for v in fact.get("arguments", {}).values()),
            *(_norm_text(fact["predicate"]).split()),
        })

        shards.append(
            PrimeIndexShard(
                shard_id=f"shard::{fact['fact_id']}",
                artifact_revision="rev-1",
                selector_terms=selector_terms,
                fact_ids=[fact["fact_id"]],
                phi=phi,
                embedding=embedding,
                hecke_sig=hecke_sig,
                provenance_ids=[f"{fact['fact_id']}::span0"],
                promotion_receipts=[fact["promotion_receipt"]],
                sink_refs=[SinkRef("file", str(path_map[fact["fact_id"]]))],
            )
        )
    return shards


def _collect_fixture_deltas(shards: Sequence[PrimeIndexShard]) -> List[Dict[int, int]]:
    deltas: List[Dict[int, int]] = []
    for i in range(len(shards)):
        for j in range(i + 1, len(shards)):
            deltas.append(delta_vec(shards[i].embedding.exact_addr, shards[j].embedding.exact_addr))
    return deltas


def test_query_shard_grounded_overlap_nonzero(tmp_dir: Path) -> None:
    shards = _build_fixture_shards(tmp_dir)
    selector = LogicalShardSelector(shards)
    M = default_signature_matrix()
    cfg = RetrievalConfig(min_grounded_overlap=1.0, min_domain_overlap=0, min_required_gain=0.0, cone_eps=1e12)
    out = retrieve("pet policy contract", selector, M, cfg)
    assert len(out) > 0, "expected grounded overlap retrieval to return at least one shard"


def test_unknown_domain_does_not_soft_match(tmp_dir: Path) -> None:
    shards = _build_fixture_shards(tmp_dir)
    selector = LogicalShardSelector(shards)
    M = default_signature_matrix()
    cfg = RetrievalConfig(min_grounded_overlap=1.0, min_domain_overlap=1, min_required_gain=0.0, cone_eps=1e12)
    out = retrieve("banana spaceship", selector, M, cfg)
    assert len(out) == 0, "unknown domain/query should not soft-match into results"


def test_resonance_cannot_rescue_inadmissible(tmp_dir: Path) -> None:
    shards = _build_fixture_shards(tmp_dir)
    selector = LogicalShardSelector(shards)
    # Deliberately use tight cone so everything fails cone if needed.
    M = default_signature_matrix()
    cfg = RetrievalConfig(min_grounded_overlap=1.0, min_domain_overlap=0, min_required_gain=999999.0, cone_eps=-1e12)
    out = retrieve("pet policy contract", selector, M, cfg)
    assert len(out) == 0, "proposal-only resonance must not rescue inadmissible shards"


def run_tests() -> None:
    tmp_dir = Path("prime_index_fixture")
    tmp_dir.mkdir(exist_ok=True)
    test_query_shard_grounded_overlap_nonzero(tmp_dir)
    test_unknown_domain_does_not_soft_match(tmp_dir)
    test_resonance_cannot_rescue_inadmissible(tmp_dir)
    print("tests: ok")


def demo() -> None:
    base = Path("prime_index_fixture")
    shards = _build_fixture_shards(base)
    selector = LogicalShardSelector(shards)

    # Derive a bounded signature matrix from fixture deltas.
    deltas = _collect_fixture_deltas(shards)
    M = signature_matrix_from_delta_stats(deltas, time_prime=7, space_primes=(2, 3, 5))

    cfg = RetrievalConfig(
        min_grounded_overlap=1.0,
        min_domain_overlap=0,
        min_required_gain=0.0,
        max_candidates_after_selector=16,
        max_fetch=8,
        cone_eps=1e12,  # permissive for fixture
    )

    results = retrieve("pet policy contract", selector, M, cfg)

    print("retrieval results:")
    for shard, metrics in results:
        print(f"  {shard.shard_id} -> {metrics}")

    facts = _fixture_facts()
    zelph = build_zelph_input(facts, [s for s, _ in results])
    Path("zelph_input_example.json").write_text(json.dumps(zelph, indent=2), encoding="utf-8")
    print("wrote zelph_input_example.json")


if __name__ == "__main__":
    run_tests()
    demo()
