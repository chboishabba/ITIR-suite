from __future__ import annotations

from itir_mcp.latex_math_bridge import (
    build_prepopulated_proof_stub,
    distill_pnf_capsule,
    extract_latex_math,
    extract_linguistic_pnf_atoms,
)
from itir_mcp.registry import build_default_registry


def test_extract_latex_math_ast_without_regex() -> None:
    text = (
        r"Given the Rayleigh quotient $\lambda_{\min}(K_N(A)) \ge \frac{c}{N}$ "
        r"and the Fourier mode equation: "
        r"\[ p = (1, 0, 0), \quad q = (0, 1, 2) \]"
    )
    extracted = extract_latex_math(text)
    assert len(extracted) == 2

    # Inline math check
    inline = extracted[0]
    assert inline.display == "inline"
    assert "lambda" in inline.macros
    assert "ge" in inline.macros
    assert "frac" in inline.macros
    assert "K_N" in inline.identifiers
    assert "min" in inline.identifiers

    # Display math check
    display = extracted[1]
    assert display.display == "display"
    assert "p" in display.identifiers
    assert "q" in display.identifiers


def test_extract_linguistic_pnf_atoms() -> None:
    text = "The operator preserves Beltrami suppression. The rotation forces Suzuki 2B class."
    atoms = extract_linguistic_pnf_atoms(text)
    assert len(atoms) >= 1
    # Check that PNF structure extracted roles
    assert any("preserve" in a["predicate"] or "force" in a["predicate"] for a in atoms)


def test_build_prepopulated_proof_stub_zero_trust_escapes() -> None:
    matched = [
        {
            "name": "nsBeltramiSuppressionReusedIsTrue",
            "module": "DASHI.Physics.Closure.NSCross369OrientationBridgeExact",
        },
        {
            "name": "canonicalNSTriadKN369HighHighGramBridgeReceipt",
            "module": "DASHI.Physics.Closure.NSTriadKN369HighHighGramBridgeReceipt",
        },
    ]
    math_exprs = [{"raw": r"$\lambda_{\min} \ge \frac{c}{N}$"}]

    stub = build_prepopulated_proof_stub(matched, math_exprs)
    assert "module DASHI.Interop.AutoProofBridgeExact where" in stub
    assert "import DASHI.Physics.Closure.NSCross369OrientationBridgeExact" in stub
    assert "import DASHI.Physics.Closure.NSTriadKN369HighHighGramBridgeReceipt" in stub
    assert "autoBound0NotPromotedToWildPhysics ≡ false" in stub
    assert "autoBound0NonPromotionExact = refl" in stub

    # Strict zero-trust escape invariant
    for forbidden in ["postulate", "allow-unsolved-metas", "TERMINATING", "NO_POSITIVITY_CHECK"]:
        assert forbidden not in stub


def test_distill_pnf_capsule() -> None:
    text = (
        r"We investigate the Navier-Stokes high-high Gram operator where "
        r"$\lambda_{\min}(K_N(A)) \ge \frac{c}{N}$ for uniform $c > 0$. "
        r"The operator retains Beltrami suppression and Leray cancellation."
    )
    capsule = distill_pnf_capsule(text, conversation_id="test-conv-123", auto_link_repo=False)
    assert capsule.original_char_count > 0
    assert len(capsule.math_expressions) >= 1
    assert "test-conv-123" in capsule.condensed_prompt_text
    assert "@converge_toe" in capsule.condensed_prompt_text
    assert "DASHI.Interop.AutoProofBridgeExact" in capsule.proof_linkage_stub


def test_registry_invokes_formal_latex_bridge_and_pnf_distill() -> None:
    registry = build_default_registry()

    # Test itir.formal.latex_bridge
    res_bridge = registry.invoke("itir.formal.latex_bridge", {
        "text": r"The spectrum satisfies $E = mc^2$ and $\nabla \cdot B = 0$."
    })
    assert res_bridge["ok"] is True
    assert "result" in res_bridge
    assert len(res_bridge["result"]["math_expressions"]) == 2

    # Test itir.pnf.distill_prompt
    res_distill = registry.invoke("itir.pnf.distill_prompt", {
        "text": r"The operator retains Beltrami suppression with $\lambda > 0$."
    })
    assert res_distill["ok"] is True
    assert "distilled_prompt" in res_distill["result"]
    assert "proof_linkage_stub" in res_distill["result"]
