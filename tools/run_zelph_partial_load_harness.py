#!/usr/bin/env python3
"""Run a bounded partial-load validation matrix for local Zelph artifacts.

This harness exists to close the remaining manifest/sharding implementation gap:
it distinguishes working selector behavior from manifest chunk failures and from
graceful sequential fallback.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


TIME_PATTERN = re.compile(r"Time needed for partial loading:\s+([0-9hms.]+)")
SELECTOR_PATTERN = re.compile(r"(left|right|nameOfNode|nodeOfName)=([^\s]+)")
MANIFEST_PATTERN = re.compile(r"manifest=([^\s]+)")


@dataclass
class HarnessCase:
    name: str
    command: str
    expected_mode: str
    artifact_kind: str = "bin"


@dataclass
class HarnessResult:
    artifact: str
    case: str
    command: str
    expected_mode: str
    exit_code: int
    ok: bool
    fallback_used: bool
    had_repl_error: bool
    wall_time_seconds: float
    reported_partial_time: str | None
    output_excerpt: str
    fetch_plan: dict[str, Any] | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Zelph partial-load validation cases against local artifacts.")
    parser.add_argument(
        "--artifact",
        action="append",
        required=True,
        help="Path to a local .bin artifact. Repeat for multiple bins.",
    )
    parser.add_argument(
        "--zelph-bin",
        default="/home/c/Documents/code/ITIR-suite/aur/zelph/build-local/bin/zelph",
        help="Path to the Zelph REPL binary.",
    )
    parser.add_argument(
        "--manifest-builder",
        default="/home/c/Documents/code/ITIR-suite/tools/build_zelph_hf_manifest.py",
        help="Path to build_zelph_hf_manifest.py.",
    )
    parser.add_argument(
        "--work-dir",
        default="/tmp/zelph-partial-load-harness",
        help="Directory for generated indexes/manifests/shards/results.",
    )
    parser.add_argument(
        "--include-name-cases",
        action="store_true",
        help="Also run nameOfNode/nodeOfName selector cases.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional explicit path for the summary JSON output.",
    )
    return parser.parse_args()


def run_repl_command(zelph_bin: Path, command: str) -> tuple[int, str, float]:
    payload = f"{command}\n.exit\n"
    started = time.monotonic()
    proc = subprocess.run(
        [str(zelph_bin)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.monotonic() - started
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output, elapsed


def run_checked(args: list[str]) -> None:
    subprocess.run(args, check=True, text=True, capture_output=True)


def parse_selectors(command: str) -> dict[str, str]:
    return {match.group(1): match.group(2) for match in SELECTOR_PATTERN.finditer(command)}


def parse_manifest_path(command: str) -> Path | None:
    match = MANIFEST_PATTERN.search(command)
    return Path(match.group(1)) if match else None


def chunk_refs_for_selector(
    manifest: dict[str, Any],
    section_name: str,
    selector_value: str,
) -> list[dict[str, Any]]:
    if selector_value == "none":
        return []
    chunk_index = int(selector_value)
    chunks = manifest.get("sections", {}).get(section_name, {}).get("chunks", [])
    return [chunk for chunk in chunks if int(chunk["chunkIndex"]) == chunk_index]


def build_fetch_plan(case: HarnessCase, artifact: Path) -> dict[str, Any] | None:
    selectors = parse_selectors(case.command)
    selected_sections = {name: value for name, value in selectors.items() if value != "none"}

    if case.artifact_kind == "bin":
        return {
            "transport": "local-file",
            "artifactPath": str(artifact),
            "selectors": selectors,
            "selectedSections": selected_sections,
        }

    manifest_path = parse_manifest_path(case.command)
    if manifest_path is None:
        return None

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_version = str(manifest.get("manifestVersion", ""))
    refs: list[dict[str, Any]] = []
    for section_name, selector_value in selected_sections.items():
        for chunk in chunk_refs_for_selector(manifest, section_name, selector_value):
            if manifest_version == "zelph-hf-layout/v1":
                refs.append(
                    {
                        "section": section_name,
                        "chunkIndex": int(chunk["chunkIndex"]),
                        "transport": "http-range",
                        "objectPath": manifest["hfObjects"]["bin"]["path"],
                        "range": chunk["range"],
                    }
                )
            else:
                refs.append(
                    {
                        "section": section_name,
                        "chunkIndex": int(chunk["chunkIndex"]),
                        "transport": "hf-object-fetch",
                        "objectPath": chunk["objectPath"],
                        "sizeBytes": int(chunk["length"]),
                    }
                )

    return {
        "transport": manifest.get("transport", {}).get("primary"),
        "manifestVersion": manifest_version,
        "manifestPath": str(manifest_path),
        "selectors": selectors,
        "selectedSections": selected_sections,
        "headerProbeOnly": not refs,
        "fetchRefs": refs,
        "nodeRouteIndex": manifest.get("hfObjects", {}).get("nodeRouteIndex"),
    }


def build_manifests_for_artifact(
    zelph_bin: Path,
    manifest_builder: Path,
    artifact: Path,
    artifact_dir: Path,
) -> tuple[Path, Path, Path]:
    index_path = artifact_dir / f"{artifact.stem}.index.json"
    manifest_v1 = artifact_dir / f"{artifact.stem}.hf-v1.json"
    manifest_v2 = artifact_dir / f"{artifact.stem}.hf-v2.json"
    shard_root = artifact_dir / f"{artifact.stem}-shards"

    run_repl_command(zelph_bin, f".index-file {artifact} {index_path}")
    run_checked(
        [
            sys.executable,
            str(manifest_builder),
            "--bin",
            str(artifact),
            "--index",
            str(index_path),
            "--output",
            str(manifest_v1),
            "--layout",
            "v1",
        ]
    )
    run_checked(
        [
            sys.executable,
            str(manifest_builder),
            "--bin",
            str(artifact),
            "--index",
            str(index_path),
            "--output",
            str(manifest_v2),
            "--layout",
            "v2",
            "--emit-shards",
            "--shard-root",
            str(shard_root),
        ]
    )
    return manifest_v1, manifest_v2, shard_root


def build_case_matrix(
    artifact: Path,
    manifest_v1: Path,
    manifest_v2: Path,
    shard_root: Path,
    include_name_cases: bool,
) -> list[HarnessCase]:
    cases = [
        HarnessCase(
            "bin_meta_only",
            f".load-partial {artifact} left=none right=none nameOfNode=none nodeOfName=none meta-only",
            "ok",
            artifact_kind="bin",
        ),
        HarnessCase(
            "bin_left0",
            f".load-partial {artifact} left=0 right=none nameOfNode=none nodeOfName=none",
            "ok",
            artifact_kind="bin",
        ),
        HarnessCase(
            "manifest_v1_meta_only",
            f".load-partial {manifest_v1} left=none right=none nameOfNode=none nodeOfName=none manifest={manifest_v1}",
            "ok",
            artifact_kind="manifest",
        ),
        HarnessCase(
            "manifest_v1_left0",
            f".load-partial {manifest_v1} left=0 right=none nameOfNode=none nodeOfName=none manifest={manifest_v1}",
            "fallback_or_ok",
            artifact_kind="manifest",
        ),
        HarnessCase(
            "manifest_v2_meta_only",
            f".load-partial {manifest_v2} left=none right=none nameOfNode=none nodeOfName=none manifest={manifest_v2} shard-root={shard_root}",
            "ok",
            artifact_kind="manifest",
        ),
        HarnessCase(
            "manifest_v2_left0",
            f".load-partial {manifest_v2} left=0 right=none nameOfNode=none nodeOfName=none manifest={manifest_v2} shard-root={shard_root}",
            "fallback_or_ok",
            artifact_kind="manifest",
        ),
    ]

    if include_name_cases:
        cases.extend(
            [
                HarnessCase(
                    "bin_nameOfNode0",
                    f".load-partial {artifact} left=none right=none nameOfNode=0 nodeOfName=none",
                    "ok",
                    artifact_kind="bin",
                ),
                HarnessCase(
                    "manifest_v1_nameOfNode0",
                    f".load-partial {manifest_v1} left=none right=none nameOfNode=0 nodeOfName=none manifest={manifest_v1}",
                    "fallback_or_ok",
                    artifact_kind="manifest",
                ),
                HarnessCase(
                    "manifest_v2_nameOfNode0",
                    f".load-partial {manifest_v2} left=none right=none nameOfNode=0 nodeOfName=none manifest={manifest_v2} shard-root={shard_root}",
                    "fallback_or_ok",
                    artifact_kind="manifest",
                ),
                HarnessCase(
                    "bin_nodeOfName0",
                    f".load-partial {artifact} left=none right=none nameOfNode=none nodeOfName=0",
                    "ok",
                    artifact_kind="bin",
                ),
                HarnessCase(
                    "manifest_v1_nodeOfName0",
                    f".load-partial {manifest_v1} left=none right=none nameOfNode=none nodeOfName=0 manifest={manifest_v1}",
                    "fallback_or_ok",
                    artifact_kind="manifest",
                ),
                HarnessCase(
                    "manifest_v2_nodeOfName0",
                    f".load-partial {manifest_v2} left=none right=none nameOfNode=none nodeOfName=0 manifest={manifest_v2} shard-root={shard_root}",
                    "fallback_or_ok",
                    artifact_kind="manifest",
                ),
                HarnessCase(
                    "bin_left0_nameOfNode0",
                    f".load-partial {artifact} left=0 right=none nameOfNode=0 nodeOfName=none",
                    "ok",
                    artifact_kind="bin",
                ),
                HarnessCase(
                    "manifest_v1_left0_nameOfNode0",
                    f".load-partial {manifest_v1} left=0 right=none nameOfNode=0 nodeOfName=none manifest={manifest_v1}",
                    "fallback_or_ok",
                    artifact_kind="manifest",
                ),
                HarnessCase(
                    "manifest_v2_left0_nameOfNode0",
                    f".load-partial {manifest_v2} left=0 right=none nameOfNode=0 nodeOfName=none manifest={manifest_v2} shard-root={shard_root}",
                    "fallback_or_ok",
                    artifact_kind="manifest",
                ),
            ]
        )

    return cases


def classify_result(artifact: Path, case: HarnessCase, exit_code: int, output: str, elapsed: float) -> HarnessResult:
    had_repl_error = "Error in line" in output
    fallback_used = "falling back to sequential bin load" in output
    ok = exit_code == 0 and not had_repl_error
    if case.expected_mode == "fallback_or_ok":
        ok = ok and (fallback_used or "String pool size after partial load:" in output or "Header-only manifest load complete." in output)

    time_match = TIME_PATTERN.search(output)
    excerpt_lines = [line for line in output.strip().splitlines() if line.strip()]
    excerpt = "\n".join(excerpt_lines[-12:])

    return HarnessResult(
        artifact=str(artifact),
        case=case.name,
        command=case.command,
        expected_mode=case.expected_mode,
        exit_code=exit_code,
        ok=ok,
        fallback_used=fallback_used,
        had_repl_error=had_repl_error,
        wall_time_seconds=round(elapsed, 3),
        reported_partial_time=time_match.group(1) if time_match else None,
        output_excerpt=excerpt,
        fetch_plan=build_fetch_plan(case, artifact),
    )


def write_summary(output_path: Path, results: Iterable[HarnessResult]) -> None:
    payload = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": [asdict(result) for result in results],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def print_console_summary(results: list[HarnessResult]) -> None:
    for result in results:
        mode = "fallback" if result.fallback_used else "direct"
        status = "ok" if result.ok else "error"
        print(
            f"[{status}] {Path(result.artifact).name} :: {result.case} :: mode={mode} :: "
            f"wall={result.wall_time_seconds}s :: partial={result.reported_partial_time or '-'}"
        )


def main() -> int:
    args = parse_args()
    zelph_bin = Path(args.zelph_bin)
    manifest_builder = Path(args.manifest_builder)
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    results: list[HarnessResult] = []

    for artifact_str in args.artifact:
        artifact = Path(artifact_str).resolve()
        artifact_dir = work_dir / artifact.stem
        artifact_dir.mkdir(parents=True, exist_ok=True)

        manifest_v1, manifest_v2, shard_root = build_manifests_for_artifact(
            zelph_bin=zelph_bin,
            manifest_builder=manifest_builder,
            artifact=artifact,
            artifact_dir=artifact_dir,
        )

        for case in build_case_matrix(artifact, manifest_v1, manifest_v2, shard_root, args.include_name_cases):
            exit_code, output, elapsed = run_repl_command(zelph_bin, case.command)
            results.append(classify_result(artifact, case, exit_code, output, elapsed))

    output_json = Path(args.output_json) if args.output_json else work_dir / "summary.json"
    write_summary(output_json, results)
    print_console_summary(results)
    print(f"summary_json={output_json}")

    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
