#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ITIR_SRC = REPO_ROOT / "itir-mcp" / "src"
if str(ITIR_SRC) not in sys.path:
    sys.path.insert(0, str(ITIR_SRC))

from itir_mcp.spectral_plot_tools import (
    project_semantic_spine_hierarchy_to_docs,
    stream_postgres_corpus as _stream_postgres_corpus,
    stream_slrw_corpus as _stream_slrw_corpus,
)


DEFAULT_WORLD_DIR = Path.home() / ".chatgpt_fleet_world"
DEFAULT_SLRW = DEFAULT_WORLD_DIR / "fleet_top500_iter1.slrw"


def stream_postgres_corpus(database_url: str | None = None):
    """Public script-level PostgreSQL semantic-spine stream."""
    return _stream_postgres_corpus(database_url)


def stream_slrw_corpus(path: str | Path = DEFAULT_SLRW):
    """Public script-level offline SLRW fallback stream."""
    return _stream_slrw_corpus(path)



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Project the canonical PNF semantic spine into hierarchical spectral artifacts."
    )
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--slrw-fallback", type=Path, default=DEFAULT_SLRW)
    parser.add_argument("--sqlite-history", type=Path, default=Path.home() / ".chatgpt_history.sqlite3")
    parser.add_argument("--output-dir", type=Path, default=Path("docs/fleet"))
    parser.add_argument("--max-features", type=int, default=256)
    parser.add_argument("--max-spectral-dimensions", type=int, default=16)
    parser.add_argument(
        "--no-register-chat-coordinates",
        action="store_true",
        help="Do not attempt reference-only SQLite chat coordinate registration in PostgreSQL.",
    )
    args = parser.parse_args()

    receipt = project_semantic_spine_hierarchy_to_docs(
        args.output_dir,
        database_url=args.database_url,
        slrw_fallback_path=args.slrw_fallback,
        sqlite_history_path=args.sqlite_history,
        register_chat_coordinates=not args.no_register_chat_coordinates,
        max_features=args.max_features,
        max_spectral_dimensions=args.max_spectral_dimensions,
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
