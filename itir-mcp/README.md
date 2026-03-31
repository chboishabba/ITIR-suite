# itir-mcp

`itir-mcp` is the suite-level MCP adapter project for `ITIR-suite`.

It exists to expose bounded, namespaced tools/resources over existing producer
logic without taking canonical ownership away from the underlying components.

## Scope

Current scope:
- local tool/spec registry
- SensibLaw-first read-only tool adapters
- chat-export-structurer read-only archive lookup adapters
- optional FastMCP transport when the Python MCP SDK is available
- persistent JSON bridge protocol for `dioxus` via `python -m itir_mcp --bridge`

Not in scope for the first increment:
- broad mutable actions
- direct browser-WASM transport for Dioxus web
- redefining component schemas or producer semantics

## Initial tool family

- `sensiblaw.obligations_query`
- `sensiblaw.obligations_explain`
- `sensiblaw.obligations_alignment`
- `sensiblaw.obligations_projection`
- `sensiblaw.obligations_activate`
- `chat_export_structurer.resolve_thread`
- `chat_export_structurer.search_threads`
- `chat_export_structurer.thread_messages`

## Chat Archive Platform Filtering

The `chat_export_structurer.*` tools accept an optional `platform` field so
clients can scope archive lookups to a specific source instead of mixing chat
systems in one result set.

Examples:

```json
{"selector":"James Michael","platform":"telegram"}
{"selector":"incident review","platform":"discord","limit":10}
{"canonical_thread_id":"<thread-id>","platform":"telegram","limit":200}
```

This works for any platform already present in the archive DB, including
Telegram and Discord. If Facebook/Messenger data is ingested into the same
archive with `platform="facebook"` or `platform="messenger"`, the MCP tools
can filter and fetch it the same way.

## Development

Run local tests:

```bash
pytest itir-mcp/tests -q
```

If you want to run the optional FastMCP transport bridge, install the transport
extra first:

```bash
pip install -e itir-mcp[transport]
python -m itir_mcp
```

For the long-lived JSON bridge used by native Dioxus:

```bash
python -m itir_mcp --bridge
```

Tool responses and failures are wrapped in the same envelope schema for both HTTP
bridges and local adapters:

```json
{"ok": true, "result": {...}}
{"ok": false, "error": {"code": "input_error", "message": "...", "details": {...}}}
```

For persistent bridge sessions, clients may include `request_id` on any valid
request object (`health`/`info`/`list`/`call`); the bridge echoes it on the
response for deterministic correlation.

## Relationship to Dioxus

`itir-mcp` is the suite adapter/server side of the boundary. For Dioxus:

- `dioxus/web` should call a backend/native seam that talks to this adapter
- existing internal Dioxus MCP-like registries remain useful UI/debug surfaces
  but are not the canonical suite transport layer
