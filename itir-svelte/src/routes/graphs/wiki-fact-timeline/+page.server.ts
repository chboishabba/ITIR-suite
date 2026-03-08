import path from 'node:path';
import { existsSync } from 'node:fs';

import {
  loadWikiTimelineAoo,
  type AooTimelineFact,
  type AooProposition,
  type AooPropositionLink
} from '$lib/server/wikiTimelineAoo';

const GWB_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_gwb_aoo.json');
const HCA_REL = path.join('SensibLaw', '.cache_local', 'wiki_timeline_hca_s942025_aoo.json');
const LEGAL_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'legal_principles_au_v1',
  'wiki_timeline_legal_principles_au_v1_aoo.json'
);
const LEGAL_FOLLOW_REL = path.join(
  'SensibLaw',
  'demo',
  'ingest',
  'legal_principles_au_v1',
  'follow',
  'wiki_timeline_legal_principles_au_v1_follow_aoo.json'
);

const SOURCE_PATHS = { gwb: GWB_REL, hca: HCA_REL, legal: LEGAL_REL, legal_follow: LEGAL_FOLLOW_REL } as const;

type FactRow = {
  fact_id: string;
  event_id: string;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  event_anchor?: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string } | null;
  anchor_source: 'event' | 'mention';
  party: string;
  subjects: string[];
  action: string | null;
  negation?: { kind: string; scope?: string; source?: string };
  objects: string[];
  purpose: string | null;
  text: string;
  section: string;
  prev_fact_ids: string[];
  next_fact_ids: string[];
  chain_kinds: string[];
};

type PropositionRow = {
  proposition_id: string;
  event_id: string;
  proposition_kind: string;
  predicate_key: string;
  negation?: { kind: string; scope?: string; source?: string };
  source_fact_id?: string;
  source_signal?: string;
  anchor_text?: string;
  arguments: Array<{ role: string; value: string }>;
  receipts: Array<{ kind: string; value: string }>;
};

type PropositionLinkRow = {
  link_id: string;
  event_id: string;
  source_proposition_id: string;
  target_proposition_id: string;
  link_kind: string;
  receipts: Array<{ kind: string; value: string }>;
};

function normText(value: string): string {
  return String(value || '')
    .trim()
    .replace(/\s+/g, ' ')
    .toLowerCase();
}

function normDeterminer(value: string): string {
  const t = normText(value);
  if (!t) return t;
  const parts = t.split(' ').filter(Boolean);
  if (parts.length <= 1) return t;
  const first = String(parts[0] || '').toLowerCase();
  if (first === 'the' || first === 'a' || first === 'an') return parts.slice(1).join(' ');
  return t;
}

function sortedUnique(values: string[]): string[] {
  return Array.from(new Set((values || []).map((x) => String(x)).filter(Boolean))).sort((a, b) => a.localeCompare(b));
}

function factIdentityKey(row: FactRow): string {
  const action = normText(String(row.action || ''));
  const neg = normText(String(row.negation?.kind || ''));
  const subjects = sortedUnique((row.subjects || []).map((s) => normDeterminer(s)));
  const objects = sortedUnique((row.objects || []).map((o) => normDeterminer(o)));
  const kinds = sortedUnique((row.chain_kinds || []).map((k) => normText(k)));
  const a = row.anchor || { year: 0, month: null, day: null, precision: '', kind: '' };
  return JSON.stringify({
    event_id: String(row.event_id || ''),
    anchor: {
      year: Number(a.year || 0),
      month: a.month == null ? null : Number(a.month),
      day: a.day == null ? null : Number(a.day),
      precision: String(a.precision || ''),
      kind: String(a.kind || '')
    },
    action,
    negation_kind: neg,
    subjects,
    objects,
    chain_kinds: kinds
  });
}

