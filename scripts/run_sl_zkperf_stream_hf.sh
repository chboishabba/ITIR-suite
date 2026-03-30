#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

SL_INPUT=""
SL_DB_PATH="${SL_DB_PATH:-}"
SL_REVIEW_RUN_ID="${SL_REVIEW_RUN_ID:-}"
SL_OUTPUT="${SL_OUTPUT:-}"
SL_CWD="${SL_CWD:-}"
SL_COMMAND=()
RUN_ID="${RUN_ID:-}"
TRACE_ID="${TRACE_ID:-}"
ASSERTED_AT="${ASSERTED_AT:-}"
THEORY_EVIDENCE_JSON="${THEORY_EVIDENCE_JSON:-}"
THEORY_FAMILY="${THEORY_FAMILY:-}"
STREAM_ID="${STREAM_ID:-}"
STREAM_REVISION="${STREAM_REVISION:-}"
CREATED_AT_UTC="${CREATED_AT_UTC:-}"
MAX_OBSERVATIONS_PER_WINDOW="${MAX_OBSERVATIONS_PER_WINDOW:-}"
HF_URI="${HF_URI:-}"
INDEX_HF_URI="${INDEX_HF_URI:-}"
RETAIN_LATEST_N="${RETAIN_LATEST_N:-2}"
COMMIT_MESSAGE=""
OUTPUT_ROOT="${OUTPUT_ROOT:-/tmp/sl-zkperf-stream-run}"
VERIFY_MODE="${VERIFY_MODE:-latest}"
WINDOW_ID="${WINDOW_ID:-}"
SEQUENCE_START="${SEQUENCE_START:-}"
SEQUENCE_END="${SEQUENCE_END:-}"

print_help() {
  cat <<'EOF'
Derive a bounded ZKPerfObservation from an SL payload, then publish -> index -> verify on HF.

Usage:
  scripts/run_sl_zkperf_stream_hf.sh --sl-input PATH [options]
  scripts/run_sl_zkperf_stream_hf.sh --sl-db-path PATH [options]
  scripts/run_sl_zkperf_stream_hf.sh --sl-db-path PATH [options] -- COMMAND [ARGS...]
  scripts/run_sl_zkperf_stream_hf.sh --sl-output PATH [options] -- COMMAND [ARGS...]

Required:
  --sl-input PATH            existing SL JSON payload path
  --sl-db-path PATH          existing SQLite DB for a persisted contested-review run
  --sl-output PATH           output JSON path that the executed SL command will create

Optional:
  --sl-cwd DIR               working directory for the executed SL command
  --sl-review-run-id ID      explicit persisted contested-review run id for --sl-db-path
  --theory-evidence-json PATH
                            optional bounded external theory evidence JSON
  --theory-family NAME       optional family selector for aggregate theory evidence
  --run-id ID                override derived run_id
  --trace-id ID              override derived trace_id
  --asserted-at TS           override derived asserted_at
  --stream-id ID             stream id for generated stream fixture
  --stream-revision ID       stream revision for generated stream fixture
  --created-at-utc TS        createdAtUtc for generated stream fixture
  --max-observations-per-window N
  --hf-uri URI               defaults to a per-stream object under chbwa/itir-zos-ack-probe
  --index-hf-uri URI         defaults to a per-stream index object under chbwa/itir-zos-ack-probe
  --retain-latest-n N
  --commit-message TEXT
  --output-root DIR
  --verify latest|window|range
  --window-id ID
  --sequence-start N
  --sequence-end N
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sl-input)
      SL_INPUT="${2:-}"
      shift 2
      ;;
    --sl-db-path)
      SL_DB_PATH="${2:-}"
      shift 2
      ;;
    --sl-review-run-id)
      SL_REVIEW_RUN_ID="${2:-}"
      shift 2
      ;;
    --sl-output)
      SL_OUTPUT="${2:-}"
      shift 2
      ;;
    --sl-cwd)
      SL_CWD="${2:-}"
      shift 2
      ;;
    --run-id)
      RUN_ID="${2:-}"
      shift 2
      ;;
    --trace-id)
      TRACE_ID="${2:-}"
      shift 2
      ;;
    --asserted-at)
      ASSERTED_AT="${2:-}"
      shift 2
      ;;
    --theory-evidence-json)
      THEORY_EVIDENCE_JSON="${2:-}"
      shift 2
      ;;
    --theory-family)
      THEORY_FAMILY="${2:-}"
      shift 2
      ;;
    --stream-id)
      STREAM_ID="${2:-}"
      shift 2
      ;;
    --stream-revision)
      STREAM_REVISION="${2:-}"
      shift 2
      ;;
    --created-at-utc)
      CREATED_AT_UTC="${2:-}"
      shift 2
      ;;
    --max-observations-per-window)
      MAX_OBSERVATIONS_PER_WINDOW="${2:-}"
      shift 2
      ;;
    --hf-uri)
      HF_URI="${2:-}"
      shift 2
      ;;
    --index-hf-uri)
      INDEX_HF_URI="${2:-}"
      shift 2
      ;;
    --retain-latest-n)
      RETAIN_LATEST_N="${2:-}"
      shift 2
      ;;
    --commit-message)
      COMMIT_MESSAGE="${2:-}"
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT="${2:-}"
      shift 2
      ;;
    --verify)
      VERIFY_MODE="${2:-}"
      shift 2
      ;;
    --window-id)
      WINDOW_ID="${2:-}"
      shift 2
      ;;
    --sequence-start)
      SEQUENCE_START="${2:-}"
      shift 2
      ;;
    --sequence-end)
      SEQUENCE_END="${2:-}"
      shift 2
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    --)
      shift
      SL_COMMAND=("$@")
      break
      ;;
    *)
      echo "Unknown argument: $1" >&2
      print_help >&2
      exit 2
      ;;
  esac
