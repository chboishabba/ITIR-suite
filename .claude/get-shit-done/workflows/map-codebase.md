<purpose>
Orchestrate parallel inheriting agents to analyze the codebase and produce structured documents in `.planning/codebase/`.

This overrides the user-level GSD workflow for this repository so background analysis uses the custom `gsd-code-explorer` agent instead of the built-in `Explore` agent.
</purpose>

<process>

<step name="check_existing" priority="first">
Check whether `.planning/codebase/` already exists.

If it exists, show the user the current files and ask whether to refresh, selectively update, or skip.
If it does not exist, continue.
</step>

<step name="create_structure">
Create `.planning/codebase/`.

Expected output files:
- `STACK.md`
- `ARCHITECTURE.md`
- `STRUCTURE.md`
- `CONVENTIONS.md`
- `TESTING.md`
- `INTEGRATIONS.md`
- `CONCERNS.md`
</step>

<step name="spawn_agents">
Spawn 4 parallel background tasks using the Task tool with:

```text
subagent_type: "gsd-code-explorer"
run_in_background: true
```

Agent 1 scope:
- Stack
- Integrations

Agent 2 scope:
- Architecture
- Structure

Agent 3 scope:
- Conventions
- Testing

Agent 4 scope:
- Concerns

For each agent:
- pass a focused prompt for its scope
- require concrete file paths in findings
- keep it read-only
</step>

<step name="collect_results">
Wait for all 4 agents to complete and collect their outputs.
</step>

<step name="write_documents">
Write the 7 output documents in `.planning/codebase/` using the referenced templates and the collected findings.

Document requirements:
- practical and navigable
- path-heavy, not vague
- grounded in actual repository evidence
- concise, but detailed enough to support planning
</step>

<step name="finish">
Report what was created and suggest next steps, typically `/gsd:new-project` or `/gsd:plan-phase`.
</step>

</process>

<success_criteria>
- `.planning/codebase/` created
- 4 parallel `gsd-code-explorer` agents launched successfully
- 7 codebase documents written
- findings include actionable file paths
</success_criteria>
