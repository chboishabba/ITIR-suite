# Evidence-driven fleet convergence v1

Conversation graphs and canonical SQLite archive remain authoritative for conversation bodies. This control plane stores only references and task/gap evidence; it does not replicate transcripts.

Bulk export, deduplication and FTS belong to chat-export-structurer. chat-context-sync refreshes only selected active threads. After a worker result: exact refresh, incremental archive ingest, PNF/exact-gap reduction, then rescore. No global replay per tick.

The historical scripts/autonomous_fleet_daemon.py is a **legacy unsafe carousel**, not a production PostgreSQL eight-lane scheduler. It includes title-keyword prompts and a browser fallback. It is disabled by default; never use it for production dispatch.

Operator: run `python -m scripts.evidence_fleet_controller --db PATH --plan` to inspect a bounded plan. No ChatGPT mutation occurs. Store task metadata in SQLite alongside the archive, without prompt bodies. Work units are evidence-derived task/gap clusters. All worker dispatch must separately claim an .autonomous-orchestrator lane and use headless direct async curl_cffi with write_transport="async", dom_fallback=False. On uncertain mutations, stop and reconcile exact conversation state before any new write.

Completion requires an independently checkable PR, test, Colab or formal receipt; assistant prose cannot close a task. MCP stdio adapters may wrap these Python functions without a second scheduler or HTTP facade. The migration is CREATE TABLE IF NOT EXISTS and leaves legacy conversation_lineage untouched.

## Roadmap reconciliation and safety

The suite AGENTS.md/README.md/ROADMAP.md/plan.md require generic evidence carriers and reviewed promotion. SensibLaw docs/roadmaps/roadmap.md and DB_ROADMAP.md describe provenance and ontology persistence, not dispatch authority. DASHI Docs/roadmaps/ClayYMProofRoadmap.md is non-promoting. DASHI plan.md anchors include DASHI/Physics/YangMills/BalabanRGLane.agda and DASHI/Physics/Closure/YMBalabanRGScaleTransferFrontierReceipt.agda. Lean docs/DECLARATION_LANDSCAPE.md is a name-only index, not certification.

The .agents/skills/autonomous-orchestrator/SKILL.md exposes itir.ao.claim_lane, itir.ao.heartbeat, itir.ao.report_result, itir.ao.gap_check. The Colab runner tools/colab-runner/README.md accepts exact-SHA lake_build, lake_env_lean, agda_module only for DASHI repositories; no prover job is needed for this Python cut.

Legacy scripts/autonomous_fleet_daemon.py CLI exits before transport imports. Never import its historical dispatcher into production. Use python -m scripts.evidence_fleet_controller --db PATH --plan --limit 3 for a bounded proposal only. This may create reference tables but sends no prompts. Receipt links require independent verification before promotion.