done

if [[ -n "$SL_INPUT" && ( -n "$SL_DB_PATH" || -n "$SL_OUTPUT" ) ]]; then
  echo "Use --sl-input only by itself; do not combine it with --sl-db-path or --sl-output" >&2
  exit 2
fi

if [[ -z "$SL_INPUT" && -z "$SL_DB_PATH" && -z "$SL_OUTPUT" ]]; then
  echo "Missing --sl-input, --sl-db-path, or --sl-output" >&2
  print_help >&2
  exit 2
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing Python interpreter: $PYTHON_BIN" >&2
  exit 1
fi

mkdir -p "$OUTPUT_ROOT"
OBSERVATION_JSON="$OUTPUT_ROOT/generated-zkperf-observation.json"
TRACE_OBSERVATIONS_JSON="$OUTPUT_ROOT/generated-zkperf-trace-observations.json"
STREAM_OBSERVATIONS_JSON="$OUTPUT_ROOT/generated-zkperf-stream-observations.json"

if [[ -n "$SL_INPUT" ]]; then
  if [[ ! -f "$SL_INPUT" ]]; then
    echo "SL input file does not exist: $SL_INPUT" >&2
    exit 1
  fi

  build_args=(
    scripts/build_zkperf_observation_from_sl.py
    --input "$SL_INPUT"
    --output "$OBSERVATION_JSON"
  )
  if [[ -n "$RUN_ID" ]]; then
    build_args+=(--run-id "$RUN_ID")
  fi
  if [[ -n "$TRACE_ID" ]]; then
    build_args+=(--trace-id "$TRACE_ID")
  fi
  if [[ -n "$ASSERTED_AT" ]]; then
    build_args+=(--asserted-at "$ASSERTED_AT")
  fi
  if [[ -n "$THEORY_EVIDENCE_JSON" ]]; then
    build_args+=(--theory-evidence-json "$THEORY_EVIDENCE_JSON")
  fi
  if [[ -n "$THEORY_FAMILY" ]]; then
    build_args+=(--theory-family "$THEORY_FAMILY")
  fi

  (
    cd "$ROOT_DIR"
    "$PYTHON_BIN" "${build_args[@]}"
  )