function coalesceFactRows(rows: FactRow[]): FactRow[] {
  if (!rows.length) return rows;

  const keyToCanon = new Map<string, FactRow>();
  const factIdAlias = new Map<string, string>();

  for (const row of rows) {
    const key = factIdentityKey(row);
    const current = keyToCanon.get(key);
    if (!current) {
      const base: FactRow = {
        ...row,
        prev_fact_ids: sortedUnique(row.prev_fact_ids || []),
        next_fact_ids: sortedUnique(row.next_fact_ids || []),
        chain_kinds: sortedUnique(row.chain_kinds || [])
      };
      keyToCanon.set(key, base);
      factIdAlias.set(String(row.fact_id), String(base.fact_id));
      continue;
    }
    factIdAlias.set(String(row.fact_id), String(current.fact_id));
    current.prev_fact_ids = sortedUnique([...(current.prev_fact_ids || []), ...(row.prev_fact_ids || [])]);
    current.next_fact_ids = sortedUnique([...(current.next_fact_ids || []), ...(row.next_fact_ids || [])]);
    current.chain_kinds = sortedUnique([...(current.chain_kinds || []), ...(row.chain_kinds || [])]);
  }

  const out = Array.from(keyToCanon.values());
  const canonIds = new Set(out.map((r) => String(r.fact_id)));
  for (const row of out) {
    const self = String(row.fact_id);
    row.prev_fact_ids = sortedUnique((row.prev_fact_ids || []).map((x) => factIdAlias.get(String(x)) || String(x)))
      .filter((x) => x !== self && canonIds.has(x));
    row.next_fact_ids = sortedUnique((row.next_fact_ids || []).map((x) => factIdAlias.get(String(x)) || String(x)))
      .filter((x) => x !== self && canonIds.has(x));
    row.chain_kinds = sortedUnique(row.chain_kinds || []);
  }
  return out;
}

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

function keyForAnchor(a: { year: number; month: number | null; day: number | null }): number {
  return (a.year || 9999) * 10_000 + (a.month ?? 99) * 100 + (a.day ?? 99);
}

function normalizeAnchor(raw: any): { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string } {
  return {
    year: Number(raw?.year ?? 0) || 0,
    month: Number.isFinite(Number(raw?.month)) ? Number(raw?.month) : null,
    day: Number.isFinite(Number(raw?.day)) ? Number(raw?.day) : null,
    precision: String(raw?.precision ?? 'year'),
    text: String(raw?.text ?? ''),
    kind: String(raw?.kind ?? '')
  };
}

function sameAnchor(
  a: { year: number; month: number | null; day: number | null },
  b: { year: number; month: number | null; day: number | null }
): boolean {
  return Number(a.year || 0) === Number(b.year || 0)
    && Number(a.month ?? -1) === Number(b.month ?? -1)
    && Number(a.day ?? -1) === Number(b.day ?? -1);
}

function coerceFactRow(
  raw: AooTimelineFact,
  sectionByEvent: Map<string, string>,
  textByEvent: Map<string, string>,
  eventAnchorByEvent: Map<string, { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string }>
): FactRow {
  const mentionAnchor = normalizeAnchor(raw.anchor);
  const eventId = String(raw.event_id || '');
  const eventAnchor = eventAnchorByEvent.get(eventId);
  const mentionValid = Number(mentionAnchor.year || 0) > 0;
  const useEvent = !mentionValid && Boolean(eventAnchor && Number(eventAnchor.year || 0) > 0);
  const primaryAnchor = mentionValid ? mentionAnchor : (useEvent ? (eventAnchor as typeof mentionAnchor) : mentionAnchor);
  const eventOut = eventAnchor && !sameAnchor(primaryAnchor, eventAnchor) ? eventAnchor : null;
  return {
    fact_id: String(raw.fact_id || ''),
    event_id: eventId,
    anchor: primaryAnchor,
    event_anchor: eventOut,
    anchor_source: useEvent ? 'event' : 'mention',
    party: String(raw.party ?? ''),
    subjects: Array.isArray(raw.subjects) ? raw.subjects.map((x) => String(x)).filter(Boolean) : [],
    action: typeof raw.action === 'string' ? raw.action : null,
    negation: raw.negation && typeof raw.negation.kind === 'string'
      ? { kind: String(raw.negation.kind), scope: raw.negation.scope, source: raw.negation.source }
      : undefined,
    objects: Array.isArray(raw.objects) ? raw.objects.map((x) => String(x)).filter(Boolean) : [],
    purpose: typeof raw.purpose === 'string' ? raw.purpose : null,
    text: String(raw.text ?? textByEvent.get(eventId) ?? ''),
    section: String(sectionByEvent.get(eventId) ?? ''),
    prev_fact_ids: Array.isArray(raw.prev_fact_ids) ? raw.prev_fact_ids.map((x) => String(x)).filter(Boolean) : [],
    next_fact_ids: Array.isArray(raw.next_fact_ids) ? raw.next_fact_ids.map((x) => String(x)).filter(Boolean) : [],
    chain_kinds: Array.isArray(raw.chain_kinds) ? raw.chain_kinds.map((x) => String(x)).filter(Boolean) : []
  };
}

