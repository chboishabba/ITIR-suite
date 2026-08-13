#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Keep this suite dependency-light: it should run even when the full SensibLaw
# test tree requires optional extras (pdfminer, hypothesis, etc).
python -m unittest \
  SensibLaw.tests_minimal.test_wiki_timeline_aoo_extract_pronoun_fallback \
  SensibLaw.tests_minimal.test_gwb_corpus_timeline_build_filters \
  SensibLaw.tests_minimal.test_wiki_timeline_no_semantic_regex_regressions

(
  cd itir-svelte
  node --test tests/*.test.js
)
