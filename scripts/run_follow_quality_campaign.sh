#!/usr/bin/env bash
set -euo pipefail

PY="${PY:-.venv/bin/python}"
RUNS="${RUNS:-1}"
COUNT="${COUNT:-8}"
FOLLOW_HOPS="${FOLLOW_HOPS:-2}"
MAX_FOLLOW_LINKS_PER_PAGE="${MAX_FOLLOW_LINKS_PER_PAGE:-2}"
MAX_LINKS="${MAX_LINKS:-30}"
MAX_CATEGORIES="${MAX_CATEGORIES:-30}"
TIMEOUT_S="${TIMEOUT_S:-60}"
WIKI_RPS="${WIKI_RPS:-0.25}"
OUT_ROOT="${OUT_ROOT:-/tmp/wiki_follow_quality_campaign}"
EMIT_PAGE_ROWS="${EMIT_PAGE_ROWS:-1}"
NO_SPACY="${NO_SPACY:-1}"

mkdir -p "$OUT_ROOT"

run_index=1
while [ "$run_index" -le "$RUNS" ]; do
  run_dir="$(printf "%s/run_%02d" "$OUT_ROOT" "$run_index")"
  manifest="$run_dir/manifest.json"
  report="$run_dir/report.json"
  samples="$run_dir/samples"
  mkdir -p "$run_dir"

  echo "[run $run_index/$RUNS] Generating multi-hop manifest"
  "$PY" SensibLaw/scripts/wiki_random_page_samples.py \
    --count "$COUNT" \
    --namespace 0 \
    --out-dir "$samples" \
    --out-manifest "$manifest" \
    --follow-hops "$FOLLOW_HOPS" \
    --max-follow-links-per-page "$MAX_FOLLOW_LINKS_PER_PAGE" \
    --max-links "$MAX_LINKS" \
    --max-categories "$MAX_CATEGORIES" \
    --timeout-s "$TIMEOUT_S" \
    --wiki-rps "$WIKI_RPS"

  echo "[run $run_index/$RUNS] Scoring manifest"
  score_args=(
    SensibLaw/scripts/report_wiki_random_article_ingest_coverage.py
    --manifest "$manifest"
    --output "$report"
  )
  if [ "$EMIT_PAGE_ROWS" = "1" ]; then
    score_args+=(--emit-page-rows)
  fi
  if [ "$NO_SPACY" = "1" ]; then
    score_args+=(--no-spacy)
  fi
  "$PY" "${score_args[@]}"

  echo "[run $run_index/$RUNS] Run summary"
  "$PY" - <<PY
import json, pathlib
path = pathlib.Path("$report")
report = json.loads(path.read_text())
summary = report["summary"]
print("report", path)
print("page_count", summary["page_count"])
print("dominant_regime_counts", summary.get("dominant_regime_counts"))
print("average_follow_yield_metrics", summary.get("average_follow_yield_metrics"))
print("average_two_hop_metrics", summary.get("average_two_hop_metrics"))
print("average_best_path_metrics", summary.get("average_best_path_metrics"))
print("follow_failure_bucket_counts", summary.get("follow_failure_bucket_counts"))
missing = [page["title"] for page in report.get("pages", []) if "snapshot_missing_wikitext" in page.get("issues", [])]
print("snapshot_missing_wikitext_count", len(missing))
if missing:
    print("snapshot_missing_wikitext_titles", missing[:10])
PY

  run_index=$((run_index + 1))
done

aggregate="$OUT_ROOT/aggregate_summary.json"
echo "[aggregate] Collating reports under $OUT_ROOT"
"$PY" SensibLaw/scripts/analyze_follow_quality_reports.py \
  "$OUT_ROOT" \
  --worst-limit 15 \
  --output "$aggregate"

echo "[done] aggregate summary written to $aggregate"