function synthesizeFactsFromEvents(payload: Awaited<ReturnType<typeof loadWikiTimelineAoo>>): AooTimelineFact[] {
  const rows: AooTimelineFact[] = [];
  for (const e of payload.events) {
    const steps = Array.isArray(e.steps) && e.steps.length
      ? e.steps
      : [{
          action: e.action ?? null,
          subjects: e.actors.filter((a) => (a.role ?? '') !== 'requester').map((a) => a.resolved || a.label),
          objects: e.objects.map((o) => o.title),
          purpose: e.purpose ?? null
        }];
    const eventRows: AooTimelineFact[] = [];
    const factIdByStep = new Map<number, string>();
    for (let i = 0; i < steps.length; i++) {
      const s = steps[i] as any;
      const subjects = Array.isArray(s?.subjects) ? s.subjects.map((x: any) => String(x)).filter(Boolean) : [];
      const objects = Array.isArray(s?.objects) ? s.objects.map((x: any) => String(x)).filter(Boolean) : [];
      const action = typeof s?.action === 'string' ? s.action : null;
      if (!action && !subjects.length && !objects.length) continue;
      const factId = `${e.event_id}:f${String(i + 1).padStart(2, '0')}`;
      const row: AooTimelineFact = {
        fact_id: factId,
        event_id: e.event_id,
        step_index: i,
        anchor: e.anchor,
        party: e.party ?? '',
        subjects,
        action,
        negation: s?.negation && typeof s.negation.kind === 'string'
          ? { kind: String(s.negation.kind), scope: s.negation.scope, source: s.negation.source }
          : undefined,
        objects,
        purpose: typeof s?.purpose === 'string' ? s.purpose : (e.purpose ?? null),
        text: e.text,
        prev_fact_ids: [],
        next_fact_ids: [],
        chain_kinds: []
      };
      factIdByStep.set(i, factId);
      eventRows.push(row);
    }
    const byFactId = new Map(eventRows.map((r) => [String(r.fact_id), r]));
    for (let i = 0; i < eventRows.length - 1; i++) {
      const cur = eventRows[i];
      const nxt = eventRows[i + 1];
      if (!cur || !nxt) continue;
      const from = String(cur.fact_id);
      const to = String(nxt.fact_id);
      cur.next_fact_ids = Array.from(new Set([...(cur.next_fact_ids ?? []), to]));
      cur.chain_kinds = Array.from(new Set([...(cur.chain_kinds ?? []), 'sequence']));
      nxt.prev_fact_ids = Array.from(new Set([...(nxt.prev_fact_ids ?? []), from]));
    }
    if (Array.isArray((e as any).chains)) {
      for (const c of (e as any).chains) {
        const fromStep = Number.isFinite(Number(c?.from_step)) ? Number(c.from_step) : null;
        const toStep = Number.isFinite(Number(c?.to_step)) ? Number(c.to_step) : null;
        if (fromStep === null || toStep === null) continue;
        const fromFact = factIdByStep.get(fromStep);
        const toFact = factIdByStep.get(toStep);
        if (!fromFact || !toFact) continue;
        const fromRow = byFactId.get(fromFact);
        const toRow = byFactId.get(toFact);
        const kind = String(c?.kind ?? 'sequence');
        if (!fromRow || !toRow) continue;
        fromRow.next_fact_ids = Array.from(new Set([...(fromRow.next_fact_ids ?? []), toFact]));
        fromRow.chain_kinds = Array.from(new Set([...(fromRow.chain_kinds ?? []), kind]));
        toRow.prev_fact_ids = Array.from(new Set([...(toRow.prev_fact_ids ?? []), fromFact]));
      }
    }
    rows.push(...eventRows);
  }
  return rows;
}

function coerceProposition(raw: AooProposition): PropositionRow | null {
  const proposition_id = String(raw.proposition_id || '');
  const event_id = String(raw.event_id || '');
  const proposition_kind = String(raw.proposition_kind || '');
  const predicate_key = String(raw.predicate_key || '');
  if (!proposition_id || !event_id || !proposition_kind || !predicate_key) return null;
  return {
    proposition_id,
    event_id,
    proposition_kind,
    predicate_key,
    negation: raw.negation && typeof raw.negation.kind === 'string'
      ? { kind: String(raw.negation.kind), scope: raw.negation.scope, source: raw.negation.source }
      : undefined,
    source_fact_id: typeof raw.source_fact_id === 'string' ? String(raw.source_fact_id) : undefined,
    source_signal: typeof raw.source_signal === 'string' ? String(raw.source_signal) : undefined,
    anchor_text: typeof raw.anchor_text === 'string' ? String(raw.anchor_text) : undefined,
    arguments: Array.isArray(raw.arguments)
      ? raw.arguments
          .filter((arg) => typeof arg?.role === 'string' && typeof arg?.value === 'string')
          .map((arg) => ({ role: String(arg.role), value: String(arg.value) }))
      : [],
    receipts: Array.isArray(raw.receipts)
      ? raw.receipts
          .filter((receipt) => typeof receipt?.kind === 'string' && typeof receipt?.value === 'string')
          .map((receipt) => ({ kind: String(receipt.kind), value: String(receipt.value) }))
      : []
  };
}

