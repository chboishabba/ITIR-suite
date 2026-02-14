import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

export type AooActor = {
  label: string;
  resolved: string;
  role: string;
  source: string;
};

export type AooObject = {
  title: string;
  source: string;
  resolver_hints?: Array<{
    lane: string;
    kind: string;
    title: string;
    score: number;
  }>;
};

export type AooCitation = {
  text: string;
  kind?: string;
  source?: string;
  targets?: number[];
  follower_order?: string[];
  follow?: Array<Record<string, unknown>>;
};

export type AooSlReference = {
  lane: string;
  authority?: string;
  ref_kind?: string;
  ref_value?: string;
  text?: string;
  source_document_json?: string;
  source_pdf?: string;
  provision_stable_id?: string;
  rule_atom_stable_id?: string;
  follower_order?: string[];
  follow?: Array<Record<string, unknown>>;
};

export type AooNegation = {
  kind: string;
  scope?: string;
  source?: string;
};

export type AooTimelineFact = {
  fact_id: string;
  event_id: string;
  step_index?: number;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  party?: string;
  subjects?: string[];
  action?: string | null;
  negation?: AooNegation;
  objects?: string[];
  numeric_objects?: string[];
  purpose?: string | null;
  text?: string;
  prev_fact_ids?: string[];
  next_fact_ids?: string[];
  chain_kinds?: string[];
};

export type SpanCandidate = {
  span_id: string;
  event_id: string;
  span: { kind: string; start: number; end: number; revision_id?: string };
  text: string;
  span_type: string;
  recurrence?: { seen_events: number };
  hygiene?: {
    token_count?: number;
    is_time_expression?: boolean;
    overlaps_resolved_entity?: boolean;
    view_score?: number;
  };
};

export type AooEvent = {
  event_id: string;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  section: string;
  text: string;
  actors: AooActor[];
  action: string | null;
  action_meta?: {
    surface?: string;
    tense?: string | null;
    aspect?: string | null;
    verb_form?: string | null;
    voice?: string | null;
    source?: string;
  };
  action_surface?: string | null;
  negation?: AooNegation;
  steps?: Array<{
    action: string;
    action_meta?: {
      surface?: string;
      tense?: string | null;
      aspect?: string | null;
      verb_form?: string | null;
      voice?: string | null;
      source?: string;
    };
    action_surface?: string | null;
    negation?: AooNegation;
    subjects: string[];
    entity_objects?: string[];
    numeric_objects?: string[];
    modifier_objects?: string[];
    objects: string[];
    purpose: string | null;
  }>;
  chains?: Array<{
    from_step?: number;
    to_step?: number;
    to?: string;
    kind: string;
  }>;
  objects: AooObject[];
  entity_objects?: string[];
  numeric_objects?: string[];
  modifier_objects?: string[];
  citations?: AooCitation[];
  sl_references?: AooSlReference[];
  party?: string;
  party_source?: string;
  party_evidence?: string[];
  toc_context?: Array<{ node_type?: string; identifier?: string; title?: string; path?: string }>;
  legal_section_markers?: {
    citation_prefixes?: string[];
    sl_reference_lanes?: string[];
    provision_stable_ids?: string[];
    rule_atom_stable_ids?: string[];
  };
  timeline_facts?: AooTimelineFact[];
  purpose: string | null;
  span_candidates?: SpanCandidate[];
  warnings: string[];
};

export type WikiTimelineAooPayload = {
  root_actor: { label: string; surname: string };
  events: AooEvent[];
  fact_timeline?: AooTimelineFact[];
  parser?: any;
};

function isObj(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === 'object';
}

async function fileExists(p: string): Promise<boolean> {
  try {
    await fs.stat(p);
    return true;
  } catch {
    return false;
  }
}

async function runPythonJson(repoRoot: string, args: string[]): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const script = path.join(repoRoot, 'SensibLaw', 'scripts', 'query_wiki_timeline_aoo_db.py');
    const child = spawn('python3', [script, ...args], { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += String(d)));
    child.stderr.on('data', (d) => (stderr += String(d)));
    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code !== 0) return reject(new Error(`query_wiki_timeline_aoo_db.py failed (exit ${code}).\n${stderr || stdout}`));
      try {
        resolve(JSON.parse(stdout));
      } catch {
        reject(new Error(`query_wiki_timeline_aoo_db.py returned non-JSON output.\n${stderr || ''}\n${stdout.slice(0, 2000)}`));
      }
    });
  });
}

function parseNegation(v: unknown): AooNegation | undefined {
  if (!isObj(v)) return undefined;
  const kind = typeof v.kind === 'string' ? String(v.kind).trim() : '';
  if (!kind) return undefined;
  return {
    kind,
    scope: typeof v.scope === 'string' ? String(v.scope) : undefined,
    source: typeof v.source === 'string' ? String(v.source) : undefined
  };
}

