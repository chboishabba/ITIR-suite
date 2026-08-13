# ITIR Security Posture: Secrets Without Agency (2026-02-09)

## Canonical threads (use `$robust-context-fetch`)
- `6988c298-69e8-839a-a5bd-65a6c0a21f6b` — ITIR vs OpenClaw “trove of secrets” and non-agentic boundary.

## Core stance
- ITIR is a **high-value trove** (credentials, timelines, legal/medical records), but **secrets never acquire agency**.
- ITIR is a **ledger with eyes**, not a **brain with hands**: observe/record/summarize only; zero autonomous execution or tool calls.
- Explicit non-goals: no execution, no tool invocation, no intent inference from language, no mutable prompts/memory, no background actions.

## Boundaries to document
- Secrets stay **inert artifacts**; they are referenced, not consumed.
- LLMs are demoted to summarizers/indexers/compressors/classifiers; they cannot act, persist instructions, or drive tools.
- Persistence is append-only/versioned; injected text cannot mutate future behaviour.
- Inputs are evidence, not control; “code in chats” stays text (pattern detection only).

## Threat framing to cite
- OpenClaw risk = secrets + autonomy + execution + mutable memory (agentic trojan horse).
- ITIR survival invariant: **secrets never become capability**.

## Doctrine sentences to reuse
- “ITIR systems may store sensitive material, but SHALL NOT use that material to initiate, decide, or execute actions.”
- “Detected code is evidence, not instruction.”
- “Openness increases the cost of surprise, not the probability of attack.”

## Suggested follow-through
- Add a short “Secrets Without Agency” section to security/FAQ docs.
- Add a red-line checklist: if any feature enables autonomous action, it violates posture.
- Keep daily/weekly briefs strictly observational; no action suggestions derived from stored secrets.
