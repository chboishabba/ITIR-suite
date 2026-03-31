<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';
  import LayeredGraph, { type LayerNode, type LayeredEdge } from '$lib/ui/LayeredGraph.svelte';
  import { afterUpdate } from 'svelte';
  import ControlsPanel from '$lib/wiki_timeline/components/ControlsPanel.svelte';
  import ContextPanel from '$lib/wiki_timeline/components/ContextPanel.svelte';
  import CorpusDocsPanel from './_components/CorpusDocsPanel.svelte';
  import { defaultFilters, viewportKey } from '$lib/wiki_timeline/filters';
  import {
    pad2,
    canonicalUnitToken,
    collapseWhitespace,
    parseNumericValueToken,
    normalizeNumericMention,
    numericKey,
    numericMentionsFromValues,
    numericMentionsForEvent,
    numericLabelFromKey,
    numericSortValueFromKey,
    numericSortUnitFromKey,
    compareNumericLaneEntries,
    actionLabel,
    stepEntityObjects,
    eventEntityObjects,
    stepNumericObjects,
    eventNumericObjects,
    sourceLabelsForEvent as _sourceLabelsForEvent,
    lensLabelsForEvent as _lensLabelsForEvent,
    evidenceLabelsFromEvent as _evidenceLabelsFromEvent,
    timeKeyForEvent,
    factAnchorKey,
    uniqueStrings,
    collectFollowProviders,
    type NumericMention,
  } from '$lib/wiki_timeline/graph';
  import {
    keyFromNodeId,
    top,
    countLabels,
    defaultFollowOrder,
    requesterFlags,
    hasRequesterActor as _hasRequesterActor,
  } from '$lib/wiki_timeline/selection';

  type RequesterCoverage = {
    request_signal_events?: number;
    requester_events?: number;
    total_events?: number;
    missing_requester_event_ids?: string[];
  };

  export let data: {
    payload: {
      root_actor: { label: string; surname: string };
      requester_coverage?: RequesterCoverage;
      source_entity?: {
        id?: string;
        type?: string;
        title?: string;
        url?: string;
        publication_date?: string;
        version_hash?: string;
      };
      extraction_record?: {
        id?: string;
        source_entity_id?: string;
        parser_version?: string;
        extraction_timestamp?: string;
        confidence_score?: number;
      };
      extraction_profile?: {
        profile_id?: string;
        profile_version?: string;
        predicate_classifier?: string;
        path?: string;
      };
      run_id?: string;
      generated_at?: string;
      __loaded_from_db?: boolean;
      source_timeline?: { path?: string; snapshot?: any } | null;
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
          claim_bearing?: boolean;
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
        claim_bearing?: boolean;
        warnings: string[];
      }>;
    };
    relPath: string;
    source?: string;
    corpusDocs?: Array<{ relPath: string; name: string; bytes: number; ext: string }>;
    error: string | null;
  };

  type TimeGranularity = 'year' | 'month' | 'day';
  const filterDefaults = defaultFilters();
  let timeGranularity: TimeGranularity = filterDefaults.timeGranularity;
  let limitEvents = filterDefaults.limitEvents;
  let maxSubjects = filterDefaults.maxSubjects;
  let maxObjects = filterDefaults.maxObjects;
  let maxNumbers = filterDefaults.maxNumbers;
  let maxSources = filterDefaults.maxSources;
  let maxLenses = filterDefaults.maxLenses;
  let maxEvidence = filterDefaults.maxEvidence;
  let includeSources = filterDefaults.includeSources;
  let includeLenses = filterDefaults.includeLenses;
  let includeRequesters = filterDefaults.includeRequesters;
  let includePurpose = filterDefaults.includePurpose;
  let includeEvidence = filterDefaults.includeEvidence;
  let orderByFactDate = filterDefaults.orderByFactDate;
  let showAllContextRows = false;

  let selectedNodeId: string | null = null;
  let contextBox: HTMLDivElement | null = null;
  let lastScrollKey = '';
  // Wider lane spacing for readability in dense AAO-all layouts.
  const GRAPH_HEIGHT = 900;
  const GRAPH_COL_GAP = 800;
  const GRAPH_LEFT_PAD = 100;
  // Reset the viewport only when the graph layout meaningfully changes (dataset/filters),
  // not when the user clicks around selecting nodes.
  $: filters = {
    timeGranularity,
    limitEvents,
    maxSubjects,
    maxObjects,
    maxNumbers,
    maxSources,
    maxLenses,
    maxEvidence,
    includeSources,
    includeLenses,
    includeRequesters,
    includePurpose,
    includeEvidence,
    orderByFactDate
  };
  $: graphViewportKey = viewportKey(data?.source, filters, graphEvents?.length ?? 0);
  $: graphWidth = Math.max(
    3600,
    GRAPH_LEFT_PAD * 2 + Math.max(0, (graph as any)?.layers?.length ? (graph as any).layers.length - 1 : 8) * GRAPH_COL_GAP + 720
  );

  function node(id: string, label: string, color: string, tooltip?: string): LayerNode {
    const short = label.length > 54 ? label.slice(0, 54) + '...' : label;
    return { id, label: short, fullLabel: label, color, tooltip: tooltip ?? label };
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
  $: graphEvents = eventsAll.slice(0, Math.max(10, Math.min(eventsAll.length, Math.floor(limitEvents))));
  $: contextEvents = eventsAll;
  $: requesterCoverage = ((data.payload as any)?.requester_coverage ?? null) as RequesterCoverage | null;
  $: missingRequesterEventIds = Array.isArray(requesterCoverage?.missing_requester_event_ids)
    ? requesterCoverage.missing_requester_event_ids.map((x) => String(x ?? '')).filter(Boolean)
    : [];
  $: missingRequesterEventIdSet = new Set<string>(missingRequesterEventIds);

  type CtxRow = {
    key: string;
    // Disambiguates duplicate event_ids in some merged/union datasets.
    // This keeps Svelte keyed {#each} stable and prevents runtime crashes.
    instance: number;
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
    numericClaims: string[];
    sources: string[];
    lenses: string[];
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

  type RequesterCoverageSnapshot = {
    requestSignalEvents: number;
    requesterEvents: number;
    totalEvents: number;
    missingRequesterEventIds: string[];
  };


  const sourceLabelsForEvent = (e: any): string[] => _sourceLabelsForEvent(e, data.payload);

  const lensLabelsForEvent = (e: any): string[] => _lensLabelsForEvent(e, data.payload);

  const hasRequesterActor = (e: any): boolean => _hasRequesterActor(e);

  const evidenceLabelsFromEvent = _evidenceLabelsFromEvent;

  function asCount(raw: any): number {
    const n = Number(raw);
    if (!Number.isFinite(n)) return 0;
    if (n <= 0) return 0;
    return Math.floor(n);
  }

  $: requesterCoverageGlobal = (() => {
    if (!requesterCoverage) return null as RequesterCoverageSnapshot | null;
    return {
      requestSignalEvents: asCount(requesterCoverage.request_signal_events),
      requesterEvents: asCount(requesterCoverage.requester_events),
      totalEvents: asCount(requesterCoverage.total_events ?? eventsAll.length),
      missingRequesterEventIds: uniqueStrings(requesterCoverage.missing_requester_event_ids ?? [])
    } as RequesterCoverageSnapshot;
  })();

  $: requesterCoverageWindow = (() => {
    const missingRequesterEventIds: string[] = [];
    let requestSignalEvents = 0;
    let requesterEvents = 0;
    for (const e of graphEvents ?? []) {
      const eventId = String((e as any)?.event_id ?? '');
      const hasRequester = hasRequesterActor(e);
      const missingRequester = eventId ? missingRequesterEventIdSet.has(eventId) : false;
      if (hasRequester) requesterEvents += 1;
      if (hasRequester || missingRequester) requestSignalEvents += 1;
      if (missingRequester && eventId) missingRequesterEventIds.push(eventId);
    }
    return {
      requestSignalEvents,
      requesterEvents,
      totalEvents: graphEvents.length,
      missingRequesterEventIds
    } as RequesterCoverageSnapshot;
  })();

  $: requesterCoverageWindowGap = requesterCoverageWindow.requestSignalEvents > requesterCoverageWindow.requesterEvents;
  $: requesterCoverageGlobalGap = requesterCoverageGlobal
    ? requesterCoverageGlobal.requestSignalEvents > requesterCoverageGlobal.requesterEvents
    : false;

  $: numericLabelByKey = (() => {
    const out = new Map<string, string>();
    for (const e of contextEvents ?? []) {
      for (const m of numericMentionsForEvent(e)) if (!out.has(m.key)) out.set(m.key, m.label);
    }
    return out;
  })();

  const followOrder = defaultFollowOrder();

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
      if (key === 'missing') return missingRequesterEventIdSet.has(String((e as any)?.event_id ?? ''));
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
      return numericMentionsForEvent(e).some((m: NumericMention) => m.key === key);
    }
    if (nodeId.startsWith('evd:')) {
      const key = nodeId.slice('evd:'.length);
      return evidenceLabelsFromEvent(e).includes(key);
    }
    if (nodeId.startsWith('src:')) {
      const key = nodeId.slice('src:'.length);
      return sourceLabelsForEvent(e).includes(key);
    }
    if (nodeId.startsWith('lens:')) {
      const key = nodeId.slice('lens:'.length);
      return lensLabelsForEvent(e).includes(key);
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
    const eventIdCounts = new Map<string, number>();
    for (const e of contextEvents) {
      if (!eventMatchesNode(e, selectedNodeId)) continue;
      const eventId = String(e.event_id ?? '');
      const instance = (eventIdCounts.get(eventId) ?? 0) + 1;
      eventIdCounts.set(eventId, instance);
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
      const numMentions = numericMentionsForEvent(e);
      const nums = numMentions.map((m) => m.label);
      const numKeys = numMentions.map((m) => m.key);
      const srcs = sourceLabelsForEvent(e);
      const lenses = lensLabelsForEvent(e);
      const numericClaims = Array.isArray((e as any).numeric_claims)
        ? uniqueStrings(
            (e as any).numeric_claims.map((c: any) => {
              const key = String(c?.key ?? '').trim();
              const role = String(c?.role ?? '').trim();
              const exprScale = String(c?.normalized?.expression?.scale_word ?? '').trim();
              const exprExp = c?.normalized?.expression?.exponent_from_scale;
              const surfSpacing = String(c?.normalized?.surface?.spacing_pattern ?? '').trim();
              const years = Array.isArray(c?.time_years) ? c.time_years.map((x: any) => String(x ?? '').trim()).filter(Boolean).join(',') : '';
              const ta = c?.time_anchor && typeof c.time_anchor === 'object'
                ? [c.time_anchor.year, c.time_anchor.month, c.time_anchor.day]
                    .filter((x: any) => x !== null && x !== undefined && String(x).trim() !== '')
                    .map((x: any) => String(x))
                    .join('-')
                : '';
              const bits = [
                key,
                role ? `role=${role}` : '',
                exprScale ? `scale=${exprScale}` : '',
                Number.isFinite(exprExp) ? `exp=${String(exprExp)}` : '',
                surfSpacing ? `spacing=${surfSpacing}` : '',
                years ? `years=${years}` : '',
                ta ? `anchor=${ta}` : ''
              ]
                .filter(Boolean)
                .join(' ');
              return bits;
            })
          )
        : [];
      const stepActs = Array.isArray((e as any).steps)
        ? uniqueStrings((e as any).steps.map((s: any) => actionLabel(s?.action, s?.negation)).filter(Boolean))
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
        ...(citations.length || slRefs.length ? followOrder : [])
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
        ...numKeys.map((x: string) => `num:${x}`),
        ...evidenceLabelsFromEvent(e).map((x: string) => `evd:${x}`),
        ...srcs.map((x: string) => `src:${x}`),
        ...lenses.map((x: string) => `lens:${x}`)
      ]);
      rows.push({
        key: `${selectedNodeId}:${eventId}:${instance}`,
        instance,
        event_id: eventId,
        time: timeKeyForEvent(e, 'day'),
        section: e.section ?? '',
        text: e.text ?? '',
        requesters: reqs,
        subjects: subs,
        action: typeof e.action === 'string' ? e.action : null,
        negation: (e as any).negation && typeof (e as any).negation.kind === 'string' ? (e as any).negation : undefined,
        actions: stepActs,
        objects: objs,
        numerics: nums,
        numericClaims,
        sources: srcs,
        lenses: lenses,
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
    if (id.startsWith('num:')) {
      const key = id.slice('num:'.length);
      return numericLabelByKey.get(key) ?? numericLabelFromKey(key);
    }
    if (id.startsWith('evd:')) return id.slice('evd:'.length);
    if (id.startsWith('src:')) return id.slice('src:'.length);
    if (id.startsWith('lens:')) return id.slice('lens:'.length);
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
    const sourceCount = new Map<string, number>();
    const lensCount = new Map<string, number>();
    const requesterCount = new Map<string, number>();
    const evidenceCount = new Map<string, number>();

    for (const e of graphEvents) {
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
      for (const m of numericMentionsForEvent(e)) numericCount.set(m.key, (numericCount.get(m.key) ?? 0) + 1);
      for (const src of sourceLabelsForEvent(e)) sourceCount.set(src, (sourceCount.get(src) ?? 0) + 1);
      for (const lens of lensLabelsForEvent(e)) lensCount.set(lens, (lensCount.get(lens) ?? 0) + 1);
      for (const ev of evidenceLabelsFromEvent(e)) evidenceCount.set(ev, (evidenceCount.get(ev) ?? 0) + 1);
    }

    const topSubjects = top(subjectCount, maxSubjects);
    const topObjects = top(objectCount, maxObjects);
    const topNumbers = top(numericCount, maxNumbers).sort(compareNumericLaneEntries);
    const topSources = includeSources ? top(sourceCount, Math.max(10, maxSources)) : [];
    const topLenses = includeLenses ? top(lensCount, Math.max(10, maxLenses)) : [];
    const topRequesters = includeRequesters ? top(requesterCount, Math.min(60, maxSubjects)) : [];
    const topEvidence = includeEvidence ? top(evidenceCount, maxEvidence) : [];

    const subjectSet = new Set(topSubjects.map(([k]) => k));
    const objectSet = new Set(topObjects.map(([k]) => k));
    const numericSet = new Set(topNumbers.map(([k]) => k));
    const sourceSet = new Set(topSources.map(([k]) => k));
    const lensSet = new Set(topLenses.map(([k]) => k));
    const requesterSet = new Set(topRequesters.map(([k]) => k));
    const evidenceSet = new Set(topEvidence.map(([k]) => k));

    const missingRequesterIdsInWindow = uniqueStrings(
      (graphEvents ?? [])
        .map((e: any) => String(e?.event_id ?? ''))
        .filter((eventId: string) => Boolean(eventId) && missingRequesterEventIdSet.has(eventId))
    );
    const requesterNodes = topRequesters.map(([k, c]) => node(`req:${k}`, `${k} (${c})`, '#e9d5ff'));
    const subjectNodes = topSubjects.map(([k, c]) => node(`sub:${k}`, `${k} (${c})`, '#bbf7d0'));
    const objectNodes = topObjects.map(([k, c]) => node(`obj:${k}`, `${k} (${c})`, '#f6f6f6'));
    const numericNodes = topNumbers.map(([k, c]) => {
      const label = numericLabelByKey.get(k) ?? numericLabelFromKey(k);
      return node(`num:${k}`, `${label} (${c})`, '#fee2e2', `key=${k}`);
    });
    const sourceNodes = topSources.map(([k, c]) => node(`src:${k}`, `${k} (${c})`, '#d1fae5'));
    const lensNodes = topLenses.map(([k, c]) => node(`lens:${k}`, `${k} (${c})`, '#ede9fe'));
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

    for (const e of graphEvents) {
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
      for (const m of numericMentionsForEvent(e)) if (numericSet.has(m.key)) edges.push({ from: actId, to: `num:${m.key}`, kind: 'role' });
      if (includeSources) {
        for (const src of sourceLabelsForEvent(e)) {
          if (sourceSet.has(src)) edges.push({ from: `src:${src}`, to: actId, kind: 'context' });
        }
      }
      if (includeLenses) {
        for (const lens of lensLabelsForEvent(e)) {
          if (lensSet.has(lens)) edges.push({ from: `lens:${lens}`, to: actId, kind: 'context' });
        }
      }

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
    if (includeSources) layers.push({ id: 'src', title: 'Source', nodes: sourceNodes.length ? sourceNodes : [node('src:none', '(none)', '#ffffff')] });
    if (includeLenses) layers.push({ id: 'lens', title: 'Lens', nodes: lensNodes.length ? lensNodes : [node('lens:none', '(none)', '#ffffff')] });
    if (includeRequesters) {
      const reqLane: LayerNode[] = [];
      if (requesterNodes.length) reqLane.push(...requesterNodes);
      if (missingRequesterEventIdSet.size) {
        const ids = Array.from(missingRequesterEventIdSet.values());
        const sample = ids.slice(0, 30).join(', ');
        const suffix = ids.length > 30 ? ` (+${ids.length - 30} more)` : '';
        reqLane.push(
          node(
            'req:missing',
            `(missing requester: ${missingRequesterEventIdSet.size})`,
            '#fff7ed',
            ids.length ? `Request-signal events missing requester: ${sample}${suffix}` : 'Request-signal events missing requester'
          )
        );
      }
      if (reqLane.length) layers.push({ id: 'req', title: 'Requester', nodes: reqLane });
    }
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
  <ControlsPanel
    {data}
    eventsAllLength={eventsAll.length}
    bind:timeGranularity
    bind:limitEvents
    bind:maxSubjects
    bind:maxObjects
    bind:maxNumbers
    bind:maxSources
    bind:maxLenses
    bind:maxEvidence
    bind:includeSources
    bind:includeLenses
    bind:includeRequesters
    bind:includePurpose
    bind:includeEvidence
    bind:orderByFactDate
  />

  <CorpusDocsPanel corpusDocs={data.corpusDocs ?? []} events={eventsAll} />

  {#if data.error}
    <Panel tone="danger">
      <div class="text-xs uppercase tracking-[0.28em] text-red-800/80">Load error</div>
      <pre class="mt-3 whitespace-pre-wrap font-mono text-xs text-ink-950">{data.error}</pre>
    </Panel>
  {/if}

  <LayeredGraph
    layers={graph.layers}
    edges={graph.edges}
    width={graphWidth}
    height={GRAPH_HEIGHT}
    colGap={GRAPH_COL_GAP}
    leftPad={GRAPH_LEFT_PAD}
    fitToWidth={false}
    scrollWhenOverflow={true}
    viewportResetKey={graphViewportKey}
    on:nodeSelect={(e) => (selectedNodeId = (e as CustomEvent<{ nodeId: string }>).detail.nodeId)}
  />

  <ContextPanel
    bind:showAllContextRows
    bind:contextBox
    selectedNodeId={selectedNodeId}
    contextRows={contextRows}
    contextRowsShown={contextRowsShown}
    requesterCoverageWindow={requesterCoverageWindow}
    requesterCoverageGlobal={requesterCoverageGlobal}
    requesterCoverageWindowGap={requesterCoverageWindowGap}
    requesterCoverageGlobalGap={requesterCoverageGlobalGap}
    contextNeedle={contextNeedle}
  />
</div>
