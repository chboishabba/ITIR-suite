# SB Shell Command Intent Model (2026-02-09)

## Canonical threads (use `$robust-context-fetch`)
- `6988c41f-47a4-8398-ac05-2105febb0dd0` — command/arg variations, referents, attempts, outcomes.
- `6988c676-f6b4-8398-9824-b5ca2684be52` — argument-set variation & signatures.
- `6988c83e-1cd0-8399-bd79-b8a904e5f1be` — “file as referent” separation.
- `6988ec25-5e54-83a0-919b-904626712c78` — typo/failed-run handling.

## Core modelling rules
- **Invocation = operator × argument set × referents.** Arguments have meaning only in operator context.
- **Referents ≠ args.** `file` is a referent slot (positional/flagged), resolved separately, and canonicalised as an artifact (`fs:sha256:...`).
- **Signatures are operator-scoped.** `cat::pos1` ≠ `rm::pos1` even with identical args/referents.
- **Attempts first, outcomes later.** Always record the attempted invocation; attach success/failure/abort as a refinement.
- **Order sensitivity is explicit.** Support ordered vs unordered signatures (e.g., filters vs set semantics).

## Attempt taxonomy (store as state machine)
1) Parse failure (no operator)  
2) Invocation failure (bad args)  
3) Resolution failure (referent missing)  
4) Permission/env failure  
5) Partial execution (indeterminate effects)  
6) Successful execution

## Data separation
- Command event: raw line + argv + operator + arg signature + referent slots.
- Resolution: slot → artifact(s) with cwd, existence, type.
- Artifact: stable hash/size/mtime; independent of commands.
- Outcome: status, failure_class, exit_code, stderr_excerpt (optional).

## Compression / summarisation
- Cluster retries/typos by operator + similar argv + time window; keep raw attempts.
- Never compress across operators (same args ≠ same intent).
- Summaries may speak in terms of operator families (read/inspect/write/destroy) but must retain concrete operator identity.

## Schema TODO (to implement)
- Add an explicit `command_attempt` entity with `arg_signature`, `referents`, `resolution_id`, `outcome`.
- Add `failure_class` enum covering the attempt taxonomy above.
- Add optional `operator_family` tag for reporting (read/inspect/write/destroy/transfer).
