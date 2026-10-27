from __future__ import annotations

import sys
import types

from itir_mcp.sensiblaw_spectral_adapter import (
    UNAVAILABLE,
    analyze_pareto_distribution,
    compute_hierarchical_eigen_coordinates,
    materialize_sensiblaw_spectral_payload,
)


def test_sensiblaw_spectral_adapter_unavailable_has_no_fabricated_receipts(monkeypatch) -> None:
    before_path = list(sys.path)

    def fake_import(name: str):
        if name in {"SensibLaw", "sensiblaw"}:
            sys.modules["src.polluted_by_failed_adapter"] = types.ModuleType("src.polluted_by_failed_adapter")
            raise ImportError(name)
        raise AssertionError(name)

    monkeypatch.setattr("itir_mcp.sensiblaw_spectral_adapter.importlib.import_module", fake_import)
    result = materialize_sensiblaw_spectral_payload({"text": "candidate"})
    assert result["status"] == UNAVAILABLE
    assert result["receipt_ids"] == []
    assert result["diagnostic_only"] is True
    assert sys.path == before_path
    assert "src.polluted_by_failed_adapter" not in sys.modules


def test_sensiblaw_spectral_adapter_exposes_dynamic_eigen_analysis() -> None:
    rows = [
        {"thread_id": "t1", "factors": {"alpha": 9, "beta": 8, "leaf": 1}},
        {"thread_id": "t2", "factors": {"alpha": 8, "beta": 7, "leaf": 0}},
        {"thread_id": "t3", "factors": {"alpha": 7, "beta": 6, "leaf": 1}},
        {"thread_id": "t4", "factors": {"alpha": 2, "beta": 1, "leaf": 3}},
        {"thread_id": "t5", "factors": {"alpha": 1, "beta": 0, "leaf": 4}},
        {"thread_id": "t6", "factors": {"alpha": 0, "beta": 1, "leaf": 5}},
    ]

    result = compute_hierarchical_eigen_coordinates(rows, k_eigens=3)

    assert result["method"] == "symmetric_covariance_svd_jacobi"
    assert result["thread_count"] == 6
    assert result["factor_names"] == ["alpha", "beta", "leaf"]
    assert len(result["singular_values"]) == 3
    assert result["marchenko_pastur"]["lambda_plus"] >= 0
    assert len(result["thread_coordinates"]) == 6
    assert set(result["thread_coordinates"][0]["hierarchical"]) == {
        "x_main_eigen", "y_sub_eigen", "z_leaf"
    }
    assert "alpha" in result["components"][0]["motif_name"]
    assert result["authority_boundary"]["motif_name_creates_semantic_identity"] is False


def test_sensiblaw_spectral_adapter_exposes_pareto_non_promotion() -> None:
    result = analyze_pareto_distribution(
        {
            "scale_density": [1.0, 2.0, 4.0, 8.0, 16.0],
            "token_rank": [100, 50, 33, 25, 20],
        }
    )

    assert result["factors"]["scale_density"]["continuous_pareto"]["status"] == "fit"
    discrete = result["factors"]["token_rank"]["discrete_zipf"]
    assert discrete["status"] == "fit"
    assert 0.5 < discrete["nu"] < 1.5
    receipt = result["non_promotion_receipt"]
    assert receipt["discrete_zipf_rank_creates_mathematical_theorem_truth"] is False
    assert receipt["mathematical_theorem_truth_requires_independent_formal_verification"] is True