elif [[ -n "$SL_DB_PATH" && -z "$SL_OUTPUT" && ${#SL_COMMAND[@]} -eq 0 ]]; then
  build_args=(
    scripts/build_zkperf_observation_from_sl.py
    --db-path "$SL_DB_PATH"
    --output "$OBSERVATION_JSON"
  )
  if [[ -n "$SL_REVIEW_RUN_ID" ]]; then
    build_args+=(--review-run-id "$SL_REVIEW_RUN_ID")
  fi
  if [[ -n "$RUN_ID" ]]; then
    build_args+=(--run-id "$RUN_ID")
  fi
  if [[ -n "$TRACE_ID" ]]; then
    build_args+=(--trace-id "$TRACE_ID")
  fi
  if [[ -n "$ASSERTED_AT" ]]; then
    build_args+=(--asserted-at "$ASSERTED_AT")
  fi
  if [[ -n "$THEORY_EVIDENCE_JSON" ]]; then
    build_args+=(--theory-evidence-json "$THEORY_EVIDENCE_JSON")
  fi
  if [[ -n "$THEORY_FAMILY" ]]; then
    build_args+=(--theory-family "$THEORY_FAMILY")
  fi

  (
    cd "$ROOT_DIR"
    "$PYTHON_BIN" "${build_args[@]}"
  )
else
  if [[ ${#SL_COMMAND[@]} -eq 0 ]]; then
    echo "Missing SL command after --" >&2
    print_help >&2
    exit 2
  fi

  run_args=(
    scripts/run_sl_with_zkperf.py
    --sl-output "$SL_OUTPUT"
    --observation-output "$OBSERVATION_JSON"
    --trace-observations-output "$TRACE_OBSERVATIONS_JSON"
    --stream-observations-output "$STREAM_OBSERVATIONS_JSON"
  )
  if [[ -n "$SL_DB_PATH" ]]; then
    run_args+=(--sl-db-path "$SL_DB_PATH")
  fi
  if [[ -n "$SL_REVIEW_RUN_ID" ]]; then
    run_args+=(--sl-review-run-id "$SL_REVIEW_RUN_ID")
  fi
  if [[ -n "$SL_CWD" ]]; then
    run_args+=(--cwd "$SL_CWD")
  fi
  if [[ -n "$RUN_ID" ]]; then
    run_args+=(--run-id "$RUN_ID")
  fi
  if [[ -n "$TRACE_ID" ]]; then
    run_args+=(--trace-id "$TRACE_ID")
  fi
  if [[ -n "$ASSERTED_AT" ]]; then
    run_args+=(--asserted-at "$ASSERTED_AT")
  fi
  if [[ -n "$THEORY_EVIDENCE_JSON" ]]; then
    run_args+=(--theory-evidence-json "$THEORY_EVIDENCE_JSON")
  fi
  if [[ -n "$THEORY_FAMILY" ]]; then
    run_args+=(--theory-family "$THEORY_FAMILY")
  fi
  run_args+=(-- "${SL_COMMAND[@]}")

  (
    cd "$ROOT_DIR"
    "$PYTHON_BIN" "${run_args[@]}"
  )
fi

if [[ -z "$STREAM_ID" ]]; then
  STREAM_ID="$(python - <<'PY' "$OBSERVATION_JSON"
import json, sys
payload = json.load(open(sys.argv[1]))
run_id = str(payload.get("run_id") or "sl-zkperf")
chars = [c.lower() if c.isalnum() else "-" for c in run_id]
slug = "".join(chars).strip("-")
while "--" in slug:
    slug = slug.replace("--", "-")
print(f"zkperf-stream-{slug or 'sl-zkperf'}")
PY
)"
fi

if [[ -z "$HF_URI" ]]; then
  HF_URI="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/${STREAM_ID}.tar"
fi

if [[ -z "$INDEX_HF_URI" ]]; then
  INDEX_HF_URI="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/${STREAM_ID}.index.json"
fi

stream_args=(
  scripts/run_zkperf_stream_hf.sh
  --observations "$OBSERVATION_JSON"
  --hf-uri "$HF_URI"
  --index-hf-uri "$INDEX_HF_URI"
  --retain-latest-n "$RETAIN_LATEST_N"
  --output-root "$OUTPUT_ROOT"
  --verify "$VERIFY_MODE"
)
if [[ -s "$STREAM_OBSERVATIONS_JSON" ]]; then
  stream_args[2]="$STREAM_OBSERVATIONS_JSON"
fi
if [[ -n "$STREAM_ID" ]]; then
  stream_args+=(--stream-id "$STREAM_ID")
fi
if [[ -n "$STREAM_REVISION" ]]; then
  stream_args+=(--stream-revision "$STREAM_REVISION")
fi
if [[ -n "$CREATED_AT_UTC" ]]; then
  stream_args+=(--created-at-utc "$CREATED_AT_UTC")
fi
if [[ -n "$MAX_OBSERVATIONS_PER_WINDOW" ]]; then
  stream_args+=(--max-observations-per-window "$MAX_OBSERVATIONS_PER_WINDOW")
fi
if [[ -n "$COMMIT_MESSAGE" ]]; then
  stream_args+=(--commit-message "$COMMIT_MESSAGE")
fi
if [[ -n "$WINDOW_ID" ]]; then
  stream_args+=(--window-id "$WINDOW_ID")
fi
if [[ -n "$SEQUENCE_START" ]]; then
  stream_args+=(--sequence-start "$SEQUENCE_START")
fi
if [[ -n "$SEQUENCE_END" ]]; then
  stream_args+=(--sequence-end "$SEQUENCE_END")
fi

(
  cd "$ROOT_DIR"
  "${stream_args[@]}"
)