function normalizeActionAndNegation(rawAction: unknown, rawNegation: unknown): { action: string | null; negation?: AooNegation } {
  const parsedNegation = parseNegation(rawNegation);
  const actionText = typeof rawAction === 'string' ? String(rawAction).trim() : '';
  if (!actionText) return { action: null, negation: parsedNegation };
  if (actionText.startsWith('not_')) {
    const base = actionText.slice(4).trim();
    if (!base) return { action: null, negation: parsedNegation ?? { kind: 'not', scope: 'action', source: 'legacy:not_prefix' } };
    return {
      action: base,
      negation: parsedNegation ?? { kind: 'not', scope: 'action', source: 'legacy:not_prefix' }
    };
  }
  return { action: actionText, negation: parsedNegation };
}

export async function loadWikiTimelineAoo(repoRoot: string, relPath: string): Promise<WikiTimelineAooPayload> {
  // Canonical DB-first: attempt to load from the local AAO SQLite store when present.
  // Legacy fallback remains JSON on disk for regression/debug.
  const dbEnv = process.env.SL_WIKI_TIMELINE_AOO_DB;
  const dbPath = dbEnv && dbEnv.trim() ? path.resolve(repoRoot, dbEnv.trim()) : path.resolve(repoRoot, 'SensibLaw', '.cache_local', 'wiki_timeline_aoo.sqlite');

  // Heuristic mapping: AOO artifact path suffix -> timeline input path suffix.
  // Example: `.../wiki_timeline_gwb_public_bios_v1_aoo.json` -> `.../wiki_timeline_gwb_public_bios_v1.json`
  const base = path.basename(relPath);
  const timelineSuffix = base.endsWith('_aoo.json') ? `${base.slice(0, -'_aoo.json'.length)}.json` : base;

  if (await fileExists(dbPath)) {
    try {
      const raw = await runPythonJson(repoRoot, ['--db-path', dbPath, '--timeline-path-suffix', timelineSuffix]);
      if (raw && typeof raw === 'object') {
        // The DB payload is already the JSON export shape; normalize through the existing parser below.
        const parsed = raw as any;
        // Fall through into the JSON parsing block by stringifying (keeps one normalization codepath).
        // Avoid persisting JSON; this is in-memory only.
        const p = parsed;
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        (p as any).__loaded_from_db = true;
        // Parse using the same logic as disk JSON.
        const events = Array.isArray(p?.events) ? (p.events as any[]) : [];
        const root_actor = isObj(p?.root_actor) ? p.root_actor : { label: '', surname: '' };
        const fact_timeline = Array.isArray(p?.fact_timeline) ? (p.fact_timeline as any[]) : undefined;
        const parser = p?.parser;

        const outEvents: AooEvent[] = [];
        for (const e of events) {
          if (!isObj(e)) continue;
          const event_id = String(e.event_id ?? '').trim();
          const text = String(e.text ?? '').trim();
          if (!event_id || !text) continue;
          const anchor = isObj(e.anchor) ? e.anchor : {};
          const actors = Array.isArray(e.actors) ? (e.actors as any[]) : [];
          const objects = Array.isArray(e.objects) ? (e.objects as any[]) : [];
          const eventAction = normalizeActionAndNegation(e.action, (e as any).negation);
          outEvents.push({
            event_id,
            anchor: {
              year: Number((anchor as any).year ?? 0) || 0,
              month: Number.isFinite(Number((anchor as any).month)) ? Number((anchor as any).month) : null,
              day: Number.isFinite(Number((anchor as any).day)) ? Number((anchor as any).day) : null,
              precision: String((anchor as any).precision ?? 'year'),
              text: String((anchor as any).text ?? ''),
              kind: String((anchor as any).kind ?? '')
            },
            section: String(e.section ?? ''),
            text,
            actors: actors
              .filter((a) => isObj(a) && typeof (a as any).resolved === 'string')
              .map((a) => ({
                label: String((a as any).label ?? ''),
                resolved: String((a as any).resolved ?? ''),
                role: String((a as any).role ?? ''),
                source: String((a as any).source ?? '')
              })),
            action: eventAction.action,
            action_meta: isObj((e as any).action_meta)
              ? {
                  surface: typeof (e as any).action_meta.surface === 'string' ? String((e as any).action_meta.surface) : undefined,
                  tense: typeof (e as any).action_meta.tense === 'string' ? String((e as any).action_meta.tense) : null,
                  aspect: typeof (e as any).action_meta.aspect === 'string' ? String((e as any).action_meta.aspect) : null,
                  verb_form: typeof (e as any).action_meta.verb_form === 'string' ? String((e as any).action_meta.verb_form) : null,
                  voice: typeof (e as any).action_meta.voice === 'string' ? String((e as any).action_meta.voice) : null,
                  source: typeof (e as any).action_meta.source === 'string' ? String((e as any).action_meta.source) : undefined
                }
              : undefined,
            action_surface: typeof (e as any).action_surface === 'string' ? String((e as any).action_surface) : undefined,
            negation: eventAction.negation,
            steps: Array.isArray((e as any).steps)
              ? (e as any).steps
                  .filter((s: any) => isObj(s) && typeof s.action === 'string')
                  .map((s: any) => {
                    const normalized = normalizeActionAndNegation(s.action, s.negation);
                    return {
                      action: normalized.action ?? '',
                      action_meta: isObj(s.action_meta)
                        ? {
                            surface: typeof s.action_meta.surface === 'string' ? String(s.action_meta.surface) : undefined,
                            tense: typeof s.action_meta.tense === 'string' ? String(s.action_meta.tense) : null,
                            aspect: typeof s.action_meta.aspect === 'string' ? String(s.action_meta.aspect) : null,
                            verb_form: typeof s.action_meta.verb_form === 'string' ? String(s.action_meta.verb_form) : null,
                            voice: typeof s.action_meta.voice === 'string' ? String(s.action_meta.voice) : null,
                            source: typeof s.action_meta.source === 'string' ? String(s.action_meta.source) : undefined
                          }
                        : undefined,
                      action_surface: typeof s.action_surface === 'string' ? String(s.action_surface) : undefined,
                      negation: normalized.negation,
                      subjects: Array.isArray(s.subjects) ? s.subjects.map((x: any) => String(x)) : [],
                      entity_objects: Array.isArray(s.entity_objects) ? s.entity_objects.map((x: any) => String(x)) : undefined,
                      numeric_objects: Array.isArray(s.numeric_objects) ? s.numeric_objects.map((x: any) => String(x)) : undefined,
                      modifier_objects: Array.isArray(s.modifier_objects) ? s.modifier_objects.map((x: any) => String(x)) : undefined,
                      objects: Array.isArray(s.objects) ? s.objects.map((x: any) => String(x)) : [],
                      purpose: typeof s.purpose === 'string' ? s.purpose : null
                    };
                  })
              : undefined,
            chains: Array.isArray((e as any).chains)
              ? (e as any).chains
                  .filter((c: any) => isObj(c) && typeof c.kind === 'string')
                  .map((c: any) => ({
                    from_step: typeof c.from_step === 'number' ? c.from_step : undefined,
                    to_step: typeof c.to_step === 'number' ? c.to_step : undefined,
                    to: typeof c.to === 'string' ? c.to : undefined,
                    kind: String(c.kind ?? '')
                  }))
              : undefined,
            objects: objects
              .filter((o) => isObj(o))
              .map((o) => ({
                title: String((o as any).title ?? ''),
                source: String((o as any).source ?? ''),
                resolver_hints: Array.isArray((o as any).resolver_hints)
                  ? (o as any).resolver_hints
                      .filter((h: any) => isObj(h))
                      .map((h: any) => ({
                        lane: String(h.lane ?? ''),
                        kind: String(h.kind ?? ''),
                        title: String(h.title ?? ''),
                        score: Number(h.score ?? 0) || 0
                      }))
                  : undefined
              })),
            entity_objects: Array.isArray((e as any).entity_objects) ? (e as any).entity_objects.map((x: any) => String(x)) : undefined,
            numeric_objects: Array.isArray((e as any).numeric_objects) ? (e as any).numeric_objects.map((x: any) => String(x)) : undefined,
            modifier_objects: Array.isArray((e as any).modifier_objects) ? (e as any).modifier_objects.map((x: any) => String(x)) : undefined,
            citations: Array.isArray((e as any).citations)
              ? (e as any).citations
                  .filter((c: any) => isObj(c))
                  .map((c: any) => ({
                    text: String(c.text ?? ''),
                    kind: typeof c.kind === 'string' ? String(c.kind) : undefined,
                    source: typeof c.source === 'string' ? String(c.source) : undefined,
                    targets: Array.isArray(c.targets) ? c.targets.map((x: any) => Number(x)).filter((n: any) => Number.isFinite(n)) : undefined,
                    follower_order: Array.isArray(c.follower_order) ? c.follower_order.map((x: any) => String(x)) : undefined,
                    follow: Array.isArray(c.follow) ? c.follow : undefined
                  }))
              : undefined,
            sl_references: Array.isArray((e as any).sl_references)
              ? (e as any).sl_references
                  .filter((r: any) => isObj(r))
                  .map((r: any) => ({
                    lane: String(r.lane ?? ''),
                    authority: typeof r.authority === 'string' ? String(r.authority) : undefined,
                    ref_kind: typeof r.ref_kind === 'string' ? String(r.ref_kind) : undefined,
                    ref_value: typeof r.ref_value === 'string' ? String(r.ref_value) : undefined,
                    text: typeof r.text === 'string' ? String(r.text) : undefined,
                    source_document_json: typeof r.source_document_json === 'string' ? String(r.source_document_json) : undefined,
                    source_pdf: typeof r.source_pdf === 'string' ? String(r.source_pdf) : undefined,
                    provision_stable_id: typeof r.provision_stable_id === 'string' ? String(r.provision_stable_id) : undefined,
                    rule_atom_stable_id: typeof r.rule_atom_stable_id === 'string' ? String(r.rule_atom_stable_id) : undefined,
                    follower_order: Array.isArray(r.follower_order) ? r.follower_order.map((x: any) => String(x)) : undefined,
                    follow: Array.isArray(r.follow) ? r.follow : undefined
                  }))
              : undefined,
            party: typeof (e as any).party === 'string' ? String((e as any).party) : undefined,
            party_source: typeof (e as any).party_source === 'string' ? String((e as any).party_source) : undefined,
            party_evidence: Array.isArray((e as any).party_evidence) ? (e as any).party_evidence.map((x: any) => String(x)) : undefined,
            toc_context: Array.isArray((e as any).toc_context)
              ? (e as any).toc_context
                  .filter((t: any) => isObj(t))
                  .map((t: any) => ({
                    node_type: typeof t.node_type === 'string' ? String(t.node_type) : undefined,
                    identifier: typeof t.identifier === 'string' ? String(t.identifier) : undefined,
                    title: typeof t.title === 'string' ? String(t.title) : undefined,
                    path: typeof t.path === 'string' ? String(t.path) : undefined
                  }))
              : undefined,
            legal_section_markers: isObj((e as any).legal_section_markers)
              ? {
                  citation_prefixes: Array.isArray((e as any).legal_section_markers.citation_prefixes)
                    ? (e as any).legal_section_markers.citation_prefixes.map((x: any) => String(x))
                    : undefined,
                  sl_reference_lanes: Array.isArray((e as any).legal_section_markers.sl_reference_lanes)
                    ? (e as any).legal_section_markers.sl_reference_lanes.map((x: any) => String(x))
                    : undefined,
                  provision_stable_ids: Array.isArray((e as any).legal_section_markers.provision_stable_ids)
                    ? (e as any).legal_section_markers.provision_stable_ids.map((x: any) => String(x))
                    : undefined,
                  rule_atom_stable_ids: Array.isArray((e as any).legal_section_markers.rule_atom_stable_ids)
                    ? (e as any).legal_section_markers.rule_atom_stable_ids.map((x: any) => String(x))
                    : undefined
                }
              : undefined,
            timeline_facts: Array.isArray((e as any).timeline_facts)
              ? (e as any).timeline_facts
                  .filter((f: any) => isObj(f) && typeof f.fact_id === 'string')
                  .map((f: any) => ({
                    fact_id: String(f.fact_id ?? ''),
                    event_id,
                    step_index: typeof f.step_index === 'number' ? f.step_index : undefined,
                    anchor: isObj(f.anchor)
                      ? {
                          year: Number((f.anchor as any).year ?? 0) || 0,
                          month: Number.isFinite(Number((f.anchor as any).month)) ? Number((f.anchor as any).month) : null,
                          day: Number.isFinite(Number((f.anchor as any).day)) ? Number((f.anchor as any).day) : null,
                          precision: String((f.anchor as any).precision ?? 'year'),
                          text: String((f.anchor as any).text ?? ''),
                          kind: String((f.anchor as any).kind ?? '')
                        }
                      : { year: 0, month: null, day: null, precision: 'year', text: '', kind: '' },
                    party: typeof f.party === 'string' ? String(f.party) : undefined,
                    subjects: Array.isArray(f.subjects) ? f.subjects.map((x: any) => String(x)) : undefined,
                    action: typeof f.action === 'string' ? String(f.action) : null,
                    negation: parseNegation((f as any).negation),
                    objects: Array.isArray(f.objects) ? f.objects.map((x: any) => String(x)) : undefined,
                    numeric_objects: Array.isArray(f.numeric_objects) ? f.numeric_objects.map((x: any) => String(x)) : undefined,
                    purpose: typeof f.purpose === 'string' ? String(f.purpose) : null,
                    text: typeof f.text === 'string' ? String(f.text) : undefined,
                    prev_fact_ids: Array.isArray(f.prev_fact_ids) ? f.prev_fact_ids.map((x: any) => String(x)) : undefined,
                    next_fact_ids: Array.isArray(f.next_fact_ids) ? f.next_fact_ids.map((x: any) => String(x)) : undefined,
                    chain_kinds: Array.isArray(f.chain_kinds) ? f.chain_kinds.map((x: any) => String(x)) : undefined
                  }))
              : undefined,
            purpose: typeof e.purpose === 'string' ? e.purpose : null,
            span_candidates: Array.isArray((e as any).span_candidates)
              ? (e as any).span_candidates
                  .filter((s: any) => isObj(s) && typeof s.text === 'string' && isObj((s as any).span))
                  .map((s: any) => ({
                    span_id: String(s.span_id ?? ''),
                    event_id,
                    span: {
                      kind: String((s.span as any).kind ?? ''),
                      start: Number((s.span as any).start ?? 0) || 0,
                      end: Number((s.span as any).end ?? 0) || 0,
                      revision_id: typeof (s.span as any).revision_id === 'string' ? String((s.span as any).revision_id) : undefined
                    },
                    text: String(s.text ?? ''),
                    span_type: String(s.span_type ?? ''),
                    recurrence: isObj((s as any).recurrence) ? { seen_events: Number((s as any).recurrence.seen_events ?? 0) || 0 } : undefined,
                    hygiene: isObj((s as any).hygiene)
                      ? {
                          token_count: typeof (s as any).hygiene.token_count === 'number' ? (s as any).hygiene.token_count : undefined,
                          is_time_expression: typeof (s as any).hygiene.is_time_expression === 'boolean' ? (s as any).hygiene.is_time_expression : undefined,
                          overlaps_resolved_entity:
                            typeof (s as any).hygiene.overlaps_resolved_entity === 'boolean' ? (s as any).hygiene.overlaps_resolved_entity : undefined,
                          view_score: typeof (s as any).hygiene.view_score === 'number' ? (s as any).hygiene.view_score : undefined
                        }
                      : undefined
                  }))
              : undefined,
            warnings: Array.isArray((e as any).warnings) ? (e as any).warnings.map((x: any) => String(x)) : []
          });
        }

        const out: WikiTimelineAooPayload = {
          root_actor: { label: String(root_actor.label ?? ''), surname: String(root_actor.surname ?? '') },
          events: outEvents,
          fact_timeline: Array.isArray(fact_timeline) ? (fact_timeline as any) : undefined,
          parser
        };
        return out;
      }
    } catch {
      // fall back to legacy JSON
    }
  }

  const p = path.resolve(repoRoot, relPath);
  const raw = await fs.readFile(p, 'utf-8');
  const parsed = JSON.parse(raw) as any;
  const events = Array.isArray(parsed?.events) ? (parsed.events as any[]) : [];
  const root_actor = isObj(parsed?.root_actor) ? parsed.root_actor : { label: '', surname: '' };
  const parser = parsed?.parser;

  const outEvents: AooEvent[] = [];
  for (const e of events) {
    if (!isObj(e)) continue;
    const event_id = String(e.event_id ?? '').trim();
    const text = String(e.text ?? '').trim();
    if (!event_id || !text) continue;
    const anchor = isObj(e.anchor) ? e.anchor : {};
    const actors = Array.isArray(e.actors) ? (e.actors as any[]) : [];
    const objects = Array.isArray(e.objects) ? (e.objects as any[]) : [];
    const eventAction = normalizeActionAndNegation(e.action, (e as any).negation);
    outEvents.push({
      event_id,
      anchor: {
        year: Number((anchor as any).year ?? 0) || 0,
        month: Number.isFinite(Number((anchor as any).month)) ? Number((anchor as any).month) : null,
        day: Number.isFinite(Number((anchor as any).day)) ? Number((anchor as any).day) : null,
        precision: String((anchor as any).precision ?? 'year'),
        text: String((anchor as any).text ?? ''),
        kind: String((anchor as any).kind ?? '')
      },
      section: String(e.section ?? ''),
      text,
      actors: actors
        .filter((a) => isObj(a) && typeof (a as any).resolved === 'string')
        .map((a) => ({
          label: String((a as any).label ?? ''),
          resolved: String((a as any).resolved ?? ''),
          role: String((a as any).role ?? ''),
          source: String((a as any).source ?? '')
        })),
      action: eventAction.action,
      action_meta: isObj((e as any).action_meta)
        ? {
            surface: typeof (e as any).action_meta.surface === 'string' ? String((e as any).action_meta.surface) : undefined,
            tense: typeof (e as any).action_meta.tense === 'string' ? String((e as any).action_meta.tense) : null,
            aspect: typeof (e as any).action_meta.aspect === 'string' ? String((e as any).action_meta.aspect) : null,
            verb_form: typeof (e as any).action_meta.verb_form === 'string' ? String((e as any).action_meta.verb_form) : null,
            voice: typeof (e as any).action_meta.voice === 'string' ? String((e as any).action_meta.voice) : null,
            source: typeof (e as any).action_meta.source === 'string' ? String((e as any).action_meta.source) : undefined
          }
        : undefined,
      action_surface: typeof (e as any).action_surface === 'string' ? String((e as any).action_surface) : undefined,
      negation: eventAction.negation,
      steps: Array.isArray((e as any).steps)
        ? (e as any).steps
            .filter((s: any) => isObj(s) && typeof s.action === 'string')
            .map((s: any) => {
              const normalized = normalizeActionAndNegation(s.action, s.negation);
              return {
              action: normalized.action ?? '',
              action_meta: isObj(s.action_meta)
                ? {
                    surface: typeof s.action_meta.surface === 'string' ? String(s.action_meta.surface) : undefined,
                    tense: typeof s.action_meta.tense === 'string' ? String(s.action_meta.tense) : null,
                    aspect: typeof s.action_meta.aspect === 'string' ? String(s.action_meta.aspect) : null,
                    verb_form: typeof s.action_meta.verb_form === 'string' ? String(s.action_meta.verb_form) : null,
                    voice: typeof s.action_meta.voice === 'string' ? String(s.action_meta.voice) : null,
                    source: typeof s.action_meta.source === 'string' ? String(s.action_meta.source) : undefined
                  }
                : undefined,
              action_surface: typeof s.action_surface === 'string' ? String(s.action_surface) : undefined,
              negation: normalized.negation,
              subjects: Array.isArray(s.subjects) ? s.subjects.map((x: any) => String(x)) : [],
              entity_objects: Array.isArray(s.entity_objects) ? s.entity_objects.map((x: any) => String(x)) : undefined,
              numeric_objects: Array.isArray(s.numeric_objects) ? s.numeric_objects.map((x: any) => String(x)) : undefined,
              modifier_objects: Array.isArray(s.modifier_objects) ? s.modifier_objects.map((x: any) => String(x)) : undefined,
              objects: Array.isArray(s.objects) ? s.objects.map((x: any) => String(x)) : [],
              purpose: typeof s.purpose === 'string' ? s.purpose : null
            };
            })
        : undefined,
      chains: Array.isArray((e as any).chains)
        ? (e as any).chains
            .filter((c: any) => isObj(c) && typeof c.kind === 'string')
            .map((c: any) => ({
              from_step: Number.isFinite(Number(c.from_step)) ? Number(c.from_step) : undefined,
              to_step: Number.isFinite(Number(c.to_step)) ? Number(c.to_step) : undefined,
              to: typeof c.to === 'string' ? String(c.to) : undefined,
              kind: String(c.kind ?? '')
            }))
        : undefined,
      objects: objects
        .filter((o) => isObj(o) && typeof (o as any).title === 'string')
        .map((o) => ({
          title: String((o as any).title ?? ''),
          source: String((o as any).source ?? ''),
          resolver_hints: Array.isArray((o as any).resolver_hints)
            ? (o as any).resolver_hints
                .filter((h: any) => isObj(h) && typeof h.title === 'string')
                .map((h: any) => ({
                  lane: String(h.lane ?? ''),
                  kind: String(h.kind ?? ''),
                  title: String(h.title ?? ''),
                  score: Number.isFinite(Number(h.score)) ? Number(h.score) : 0
                }))
            : undefined
        })),
      entity_objects: Array.isArray((e as any).entity_objects)
        ? (e as any).entity_objects.map((x: any) => String(x))
        : undefined,
      numeric_objects: Array.isArray((e as any).numeric_objects)
        ? (e as any).numeric_objects.map((x: any) => String(x))
        : undefined,
      modifier_objects: Array.isArray((e as any).modifier_objects)
        ? (e as any).modifier_objects.map((x: any) => String(x))
        : undefined,
      citations: Array.isArray((e as any).citations)
        ? (e as any).citations
            .filter((c: any) => isObj(c) && typeof c.text === 'string')
            .map((c: any) => ({
              text: String(c.text ?? ''),
              kind: typeof c.kind === 'string' ? String(c.kind) : undefined,
              source: typeof c.source === 'string' ? String(c.source) : undefined,
              targets: Array.isArray(c.targets) ? c.targets.map((x: any) => Number(x)).filter((x: number) => Number.isFinite(x)) : undefined,
              follower_order: Array.isArray(c.follower_order) ? c.follower_order.map((x: any) => String(x)) : undefined,
              follow: Array.isArray(c.follow) ? c.follow.filter((x: any) => isObj(x)).map((x: any) => ({ ...x })) : undefined
            }))
        : undefined,
      sl_references: Array.isArray((e as any).sl_references)
        ? (e as any).sl_references
            .filter((r: any) => isObj(r) && (typeof r.text === 'string' || typeof r.lane === 'string'))
            .map((r: any) => ({
              lane: String(r.lane ?? ''),
              authority: typeof r.authority === 'string' ? String(r.authority) : undefined,
              ref_kind: typeof r.ref_kind === 'string' ? String(r.ref_kind) : undefined,
              ref_value: typeof r.ref_value === 'string' ? String(r.ref_value) : undefined,
              text: typeof r.text === 'string' ? String(r.text) : undefined,
              source_document_json: typeof r.source_document_json === 'string' ? String(r.source_document_json) : undefined,
              source_pdf: typeof r.source_pdf === 'string' ? String(r.source_pdf) : undefined,
              provision_stable_id: typeof r.provision_stable_id === 'string' ? String(r.provision_stable_id) : undefined,
              rule_atom_stable_id: typeof r.rule_atom_stable_id === 'string' ? String(r.rule_atom_stable_id) : undefined,
              follower_order: Array.isArray(r.follower_order) ? r.follower_order.map((x: any) => String(x)) : undefined,
              follow: Array.isArray(r.follow) ? r.follow.filter((x: any) => isObj(x)).map((x: any) => ({ ...x })) : undefined
            }))
        : undefined,
      party: typeof (e as any).party === 'string' ? String((e as any).party) : undefined,
      party_source: typeof (e as any).party_source === 'string' ? String((e as any).party_source) : undefined,
      party_evidence: Array.isArray((e as any).party_evidence) ? (e as any).party_evidence.map((x: any) => String(x)) : undefined,
      toc_context: Array.isArray((e as any).toc_context)
        ? (e as any).toc_context
            .filter((t: any) => isObj(t))
            .map((t: any) => ({
              node_type: typeof t.node_type === 'string' ? String(t.node_type) : undefined,
              identifier: typeof t.identifier === 'string' ? String(t.identifier) : undefined,
              title: typeof t.title === 'string' ? String(t.title) : undefined,
              path: typeof t.path === 'string' ? String(t.path) : undefined
            }))
        : undefined,
      legal_section_markers: isObj((e as any).legal_section_markers)
        ? {
            citation_prefixes: Array.isArray((e as any).legal_section_markers.citation_prefixes)
              ? (e as any).legal_section_markers.citation_prefixes.map((x: any) => String(x))
              : undefined,
            sl_reference_lanes: Array.isArray((e as any).legal_section_markers.sl_reference_lanes)
              ? (e as any).legal_section_markers.sl_reference_lanes.map((x: any) => String(x))
              : undefined,
            provision_stable_ids: Array.isArray((e as any).legal_section_markers.provision_stable_ids)
              ? (e as any).legal_section_markers.provision_stable_ids.map((x: any) => String(x))
              : undefined,
            rule_atom_stable_ids: Array.isArray((e as any).legal_section_markers.rule_atom_stable_ids)
              ? (e as any).legal_section_markers.rule_atom_stable_ids.map((x: any) => String(x))
              : undefined
          }
        : undefined,
      timeline_facts: Array.isArray((e as any).timeline_facts)
        ? (e as any).timeline_facts
            .filter((f: any) => isObj(f) && typeof f.fact_id === 'string')
            .map((f: any) => {
              const normalized = normalizeActionAndNegation(f.action, f.negation);
              return {
              fact_id: String(f.fact_id ?? ''),
              event_id: String(f.event_id ?? event_id),
              step_index: Number.isFinite(Number(f.step_index)) ? Number(f.step_index) : undefined,
              anchor: isObj(f.anchor)
                ? {
                    year: Number((f.anchor as any).year ?? 0) || 0,
                    month: Number.isFinite(Number((f.anchor as any).month)) ? Number((f.anchor as any).month) : null,
                    day: Number.isFinite(Number((f.anchor as any).day)) ? Number((f.anchor as any).day) : null,
                    precision: String((f.anchor as any).precision ?? 'year'),
                    text: String((f.anchor as any).text ?? ''),
                    kind: String((f.anchor as any).kind ?? '')
                  }
                : { year: 0, month: null, day: null, precision: 'year', text: '', kind: '' },
              party: typeof f.party === 'string' ? String(f.party) : undefined,
              subjects: Array.isArray(f.subjects) ? f.subjects.map((x: any) => String(x)) : undefined,
              action: normalized.action,
              negation: normalized.negation,
              objects: Array.isArray(f.objects) ? f.objects.map((x: any) => String(x)) : undefined,
              numeric_objects: Array.isArray(f.numeric_objects) ? f.numeric_objects.map((x: any) => String(x)) : undefined,
              purpose: typeof f.purpose === 'string' ? String(f.purpose) : null,
              text: typeof f.text === 'string' ? String(f.text) : undefined,
              prev_fact_ids: Array.isArray(f.prev_fact_ids) ? f.prev_fact_ids.map((x: any) => String(x)) : undefined,
              next_fact_ids: Array.isArray(f.next_fact_ids) ? f.next_fact_ids.map((x: any) => String(x)) : undefined,
              chain_kinds: Array.isArray(f.chain_kinds) ? f.chain_kinds.map((x: any) => String(x)) : undefined
            };
            })
        : undefined,
      purpose: typeof e.purpose === 'string' ? e.purpose : null,
      span_candidates: Array.isArray((e as any).span_candidates)
        ? (e as any).span_candidates
            .filter((c: any) => isObj(c) && typeof c.span_id === 'string' && typeof c.text === 'string')
            .map((c: any) => ({
              span_id: String(c.span_id ?? ''),
              event_id: String(c.event_id ?? event_id),
              span: isObj(c.span)
                ? {
                    kind: String((c.span as any).kind ?? 'event_text'),
                    start: Number((c.span as any).start ?? 0) || 0,
                    end: Number((c.span as any).end ?? 0) || 0,
                    revision_id: typeof (c.span as any).revision_id === 'string' ? String((c.span as any).revision_id) : undefined
                  }
                : { kind: 'event_text', start: 0, end: 0 },
              text: String(c.text ?? ''),
              span_type: String(c.span_type ?? ''),
              recurrence: isObj(c.recurrence) && Number.isFinite(Number((c.recurrence as any).seen_events))
                ? { seen_events: Number((c.recurrence as any).seen_events) }
                : undefined,
              hygiene: isObj(c.hygiene)
                ? {
                    token_count: Number.isFinite(Number((c.hygiene as any).token_count)) ? Number((c.hygiene as any).token_count) : undefined,
                    is_time_expression: typeof (c.hygiene as any).is_time_expression === 'boolean' ? Boolean((c.hygiene as any).is_time_expression) : undefined,
                    overlaps_resolved_entity:
                      typeof (c.hygiene as any).overlaps_resolved_entity === 'boolean' ? Boolean((c.hygiene as any).overlaps_resolved_entity) : undefined,
                    view_score: Number.isFinite(Number((c.hygiene as any).view_score)) ? Number((c.hygiene as any).view_score) : undefined
                  }
                : undefined
            }))
        : undefined,
      warnings: Array.isArray(e.warnings) ? e.warnings.map((x: any) => String(x)) : []
    });
  }

  outEvents.sort((a, b) => {
    const ka = (a.anchor.year || 9999) * 10_000 + (a.anchor.month ?? 99) * 100 + (a.anchor.day ?? 99);
    const kb = (b.anchor.year || 9999) * 10_000 + (b.anchor.month ?? 99) * 100 + (b.anchor.day ?? 99);
    return ka - kb || a.event_id.localeCompare(b.event_id);
  });

  return {
    root_actor: {
      label: typeof (root_actor as any).label === 'string' ? (root_actor as any).label : '',
      surname: typeof (root_actor as any).surname === 'string' ? (root_actor as any).surname : ''
    },
    events: outEvents,
    fact_timeline: Array.isArray(parsed?.fact_timeline)
      ? parsed.fact_timeline
          .filter((f: any) => isObj(f) && typeof f.fact_id === 'string')
          .map((f: any) => {
            const normalized = normalizeActionAndNegation(f.action, f.negation);
            return {
            fact_id: String(f.fact_id ?? ''),
            event_id: String(f.event_id ?? ''),
            step_index: Number.isFinite(Number(f.step_index)) ? Number(f.step_index) : undefined,
            anchor: isObj(f.anchor)
              ? {
                  year: Number((f.anchor as any).year ?? 0) || 0,
                  month: Number.isFinite(Number((f.anchor as any).month)) ? Number((f.anchor as any).month) : null,
                  day: Number.isFinite(Number((f.anchor as any).day)) ? Number((f.anchor as any).day) : null,
                  precision: String((f.anchor as any).precision ?? 'year'),
                  text: String((f.anchor as any).text ?? ''),
                  kind: String((f.anchor as any).kind ?? '')
                }
              : { year: 0, month: null, day: null, precision: 'year', text: '', kind: '' },
            party: typeof f.party === 'string' ? String(f.party) : undefined,
            subjects: Array.isArray(f.subjects) ? f.subjects.map((x: any) => String(x)) : undefined,
            action: normalized.action,
            negation: normalized.negation,
            objects: Array.isArray(f.objects) ? f.objects.map((x: any) => String(x)) : undefined,
            numeric_objects: Array.isArray(f.numeric_objects) ? f.numeric_objects.map((x: any) => String(x)) : undefined,
            purpose: typeof f.purpose === 'string' ? String(f.purpose) : null,
            text: typeof f.text === 'string' ? String(f.text) : undefined
          };
          })
      : undefined,
    parser
  };
}
