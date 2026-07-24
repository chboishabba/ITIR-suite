#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTER = REPO_ROOT / "scripts" / "export_chat_archive_thread.py"


def _parse_config(value: str) -> tuple[int, int, int]:
    parts = value.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("config must be CHUNK_MESSAGES:TARGET_BYTES:PDF_WORKERS")
    try:
        messages, target_bytes, workers = (int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("config values must be integers") from exc
    if messages <= 0 or target_bytes <= 0 or workers <= 0:
        raise argparse.ArgumentTypeError("config values must be positive")
    return messages, target_bytes, workers


def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _summarize_bundle(out_dir: Path, elapsed_seconds: float, returncode: int) -> dict[str, Any]:
    manifest_path = out_dir / "manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = [Path(item["path"]) for item in manifest.get("files", [])]
    pdfs = sorted(path for path in out_dir.glob("*.pdf"))
    htmls = sorted(path for path in out_dir.glob("*.html"))
    chunk_plan = manifest.get("chunk_plan") or []
    estimated_bytes = [int(item.get("estimated_bytes") or 0) for item in chunk_plan]
    return {
        "ok": returncode == 0 and bool(manifest) and len(pdfs) == len(chunk_plan),
        "returncode": returncode,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "manifest": str(manifest_path) if manifest_path.exists() else None,
        "thread": manifest.get("thread"),
        "chunk_count": len(chunk_plan),
        "html_count": len(htmls),
        "pdf_count": len(pdfs),
        "pdf_total_bytes": sum(_file_size(path) for path in pdfs),
        "pdf_max_bytes": max((_file_size(path) for path in pdfs), default=0),
        "html_total_bytes": sum(_file_size(path) for path in htmls),
        "html_max_bytes": max((_file_size(path) for path in htmls), default=0),
        "estimated_max_bytes": max(estimated_bytes, default=0),
        "estimated_total_bytes": sum(estimated_bytes),
        "file_count": len(files),
    }


def _run_config(args: argparse.Namespace, config: tuple[int, int, int]) -> dict[str, Any]:
    chunk_messages, target_bytes, pdf_workers = config
    name = f"m{chunk_messages}-b{target_bytes}-w{pdf_workers}"
    out_dir = Path(args.out_root).expanduser() / name
    out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(EXPORTER),
        "--db",
        str(Path(args.db).expanduser()),
        "--out",
        str(out_dir),
        "--bundle",
        "--format",
        "all",
        "--pdf",
        "--pdf-workers",
        str(pdf_workers),
        "--pdf-timeout-seconds",
        str(args.pdf_timeout_seconds),
        "--chunk-messages",
        str(chunk_messages),
        "--chunk-target-bytes",
        str(target_bytes),
        "--json",
    ]
    if args.source_thread_id:
        command.extend(["--source-thread-id", args.source_thread_id])
    elif args.canonical_thread_id:
        command.extend(["--canonical-thread-id", args.canonical_thread_id])
    elif args.selector:
        command.extend(["--selector", args.selector])
    else:
        raise SystemExit("one of --source-thread-id, --canonical-thread-id, or --selector is required")
    if args.platform:
        command.extend(["--platform", args.platform])
    print(
        f"benchmark: start {name} chunk_messages={chunk_messages} target_bytes={target_bytes} workers={pdf_workers}",
        file=sys.stderr,
        flush=True,
    )
    start = time.monotonic()
    completed = subprocess.run(command, cwd=REPO_ROOT)
    elapsed = time.monotonic() - start
    summary = _summarize_bundle(out_dir, elapsed, completed.returncode)
    summary.update(
        {
            "name": name,
            "out_dir": str(out_dir),
            "chunk_messages": chunk_messages,
            "chunk_target_bytes": target_bytes,
            "pdf_workers": pdf_workers,
        }
    )
    print(
        "benchmark: done "
        f"{name} ok={summary['ok']} elapsed={summary['elapsed_seconds']}s "
        f"pdfs={summary['pdf_count']}/{summary['chunk_count']} "
        f"pdf_total={summary['pdf_total_bytes']}",
        file=sys.stderr,
        flush=True,
    )
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark chunked chat archive HTML/PDF export settings.")
    parser.add_argument("--db", default="/home/c/chat_archive.sqlite")
    parser.add_argument("--source-thread-id")
    parser.add_argument("--canonical-thread-id")
    parser.add_argument("--selector")
    parser.add_argument("--platform")
    parser.add_argument("--out-root", default="/tmp/chat-archive-export-chunk-bench")
    parser.add_argument("--pdf-timeout-seconds", type=int, default=180)
    parser.add_argument(
        "--config",
        action="append",
        type=_parse_config,
        default=[],
        help="Candidate as CHUNK_MESSAGES:TARGET_BYTES:PDF_WORKERS. May be repeated.",
    )
    parser.add_argument("--json-out", help="Optional path for the benchmark summary JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    configs = args.config or [
        (40, 600_000, 2),
        (80, 1_200_000, 2),
        (120, 1_800_000, 2),
        (80, 1_200_000, 3),
    ]
    results = [_run_config(args, config) for config in configs]
    successful = [item for item in results if item["ok"]]
    fastest = min(successful, key=lambda item: item["elapsed_seconds"]) if successful else None
    summary = {
        "ok": bool(successful) and len(successful) == len(results),
        "out_root": str(Path(args.out_root).expanduser()),
        "results": results,
        "fastest_successful": fastest,
    }
    text = json.dumps(summary, indent=2, ensure_ascii=False)
    print(text)
    if args.json_out:
        Path(args.json_out).expanduser().write_text(text + "\n", encoding="utf-8")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
