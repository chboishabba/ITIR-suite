<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';
  import { afterUpdate } from 'svelte';

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      events: Array<{
        event_id: string;
        anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
        section: string;
        text: string;
        actors: Array<{ label: string; resolved: string; role: string; source: string }>;
        action: string | null;
        negation?: { kind: string; scope?: string; source?: string };
        objects: Array<{ title: string; source: string }>;
        entity_objects?: string[];
        numeric_objects?: string[];
        modifier_objects?: string[];
        steps?: Array<{
          action: string;
          negation?: { kind: string; scope?: string; source?: string };
          subjects?: string[];
          entity_objects?: string[];
          numeric_objects?: string[];
          modifier_objects?: string[];
          objects?: string[];
          purpose?: string | null;
        }>;
        citations?: Array<{
          text: string;
          kind?: string;
          follower_order?: string[];
          follow?: Array<{ provider?: string; mode?: string; url?: string; path?: string; script?: string }>;
        }>;
        sl_references?: Array<{
          text?: string;
          lane?: string;
          authority?: string;
          ref_value?: string;
          follower_order?: string[];
          follow?: Array<{ provider?: string; mode?: string; url?: string; path?: string; script?: string }>;
        }>;
        party?: string;
        toc_context?: Array<{ node_type?: string; identifier?: string; title?: string; path?: string }>;
        legal_section_markers?: {
          citation_prefixes?: string[];
          sl_reference_lanes?: string[];
          provision_stable_ids?: string[];
          rule_atom_stable_ids?: string[];
        };
        timeline_facts?: Array<{
          fact_id: string;
          anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
          subjects?: string[];
          action?: string | null;
          negation?: { kind: string; scope?: string; source?: string };
          objects?: string[];
          numeric_objects?: string[];
          party?: string;
        }>;
        purpose: string | null;
        warnings: string[];
      }>;
    };
    relPath: string;
    source?: string;
    error: string | null;
  };

  type TimeGranularity = 'year' | 'month' | 'day';
  let timeGranularity: TimeGranularity = 'month';
  let limitEvents = 80;
  let maxSubjects = 120;
  let maxObjects = 160;
  let maxNumbers = 120;
  let maxEvidence = 140;
  let includeRequesters = true;
  let includePurpose = false;
  let includeEvidence = false;
  let orderByFactDate = false;
  let showAllContextRows = false;

  let selectedNodeId: string | null = null;
  let contextBox: HTMLDivElement | null = null;
  let lastScrollKey = '';

  function node(id: string, label: string, color: string, tooltip?: string): LayerNode {
    const short = label.length > 54 ? label.slice(0, 54) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label };
  }

  function pad2(n: number): string {
    return String(n).padStart(2, '0');
  }

  function fmtYM(a: { year: number; month: number | null }): string {
    const y = a.year || 0;
    const m = a.month ?? null;
    if (!m) return String(y);
    return `${y}-${pad2(m)}`;
  }

  function fmtYMD(a: { year: number; month: number | null; day: number | null }): string {
    const y = a.year || 0;
    const m = a.month ?? null;
    const d = a.day ?? null;
    if (!m) return String(y);
    if (!d) return `${y}-${pad2(m)}`;
    return `${y}-${pad2(m)}-${pad2(d)}`;
  }

  $: eventsAll = data.payload.events ?? [];
  $: events = eventsAll.slice(0, Math.max(10, Math.min(eventsAll.length, Math.floor(limitEvents))));

  type CtxRow = {
    key: string;
    event_id: string;
    time: string;
    section: string;
    text: string;
    requesters: string[];
    subjects: string[];
    action: string | null;
    negation?: { kind: string; scope?: string; source?: string };
    actions: string[];
    objects: string[];
    numerics: string[];
    citations: string[];
    checkNext: string[];
    slRefs: string[];
    party: string;
    tocContext: string[];
    legalMarkers: string[];
    factRows: string[];
    sortTime: string;
    connected: string[];
    purpose: string | null;
  };

  function uniqueStrings(xs: any[]): string[] {
    const out = new Set<string>();
    for (const x of xs ?? []) {
      const s = String(x ?? '').trim();
      if (s) out.add(s);
    }
    return Array.from(out);
  }

  function actionLabel(action: string | null | undefined, negation?: { kind?: string | null }): string {
    const base = String(action ?? '').trim();
    if (!base) return '(no action matched)';
    if (String(negation?.kind ?? '').toLowerCase() === 'not') return `not_${base}`;
    return base;
  }

  function stepEntityObjects(step: any): string[] {
    if (Array.isArray(step?.entity_objects)) return step.entity_objects.map((x: any) => String(x)).filter(Boolean);
    if (Array.isArray(step?.objects)) return step.objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  function eventEntityObjects(e: any): string[] {
    if (Array.isArray(e?.entity_objects)) return e.entity_objects.map((x: any) => String(x)).filter(Boolean);
    if (Array.isArray(e?.objects)) return e.objects.map((o: any) => String(o?.title ?? '')).filter(Boolean);
    return [];
  }

  function stepNumericObjects(step: any): string[] {
    if (Array.isArray(step?.numeric_objects)) return step.numeric_objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  function eventNumericObjects(e: any): string[] {
    if (Array.isArray(e?.numeric_objects)) return e.numeric_objects.map((x: any) => String(x)).filter(Boolean);
    return [];
  }

  const DEFAULT_FOLLOW_ORDER = ['wikipedia', 'wiki_connector', 'austlii', 'jade', 'source_document', 'source_pdf'];

  function collectFollowProviders(rows: any[]): string[] {
    const out: string[] = [];
    for (const row of rows ?? []) {
      if (!row || typeof row !== 'object') continue;
      if (Array.isArray((row as any).follower_order)) {
        for (const x of (row as any).follower_order) out.push(String(x ?? '').trim());
      }
      if (Array.isArray((row as any).follow)) {
        for (const h of (row as any).follow) {
          const p = String((h as any)?.provider ?? '').trim();
          if (p) out.push(p);
        }
      }
    }
    return uniqueStrings(out);
  }

  function evidenceLabelsFromEvent(e: any): string[] {
    const citationTexts = Array.isArray(e?.citations)
      ? (e.citations as any[])
          .map((c: any) => String(c?.text ?? '').trim())
          .filter(Boolean)
      : [];
    const slRefTexts = Array.isArray(e?.sl_references)
      ? (e.sl_references as any[])
          .map((r: any) => {
            const t = String(r?.text ?? '').trim();
            if (t) return t;
            const auth = String(r?.authority ?? '').trim();
            const ref = String(r?.ref_value ?? '').trim();
            return `${auth} ${ref}`.trim();
          })
          .filter(Boolean)
      : [];
    return uniqueStrings([...citationTexts, ...slRefTexts]);
  }

  function keyFromNodeId(id: string): { kind: string; key: string } {
    const m = /^([a-z]+):(.+)$/.exec(id);
    if (!m) return { kind: 'other', key: id };
    const kind = m[1] ?? 'other';
    const key = m[2] ?? id;
    return { kind, key };
  }

  function timeKeyForEvent(e: { anchor: { year: number; month: number | null; day: number | null } }, g: TimeGranularity): string {
    const y = String(e.anchor.year || 0);
    if (g === 'year') return y;
    const m = e.anchor.month ?? null;
    if (!m) return y;
    const ym = `${y}-${pad2(m)}`;
    if (g === 'month') return ym;
    const d = e.anchor.day ?? null;
    if (!d) return ym;
    return `${ym}-${pad2(d)}`;
  }

  function factAnchorKey(a: any): string {
    const y = String(a?.year ?? 0);
    const m = typeof a?.month === 'number' ? pad2(a.month) : '99';
    const d = typeof a?.day === 'number' ? pad2(a.day) : '99';
    return `${y}-${m}-${d}`;
  }

  function eventMatchesNode(e: any, nodeId: string): boolean {
    if (!nodeId) return false;
    if (nodeId.startsWith('act:')) return nodeId === `act:${e.event_id}`;

    if (nodeId.startsWith('sub:')) {
      const key = nodeId.slice('sub:'.length);
      const stepSubs = Array.isArray((e as any).steps)
        ? (e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : []))
        : [];
      if (stepSubs.length) return stepSubs.some((x: any) => String(x) === key);
      return (e.actors ?? []).some((a: any) => (a.role ?? '') !== 'requester' && (a.resolved ?? a.label) === key);
    }
    if (nodeId.startsWith('req:')) {
      const key = nodeId.slice('req:'.length);
      return (e.actors ?? []).some((a: any) => (a.role ?? '') === 'requester' && (a.resolved ?? a.label) === key);
    }
    if (nodeId.startsWith('obj:')) {
      const key = nodeId.slice('obj:'.length);
      const stepObjs = Array.isArray((e as any).steps)
        ? (e as any).steps.flatMap((s: any) => stepEntityObjects(s))
        : [];
      if (stepObjs.length) return stepObjs.some((x: any) => String(x) === key);
      return eventEntityObjects(e).some((x: any) => String(x) === key);
    }
    if (nodeId.startsWith('num:')) {
      const key = nodeId.slice('num:'.length);
      const stepNums = Array.isArray((e as any).steps)
        ? (e as any).steps.flatMap((s: any) => stepNumericObjects(s))
        : [];
      if (stepNums.length) return stepNums.some((x: any) => String(x) === key);
      return eventNumericObjects(e).some((x: any) => String(x) === key);
    }
    if (nodeId.startsWith('evd:')) {
      const key = nodeId.slice('evd:'.length);
      return evidenceLabelsFromEvent(e).includes(key);
    }

    if (nodeId.startsWith('time:y:')) {
      const key = nodeId.slice('time:y:'.length);
      return String(e.anchor?.year ?? 0) === key;
    }
    if (nodeId.startsWith('time:m:')) {
      const key = nodeId.slice('time:m:'.length);
      const y = String(e.anchor?.year ?? 0);
      const m = e.anchor?.month ?? null;
      const ym = m ? `${y}-${pad2(m)}` : y;
      return ym === key;
    }
    if (nodeId.startsWith('time:d:')) {
      const key = nodeId.slice('time:d:'.length);
      const ymd = timeKeyForEvent(e, 'day');
      return ymd === key;
    }

    if (nodeId.startsWith('pur:')) return nodeId === `pur:${e.event_id}`;
    return false;
  }

  function highlightParts(text: string, needle: string): Array<{ s: string; hit: boolean }> {
    const t = String(text ?? '');
    const n = String(needle ?? '').trim();
    if (!n) return [{ s: t, hit: false }];
    const lower = t.toLowerCase();
    const nl = n.toLowerCase();
    const out: Array<{ s: string; hit: boolean }> = [];
    let i = 0;
    while (i < t.length) {
      const j = lower.indexOf(nl, i);
      if (j < 0) {
        out.push({ s: t.slice(i), hit: false });
        break;
      }
      if (j > i) out.push({ s: t.slice(i, j), hit: false });
      out.push({ s: t.slice(j, j + n.length), hit: true });
      i = j + n.length;
    }
    return out.length ? out : [{ s: t, hit: false }];
  }

  $: contextRows = (() => {
    if (!selectedNodeId) return [] as CtxRow[];
    const { kind, key } = keyFromNodeId(selectedNodeId);
    const rows: CtxRow[] = [];
    for (const e of events) {
      if (!eventMatchesNode(e, selectedNodeId)) continue;
      const reqs = (e.actors ?? []).filter((a: any) => (a.role ?? '') === 'requester').map((a: any) => String(a.resolved ?? a.label ?? '')).filter(Boolean);
      const stepSubs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : [])))
        : [];
      const subs = stepSubs.length
        ? stepSubs
        : (e.actors ?? []).filter((a: any) => (a.role ?? '') !== 'requester').map((a: any) => String(a.resolved ?? a.label ?? '')).filter(Boolean);
      const stepObjs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepEntityObjects(s)))
        : [];
      const objs = stepObjs.length
        ? stepObjs
        : eventEntityObjects(e);
      const stepNums = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepNumericObjects(s)))
        : [];
      const nums = stepNums.length
        ? stepNums
        : eventNumericObjects(e);
      const stepActs = Array.isArray((e as any).steps)
        ? (e as any).steps.map((s: any) => actionLabel(s?.action, s?.negation)).filter(Boolean)
        : [];
      const citations = Array.isArray((e as any).citations)
        ? uniqueStrings((e as any).citations.map((c: any) => String(c?.text ?? '')).filter(Boolean))
        : [];
      const citationFollowers = Array.isArray((e as any).citations) ? collectFollowProviders((e as any).citations) : [];
      const slRefs = Array.isArray((e as any).sl_references)
        ? uniqueStrings(
            (e as any).sl_references
              .map((r: any) => String(r?.text ?? `${r?.authority ?? ''} ${r?.ref_value ?? ''}`.trim()))
              .filter(Boolean)
          )
        : [];
      const slRefFollowers = Array.isArray((e as any).sl_references) ? collectFollowProviders((e as any).sl_references) : [];
      const party = String((e as any).party ?? '').trim();
      const tocContext = Array.isArray((e as any).toc_context)
        ? uniqueStrings(
            (e as any).toc_context
              .map((t: any) => String(t?.path ?? `${t?.identifier ?? ''} ${t?.title ?? ''}`.trim()))
              .filter(Boolean)
          )
        : [];
      const legalMarkers = (() => {
        const m = (e as any).legal_section_markers;
        if (!m || typeof m !== 'object') return [] as string[];
        return uniqueStrings([
          ...((Array.isArray(m.citation_prefixes) ? m.citation_prefixes : []).map((x: any) => `cit:${String(x)}`)),
          ...((Array.isArray(m.sl_reference_lanes) ? m.sl_reference_lanes : []).map((x: any) => `lane:${String(x)}`)),
          ...((Array.isArray(m.provision_stable_ids) ? m.provision_stable_ids : []).map((x: any) => `prov:${String(x)}`)),
          ...((Array.isArray(m.rule_atom_stable_ids) ? m.rule_atom_stable_ids : []).map((x: any) => `atom:${String(x)}`))
        ]);
      })();
      const hasLegalSignals = legalMarkers.length > 0 || slRefs.length > 0;
      const checkNext = uniqueStrings([
        ...citationFollowers,
        ...slRefFollowers,
        ...(citations.length || slRefs.length ? ['wikipedia', 'wiki_connector', 'source_document', 'source_pdf'] : []),
        ...(hasLegalSignals ? ['austlii', 'jade'] : []),
        ...(citations.length || slRefs.length ? DEFAULT_FOLLOW_ORDER : [])
      ]);
      const factRows = Array.isArray((e as any).timeline_facts)
        ? uniqueStrings(
            (e as any).timeline_facts.map((f: any) => {
              const fa = factAnchorKey(f?.anchor);
              const subs = Array.isArray(f?.subjects) ? f.subjects.join(', ') : '';
              const act = actionLabel(f?.action, f?.negation);
              const objs = Array.isArray(f?.objects) ? f.objects.join(', ') : '';
              const nums = Array.isArray(f?.numeric_objects) ? f.numeric_objects.join(', ') : '';
              return `${fa} | ${subs}${act && act !== '(no action matched)' ? ' -> ' + act : ''}${objs ? ' -> ' + objs : ''}${nums ? ' -> #' + nums : ''}`.trim();
            })
          )
        : [];
      const firstFactTime = Array.isArray((e as any).timeline_facts) && (e as any).timeline_facts.length
        ? factAnchorKey((e as any).timeline_facts[0]?.anchor)
        : '';
      const connected = uniqueStrings([
        ...reqs.map((x: string) => `req:${x}`),
        ...subs.map((x: string) => `sub:${x}`),
        ...stepActs.map((x: string) => `act:${x}`),
        ...objs.map((x: string) => `obj:${x}`),
        ...nums.map((x: string) => `num:${x}`),
        ...evidenceLabelsFromEvent(e).map((x: string) => `evd:${x}`)
      ]);
      rows.push({
        key: `${selectedNodeId}:${e.event_id}`,
        event_id: e.event_id,
        time: timeKeyForEvent(e, timeGranularity),
        section: e.section ?? '',
        text: e.text ?? '',
        requesters: reqs,
        subjects: subs,
        action: typeof e.action === 'string' ? e.action : null,
        negation: (e as any).negation && typeof (e as any).negation.kind === 'string' ? (e as any).negation : undefined,
        actions: stepActs,
        objects: objs,
        numerics: nums,
        citations,
        checkNext,
        slRefs,
        party,
        tocContext,
        legalMarkers,
        factRows,
        sortTime: firstFactTime || timeKeyForEvent(e, 'day'),
        connected,
        purpose: typeof e.purpose === 'string' ? e.purpose : null
      });
    }
    // Keep chronological-ish by time bucket, then event_id.
    if (orderByFactDate) {
      rows.sort((a, b) => a.sortTime.localeCompare(b.sortTime) || a.event_id.localeCompare(b.event_id));
    } else {
      rows.sort((a, b) => a.time.localeCompare(b.time) || a.event_id.localeCompare(b.event_id));
    }
    return rows;
  })();

  $: contextRowsShown = showAllContextRows ? contextRows : contextRows.slice(0, 80);

  $: contextNeedle = (() => {
    const id = selectedNodeId ?? '';
    if (!id) return '';
    if (id.startsWith('time:')) return id.split(':').slice(-1)[0] ?? '';
    if (id.startsWith('act:')) return '';
    if (id.startsWith('sub:')) return id.slice('sub:'.length);
    if (id.startsWith('req:')) return id.slice('req:'.length);
    if (id.startsWith('obj:')) return id.slice('obj:'.length);
    if (id.startsWith('num:')) return id.slice('num:'.length);
    if (id.startsWith('evd:')) return id.slice('evd:'.length);
    return '';
  })();

  afterUpdate(() => {
    if (!contextBox || !selectedNodeId) return;
    const k = `${selectedNodeId}:${contextRowsShown[0]?.event_id ?? ''}`;
    if (!k || k === lastScrollKey) return;
    lastScrollKey = k;
    const first = contextRowsShown[0];
    if (!first) return;
    const el = contextBox.querySelector(`[data-ctx-id="${first.event_id}"]`);
    if (el && 'scrollIntoView' in el) (el as HTMLElement).scrollIntoView({ block: 'center' });
  });

  $: graph = (() => {
    const yearNodes = new Map<string, LayerNode>();
    const monthNodes = new Map<string, LayerNode>();
    const dayNodes = new Map<string, LayerNode>();

    const subjectCount = new Map<string, number>();
    const objectCount = new Map<string, number>();
    const numericCount = new Map<string, number>();
    const requesterCount = new Map<string, number>();
    const evidenceCount = new Map<string, number>();

    for (const e of events) {
      const y = String(e.anchor.year || 0);
      yearNodes.set(y, node(`time:y:${y}`, y, '#e8f4ff', 'Year bucket (non-authoritative)'));
      if (timeGranularity !== 'year' && e.anchor.month) {
        const ym = fmtYM(e.anchor);
        monthNodes.set(ym, node(`time:m:${ym}`, ym, '#e8f4ff', 'Month bucket (non-authoritative)'));
      }
      if (timeGranularity === 'day' && e.anchor.month && e.anchor.day) {
        const ymd = fmtYMD(e.anchor);
        dayNodes.set(ymd, node(`time:d:${ymd}`, ymd, '#e8f4ff', 'Day bucket (non-authoritative)'));
      }

      for (const a of e.actors ?? []) {
        const key = a.resolved || a.label;
        if (!key) continue;
        if (a.role === 'requester') requesterCount.set(key, (requesterCount.get(key) ?? 0) + 1);
      }
      const stepSubs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : [])))
        : [];
      const uniqueSubs = stepSubs.length
        ? stepSubs
        : uniqueStrings((e.actors ?? []).filter((a: any) => (a.role ?? '') !== 'requester').map((a: any) => a.resolved ?? a.label));
      for (const key of uniqueSubs) subjectCount.set(key, (subjectCount.get(key) ?? 0) + 1);
      const stepObjsForCounts = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepEntityObjects(s)))
        : [];
      const objKeys = stepObjsForCounts.length
        ? stepObjsForCounts
        : uniqueStrings(eventEntityObjects(e));
      for (const key of objKeys) objectCount.set(key, (objectCount.get(key) ?? 0) + 1);
      const stepNumsForCounts = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepNumericObjects(s)))
        : [];
      const numKeys = stepNumsForCounts.length
        ? stepNumsForCounts
        : uniqueStrings(eventNumericObjects(e));
      for (const key of numKeys) numericCount.set(key, (numericCount.get(key) ?? 0) + 1);
      for (const ev of evidenceLabelsFromEvent(e)) evidenceCount.set(ev, (evidenceCount.get(ev) ?? 0) + 1);
    }

    const top = (m: Map<string, number>, n: number) =>
      Array.from(m.entries())
        .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
        .slice(0, Math.max(0, Math.floor(n)));

    const topSubjects = top(subjectCount, maxSubjects);
    const topObjects = top(objectCount, maxObjects);
    const topNumbers = top(numericCount, maxNumbers);
    const topRequesters = includeRequesters ? top(requesterCount, Math.min(60, maxSubjects)) : [];
    const topEvidence = includeEvidence ? top(evidenceCount, maxEvidence) : [];

    const subjectSet = new Set(topSubjects.map(([k]) => k));
    const objectSet = new Set(topObjects.map(([k]) => k));
    const numericSet = new Set(topNumbers.map(([k]) => k));
    const requesterSet = new Set(topRequesters.map(([k]) => k));
    const evidenceSet = new Set(topEvidence.map(([k]) => k));

    const requesterNodes = topRequesters.map(([k, c]) => node(`req:${k}`, `${k} (${c})`, '#e9d5ff'));
    const subjectNodes = topSubjects.map(([k, c]) => node(`sub:${k}`, `${k} (${c})`, '#bbf7d0'));
    const objectNodes = topObjects.map(([k, c]) => node(`obj:${k}`, `${k} (${c})`, '#f6f6f6'));
    const numericNodes = topNumbers.map(([k, c]) => node(`num:${k}`, `${k} (${c})`, '#fee2e2'));
    const evidenceNodes = topEvidence.map(([k, c]) => node(`evd:${k}`, `${k} (${c})`, '#dbeafe'));

    const actionNodes: LayerNode[] = [];
    const purposeNodes: LayerNode[] = [];

    const edges: LayeredEdge[] = [];

    // Time chain edges (unique, no per-event duplication).
    if (timeGranularity !== 'year') {
      for (const ym of monthNodes.keys()) {
        const y = ym.split('-')[0] ?? ym;
        edges.push({ from: `time:y:${y}`, to: `time:m:${ym}`, kind: 'sequence' });
      }
    }
    if (timeGranularity === 'day') {
      for (const ymd of dayNodes.keys()) {
        const ym = ymd.slice(0, 7);
        edges.push({ from: `time:m:${ym}`, to: `time:d:${ymd}`, kind: 'sequence' });
      }
    }

    for (const e of events) {
      const actionText = actionLabel(e.action, (e as any).negation);
      const snippet = e.text.length > 58 ? e.text.slice(0, 58) + '...' : e.text;
      const actId = `act:${e.event_id}`;
      const stepActs = Array.isArray((e as any).steps)
        ? (e as any).steps.map((s: any) => actionLabel(s?.action, s?.negation)).filter(Boolean)
        : [];
      const actionPathLabel = stepActs.length > 1 ? stepActs.join(' -> ') : actionText;
      actionNodes.push(node(actId, `${actionPathLabel}: ${snippet}`, '#fde68a', `${e.event_id} | ${e.anchor.text} | section=${e.section}`));

      // Time -> action (attach at most specific available for selected granularity).
      const y = String(e.anchor.year || 0);
      const ym = fmtYM(e.anchor);
      const ymd = fmtYMD(e.anchor);
      const t =
        timeGranularity === 'day' && e.anchor.month && e.anchor.day
          ? `time:d:${ymd}`
          : timeGranularity !== 'year' && e.anchor.month
            ? `time:m:${ym}`
            : `time:y:${y}`;
      edges.push({ from: t, to: actId, kind: 'sequence' });

      // Requester/subjects -> action (filtered by top sets for UI sanity).
      for (const a of e.actors ?? []) {
        const key = a.resolved || a.label;
        if (!key) continue;
        if (a.role === 'requester') {
          if (includeRequesters && requesterSet.has(key)) edges.push({ from: `req:${key}`, to: actId, kind: 'role' });
        }
      }
      const edgeSubs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => (Array.isArray(s?.subjects) ? s.subjects : [])))
        : [];
      const uniqueEdgeSubs = edgeSubs.length
        ? edgeSubs
        : uniqueStrings((e.actors ?? []).filter((a: any) => (a.role ?? '') !== 'requester').map((a: any) => a.resolved ?? a.label));
      for (const key of uniqueEdgeSubs) if (subjectSet.has(key)) edges.push({ from: `sub:${key}`, to: actId, kind: 'role' });

      // Action -> objects (frame/step-scoped first; event-global fallback only when steps absent).
      const edgeObjs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepEntityObjects(s)))
        : [];
      const edgeObjKeys = edgeObjs.length
        ? edgeObjs
        : uniqueStrings(eventEntityObjects(e));
      for (const key of edgeObjKeys) if (objectSet.has(key)) edges.push({ from: actId, to: `obj:${key}`, kind: 'role' });
      const edgeNums = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.flatMap((s: any) => stepNumericObjects(s)))
        : [];
      const edgeNumKeys = edgeNums.length
        ? edgeNums
        : uniqueStrings(eventNumericObjects(e));
      for (const key of edgeNumKeys) if (numericSet.has(key)) edges.push({ from: actId, to: `num:${key}`, kind: 'role' });

      if (includeEvidence) {
        const evidenceKeys = evidenceLabelsFromEvent(e);
        for (const key of evidenceKeys) {
          if (!evidenceSet.has(key)) continue;
          edges.push({ from: actId, to: `evd:${key}`, kind: 'evidence' });
        }
      }

      if (includePurpose && e.purpose) {
        const pid = `pur:${e.event_id}`;
        purposeNodes.push(node(pid, e.purpose, '#fef3c7'));
        edges.push({ from: actId, to: pid, kind: 'role' });
      }
    }

    const layers: Array<{ id: string; title: string; nodes: LayerNode[] }> = [
      { id: 'year', title: 'Year', nodes: Array.from(yearNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) }
    ];
    if (timeGranularity !== 'year') {
      layers.push({ id: 'month', title: 'Month', nodes: Array.from(monthNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) });
    }
    if (timeGranularity === 'day') {
      layers.push({ id: 'day', title: 'Day', nodes: Array.from(dayNodes.values()).sort((a, b) => a.id.localeCompare(b.id)) });
    }
    if (includeRequesters) layers.push({ id: 'req', title: 'Requester', nodes: requesterNodes.length ? requesterNodes : [node('req:none', '(none)', '#ffffff')] });
    layers.push({ id: 'sub', title: 'Subjects', nodes: subjectNodes.length ? subjectNodes : [node('sub:none', '(none)', '#ffffff')] });
    layers.push({ id: 'act', title: 'Action', nodes: actionNodes.length ? actionNodes : [node('act:none', '(none)', '#ffffff')] });
    layers.push({ id: 'obj', title: 'Objects', nodes: objectNodes.length ? objectNodes : [node('obj:none', '(none)', '#ffffff')] });
    layers.push({ id: 'num', title: 'Numeric', nodes: numericNodes.length ? numericNodes : [node('num:none', '(none)', '#ffffff')] });
    if (includeEvidence) layers.push({ id: 'evd', title: 'Evidence', nodes: evidenceNodes.length ? evidenceNodes : [node('evd:none', '(none)', '#ffffff')] });
    if (includePurpose) layers.push({ id: 'pur', title: 'Purpose', nodes: purposeNodes.length ? purposeNodes : [node('pur:none', '(none)', '#ffffff')] });

    return { layers, edges };
  })();
