from __future__ import annotations

import sys

from .artifact_receipt import main as artifact_receipt_main
from .cli import main as bridge_main
from .xpollenation_artifact import main as xpollenation_artifact_main


def main(argv: list[str] | None = None) -> int:
    """Dispatch canonical ITIR bridge commands, including artifact receipts."""
    actual = list(sys.argv[1:] if argv is None else argv)
    if actual and actual[0] == "emit-artifact-resolution-receipt":
        return artifact_receipt_main(actual[1:])
    if actual and actual[0] == "emit-xpollenation-artifact":
        return xpollenation_artifact_main(actual[1:])
    return bridge_main(actual)


if __name__ == "__main__":
    raise SystemExit(main())
