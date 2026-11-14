from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "colab-runner" / "src"))

from itir_colab_runner import authority


def test_compiler_receipts_never_promote_authority():
    assert authority.COMPILER_RECEIPT_CREATES_THEOREM_TRUTH is False
    assert authority.COMPILER_RECEIPT_MERGES_SOURCE is False
    assert authority.COMPILER_RECEIPT_PROMOTES_CLAY_STATUS is False
    assert authority.RUNTIME_STATE_BRANCH == "colab-runner-state"