function coercePropositionLink(raw: AooPropositionLink): PropositionLinkRow | null {
  const link_id = String(raw.link_id || '');
  const event_id = String(raw.event_id || '');
  const source_proposition_id = String(raw.source_proposition_id || '');
  const target_proposition_id = String(raw.target_proposition_id || '');
  const link_kind = String(raw.link_kind || '');
  if (!link_id || !event_id || !source_proposition_id || !target_proposition_id || !link_kind) return null;
  return {
    link_id,
    event_id,
    source_proposition_id,
    target_proposition_id,
    link_kind,
    receipts: Array.isArray(raw.receipts)
      ? raw.receipts
          .filter((receipt) => typeof receipt?.kind === 'string' && typeof receipt?.value === 'string')
          .map((receipt) => ({ kind: String(receipt.kind), value: String(receipt.value) }))
      : []
  };
}

export async function load({ url }: { url: URL }) {
  const repoRoot = resolveRepoRoot();
  const source = (url.searchParams.get('source') || 'hca').toLowerCase();
  const rel = SOURCE_PATHS[source as keyof typeof SOURCE_PATHS] ?? HCA_REL;
  try {
    const payload = await loadWikiTimelineAoo(repoRoot, rel);
    const sectionByEvent = new Map(payload.events.map((e) => [e.event_id, e.section || '']));
    const textByEvent = new Map(payload.events.map((e) => [e.event_id, e.text || '']));
    const eventAnchorByEvent = new Map(
      payload.events.map((e) => [
        e.event_id,
        normalizeAnchor(e.anchor)
      ])
    );

    let factRowSource: 'native_fact_timeline' | 'nested_event_timeline_facts' | 'synthesized_from_steps' = 'native_fact_timeline';
    let rawFacts: AooTimelineFact[] = [];
    if (Array.isArray(payload.fact_timeline) && payload.fact_timeline.length) {
      rawFacts = payload.fact_timeline;
      factRowSource = 'native_fact_timeline';
    } else {
      const nested = payload.events.flatMap((e) => Array.isArray(e.timeline_facts) ? e.timeline_facts : []);
      if (nested.length) {
        rawFacts = nested;
        factRowSource = 'nested_event_timeline_facts';
      } else {
        rawFacts = synthesizeFactsFromEvents(payload);
        factRowSource = 'synthesized_from_steps';
      }
    }

    const facts = coalesceFactRows(
      rawFacts
      .map((f) => coerceFactRow(f, sectionByEvent, textByEvent, eventAnchorByEvent))
      .filter((f) => Boolean(f.fact_id) && Boolean(f.event_id))
      .sort((a, b) => keyForAnchor(a.anchor) - keyForAnchor(b.anchor) || a.fact_id.localeCompare(b.fact_id))
    );
    const propositions = Array.isArray(payload.propositions)
      ? payload.propositions.map(coerceProposition).filter(Boolean) as PropositionRow[]
      : [];
    const proposition_links = Array.isArray(payload.proposition_links)
      ? payload.proposition_links.map(coercePropositionLink).filter(Boolean) as PropositionLinkRow[]
      : [];

    return {
      payload: {
        root_actor: payload.root_actor,
        parser: payload.parser ?? null,
        facts,
        propositions,
        proposition_links,
        diagnostics: {
          event_count: payload.events.length,
          fact_row_source: factRowSource,
          raw_fact_rows: rawFacts.length,
          output_fact_rows: facts.length
        }
      },
      relPath: rel,
      source,
      error: null as string | null
    };
  } catch (e) {
    return {
      payload: {
        root_actor: { label: '', surname: '' },
        parser: null,
        facts: [] as FactRow[],
        propositions: [] as PropositionRow[],
        proposition_links: [] as PropositionLinkRow[],
        diagnostics: {
          event_count: 0,
          fact_row_source: 'native_fact_timeline',
          raw_fact_rows: 0,
          output_fact_rows: 0
        }
      },
      relPath: rel,
      source,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
