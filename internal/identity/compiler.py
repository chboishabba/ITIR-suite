"""Bounded, user-sovereign identity/trust overlay.

Source: ITIR-suite docs/planning/itir_sensiblaw_identity_trust_alignment_layer_20260328.md.
This module does not parse narrative, diagnose people, or promote facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping, Sequence

KINDS = frozenset({
    "TrustBoundary", "FrictionNode", "ConfidenceDrop", "WorkflowPattern",
    "EvidenceStrategy", "PrimaryNeed", "RejectionCondition", "FailureMode",
})
MAX_ATOMS = 32
MAX_LABEL = 200
MAX_REF = 240


@dataclass(frozen=True)
class ReviewedAtom:
    identifier: str
    kind: str
    label: str
    source_ref: str
    reviewed_by_user: bool


@dataclass(frozen=True)
class Abstention:
    identifier: str
    reason: str


@dataclass(frozen=True)
class IdentityOverlay:
    """Non-canonical overlay; not a diagnosis, truth graph or user profile."""
    accepted: tuple[ReviewedAtom, ...]
    abstentions: tuple[Abstention, ...]
    scope: Literal["user_reviewed_non_diagnostic"] = "user_reviewed_non_diagnostic"

    def display(self) -> tuple[dict[str, str], ...]:
        """Output only user-reviewed labels and their local source references."""
        return tuple({"id": a.identifier, "kind": a.kind,
                      "label": a.label, "source_ref": a.source_ref}
                     for a in self.accepted)

    def revoke(self, identifier: str) -> IdentityOverlay:
        """User-controlled removal. Do not keep revoked content in the result."""
        return IdentityOverlay(
            accepted=tuple(a for a in self.accepted if a.identifier != identifier),
            abstentions=tuple(a for a in self.abstentions if a.identifier != identifier),
        )


def _valid_text(value: object, max_length: int) -> bool:
    return isinstance(value, str) and 0 < len(value.strip()) <= max_length


def compile_identity_overlay(
    atoms: Sequence[Mapping[str, object]], *, user_opt_in: bool = False
) -> IdentityOverlay:
    """Compile ONLY explicit, source-bound, individually user-reviewed atoms.

    Preconditions: finite sequence, at most 32 records, explicit opt-in.
    Invariants: never infer a diagnosis, motive, identity or strong truth.
    Postcondition: all accepted records are user-reviewed and source-linked.
    Without opt-in, content is not retained, even in abstention receipts.
    """
    if not isinstance(atoms, (tuple, list)) or len(atoms) > MAX_ATOMS:
        raise ValueError(f"identity input must contain at most {MAX_ATOMS} atoms")
    if not user_opt_in:
        return IdentityOverlay(accepted=(), abstentions=())
    accepted: list[ReviewedAtom] = []
    abstentions: list[Abstention] = []
    seen: set[str] = set()
    for index, candidate in enumerate(atoms):
        if not isinstance(candidate, Mapping):
            abstentions.append(Abstention(str(index), "invalid_record"))
            continue
        identifier = candidate.get("id")
        if not _valid_text(identifier, 80) or identifier in seen:
            abstentions.append(Abstention(str(index), "invalid_or_duplicate_id"))
            continue
        assert isinstance(identifier, str)
        seen.add(identifier)
        if candidate.get("kind") not in KINDS:
            abstentions.append(Abstention(identifier, "unknown_kind"))
        elif not _valid_text(candidate.get("label"), MAX_LABEL):
            abstentions.append(Abstention(identifier, "invalid_label"))
        elif not _valid_text(candidate.get("source_ref"), MAX_REF):
            abstentions.append(Abstention(identifier, "missing_source_ref"))
        elif candidate.get("reviewed_by_user") is not True:
            abstentions.append(Abstention(identifier, "awaiting_user_review"))
        else:
            accepted.append(ReviewedAtom(identifier, candidate["kind"],
                                         candidate["label"].strip(),
                                         candidate["source_ref"].strip(), True))
    return IdentityOverlay(tuple(accepted), tuple(abstentions))
