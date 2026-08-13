import type { AooNegation, AooProposition, AooPropositionArgument, AooPropositionLink, AooTimelineFact, WikiTimelineAooPayload, AooEvent } from './types';

function isObj(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === 'object';
}

export function normalizePropositionArgument(raw: unknown): AooPropositionArgument | null {
  if (!isObj(raw)) return null;
  const role = String((raw as any).role ?? '').trim();
  const value = String((raw as any).value ?? '').trim();
  if (!role || !value) return null;
  return { role, value };
}

export function normalizeReceipts(raw: unknown): Array<{ kind: string; value: string }> | undefined {
  if (!Array.isArray(raw)) return undefined;
  const receipts = raw
    .map((entry) => {
      if (!isObj(entry)) return null;
      const kind = String((entry as any).kind ?? '').trim();
      const value = String((entry as any).value ?? '').trim();
      if (!kind || !value) return null;
      return { kind, value };
    })
    .filter(Boolean) as Array<{ kind: string; value: string }>;
  return receipts.length ? receipts : undefined;
}

export function parseNegation(v: unknown): AooNegation | undefined {
  if (!isObj(v)) return undefined;
  const kind = typeof (v as any).kind === 'string' ? String((v as any).kind).trim() : '';
  if (!kind) return undefined;
  return {
    kind,
    scope: typeof (v as any).scope === 'string' ? String((v as any).scope) : undefined,
    source: typeof (v as any).source === 'string' ? String((v as any).source) : undefined
  };
}

export function normalizeActionAndNegation(
  rawAction: unknown,
  rawNegation: unknown
): { action: string | null; negation?: AooNegation } {
  const parsedNegation = parseNegation(rawNegation);
  const actionText = typeof rawAction === 'string' ? String(rawAction).trim() : '';
  if (!actionText) return { action: null, negation: parsedNegation };
  if (actionText.startsWith('not_')) {
    const base = actionText.slice(4).trim();
    if (!base) {
      return { action: null, negation: parsedNegation ?? { kind: 'not', scope: 'action', source: 'legacy:not_prefix' } };
    }
    return {
      action: base,
      negation: parsedNegation ?? { kind: 'not', scope: 'action', source: 'legacy:not_prefix' }
    };
  }
  return { action: actionText, negation: parsedNegation };
}

