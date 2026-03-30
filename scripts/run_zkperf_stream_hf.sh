#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"

FIXTURE=""
OBSERVATIONS=""
STREAM_ID="${STREAM_ID:-}"
STREAM_REVISION="${STREAM_REVISION:-}"
CREATED_AT_UTC="${CREATED_AT_UTC:-}"
MAX_OBSERVATIONS_PER_WINDOW="${MAX_OBSERVATIONS_PER_WINDOW:-}"
HF_URI="${HF_URI:-}"
INDEX_HF_URI="${INDEX_HF_URI:-}"
RETAIN_LATEST_N="${RETAIN_LATEST_N:-2}"
COMMIT_MESSAGE=""
OUTPUT_ROOT="${OUTPUT_ROOT:-/tmp/zkperf-stream-run}"
VERIFY_MODE="${VERIFY_MODE:-latest}"
WINDOW_ID="${WINDOW_ID:-}"
SEQUENCE_START="${SEQUENCE_START:-}"
SEQUENCE_END="${SEQUENCE_END:-}"

print_help() {
  cat <<'EOF'
Run one zkperf stream publish -> HF -> index -> read-back verification cycle.

Usage:
  scripts/run_zkperf_stream_hf.sh --fixture PATH [options]
  scripts/run_zkperf_stream_hf.sh --observations PATH [options]

Required:
  --fixture PATH              zkperf stream JSON fixture to publish
  --observations PATH         raw ZKPerfObservation JSON/NDJSON to convert then publish

Optional:
  --stream-id ID             optional stream id for generated fixture
  --stream-revision ID       optional stream revision for generated fixture
  --created-at-utc TS        optional createdAtUtc for generated fixture
  --max-observations-per-window N
                              optional chunk size for generated fixture
  --hf-uri URI               HF tar object URI
  --index-hf-uri URI         HF index object URI
  --retain-latest-n N        active index retention count
  --commit-message TEXT      HF commit message
  --output-root DIR          local artifact output root
  --verify latest            verify latest window from HF index
  --verify window            verify one explicit window from HF index
  --verify range             verify a sequence range from HF index
  --window-id ID             required for --verify window
  --sequence-start N         used by --verify range
  --sequence-end N           used by --verify range

Environment overrides:
  PYTHON_BIN
  STREAM_ID
  STREAM_REVISION
  CREATED_AT_UTC
  MAX_OBSERVATIONS_PER_WINDOW
  HF_URI
  INDEX_HF_URI
  RETAIN_LATEST_N
  OUTPUT_ROOT
  VERIFY_MODE
  WINDOW_ID
  SEQUENCE_START
  SEQUENCE_END
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fixture)
      FIXTURE="${2:-}"
      shift 2
      ;;
    --observations)
      OBSERVATIONS="${2:-}"
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
    *)
      echo "Unknown argument: $1" >&2
      print_help >&2
      exit 2
      ;;
  esac
done

if [[ -n "$FIXTURE" && -n "$OBSERVATIONS" ]]; then
  echo "Use either --fixture or --observations, not both" >&2
  exit 2
fi

if [[ -z "$FIXTURE" && -z "$OBSERVATIONS" ]]; then
  echo "Missing --fixture or --observations" >&2
  print_help >&2
  exit 2
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing Python interpreter: $PYTHON_BIN" >&2
  exit 1
fi

mkdir -p "$OUTPUT_ROOT"
PIPELINE_STARTED_MS="$(date +%s%3N)"
OBSERVATION_JSON=""

