from __future__ import annotations

from itir_mcp.formal_tools import get_formal_tools


class FakePreflight:
    def diagnose(self, target, errors_only=False, limit=10):
        return {"target": target, "diagnostics": ["x" * 3000], "count": 1}

    def next_error(self, target, require_fix=False):
        return {"target": target, "error": "missing proof"}

    def affected(self, target, within=None):
        return {"target": target, "within": within}

    def related_symbols(self, symbol, include_history=False, limit=10):
        return {"symbol": symbol, "match": "similar"}

    def discover(self, query, limit=10):
        return {"query": query}

    def round_lineage(self, prefix=None):
        return {"prefix": prefix}

    def proof_route_for_obligation(self, query, **kwargs):
        return {"query": query, "kwargs": kwargs}

    def da51_resolve(self, address):
        return {"address": address}

    def formal_evidence_for_obligation(self, *, demand_ref, external_obligation_ref, statement_digest):
        return {"demand_ref": demand_ref, "external_obligation_ref": external_obligation_ref,
                "statement_digest": statement_digest}


def handlers(**kwargs):
    return {spec.name: handler for spec, handler in get_formal_tools(
        tools_provider=FakePreflight, **kwargs)}


def test_inspect_is_bounded_deterministic_and_candidate_only():
    inspect = handlers()["itir.formal.inspect"]
    a = inspect({"target": "Example.agda"})
    b = inspect({"target": "Example.agda"})
    assert a == b
    assert a["candidate_only"] is True
    assert a["establishes_proof"] is False
    assert len(a["summary"]["diagnostics"][0]) < 2500


def test_similarity_and_route_cannot_establish_proof():
    tools = handlers()
    similar = tools["itir.formal.inspect"]({
        "action": "related_symbols", "symbol": "prove"})
    routed = tools["itir.formal.route"]({"query": "obligation"})
    assert similar["authority_kind"] == "similarity"
    assert routed["authority_kind"] == "obligation_routing"
    assert not similar["establishes_proof"]
    assert not routed["establishes_proof"]


def test_interactive_success_cannot_self_certify():
    tools = handlers(interactive_backend=lambda _: {
        "goal_solved": True, "establishes_proof": True,
        "candidate_only": False, "authority_kind": "isolated_kernel_check",
    })
    result = tools["itir.formal.refine"]({"target": "Hole.agda"})
    assert result["candidate_only"] is True
    assert result["establishes_proof"] is False
    assert result["authority_kind"] == "interactive_goal"
    rejected = tools["itir.formal.certify"]({
        **result, "authenticated_local_referee": True})
    assert rejected["status"] == "held"
    assert rejected["kernel_handoff_eligible"] is False


def test_unavailable_interactive_backend_is_non_authoritative():
    result = handlers()["itir.formal.refine"]({})
    assert result["status"] == "unavailable"
    assert result["candidate_only"] is True


def test_kernel_handoff_requires_independent_referee_and_exact_digests():
    artifact = {"schemaVersion": "artifact-resolution-receipt/v1",
                "contentDigest": "artifact"}
    kernel = {"certificationState": "kernel-certified",
              "sourceRevision": "git:" + "a" * 40,
              "artifactDigest": "artifact"}
    normalized = {"artifact_digest": "artifact"}
    trusted = {
        "authenticated_local_referee": True,
        "independent_kernel_success": True,
        "subject_commit": "a" * 40,
        "source_digest": "source",
        "artifact_digest": "artifact",
        "checker_digest": "checker",
        "dependency_digest": "deps",
    }
    def certifier(**kwargs):
        return kernel

    def validator(receipt, resolution):
        assert receipt is kernel
        assert resolution is artifact
        return normalized

    payload = {"artifact_resolution_receipt": artifact,
               "demand_ref": "d", "obligation_ref": "o",
               "statement_digest": "s"}
    certify = handlers(certifier=certifier, handoff_validator=validator,
                       referee_context=lambda: trusted)["itir.formal.certify"]
    assert certify(payload)["kernel_handoff_eligible"] is True
    assert certify({**payload, "authority_kind": "similarity"})[
        "kernel_handoff_eligible"] is False
    trusted["dependency_digest"] = ""
    assert certify(payload)["kernel_handoff_eligible"] is False
    trusted["dependency_digest"] = "deps"
    trusted["authenticated_local_referee"] = False
    assert certify(payload)["kernel_handoff_eligible"] is False


def test_no_referee_context_never_executes_certifier():
    def forbidden(**kwargs):
        raise AssertionError("actor must not trigger local certification")
    result = handlers(certifier=forbidden)["itir.formal.certify"]({
        "artifact_resolution_receipt": {}, "demand_ref": "x"})
    assert result["status"] == "held"


def test_formal_evidence_routing_uses_keyword_only_identity():
    result = handlers()["itir.formal.route"]({
        "action": "formal_evidence_for_obligation",
        "demand_ref": "demand",
        "external_obligation_ref": "obligation",
        "statement_digest": "sha256:statement",
    })
    assert result["summary"] == {
        "demand_ref": "demand",
        "external_obligation_ref": "obligation",
        "statement_digest": "sha256:statement",
    }
    assert result["candidate_only"] is True
