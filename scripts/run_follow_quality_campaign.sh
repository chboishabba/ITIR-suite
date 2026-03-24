#!/usr/bin/env bash
set -euo pipefail

PY=".venv/bin/python"
MANIFEST="/tmp/wiki_random_manifest_large.json"
REPORT="/tmp/wiki_random_article_ingest_report_large.json"
SAMPLES="/tmp/wiki_random_samples_large"

echo "[1/4] Generating multi-hop manifest"
$PY SensibLaw/scripts/wiki_random_page_samples.py \
  --count 8 \
  --namespace 0 \
  --out-dir "$SAMPLES" \
  --out-manifest "$MANIFEST" \
  --follow-hops 2 \
  --max-follow-links-per-page 2 \
  --max-links 30 \
  --max-categories 30 \
  --timeout-s 60 \
  --wiki-rps 0.25

echo "[2/4] Scoring the manifest"
$PY SensibLaw/scripts/report_wiki_random_article_ingest_coverage.py \
  --manifest "$MANIFEST" \
  --output "$REPORT" \
  --emit-page-rows \
  --no-spacy

echo "[3/4] Summary metrics"
$PY - <<'PY'
import json, pathlib
path = pathlib.Path("/tmp/wiki_random_article_ingest_report_large.json")
report = json.loads(path.read_text())
summary = report["summary"]
print("page_count", summary["page_count"])
print("dominant_regime_counts", summary["dominant_regime_counts"])
print("average_follow_yield_metrics", summary["average_follow_yield_metrics"])
print("average_two_hop_metrics", summary["average_two_hop_metrics"])
print("average_best_path_metrics", summary["average_best_path_metrics"])
missing = [page["title"] for page in report.get("pages", []) if "snapshot_missing_wikitext" in page.get("issues", [])]
print("snapshot_missing_wikitext_count", len(missing))
if missing:
    print("snapshot_missing_wikitext_titles", missing[:10])
PY

echo "[4/4] Worst follow targets"
$PY - <<'PY'
import heapq, json, pathlib
report = json.loads(pathlib.Path("/tmp/wiki_random_article_ingest_report_large.json").read_text())
heap = []
for page in report.get("pages", []):
    title = page["title"]
    for detail in page.get("follow_target_quality_details") or []:
        score = detail["follow_target_quality_score"]
        heapq.heappush(heap, (score, title, detail))
        if len(heap) > 5:
            heapq.heappop(heap)
while heap:
    score, title, detail = heapq.heappop(heap)
    print(f"{score:.6f} {title}: richness={detail['richness_score']:.3f} non-list={detail['non_list_score']:.3f} regime={detail['regime_similarity_score']:.3f} info={detail['information_gain_score']:.3f}")
PY
