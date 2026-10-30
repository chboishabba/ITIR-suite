# ITIR MCP direct ChatGPT TUI state/control (2026-10-30)

## Owner and intention
Agent observes *application state*, not the tmux pane or browser. Reuse tritao/chatgpt-web's existing Python ChatTui and re-gpt's owned adapter. ITIR MCP owns the narrowly governed remote interface, not UI storage or semantic logic. Golden Agda projection authority is the formal precedent; SLR remains the production semantic runtime; SensibLaw is deprecated reference.

## Production entry points
`itir.terminal.state` is read-only. It returns state from the re-gpt Unix socket provided in `ITIR_TUI_CONTROL_SOCKET`. `itir.terminal.picker` is separately opt-in and requires `ITIR_TUI_ALLOW_CONTROL=1`; its actions are `open_picker`, `set_query`, and `select`. These are **application-level** methods, not keystrokes. The server and MCP tool validate the owner-operated 0600 socket and owner-only parent directory. There is no network listener and no shell/Chrome/tmux.

Sample MCP host environment:

```sh
export ITIR_TUI_CONTROL_SOCKET="$XDG_RUNTIME_DIR/re-gpt-tui/control.sock"
# Only if intentionally allowing agent interaction:
export ITIR_TUI_ALLOW_CONTROL=1
```

Example read invocation: `registry.invoke("itir.terminal.state", {})`
Example picker invocation: `registry.invoke("itir.terminal.picker", {"action":"set_query","query":"twin prime"})`.

## Non-authority and limits
The control socket exists only while the interactive TUI is running with `--control-socket`. It does not discover arbitrary processes, access ChatGPT credentials, send model messages, edit conversations, or acquire semantic promotion authority. Same-UID access is not an adversarial sandbox; do not enable on multi-user shared runtimes without stronger authorization. Current actions return queued acknowledgments; poll state to see completion. The current upstream remote picker may have catalog data gaps; this interface enables precise diagnosis but does not replace the planned canonical PostgreSQL-backed search.

Source-written and fixture-tested only; live local MCP/TUI handshake, CI and formal kernel verification have not been executed.
