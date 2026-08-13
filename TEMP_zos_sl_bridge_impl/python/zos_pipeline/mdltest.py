from __future__ import annotations

from typing import Iterable

from .types import FactRecord, RetrievalResult


def toy_mdl_cost(facts: Iterable[FactRecord]) -> float:
    facts = list(facts)
    pred_card = len({f.predicate for f in facts})
    role_card = len({k for f in facts for k in f.arguments})
    qual_card = len({(k, str(v)) for f in facts for k, v in f.qualifiers.items()})
    return float(len(facts) + 2 * pred_card + role_card + qual_card)


def toy_mdl_delta(selected_facts: Iterable[FactRecord], motif_bonus: float = 1.0) -> float:
    facts = list(selected_facts)
    base = toy_mdl_cost(facts)
    motif_gain = motif_bonus * len({f.predicate for f in facts})
    return (base - motif_gain) - base
