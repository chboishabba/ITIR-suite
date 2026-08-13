import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from itir_overlay_flags import DERIVED_ONLY_FLAG, as_derived_only, is_derived_only
from itir_overlay_flags import assert_not_derived_only


def test_as_derived_only_sets_fields_and_is_immutable() -> None:
    base = {"id": "demo", "overlay_flags": ["traceable"]}

    tagged = as_derived_only(base, reason="graph overlay")

    # original unchanged
    assert base == {"id": "demo", "overlay_flags": ["traceable"]}

    # new payload marked
    assert tagged["canonical_status"] == DERIVED_ONLY_FLAG
    assert DERIVED_ONLY_FLAG in tagged["overlay_flags"]
    assert "traceable" in tagged["overlay_flags"]
    assert tagged["derived_only_reason"] == "graph overlay"


def test_is_derived_only_recognizes_both_fields() -> None:
    assert is_derived_only({"canonical_status": DERIVED_ONLY_FLAG})
    assert is_derived_only({"overlay_flags": [DERIVED_ONLY_FLAG]})
    assert not is_derived_only({"overlay_flags": ["other"]})


def test_assert_not_derived_only_blocks_and_allows_opt_in() -> None:
    payload = as_derived_only({"id": "x"})
    try:
        assert_not_derived_only(payload)
        raise AssertionError("should have raised")
    except ValueError:
        pass
    # opt-in passes
    assert_not_derived_only(payload, allow_derived=True)
