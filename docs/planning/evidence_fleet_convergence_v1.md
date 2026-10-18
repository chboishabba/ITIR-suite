# Evidence-driven fleet convergence v1

Conversation graphs and canonical SQLite archive remain authoritative for conversation bodies. This control plane stores only references and task/gap evidence; it does not replicate transcripts.

Bulk export, deduplication and FTS belong to chat-export-structurer. chat-context-sync refreshes only selected active threads. After a worker result: exact refresh, incremental archive ingest, PNF/exact-gap reduction, then rescore. No global replay per tick.

The historical scripts/autonomous_fleet_daemon.py is a **legacy unsafe carousel**, not a production PostgreSQL eight-lane scheduler. It includes title-keyword prompts and a browser fallback. It is disabled by default; never use it for production dispatch.

Operator: run `python -m scripts.evidence_fleet_controller --db PATH --plan` to inspect a bounded plan. No ChatGPT mutation occurs. Store task metadata in SQLite alongside the archive, without prompt bodies. Work units are evidence-derived task/gap clusters. All worker dispatch must separately claim an .autonomous-orchestrator lane and use headless direct async curl_cffi with write_transport="async", dom_fallback=False. On uncertain mutations, stop and reconcile exact conversation state before any new write.

Completion requires an independently checkable PR, test, Colab or formal receipt; assistant prose cannot close a task. MCP stdio adapters may wrap these Python functions without a second scheduler or HTTP facade. The migration is CREATE TABLE IF NOT EXISTS and leaves legacy conversation_lineage untouched.