if [[ -n "$OBSERVATIONS" ]]; then
  OBSERVATION_JSON="$OBSERVATIONS"
  GENERATED_FIXTURE="$OUTPUT_ROOT/generated-zkperf-stream.json"
  build_args=(
    scripts/build_zkperf_stream_fixture.py
    --input "$OBSERVATIONS"
    --output "$GENERATED_FIXTURE"
  )
  if [[ -n "$STREAM_ID" ]]; then
    build_args+=(--stream-id "$STREAM_ID")
  fi
  if [[ -n "$STREAM_REVISION" ]]; then
    build_args+=(--stream-revision "$STREAM_REVISION")
  fi
  if [[ -n "$CREATED_AT_UTC" ]]; then
    build_args+=(--created-at-utc "$CREATED_AT_UTC")
  fi
  if [[ -n "$MAX_OBSERVATIONS_PER_WINDOW" ]]; then
    build_args+=(--max-observations-per-window "$MAX_OBSERVATIONS_PER_WINDOW")
  fi
  STREAM_FIXTURE_BUILD_STARTED_MS="$(date +%s%3N)"
  set +e
  (
    cd "$ROOT_DIR"
    "$PYTHON_BIN" "${build_args[@]}"
  )
  build_status=$?
  set -e
  STREAM_FIXTURE_BUILD_MS="$(( $(date +%s%3N) - STREAM_FIXTURE_BUILD_STARTED_MS ))"
  if [[ $build_status -ne 0 ]]; then
    exit "$build_status"
  fi
  FIXTURE="$GENERATED_FIXTURE"
else
  STREAM_FIXTURE_BUILD_MS=""
fi

if [[ -z "$STREAM_ID" ]]; then
  STREAM_ID="$("$PYTHON_BIN" - <<'PY' "$FIXTURE"
import json
import sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["streamId"])
PY
)"
fi

if [[ -z "$HF_URI" ]]; then
  HF_URI="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/${STREAM_ID}.tar"
fi

if [[ -z "$INDEX_HF_URI" ]]; then
  INDEX_HF_URI="hf://datasets/chbwa/itir-zos-ack-probe/zkperf-stream/${STREAM_ID}.index.json"
fi

PUBLISH_JSON="$OUTPUT_ROOT/publish.json"
VERIFY_JSON="$OUTPUT_ROOT/verify.json"

publish_args=(
  -m itir_jmd_bridge
  publish-zkperf-stream-hf
  --fixture "$FIXTURE"
  --hf-uri "$HF_URI"
  --index-hf-uri "$INDEX_HF_URI"
  --retain-latest-n "$RETAIN_LATEST_N"
  --artifact-output-root "$OUTPUT_ROOT"
  --output "$PUBLISH_JSON"
)

if [[ -n "$COMMIT_MESSAGE" ]]; then
  publish_args+=(--commit-message "$COMMIT_MESSAGE")
fi

PUBLISH_STARTED_MS="$(date +%s%3N)"
set +e
(
  cd "$ROOT_DIR"
  "$PYTHON_BIN" "${publish_args[@]}"
)
publish_status=$?
set -e
PUBLISH_WALL_MS="$(( $(date +%s%3N) - PUBLISH_STARTED_MS ))"
if [[ $publish_status -ne 0 ]]; then
  exit "$publish_status"
fi

verify_args=(
  -m itir_jmd_bridge
  resolve-zkperf-stream-from-index-hf
  --fixture "$FIXTURE"
  --index-hf-uri "$INDEX_HF_URI"
  --output "$VERIFY_JSON"
)

case "$VERIFY_MODE" in
  latest)
    verify_args+=(--latest)
    ;;
  window)
    if [[ -z "$WINDOW_ID" ]]; then
      echo "--verify window requires --window-id" >&2
      exit 2
    fi
    verify_args+=(--latest --window-id "$WINDOW_ID")
    ;;
  range)
    if [[ -z "$SEQUENCE_START" && -z "$SEQUENCE_END" ]]; then
      echo "--verify range requires --sequence-start and/or --sequence-end" >&2
      exit 2
    fi
    verify_args+=(--latest)
    if [[ -n "$SEQUENCE_START" ]]; then
      verify_args+=(--sequence-start "$SEQUENCE_START")
    fi
    if [[ -n "$SEQUENCE_END" ]]; then
      verify_args+=(--sequence-end "$SEQUENCE_END")
    fi
    ;;
  *)
    echo "Unsupported --verify mode: $VERIFY_MODE" >&2
    exit 2
    ;;
esac

