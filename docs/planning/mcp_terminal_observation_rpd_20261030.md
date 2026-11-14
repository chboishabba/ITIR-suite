# MCP terminal observation RPD (2026-10-30)

## User story
Given an operator's authenticated, existing terminal ChatGPT TUI in tmux, an authorized agent should observe the actual visible pane and diagnose UI regressions such as an empty resume picker without Chrome/CDP, DOM scraping or fabricated screenshots.

## Source ownership
- Existing terminal frontend: tritao/chatgpt-web (upstream, not copied)
- ChatGPT transport: reverse-engineered-chatgpt/re-gpt, async curl_cffi
- History authority: ITIR sole PostgreSQL spine and SLR production typed readers
- Golden formal precedent: dashi_agda/DASHI/Interop/ITIRRibbonProjectionAuthorityBridgeExact.agda (read-only projection does not mutate canonical state)
- SensibLaw: deprecated reference, not a production dependency

## Implemented bounded slice
`itir.terminal.observe` in the existing itir-mcp registry reads an exact allowlisted tmux pane with `capture-pane`. Environment variable `ITIR_TMUX_ALLOWED_PANES` must enumerate exact pane IDs (e.g. `%3`), or the tool denies access. It never sends keys, performs shell interpolation, accesses the browser or persists captured output. Its result may be sensitive: MCP consumers must observe the same account authorization and refrain from copying tokens or private transcript bodies into issue reports.

## RPD residuals
1. Add opt-in *interactive* key dispatch as a separate tool, with user-granted session-specific capability, key/target allowlist, action log and cancellation. Do not imply that read permission grants write permission.
2. Add structured `tmux display-message` diagnostics (pane dimensions, session identity, foreground process) only with the same access boundary.
3. Add reviewable TUI fixture sessions for regression reproduction. Existing TUI resume bug: re-gpt only queries the first page of the remote catalog; pending PR fixes diagnostic/pagination, but long-term picker must query the canonical PG/SLR read projection.
4. If a structural/visual screenshot is needed, prefer explicit terminal screenshot/rendering from the permitted pane. Never default to Chrome.
5. Extend source-derived Agda/Lean read-only nonpromotion formal coverage only after searching for exact reusable golden owners. No kernel proof claimed.

## Verification
Source-written and test fixtures added; no local tmux session or live UI was accessible in this execution environment. No CI or kernel verification claimed.
