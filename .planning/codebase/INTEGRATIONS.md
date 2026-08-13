# External Integrations

**Analysis Date:** 2026-03-06

## APIs & External Services

**Payment Processing:**
- Not detected

**Email/SMS:**
- Not detected

**External APIs:**
- ChatGPT (chatgpt.com) reverse-engineered client (unofficial; brittle/gray-area): `reverse-engineered-chatgpt/re_gpt/async_chatgpt.py`, `reverse-engineered-chatgpt/re_gpt/sync_chatgpt.py`
- Google NotebookLM automation client (unofficial; uses undocumented RPC/batchexecute): `notebooklm-py/CLAUDE.md`, `notebooklm-py/pyproject.toml`

## Data Storage

**Databases:**
- SQLite - used as a local persistence layer in multiple components:
  - WhisperX-WebUI backend DB default: `WhisperX-WebUI/backend/configs/.env.example`
  - tircorder Rust uses bundled SQLite via rusqlite: `tircorder-JOBBIE/Cargo.toml`
  - itir-svelte dashboards/caches (queried via Python): `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/lib/server/wikiTimelineAoo.ts`, `itir-svelte/src/lib/server/buildMissingDashboardsJob.ts`

**File Storage:**
- Not detected (no S3/GCS/Azure storage SDKs surfaced in this scan)

**Caching:**
- Not detected (no Redis/memcached surfaced in this scan)

## Authentication & Identity

**Auth Provider:**
- Not detected

**OAuth Integrations:**
- Not detected

## Monitoring & Observability

**Error Tracking:**
- Not detected

**Analytics:**
- Not detected

**Logs:**
- Not detected (no dedicated logging service surfaced; per-project logging likely varies)

## CI/CD & Deployment

**Hosting:**
- Not detected (deployment targets appear per-subproject)

**CI Pipeline:**
- Not detected from this scan (no workflow paths captured)

## Environment Configuration

**Development:**
- `.env.example` templates exist in some subprojects:
  - NotebookLM client: `notebooklm-py/.env.example`
  - WhisperX-WebUI backend (HF token, DB URL, etc.): `WhisperX-WebUI/backend/configs/.env.example`
- Other components rely on raw env vars without a single repo-wide standard (example vars used by itir-svelte: `SB_*`, `SL_WIKI_TIMELINE_AOO_DB`) in `itir-svelte/src/routes/+page.server.ts`, `itir-svelte/src/lib/server/wikiTimelineAoo.ts`

**Staging:**
- Not detected

**Production:**
- Not detected

## Webhooks & Callbacks

**Incoming:**
- Not detected

**Outgoing:**
- Not detected

---

*Integration audit: 2026-03-06*
*Update when adding/removing external services*