export function normalizePayloadObject(p: any): WikiTimelineAooPayload {
  const events = Array.isArray(p?.events) ? (p.events as any[]) : [];
  const root_actor = isObj(p?.root_actor) ? (p.root_actor as any) : { label: '', surname: '' };
  const fact_timeline = Array.isArray(p?.fact_timeline) ? (p.fact_timeline as any[]) : undefined;
  const propositions = Array.isArray(p?.propositions) ? (p.propositions as any[]) : undefined;
  const proposition_links = Array.isArray(p?.proposition_links) ? (p.proposition_links as any[]) : undefined;
  const parser = (p as any)?.parser;

  const outEvents: AooEvent[] = [];
  for (const e of events) {
    if (!isObj(e)) continue;
    const event_id = String((e as any).event_id ?? '').trim();
    const text = String((e as any).text ?? '').trim();
    if (!event_id || !text) continue;
    const anchor = isObj((e as any).anchor) ? (e as any).anchor : {};
    const actors = Array.isArray((e as any).actors) ? ((e as any).actors as any[]) : [];
    const objects = Array.isArray((e as any).objects) ? ((e as any).objects as any[]) : [];
    const eventAction = normalizeActionAndNegation((e as any).action, (e as any).negation);
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
      section: String((e as any).section ?? ''),
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
              const normalized = normalizeActionAndNegation(s.action, (s as any).negation);
              return {
                action: normalized.action ?? '',
                action_meta: isObj((s as any).action_meta)
                  ? {
                      surface: typeof (s as any).action_meta.surface === 'string' ? String((s as any).action_meta.surface) : undefined,
                      tense: typeof (s as any).action_meta.tense === 'string' ? String((s as any).action_meta.tense) : null,
                      aspect: typeof (s as any).action_meta.aspect === 'string' ? String((s as any).action_meta.aspect) : null,
                      verb_form: typeof (s as any).action_meta.verb_form === 'string' ? String((s as any).action_meta.verb_form) : null,
                      voice: typeof (s as any).action_meta.voice === 'string' ? String((s as any).action_meta.voice) : null,
                      source: typeof (s as any).action_meta.source === 'string' ? String((s as any).action_meta.source) : undefined
                    }
                  : undefined,
                action_surface: typeof (s as any).action_surface === 'string' ? String((s as any).action_surface) : undefined,
                negation: normalized.negation,
                subjects: Array.isArray((s as any).subjects) ? (s as any).subjects.map((x: any) => String(x)) : [],
                entity_objects: Array.isArray((s as any).entity_objects) ? (s as any).entity_objects.map((x: any) => String(x)) : undefined,
                numeric_objects: Array.isArray((s as any).numeric_objects) ? (s as any).numeric_objects.map((x: any) => String(x)) : undefined,
                modifier_objects: Array.isArray((s as any).modifier_objects) ? (s as any).modifier_objects.map((x: any) => String(x)) : undefined,
                objects: Array.isArray((s as any).objects) ? (s as any).objects.map((x: any) => String(x)) : [],
                purpose: typeof (s as any).purpose === 'string' ? (s as any).purpose : null
              };
            })
        : undefined,
      chains: Array.isArray((e as any).chains)
        ? (e as any).chains
            .filter((c: any) => isObj(c) && typeof c.kind === 'string')
            .map((c: any) => ({
              from_step: typeof c.from_step === 'number' ? c.from_step : undefined,
              to_step: typeof c.to_step === 'number' ? c.to_step : undefined,
              to: typeof c.to === 'string' ? String(c.to) : undefined,
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
              text: String((c as any).text ?? ''),
              kind: typeof (c as any).kind === 'string' ? String((c as any).kind) : undefined,
              source: typeof (c as any).source === 'string' ? String((c as any).source) : undefined,
              targets: Array.isArray((c as any).targets) ? (c as any).targets.map((x: any) => Number(x)).filter((n: any) => Number.isFinite(n)) : undefined,
              follower_order: Array.isArray((c as any).follower_order) ? (c as any).follower_order.map((x: any) => String(x)) : undefined,
              follow: Array.isArray((c as any).follow) ? (c as any).follow : undefined
            }))
        : undefined,
      sl_references: Array.isArray((e as any).sl_references)
        ? (e as any).sl_references
            .filter((r: any) => isObj(r))
            .map((r: any) => ({
              lane: String((r as any).lane ?? ''),
              authority: typeof (r as any).authority === 'string' ? String((r as any).authority) : undefined,
              ref_kind: typeof (r as any).ref_kind === 'string' ? String((r as any).ref_kind) : undefined,
              ref_value: typeof (r as any).ref_value === 'string' ? String((r as any).ref_value) : undefined,
              text: typeof (r as any).text === 'string' ? String((r as any).text) : undefined,
              source_document_json: typeof (r as any).source_document_json === 'string' ? String((r as any).source_document_json) : undefined,
              source_pdf: typeof (r as any).source_pdf === 'string' ? String((r as any).source_pdf) : undefined,
              provision_stable_id: typeof (r as any).provision_stable_id === 'string' ? String((r as any).provision_stable_id) : undefined,
              rule_atom_stable_id: typeof (r as any).rule_atom_stable_id === 'string' ? String((r as any).rule_atom_stable_id) : undefined,
              follower_order: Array.isArray((r as any).follower_order) ? (r as any).follower_order.map((x: any) => String(x)) : undefined,
              follow: Array.isArray((r as any).follow) ? (r as any).follow : undefined
            }))
        : undefined,
      party: typeof (e as any).party === 'string' ? String((e as any).party) : undefined,
      party_source: typeof (e as any).party_source === 'string' ? String((e as any).party_source) : undefined,
      party_evidence: Array.isArray((e as any).party_evidence) ? (e as any).party_evidence.map((x: any) => String(x)) : undefined,
      toc_context: Array.isArray((e as any).toc_context)
        ? (e as any).toc_context
            .filter((t: any) => isObj(t))
            .map((t: any) => ({
              node_type: typeof (t as any).node_type === 'string' ? String((t as any).node_type) : undefined,
              identifier: typeof (t as any).identifier === 'string' ? String((t as any).identifier) : undefined,
              title: typeof (t as any).title === 'string' ? String((t as any).title) : undefined,
              path: typeof (t as any).path === 'string' ? String((t as any).path) : undefined
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
            .filter((f: any) => isObj(f) && typeof (f as any).fact_id === 'string')
            .map((f: any) => ({
              fact_id: String((f as any).fact_id ?? ''),
              event_id,
              step_index: typeof (f as any).step_index === 'number' ? (f as any).step_index : undefined,
              anchor: isObj((f as any).anchor)
                ? {
                    year: Number((f as any).anchor.year ?? 0) || 0,
                    month: Number.isFinite(Number((f as any).anchor.month)) ? Number((f as any).anchor.month) : null,
                    day: Number.isFinite(Number((f as any).anchor.day)) ? Number((f as any).anchor.day) : null,
                    precision: String((f as any).anchor.precision ?? 'year'),
                    text: String((f as any).anchor.text ?? ''),
                    kind: String((f as any).anchor.kind ?? '')
                  }
                : { year: 0, month: null, day: null, precision: 'year', text: '', kind: '' },
              party: typeof (f as any).party === 'string' ? String((f as any).party) : undefined,
              subjects: Array.isArray((f as any).subjects) ? (f as any).subjects.map((x: any) => String(x)) : undefined,
              action: typeof (f as any).action === 'string' ? String((f as any).action) : null,
              negation: parseNegation((f as any).negation),
              objects: Array.isArray((f as any).objects) ? (f as any).objects.map((x: any) => String(x)) : undefined,
              numeric_objects: Array.isArray((f as any).numeric_objects) ? (f as any).numeric_objects.map((x: any) => String(x)) : undefined,
              purpose: typeof (f as any).purpose === 'string' ? String((f as any).purpose) : null,
              text: typeof (f as any).text === 'string' ? String((f as any).text) : undefined,
              prev_fact_ids: Array.isArray((f as any).prev_fact_ids) ? (f as any).prev_fact_ids.map((x: any) => String(x)) : undefined,
              next_fact_ids: Array.isArray((f as any).next_fact_ids) ? (f as any).next_fact_ids.map((x: any) => String(x)) : undefined,
              chain_kinds: Array.isArray((f as any).chain_kinds) ? (f as any).chain_kinds.map((x: any) => String(x)) : undefined
            }))
        : undefined,
      purpose: typeof (e as any).purpose === 'string' ? (e as any).purpose : null,
      span_candidates: Array.isArray((e as any).span_candidates)
        ? (e as any).span_candidates
            .filter((s: any) => isObj(s) && typeof (s as any).text === 'string' && isObj((s as any).span))
            .map((s: any) => ({
              span_id: String((s as any).span_id ?? ''),
              event_id,
              span: {
                kind: String((s as any).span.kind ?? ''),
                start: Number((s as any).span.start ?? 0) || 0,
                end: Number((s as any).span.end ?? 0) || 0,
                revision_id: typeof (s as any).span.revision_id === 'string' ? String((s as any).span.revision_id) : undefined
              },
              text: String((s as any).text ?? ''),
              span_type: String((s as any).span_type ?? ''),
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

  return {
    root_actor: { label: String(root_actor.label ?? ''), surname: String(root_actor.surname ?? '') },
    events: outEvents,
    fact_timeline: Array.isArray(fact_timeline) ? (fact_timeline as any) : undefined,
    propositions: propositions
      ?.map((raw) => {
        if (!isObj(raw)) return null;
        const proposition_id = String((raw as any).proposition_id ?? '').trim();
        const event_id = String((raw as any).event_id ?? '').trim();
        const proposition_kind = String((raw as any).proposition_kind ?? '').trim();
        const predicate_key = String((raw as any).predicate_key ?? '').trim();
        if (!proposition_id || !event_id || !proposition_kind || !predicate_key) return null;
        return {
          proposition_id,
          event_id,
          proposition_kind,
          predicate_key,
          negation: parseNegation((raw as any).negation),
          source_fact_id: typeof (raw as any).source_fact_id === 'string' ? String((raw as any).source_fact_id) : undefined,
          source_signal: typeof (raw as any).source_signal === 'string' ? String((raw as any).source_signal) : undefined,
          anchor_text: typeof (raw as any).anchor_text === 'string' ? String((raw as any).anchor_text) : undefined,
          arguments: Array.isArray((raw as any).arguments)
            ? (raw as any).arguments.map(normalizePropositionArgument).filter(Boolean) as AooPropositionArgument[]
            : undefined,
          receipts: normalizeReceipts((raw as any).receipts)
        } satisfies AooProposition;
      })
      .filter(Boolean) as AooProposition[] | undefined,
    proposition_links: proposition_links
      ?.map((raw) => {
        if (!isObj(raw)) return null;
        const link_id = String((raw as any).link_id ?? '').trim();
        const event_id = String((raw as any).event_id ?? '').trim();
        const source_proposition_id = String((raw as any).source_proposition_id ?? '').trim();
        const target_proposition_id = String((raw as any).target_proposition_id ?? '').trim();
        const link_kind = String((raw as any).link_kind ?? '').trim();
        if (!link_id || !event_id || !source_proposition_id || !target_proposition_id || !link_kind) return null;
        return {
          link_id,
          event_id,
          source_proposition_id,
          target_proposition_id,
          link_kind,
          receipts: normalizeReceipts((raw as any).receipts)
        } satisfies AooPropositionLink;
      })
      .filter(Boolean) as AooPropositionLink[] | undefined,
    parser,
    source_entity: (p as any).source_entity,
    extraction_record: (p as any).extraction_record,
    extraction_profile: (p as any).extraction_profile,
    requester_coverage: (p as any).requester_coverage,
    source_timeline: (p as any).source_timeline,
    generated_at: typeof (p as any).generated_at === 'string' ? String((p as any).generated_at) : undefined,
    run_id: typeof (p as any).run_id === 'string' ? String((p as any).run_id) : undefined,
    __loaded_from_db: Boolean((p as any).__loaded_from_db)
  };
}
