# itir-mcp TODO

## Current Numeric ABI Boundary

- `itir_mcp.pnf_numeric_abi` is present as a narrow
  `itir.pnf.numeric_abi.v0_1` GEMV validation/parity helper for
  receipt-bearing row maps.
- Do not treat the current ABI as spectral materialization. Signed adjacency,
  Laplacians, eigenvectors, graph versions, and rebuildability payloads remain
  future producer work.

## Docstore and Obsidian Follow-ups

- Verify `obsidian-itir-plugin` inside a real Obsidian vault after dependency
  installation.
- Exercise the plugin against a live HTTP adapter for the registered MCP tools.
- Decide whether `itir.docstore.config_plan` should become a required preflight
  for all docstore scan calls or remain an explicit planning tool.
- Add persistent cache storage only if repeated large-vault scans show measured
  latency pressure.
