# Changelog

## Unreleased
- Suite MCP contract + scaffold lane:
  - Added `docs/planning/itir_mcp_dioxus_contract_20260326.md` to define the
    first suite-level MCP boundary, the `itir-mcp/` project direction, the
    SensibLaw-first read-only tool rollout, and the Dioxus backend/native
    integration posture.
  - Updated root planning/context surfaces so the MCP lane is tracked as a
    suite contract rather than an ad hoc sidecar.
  - Added the first `itir-mcp/` scaffold as a suite adapter project instead of
    folding MCP transport directly into existing component internals.
  - Hardened `itir-mcp` with a persistent `--bridge` protocol, structured
    envelopes, and version metadata for client health/version checks.
  - Added Dioxus native-gateway persistence and optional local fallback controls
    before reducing fallback dependency for production flow.
