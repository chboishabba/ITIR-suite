from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools import prime_index as pi


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Zelph input from SL-style facts via prime index.")
    parser.add_argument("facts", type=Path, help="Path to JSON file containing facts or {'facts': [...]} object.")
    parser.add_argument("-o", "--output", type=Path, help="Output path (defaults to stdout).")
    parser.add_argument("--artifact-revision", default="rev-cli", help="Artifact revision label for shards.")
    args = parser.parse_args(argv)

    facts = pi.load_export_facts(args.facts)
    shards = pi.facts_to_shards(facts, artifact_revision=args.artifact_revision)
    zelph = pi.build_zelph_input(facts, shards)

    output = json.dumps(zelph, indent=2)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
