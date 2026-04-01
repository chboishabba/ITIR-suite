# Mirror Telegram Support-Layer Boundary

## Purpose
Record the current ITIR position for the Mirror Telegram integration so the
suite does not drift into claiming that ITIR should own top-level Telegram
routing.

## Source Basis
- sibling product docs under
  `/home/c/Documents/code/mirror_community_mgr/docs/`:
  - `MIRROR_AI_ITIR_INTEGRATION_CONTRACT.md`
  - `MIRROR_AI_ITIR_PHASE1_TOOL_MAP.md`
  - `MIRROR_AI_CORE_AI_API_CONTRACT.md`
- existing ITIR planning doctrine:
  - `docs/planning/hca_case_s942025_ingest_followups_20260211.md`
  - `docs/planning/priority_execution_sequence_20260306.md`
  - `docs/planning/wiki_timeline_extraction_gwb_20260211.md`
  - `docs/planning/assumption_stress_test_20260208.md`
- local archive follow-up:
  Telegram-related chats are now present in `~/chat_archive.sqlite`; local
  resolver checks on `2026-04-01` confirmed DB-side candidate coverage even
  though this pass did not resolve one single canonical thread title for the
  Mirror Telegram discussion.

## Decision
ITIR should not be the top-level Telegram routing authority for Mirror.

ITIR should instead act as the support layer that de-brittles the routing
substrate under Mirror's locally owned router.

Mirror keeps:
- product routing ownership
- user-facing policy ownership
- final route decisions

ITIR contributes:
- normalization
- semantic disambiguation
- parser/model lanes
- provenance and fallback labeling
- reviewable support outputs

Core AI remains a downstream execution surface, not the route owner.

## Why
The brittle part of the current Mirror Telegram surface is not that there is a
router. The brittle part is that semantic classification is still too close to
substring gates, ad hoc keyword lists, and unlabeled fallback logic.

That shape conflicts with repeated ITIR doctrine:
- parser first where structure is available
- deterministic tokenizer or lexeme handling ahead of broad regex expansion
- explicit warning labels on fallback behavior
- fixture-backed lexical-noise and assumption stress tests
- reviewable, provenance-bearing outputs rather than silent heuristic jumps

## Intended Lane Split

### 1. Ingest lane
Normalize Telegram text and event context into a canonical event envelope:
- message text
- punctuation and casing normalization
- mentions and commands
- reply or thread context
- attachment summary
- conversation metadata

### 2. Token or lexeme lane
Produce deterministic tokenization so short forms, punctuation variation,
hyphenation, and casing changes do not become accidental routing defects.

### 3. Parser-first lane
Derive structural features such as:
- greeting shape
- request shape
- quoted accusation or allegation shape
- disclosure cue
- admin intent
- market-query form
- ambiguity flags

### 4. Fallback lane
Keep regex and keyword heuristics only as bounded fallback hygiene, with:
- explicit fallback labels
- rule identifiers
- version metadata

### 5. Logic-model lane
Emit typed observations such as:
- direct_contact
- simple_crypto_question_candidate
- realtime_data_candidate
- protected_disclosure_candidate
- off_topic_candidate

These should carry confidence or conflict markers rather than pretending to be
silent truth.

### 6. Provenance lane
Attach:
- source spans where practical
- rule ids
- tokenizer or parser version
- fallback reason
- policy profile hash

### 7. Router lane
Mirror consumes the support envelope and still decides:
- ignore
- quick FAQ reply
- community reply
- route to Core AI
- admin only
- later, protected disclosure or human handoff

If ITIR support fails, Mirror must still be able to route. ITIR is support,
not authority.

## ZKP Frame

### O
- Mirror owns product routing and user-facing policy.
- ITIR owns normalization, disambiguation, parse/model lanes, provenance, and
  reviewable support outputs.
- Core AI remains downstream execution, not route selection.

### R
- reduce brittle lexical routing without turning Telegram into an opaque agent
  loop
- keep semantic disambiguation explicit, typed, versioned, and test-gated

### C
- the current brittle surface is the Telegram classifier and related routing
  heuristics in the sibling Mirror repo
- the ITIR-side pattern is tokenizer or parser first, regex only as labeled
  fallback, with fixtures and receipts

### S
- Mirror currently uses substring-heavy gates and blocklist-style checks
- ITIR doctrine prefers deterministic token streams, parser-first structure,
  fallback reasons, regression fixtures, and fail-closed gates
- therefore the right integration is not "let ITIR decide replies"; it is
  "let ITIR produce better structured evidence for Mirror's router"

### L
- brittle lexical rules
- normalized token and phrase lanes
- parser-backed semantic features
- typed support outputs with provenance
- policy-reviewed router decisions on top

### P
Implement an ITIR-shaped support envelope between Telegram ingest and Mirror
route selection.

### G
- ITIL:
  separate service design from service operation so heuristic defects are
  visible and governable
- ISO 9001:
  requirements, evidence, and change control stay auditable because each lane
  is explicit and testable
- ISO 42001:
  human oversight remains with Mirror and the AI-adjacent support logic stays
  bounded and transparent
- ISO 27001:
  sensitive classifications can be handled as controlled, minimization-aware
  outputs with explicit gates
- Six Sigma:
  collision cases, false positives, false negatives, and fallback frequency
  become measurable defect classes
- C4:
  ITIR belongs under the router as a support component, not as the product
  brain

### F
Missing today:
- a canonical token or lexeme layer for Telegram text
- typed semantic observations instead of raw keyword gates
- fallback labeling and provenance on classifier outcomes
- lexical-noise and collision fixture suites as merge gates
- a reviewed policy profile for protected-disclosure detection

## Immediate Next Step
Write a short classifier-hardening spec in the Mirror repo that replaces the
current lexical classifier with an ITIR-shaped support envelope and explicitly
separates:
- tokenizer lane
- parser lane
- fallback lane
- provenance lane
- router consumption contract
