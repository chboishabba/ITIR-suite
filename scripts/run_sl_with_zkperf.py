#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from itir_jmd_bridge.sl_zkperf import (
    build_zkperf_observation_from_contested_review_db,
    build_zkperf_observation_from_sl_file,
    build_zkperf_trace_observations_from_progress_log,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute an SL-producing command, capture bounded runtime metrics, and emit a ZKPerfObservation."
    )
    parser.add_argument("--sl-output", type=Path, help="Path to the JSON payload the SL command should produce when using artifact-backed mode")
    parser.add_argument("--sl-db-path", type=Path, help="Optional SQLite path for persisted contested-review runs; when provided, zkperf uses the DB/read-model surface instead of requiring bulky JSON artifacts")
    parser.add_argument("--sl-review-run-id", help="Optional explicit contested review run id to read from --sl-db-path; defaults to the latest persisted run")
    parser.add_argument("--theory-evidence-json", type=Path, help="Optional path to bounded external theory evidence JSON, such as ../dashi_agda regime-test artifacts")
    parser.add_argument("--theory-family", help="Optional family name to select from aggregate theory evidence JSON")
    parser.add_argument("--observation-output", type=Path, required=True, help="Where to write the derived ZKPerfObservation JSON")
    parser.add_argument("--trace-observations-output", type=Path, help="Where to write stepwise trace observations derived from CLI progress events")
    parser.add_argument("--stream-observations-output", type=Path, help="Where to write the observation list used for stream publication; combines trace observations with the final summary observation")
    parser.add_argument("--cwd", type=Path, help="Working directory for the executed command")
    parser.add_argument("--stdout-path", type=Path, help="Where to write captured stdout")
    parser.add_argument("--stderr-path", type=Path, help="Where to write captured stderr")
    parser.add_argument("--run-id")
    parser.add_argument("--trace-id")
    parser.add_argument("--asserted-at")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to execute after --")
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("missing command to execute; pass it after --")
    if args.sl_output is None and args.sl_db_path is None:
        raise SystemExit("must provide --sl-output or --sl-db-path")

    cwd = args.cwd.resolve() if args.cwd else ROOT_DIR
    stdout_path = (args.stdout_path or args.observation_output.with_suffix(".stdout.log")).resolve()
    stderr_path = (args.stderr_path or args.observation_output.with_suffix(".stderr.log")).resolve()
    trace_observations_output = (
        args.trace_observations_output.resolve()
        if args.trace_observations_output
        else None
    )
    stream_observations_output = (
        args.stream_observations_output.resolve()
        if args.stream_observations_output
        else None
    )
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    args.observation_output.parent.mkdir(parents=True, exist_ok=True)
    if trace_observations_output is not None:
        trace_observations_output.parent.mkdir(parents=True, exist_ok=True)
    if stream_observations_output is not None:
        stream_observations_output.parent.mkdir(parents=True, exist_ok=True)

    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start_monotonic = time.perf_counter()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=False,
        )
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    elapsed_ms = int(round((time.perf_counter() - start_monotonic) * 1000))
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)

    if completed.returncode != 0:
        raise SystemExit(
            f"SL command failed with exit code {completed.returncode}; see {stderr_path}"
        )
    if args.sl_db_path is None and (args.sl_output is None or not args.sl_output.exists()):
        raise SystemExit(f"SL output file was not created: {args.sl_output}")

    runtime_metrics = [
        {"metric": "elapsed_ms", "value": elapsed_ms, "unit": "milliseconds"},
        {"metric": "exit_code", "value": completed.returncode, "unit": "status"},
        {"metric": "child_user_cpu_seconds", "value": _usage_delta(usage_after.ru_utime, usage_before.ru_utime), "unit": "seconds"},
        {"metric": "child_system_cpu_seconds", "value": _usage_delta(usage_after.ru_stime, usage_before.ru_stime), "unit": "seconds"},
        {"metric": "max_rss_kb", "value": max(usage_after.ru_maxrss, usage_before.ru_maxrss), "unit": "kilobytes"},
        {"metric": "stdout_bytes", "value": stdout_path.stat().st_size, "unit": "bytes"},
        {"metric": "stderr_bytes", "value": stderr_path.stat().st_size, "unit": "bytes"},
    ]
    runtime_metrics.extend(_usage_delta_metrics(usage_before, usage_after))
    extra_trace_refs = [
        {"kind": "sl_stdout_path", "ref": str(stdout_path)},
        {"kind": "sl_stderr_path", "ref": str(stderr_path)},
        {"kind": "sl_execution_window", "ref": json.dumps({"startedAtUtc": started_at, "finishedAtUtc": finished_at}, sort_keys=True)},
        {"kind": "sl_command", "ref": json.dumps(command, ensure_ascii=True)},
        {"kind": "sl_observation_role", "ref": "summary"},
    ]

    if args.sl_db_path is not None:
        observation = build_zkperf_observation_from_contested_review_db(
            args.sl_db_path,
            review_run_id=args.sl_review_run_id,
            run_id=args.run_id,
            trace_id=args.trace_id,
            asserted_at=args.asserted_at or finished_at,
            runtime_metrics=runtime_metrics,
            extra_trace_refs=extra_trace_refs,
            theory_evidence_path=args.theory_evidence_json,
            theory_family=args.theory_family,
        )
    else:
        observation = build_zkperf_observation_from_sl_file(
            args.sl_output,
            run_id=args.run_id,
            trace_id=args.trace_id,
            asserted_at=args.asserted_at or finished_at,
            runtime_metrics=runtime_metrics,
            extra_trace_refs=extra_trace_refs,
            theory_evidence_path=args.theory_evidence_json,
            theory_family=args.theory_family,
        )
    args.observation_output.write_text(json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    trace_observations = build_zkperf_trace_observations_from_progress_log(
        stderr_path,
        run_id=str(observation["run_id"]),
        trace_id=str(observation["trace_id"]),
        started_at=started_at,
        finished_at=finished_at,
        sl_output_path=args.sl_output if args.sl_output is not None else None,
        sl_db_path=args.sl_db_path if args.sl_db_path is not None else None,
        command=command,
    )
    if trace_observations_output is not None and trace_observations:
        trace_observations_output.write_text(
            json.dumps(trace_observations, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if stream_observations_output is not None:
        stream_payload = [*trace_observations, observation] if trace_observations else [observation]
        stream_observations_output.write_text(
            json.dumps(stream_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(args.observation_output)
    if trace_observations_output is not None and trace_observations:
        print(trace_observations_output)
    if stream_observations_output is not None:
        print(stream_observations_output)
    return 0


def _usage_delta(after: float, before: float) -> float:
    return round(max(after - before, 0.0), 6)


def _usage_delta_metrics(before: resource.struct_rusage, after: resource.struct_rusage) -> list[dict[str, object]]:
    specs = [
        ("ru_minflt", "minor_page_faults", "count"),
        ("ru_majflt", "major_page_faults", "count"),
        ("ru_nvcsw", "voluntary_context_switches", "count"),
        ("ru_nivcsw", "involuntary_context_switches", "count"),
        ("ru_inblock", "block_input_ops", "count"),
        ("ru_oublock", "block_output_ops", "count"),
        ("ru_msgsnd", "ipc_messages_sent", "count"),
        ("ru_msgrcv", "ipc_messages_received", "count"),
        ("ru_nsignals", "signals_received", "count"),
        ("ru_nswap", "swaps", "count"),
    ]
    metrics: list[dict[str, object]] = []
    for attr_name, metric_name, unit in specs:
        before_value = getattr(before, attr_name, None)
        after_value = getattr(after, attr_name, None)
        if before_value is None or after_value is None:
            continue
        delta = max(int(after_value) - int(before_value), 0)
        metrics.append({"metric": metric_name, "value": delta, "unit": unit})
    return metrics


if __name__ == "__main__":
    raise SystemExit(main())