</script>

<div class="space-y-4 p-6">
  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Wiki timeline AAO: whole-article combined</div>
    <div class="mt-2 text-sm text-ink-950">
      Source: <span class="font-mono text-xs">{data.relPath}</span>
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      Union graph over many sentence-local AAO extractions. Non-causal. Non-authoritative.
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-3 text-sm">
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Dataset</span>
        <select
          class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm"
          value={data.source ?? 'gwb'}
          on:change={(e) => {
            const v = (e.currentTarget as HTMLSelectElement).value;
            window.location.href = `/graphs/wiki-timeline-aoo-all?source=${encodeURIComponent(v)}`;
          }}
        >
          <option value="gwb">gwb</option>
          <option value="hca">hca</option>
          <option value="legal">legal</option>
          <option value="legal_follow">legal_follow</option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Time</span>
        <select bind:value={timeGranularity} class="rounded-md border border-ink-950/15 bg-white px-2 py-1 text-sm">
          <option value="year">Year</option>
          <option value="month">Month</option>
          <option value="day">Day</option>
        </select>
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Events</span>
        <input
          type="number"
          min="10"
          max={eventsAll.length}
          step="5"
          bind:value={limitEvents}
          class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs"
        />
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max subjects</span>
        <input type="number" min="10" max="400" step="10" bind:value={maxSubjects} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" />
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max objects</span>
        <input type="number" min="10" max="600" step="10" bind:value={maxObjects} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" />
      </label>
      <label class="flex items-center gap-2">
        <span class="text-ink-800/70">Max numeric</span>
        <input type="number" min="10" max="600" step="10" bind:value={maxNumbers} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" />
      </label>
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includeEvidence} />
        <span class="text-ink-800/70">Evidence lane</span>
      </label>
      {#if includeEvidence}
        <label class="flex items-center gap-2">
          <span class="text-ink-800/70">Max evidence</span>
          <input type="number" min="10" max="400" step="10" bind:value={maxEvidence} class="w-24 rounded-md border border-ink-950/15 px-2 py-1 font-mono text-xs" />
        </label>
      {/if}
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includeRequesters} />
        <span class="text-ink-800/70">Requesters</span>
      </label>
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={includePurpose} />
        <span class="text-ink-800/70">Purpose</span>
      </label>
      <label class="flex items-center gap-2">
        <input type="checkbox" bind:checked={orderByFactDate} />
        <span class="text-ink-800/70">Fact-date order</span>
      </label>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Timeline
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open AAO
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-timeline-aoo?source=${encodeURIComponent(data.source ?? 'gwb')}&view=step-ribbon`}
      >
        Open Step-Ribbon
      </a>
      <a
        class="rounded-md border border-ink-950/15 px-2 py-1 text-xs text-ink-950 hover:border-ink-950/30 hover:bg-ink-950/[0.03]"
        href={`/graphs/wiki-fact-timeline?source=${encodeURIComponent(data.source ?? 'gwb')}`}
      >
        Open Fact Timeline
      </a>
    </div>
  </Panel>

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <LayeredGraph
    layers={graph.layers}
    edges={graph.edges}
    width={1600}
    height={900}
    on:nodeSelect={(e) => (selectedNodeId = (e as CustomEvent<{ nodeId: string }>).detail.nodeId)}
  />

  <Panel>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Context</div>
      <div class="flex flex-wrap items-center gap-3 text-[11px] font-mono text-ink-800/60">
        {#if selectedNodeId}
          <span>selected: {selectedNodeId}</span>
          {#if contextRows.length > 80}
            <label class="inline-flex items-center gap-1 rounded border border-ink-950/10 bg-white px-2 py-0.5">
              <input type="checkbox" bind:checked={showAllContextRows} />
              <span>all rows ({contextRows.length})</span>
            </label>
          {:else}
            <span>rows: {contextRows.length}</span>
          {/if}
        {:else}
          <span>click a node to preview the relevant extracted timeline text</span>
        {/if}
      </div>
    </div>

    <div class="mt-3 max-h-[320px] overflow-auto rounded-lg border border-ink-950/10 bg-white" bind:this={contextBox}>
      {#if !selectedNodeId}
        <div class="p-3 text-xs text-ink-800/70">
          This panel shows sentence-local timeline evidence for the selected node (from the extracted timeline substrate, not the full Wikipedia article).
        </div>
      {:else if !contextRows.length}
        <div class="p-3 text-xs text-ink-800/70">No matching extracted timeline rows for this node in the current event window.</div>
      {:else}
        {#each contextRowsShown as r (r.key)}
          <div class="border-b border-ink-950/10 p-3 last:border-b-0" data-ctx-id={r.event_id}>
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="font-mono text-[10px] text-ink-800/60">{r.time} {r.event_id}</div>
              <div class="font-mono text-[10px] text-ink-800/60">section={r.section}</div>
            </div>
            <div class="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-ink-950">
              {#if r.requesters.length}
                {#each r.requesters as x (r.event_id + ':req:' + x)}
                  <span class="rounded bg-purple-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
                <span class="font-mono text-ink-800/50">request</span>
              {/if}
              {#if r.subjects.length}
                {#each r.subjects as x (r.event_id + ':sub:' + x)}
                  <span class="rounded bg-emerald-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
                <span class="font-mono text-ink-800/50">do</span>
              {/if}
              {#if r.actions.length}
                {#each r.actions as a (r.event_id + ':act:' + a)}
                  <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{a}]</span>
                {/each}
              {:else}
                <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">[{actionLabel(r.action, r.negation)}]</span>
              {/if}
              {#if r.objects.length}
                <span class="font-mono text-ink-800/50">object</span>
                {#each r.objects as x (r.event_id + ':obj:' + x)}
                  <span class="rounded bg-slate-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
              {/if}
              {#if r.numerics.length}
                <span class="font-mono text-ink-800/50">numeric</span>
                {#each r.numerics as x (r.event_id + ':num:' + x)}
                  <span class="rounded bg-rose-100 px-1.5 py-0.5 font-mono">[{x}]</span>
                {/each}
              {/if}
              {#if r.purpose}
                <span class="font-mono text-ink-800/50">purpose</span>
                <span class="rounded bg-yellow-50 px-1.5 py-0.5 font-mono">[{r.purpose}]</span>
              {/if}
            </div>
            {#if r.connected.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">connected</span>
                {#each r.connected as x (r.event_id + ':conn:' + x)}
                  <span class="ml-1 inline-block rounded bg-slate-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.slRefs.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">sl_refs</span>
                {#each r.slRefs.slice(0, 6) as x (r.event_id + ':sl:' + x)}
                  <span class="ml-1 inline-block rounded bg-blue-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.checkNext.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">check_next</span>
                {#each r.checkNext as x (r.event_id + ':next:' + x)}
                  <span class="ml-1 inline-block rounded bg-violet-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.party}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">party</span>
                <span class="ml-1 inline-block rounded bg-emerald-50 px-1.5 py-0.5 font-mono text-ink-900">{r.party}</span>
              </div>
            {/if}
            {#if r.tocContext.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">toc</span>
                {#each r.tocContext.slice(0, 4) as x (r.event_id + ':toc:' + x)}
                  <span class="ml-1 inline-block rounded bg-slate-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.legalMarkers.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">legal_markers</span>
                {#each r.legalMarkers.slice(0, 8) as x (r.event_id + ':lm:' + x)}
                  <span class="ml-1 inline-block rounded bg-indigo-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.factRows.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">timeline_facts</span>
                {#each r.factRows.slice(0, 4) as x (r.event_id + ':fact:' + x)}
                  <span class="ml-1 inline-block rounded bg-lime-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            {#if r.citations.length}
              <div class="mt-2 text-[11px]">
                <span class="font-mono text-ink-800/50">citations</span>
                {#each r.citations.slice(0, 6) as x (r.event_id + ':cit:' + x)}
                  <span class="ml-1 inline-block rounded bg-amber-50 px-1.5 py-0.5 font-mono text-ink-900">{x}</span>
                {/each}
              </div>
            {/if}
            <div class="mt-2 text-sm text-ink-950">
              {#if contextNeedle}
                {#each highlightParts(r.text, contextNeedle) as part, i (r.event_id + ':' + i)}
                  {#if part.hit}
                    <span class="rounded bg-amber-200/60 px-1">{part.s}</span>
                  {:else}
                    {part.s}
                  {/if}
                {/each}
              {:else}
                {r.text}
              {/if}
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </Panel>
</div>
