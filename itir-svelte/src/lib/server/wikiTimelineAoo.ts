import fs from 'node:fs/promises';
import path from 'node:path';

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

export type AooTimelineFact = {
  fact_id: string;
  event_id: string;
  step_index?: number;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  party?: string;
  subjects?: string[];
  action?: string | null;
  objects?: string[];
  purpose?: string | null;
  text?: string;
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
  steps?: Array<{
    action: string;
    subjects: string[];
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

export async function loadWikiTimelineAoo(repoRoot: string, relPath: string): Promise<WikiTimelineAooPayload> {
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
      action: typeof e.action === 'string' ? e.action : null,
      steps: Array.isArray((e as any).steps)
        ? (e as any).steps
            .filter((s: any) => isObj(s) && typeof s.action === 'string')
            .map((s: any) => ({
              action: String(s.action ?? ''),
              subjects: Array.isArray(s.subjects) ? s.subjects.map((x: any) => String(x)) : [],
              objects: Array.isArray(s.objects) ? s.objects.map((x: any) => String(x)) : [],
              purpose: typeof s.purpose === 'string' ? s.purpose : null
            }))
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
            .map((f: any) => ({
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
              action: typeof f.action === 'string' ? String(f.action) : null,
              objects: Array.isArray(f.objects) ? f.objects.map((x: any) => String(x)) : undefined,
              purpose: typeof f.purpose === 'string' ? String(f.purpose) : null,
              text: typeof f.text === 'string' ? String(f.text) : undefined
            }))
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
          .map((f: any) => ({
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
            action: typeof f.action === 'string' ? String(f.action) : null,
            objects: Array.isArray(f.objects) ? f.objects.map((x: any) => String(x)) : undefined,
            purpose: typeof f.purpose === 'string' ? String(f.purpose) : null,
            text: typeof f.text === 'string' ? String(f.text) : undefined
          }))
      : undefined,
    parser
  };
}
