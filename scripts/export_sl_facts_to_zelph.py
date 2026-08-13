from __future__ import annotations

"""
Export promoted SL facts to a Zelph bundle via the prime-index pipeline.

Usage:
  /home/c/Documents/code/ITIR-suite/.venv/bin/python scripts/export_sl_facts_to_zelph.py input.json -o out.json

Input formats:
- JSON array of fact objects
- JSON object with {"facts": [...]}
- JSONL where each line is a fact object

Fact shape is the same as expected by tools/prime_index.py and schemas/zelph_input.schema.json.
"""

import argparse
import json
from pathlib import Path
from typing import Iterable

from tools import prime_index as pi


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export promoted SL facts to Zelph bundle via prime index.")
    parser.add_argument("input", type=Path, help="Path to facts JSON/JSONL")
    parser.add_argument("-o", "--output", type=Path, help="Output path (default: stdout)")
    parser.add_argument("--artifact-revision", default="rev-export", help="Artifact revision label")
    args = parser.parse_args(list(argv) if argv is not None else None)

    bundle = pi.build_zelph_bundle_from_payload(pi.load_export_payload(args.input), artifact_revision=args.artifact_revision)

    out = json.dumps(bundle, indent=2)
    if args.output:
        args.output.write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
