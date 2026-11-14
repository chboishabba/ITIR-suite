"""Non-promoting adapter for AST triangulation; never creates kernel receipts."""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def candidate_evidence_from_triangulation(
    triangulation: Mapping[str, Any], *, repo: str, sha: str,
    source_paths: Sequence[str],
) -> list[dict[str, Any]]:
    """Keep source provenance and candidate status for triangulator output.

    Shared AST invariants are NOT independent kernel checks. Referee-only
    PostgreSQL receipts must be produced by the actual formal checker.
    """
    if not repo or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("source repository and immutable commit SHA required")
    paths = sorted(set(source_paths))
    if not paths or any(not p.endswith((".agda", ".lean")) or ".." in p.split("/") for p in paths):
        raise ValueError("formal source paths required")
    raw = triangulation.get("shared_invariants", ())
    if not isinstance(raw, (list, tuple)):
        raise ValueError("shared_invariants must be a sequence")
    return [
        {"invariant_id": name, "repo": repo, "sha": sha,
         "source_paths": paths, "candidate_only": True,
         "kernel_verified": False, "establishes_proof": False,
         "authority": "triangulated_ast_observation"}
        for name in sorted({str(item) for item in raw if isinstance(item, str) and item})
    ]
