# ITIR Observer Obsidian Plugin

Read-only Obsidian UI scaffold for ITIR MCP docstore projections.

## What It Does

- Adds commands to export an observer bundle and refresh ITIR projections.
- Adds an `ITIR` status pane with export, status, question, scan, and refresh-all actions.
- Writes replaceable Markdown projections under the configured generated folder.
- Exports a JSON bundle for `itir.obsidian.vault_scan` using hashed vault/note identifiers.
- Optionally calls an HTTP MCP adapter for:
  - `itir.docstore.status`
  - `itir.docstore.open_questions`
  - `itir.obsidian.vault_scan`

The plugin does not write promoted ITIR truth. Generated files are replaceable observer projections.

## Bundle Boundary

The exported bundle defaults to:

```text
ITIR Projections/_bundles/obsidian-observer-bundle.json
```

Each record contains:

- `note_id_hash`
- `vault_id_hash`
- `authority_class: observer`
- bounded Markdown pressure excerpts from open-question/blocker/gap/assumption sections or `:itir-query:` / `:sl-query:` lines

Raw note paths, titles, tags, and backlinks are not exported as canonical identity fields.

## MCP Endpoint Shape

Set `MCP call endpoint` in plugin settings to an adapter URL. The plugin posts:

```json
{
  "tool": "itir.docstore.status",
  "name": "itir.docstore.status",
  "arguments": {"bundle_path": "/path/to/obsidian-observer-bundle.json"},
  "payload": {"bundle_path": "/path/to/obsidian-observer-bundle.json"}
}
```

If your adapter routes by tool name, include `{tool}` in the endpoint URL.

If Obsidian and ITIR MCP see different filesystem mounts, set `MCP bundle path override` to the absolute path visible to the MCP process.

## Development

Install dependencies when network access is available:

```bash
npm install
npm run build
```

Static checks that do not install dependencies:

```bash
node -e "for (const f of ['manifest.json','package.json','tsconfig.json']) JSON.parse(require('fs').readFileSync(f, 'utf8'))"
node scripts/static-check.mjs
```
