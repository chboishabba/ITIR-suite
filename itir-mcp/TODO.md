# itir-mcp TODO

## Docstore and Obsidian Follow-ups

- Verify `obsidian-itir-plugin` inside a real Obsidian vault after dependency
  installation.
- Exercise the plugin against a live HTTP adapter for the registered MCP tools.
- Decide whether `itir.docstore.config_plan` should become a required preflight
  for all docstore scan calls or remain an explicit planning tool.
- Add persistent cache storage only if repeated large-vault scans show measured
  latency pressure.
