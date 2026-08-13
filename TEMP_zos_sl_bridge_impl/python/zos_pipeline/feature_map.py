from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List

from .monster_lattice import hash_file_bytes, resonance_score_from_hash
from .trace_features import aggregate_shard_vector
from .types import FactRecord, FeatureVector, Query, ShardSummary


def _tokenize(s: str) -> List[str]:
    text = s.lower()
    for ch in ":,_/.-":
        text = text.replace(ch, " ")
    return [tok for tok in text.split() if tok.strip()]


def _lexical_counter(parts: Iterable[str]) -> Counter[str]:
    tokens = Counter()
    for part in parts:
        for token in _tokenize(part):
            tokens[token] += 1
    return tokens


def _fact_features(facts: Iterable[FactRecord]) -> Dict[str, float]:
    facts = list(facts)
    n = max(1, len(facts))
    pred = Counter(f.predicate for f in facts)
    roles = Counter()
    quals = Counter()
    lexemes = Counter()
    for f in facts:
        lexemes.update(_lexical_counter([f.predicate]))
        for k in f.arguments:
            roles[f"role::{k}"] += 1
            lexemes.update(_lexical_counter([k, str(f.arguments[k])]))
        for k, v in f.qualifiers.items():
            quals[f"qual::{k}::{v}"] += 1
            lexemes.update(_lexical_counter([k, str(v)]))

    vec: Dict[str, float] = {
        "fact_count": float(len(facts)),
        "predicate_cardinality": float(len(pred)),
        "role_cardinality": float(len(roles)),
        "qualifier_cardinality": float(len(quals)),
        "lexeme_cardinality": float(len(lexemes)),
    }
    for k, c in pred.items():
        vec[f"pred::{k}"] = c / n
    for k, c in roles.items():
        vec[k] = c / n
    for k, c in quals.items():
        vec[k] = c / n
    lex_total = max(1, sum(lexemes.values()))
    for token, c in lexemes.items():
        vec[f"lex::{token}"] = c / lex_total
    return vec


def build_phi(summary: ShardSummary) -> FeatureVector:
    fact_vec = _fact_features(summary.facts)
    trace_vec = aggregate_shard_vector(summary.trace_windows)

    summary_bytes = ("|".join(sorted(f.fact_id for f in summary.facts)) + "|" + summary.shard_id).encode("utf-8")
    res = resonance_score_from_hash(hash_file_bytes(summary_bytes))

    values = {}
    values.update(fact_vec)
    values.update({f"trace::{k}": v for k, v in trace_vec.items()})
    values.update({
        "lat::o71": float(res.o71),
        "lat::o59": float(res.o59),
        "lat::o47": float(res.o47),
        "lat::dist_primary": float(res.dist_primary),
        "lat::dist_secondary": float(res.dist_secondary),
        "lat::resonance_strength": float(res.resonance_strength),
        "lat::resonance_flag": 1.0 if res.resonance else 0.0,
    })
    return FeatureVector(shard_id=summary.shard_id, values=values)


def query_phi(query: Query) -> FeatureVector:
    token_counts = _lexical_counter([query.text])
    selector_tokens = Counter()
    for key, value in query.selectors.items():
        selector_tokens.update(_lexical_counter([key, value]))
    values: Dict[str, float] = {
        "query_token_count": float(sum(token_counts.values())),
        "query_selector_count": float(len(query.selectors)),
        "query_predicate_hint_count": float(len(query.predicate_hints)),
    }
    token_total = max(1, sum(token_counts.values()) + sum(selector_tokens.values()))
    for token, c in token_counts.items():
        values[f"lex::{token}"] = c / token_total
    for token, c in selector_tokens.items():
        values[f"lex::{token}"] = values.get(f"lex::{token}", 0.0) + (c / token_total)
    for p in query.predicate_hints:
        values[f"pred::{p}"] = 1.0
        for token in _tokenize(p):
            values[f"lex::{token}"] = max(values.get(f"lex::{token}", 0.0), 1.0 / token_total)
    for role, value in query.role_hints.items():
        values[f"role::{role}"] = 1.0
        for token in _tokenize(str(value)):
            values[f"lex::{token}"] = max(values.get(f"lex::{token}", 0.0), 1.0 / token_total)
    return FeatureVector(shard_id=None, values=values)