VERIFY_STARTED_MS="$(date +%s%3N)"
set +e
(
  cd "$ROOT_DIR"
  "$PYTHON_BIN" "${verify_args[@]}"
)
verify_status=$?
set -e
VERIFY_WALL_MS="$(( $(date +%s%3N) - VERIFY_STARTED_MS ))"
if [[ $verify_status -ne 0 ]]; then
  exit "$verify_status"
fi

"$PYTHON_BIN" - <<'PY' "$PUBLISH_JSON" "$VERIFY_JSON"
import json
import sys
publish = json.load(open(sys.argv[1]))
verify = json.load(open(sys.argv[2]))
stream_manifest = publish["streamManifest"]
stream_index = publish.get("streamIndex", {})
stream_latest = publish.get("streamLatest", {})
print("stream_id:", stream_manifest["streamId"])
print("stream_revision:", stream_manifest["streamRevision"])
print("tar_ack:", publish["hfReceipt"]["acknowledgedRevision"])
if "streamIndexReceipt" in publish:
    print("index_ack:", publish["streamIndexReceipt"]["acknowledgedRevision"])
print("latest_revision:", stream_index.get("latestRevision", stream_latest.get("latestRevision")))
print("latest_window:", stream_index.get("latestWindowId", stream_latest.get("latestWindowId")))
if "windows" in verify and verify["windows"]:
    print("verified_window:", verify["windows"][0]["window"]["windowId"])
    obs = verify["windows"][0]["payload"]["json"]["observations"][0]["zkperf_observation_id"]
    print("verified_observation:", obs)
elif "window" in verify:
    print("verified_window:", verify["window"]["windowId"])
    obs = verify["payload"]["json"]["observations"][0]["zkperf_observation_id"]
    print("verified_observation:", obs)
print("publish_json:", sys.argv[1])
print("verify_json:", sys.argv[2])
PY

TIMINGS_JSON="$OUTPUT_ROOT/timings.json"
"$PYTHON_BIN" - <<'PY' "$OBSERVATION_JSON" "$PUBLISH_JSON" "$VERIFY_JSON" "$TIMINGS_JSON" "$PIPELINE_STARTED_MS" "$STREAM_FIXTURE_BUILD_MS" "$PUBLISH_WALL_MS" "$VERIFY_WALL_MS"
import json
import sys
import time
from pathlib import Path

observation_path = Path(sys.argv[1])
publish_path = Path(sys.argv[2])
verify_path = Path(sys.argv[3])
timings_path = Path(sys.argv[4])
pipeline_started_ms = int(sys.argv[5])
stream_fixture_build_ms = sys.argv[6]
publish_wall_ms = int(sys.argv[7])
verify_wall_ms = int(sys.argv[8])

publish = json.loads(publish_path.read_text(encoding="utf-8"))
verify = json.loads(verify_path.read_text(encoding="utf-8"))
observation = (
    json.loads(observation_path.read_text(encoding="utf-8"))
    if observation_path.as_posix()
    else None
)

if isinstance(observation, list):
    summary_candidates = [
        row for row in observation
        if isinstance(row, dict)
        and any(
            isinstance(metric, dict) and metric.get("metric") == "elapsed_ms"
            for metric in row.get("metrics", [])
        )
    ]
    observation = summary_candidates[-1] if summary_candidates else (observation[-1] if observation else None)

def metric_map(payload):
    if not isinstance(payload, dict):
        return {}
    return {row["metric"]: row["value"] for row in payload.get("metrics", []) if isinstance(row, dict) and "metric" in row}

timings = {
    "wrapperTotalMs": int(round(time.time() * 1000)) - pipeline_started_ms,
    "streamFixtureBuildMs": int(stream_fixture_build_ms) if stream_fixture_build_ms else None,
    "publishWallMs": publish_wall_ms,
    "verifyWallMs": verify_wall_ms,
    "observationElapsedMs": metric_map(observation).get("elapsed_ms") if observation else None,
    "publishTimings": publish.get("timings"),
    "verifyTimings": verify.get("timings"),
    "pipelineStartedMs": pipeline_started_ms,
}
timings_path.write_text(json.dumps(timings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("timings_json:", timings_path)
PY
