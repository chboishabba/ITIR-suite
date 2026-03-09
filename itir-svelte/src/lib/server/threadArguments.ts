import path from 'node:path';
import type { ChatArchiveMessage } from '$lib/server/chatArchive';
import { fetchThreadTail, fetchThreadTailBySourceThreadId } from '$lib/server/chatArchive';
import { loadNarrativeComparison, type NarrativeComparisonReport, type NarrativeValidationReport } from '$lib/server/narrativeCompare';
import type { ArgumentAnchor, ArgumentBadge, ArgumentClaim, ArgumentEdge, ArgumentFamily, ThreadArgumentsWorkbench } from '$lib/arguments/workbench';

const FRIENDLYJORDIES_SOURCE_THREAD_ID = '69ac40e0-0cfc-839b-b2a8-0de3019379a9';
const THEME_ORDER = [
  'cprs_blocking',
  'woolworths_price',
  'government_capacity',
  'ets_delay_authority',
  'fallacies'
] as const;

const FAMILY_META: Record<string, { label: string; color: string; keywords: string[] }> = {
  cprs_blocking: {
    label: 'CPRS blocking',
    color: '#b54747',
    keywords: ['cprs', 'greens', 'blocked', 'instability', 'momentum']
  },
  woolworths_price: {
    label: 'Woolworths / price effects',
    color: '#8d6a1a',
    keywords: ['woolworths', 'grocery', 'direct cost pass-through', 'direct grocery impacts', 'cpi']
  },
  government_capacity: {
    label: 'Majority vs minority government',
    color: '#2e6f53',
    keywords: ['majority government', 'minority government', 'germany', 'green parties']
  },
  ets_delay_authority: {
    label: 'ETS authority wrappers',
    color: '#4f46e5',
    keywords: ['ross garnaut', 'imperfect ets', 'better than delay', 'kevin rudd']
  },
  fallacies: {
    label: 'Fallacies / framing',
    color: '#0f5b99',
    keywords: ['logical fallacies', 'post hoc', 'false dilemma', 'counterfactual']
  },
  other: {
    label: 'Other argument family',
    color: '#6b7280',
    keywords: []
  }
};

function familyMeta(familyId: string): { label: string; color: string; keywords: string[] } {
  if (Object.prototype.hasOwnProperty.call(FAMILY_META, familyId)) {
    return FAMILY_META[familyId] as { label: string; color: string; keywords: string[] };
  }
  return FAMILY_META.other as { label: string; color: string; keywords: string[] };
}

type LoadedThread = {
  canonicalThreadId: string;
  sourceThreadId: string | null;
  title: string | null;
  total: number;
  messages: ChatArchiveMessage[];
};

function looksLikeOnlineConversationId(v: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
}

function normalizeText(value: string | null | undefined): string {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

function compactLower(value: string | null | undefined): string {
  return normalizeText(value).toLowerCase();
}

function deriveFamilyId(predicateKey: string, surfaceText: string): string {
  const normalized = compactLower(`${predicateKey} ${surfaceText}`);
  if (normalized.includes('ross garnaut') || normalized.includes('imperfect ets') || normalized.includes('better than delay') || normalized.includes('kevin rudd')) {
    return 'ets_delay_authority';
  }
  if (normalized.includes('woolworths') || normalized.includes('grocery') || normalized.includes('pass-through') || normalized.includes('cpi')) {
    return 'woolworths_price';
  }
  if (normalized.includes('majority government') || normalized.includes('minority government') || normalized.includes('germany')) {
    return 'government_capacity';
  }
  if (normalized.includes('fallacies') || normalized.includes('post hoc') || normalized.includes('false dilemma')) {
    return 'fallacies';
  }
  if (
    normalized.includes('cprs') ||
    normalized.includes('greens blocked') ||
    normalized.includes('climate policy instability') ||
    normalized.includes('climate policy momentum')
  ) {
    return 'cprs_blocking';
  }
  return 'other';
}

async function loadThread(repoRoot: string, threadId: string): Promise<LoadedThread> {
  if (looksLikeOnlineConversationId(threadId)) {
    const mapped = await fetchThreadTailBySourceThreadId(repoRoot, threadId, { tail: 500 });
    return {
      canonicalThreadId: mapped.canonicalThreadId ?? threadId,
      sourceThreadId: threadId,
      title: mapped.title,
      total: mapped.total,
      messages: mapped.messages
    };
  }
  const thread = await fetchThreadTail(repoRoot, threadId, { tail: 500 });
  const sourceThreadId = thread.messages.find((row) => row.source_thread_id)?.source_thread_id ?? null;
  return {
    canonicalThreadId: threadId,
    sourceThreadId,
    title: thread.title,
    total: thread.total,
    messages: thread.messages
  };
}

function isFriendlyJordiesThread(thread: LoadedThread): boolean {
  if (thread.sourceThreadId && thread.sourceThreadId === FRIENDLYJORDIES_SOURCE_THREAD_ID) return true;
  const title = compactLower(thread.title);
  if (title.includes('climate change politics au')) return true;
  const corpus = compactLower(thread.messages.map((row) => row.text).join('\n'));
  return corpus.includes('cprs') && corpus.includes('woolworths') && corpus.includes('greens');
}

function buildBadgeMap(messages: ChatArchiveMessage[], anchors: ArgumentAnchor[], claimsById: Map<string, ArgumentClaim>): ArgumentBadge[] {
  return messages.map((message) => {
    const messageAnchors = anchors.filter((row) => row.messageId === message.message_id);
    const familyIds = Array.from(new Set(messageAnchors.map((row) => row.familyId)));
    const claimIds = Array.from(new Set(messageAnchors.map((row) => row.claimId)));
    const counterpointCount = claimIds.reduce((acc, id) => acc + (claimsById.get(id)?.counterpointIds.length ?? 0), 0);
    return {
      messageId: message.message_id,
      claimCount: claimIds.length,
      counterpointCount,
      refCount: claimIds.reduce((acc, id) => acc + ((claimsById.get(id)?.receipts.length ?? 0) > 0 ? 1 : 0), 0),
      abstentionCount: 0,
      familyIds
    };
  });
}

function buildFamilies(claims: ArgumentClaim[], anchors: ArgumentAnchor[]): ArgumentFamily[] {
  const map = new Map<string, ArgumentFamily>();
  for (const claim of claims) {
    const meta = familyMeta(claim.familyId);
    const family = map.get(claim.familyId) ?? {
      id: claim.familyId,
      label: meta.label,
      color: meta.color,
      messageIds: [],
      claimIds: []
    };
    family.claimIds.push(claim.id);
    for (const anchor of anchors) {
      if (anchor.claimId === claim.id && !family.messageIds.includes(anchor.messageId)) {
        family.messageIds.push(anchor.messageId);
      }
    }
    map.set(claim.familyId, family);
  }
  return Array.from(map.values()).sort((a, b) => {
    const ai = THEME_ORDER.indexOf(a.id as (typeof THEME_ORDER)[number]);
    const bi = THEME_ORDER.indexOf(b.id as (typeof THEME_ORDER)[number]);
    return (ai === -1 ? 999 : ai) - (bi === -1 ? 999 : bi);
  });
}

function buildEdges(report: NarrativeComparisonReport, claimsByPropId: Map<string, string>): ArgumentEdge[] {
  const edges: ArgumentEdge[] = [];
  for (const row of report.comparison_links ?? []) {
    const fromClaimId = claimsByPropId.get(row.left_proposition_id);
    const toClaimId = claimsByPropId.get(row.right_proposition_id);
    if (!fromClaimId || !toClaimId) continue;
    edges.push({
      id: row.link_id,
      fromClaimId,
      toClaimId,
      kind: row.link_kind,
      label: row.link_kind
    });
  }
  return edges;
}

function findMessageMatches(messages: ChatArchiveMessage[], familyId: string): ChatArchiveMessage[] {
  const meta = familyMeta(familyId);
  const matched = messages.filter((message) => {
    const text = compactLower(message.text);
    return meta.keywords.some((keyword) => text.includes(keyword.toLowerCase()));
  });
  return matched.length ? matched : messages.filter((row) => row.role === 'assistant').slice(-1);
}

function findLiteralSpan(message: ChatArchiveMessage, claim: ArgumentClaim): { start: number; end: number; exact: boolean; preview: string } {
  const haystack = message.text ?? '';
  const anchorText = claim.surfaceText || claim.normalizedText;
  const candidates = [
    anchorText,
    claim.arguments.find((row) => row.role === 'content')?.value ?? '',
    FAMILY_META[claim.familyId]?.keywords[0] ?? ''
  ].filter(Boolean);
  for (const candidate of candidates) {
    const idx = haystack.toLowerCase().indexOf(candidate.toLowerCase());
    if (idx >= 0) {
      return {
        start: idx,
        end: Math.min(haystack.length, idx + candidate.length),
        exact: candidate === anchorText,
        preview: candidate
      };
    }
  }
  return {
    start: 0,
    end: Math.min(haystack.length, Math.max(32, anchorText.length)),
    exact: false,
    preview: anchorText
  };
}

function buildAnchors(messages: ChatArchiveMessage[], claims: ArgumentClaim[]): ArgumentAnchor[] {
  const anchors: ArgumentAnchor[] = [];
  for (const claim of claims) {
    const matchedMessages = findMessageMatches(messages, claim.familyId);
    for (const message of matchedMessages) {
      const span = findLiteralSpan(message, claim);
      anchors.push({
        id: `${claim.id}:${message.message_id}`,
        claimId: claim.id,
        familyId: claim.familyId,
        messageId: message.message_id,
        charStart: span.start,
        charEnd: span.end,
        exact: span.exact,
        preview: span.preview
      });
      if (!claim.messageIds.includes(message.message_id)) claim.messageIds.push(message.message_id);
    }
  }
  return anchors;
}

function addClaimCounterpoints(claims: ArgumentClaim[], edges: ArgumentEdge[]): void {
  const claimsById = new Map(claims.map((row) => [row.id, row]));
  for (const edge of edges) {
    if (edge.kind !== 'undermines') continue;
    const from = claimsById.get(edge.fromClaimId);
    const to = claimsById.get(edge.toClaimId);
    if (from && !from.counterpointIds.includes(edge.toClaimId)) from.counterpointIds.push(edge.toClaimId);
    if (to && !to.counterpointIds.includes(edge.fromClaimId)) to.counterpointIds.push(edge.fromClaimId);
  }
}

function collectClaims(report: NarrativeComparisonReport): { claims: ArgumentClaim[]; claimsByPropId: Map<string, string> } {
  const claims: ArgumentClaim[] = [];
  const claimsByPropId = new Map<string, string>();
  for (const sourceId of Object.keys(report.reports ?? {})) {
    const sourceReport: NarrativeValidationReport = report.reports[sourceId]!;
    for (const proposition of sourceReport.propositions ?? []) {
      const claimId = `${sourceId}:${proposition.proposition_id}`;
      const surfaceText = proposition.anchor_text ?? proposition.arguments.map((row) => row.value).join(' ');
      const familyId = deriveFamilyId(proposition.predicate_key, surfaceText);
      const claim: ArgumentClaim = {
        id: claimId,
        sourceId,
        propositionId: proposition.proposition_id,
        familyId,
        predicateKey: proposition.predicate_key,
        propositionKind: proposition.proposition_kind,
        normalizedText: surfaceText,
        surfaceText,
        arguments: proposition.arguments ?? [],
        receipts: proposition.receipts ?? [],
        counterpointIds: [],
        messageIds: [],
        confidenceLabel: proposition.receipts?.some((row) => row.kind === 'claim_text') ? 'claim_text grounded' : 'derived'
      };
      claims.push(claim);
      claimsByPropId.set(proposition.proposition_id, claimId);
    }
  }
  return { claims, claimsByPropId };
}

export async function loadThreadArgumentsWorkbench(repoRoot: string, threadId: string): Promise<ThreadArgumentsWorkbench> {
  const thread = await loadThread(repoRoot, threadId);
  const base: ThreadArgumentsWorkbench = {
    threadId: thread.canonicalThreadId,
    title: thread.title,
    total: thread.total,
    messages: thread.messages,
    unavailableReason: null,
    families: [],
    anchors: [],
    badges: [],
    claims: [],
    edges: [],
    defaultSelectedClaimIds: [],
    sourceThreadId: thread.sourceThreadId
  };
  if (!isFriendlyJordiesThread(thread)) {
    return {
      ...base,
      unavailableReason: 'Argument overlay is currently implemented for the archive-backed FriendlyJordies proving thread only.'
    };
  }

  const comparisons = await Promise.all([
    loadNarrativeComparison('friendlyjordies_thread_extract'),
    loadNarrativeComparison('friendlyjordies_chat_arguments'),
    loadNarrativeComparison('friendlyjordies_authority_wrappers')
  ]);

  const allClaims: ArgumentClaim[] = [];
  const claimsByPropId = new Map<string, string>();
  const allEdges: ArgumentEdge[] = [];
  for (const payload of comparisons) {
    const collected = collectClaims(payload.comparison);
    for (const claim of collected.claims) {
      if (!claimsByPropId.has(claim.propositionId)) {
        allClaims.push(claim);
      }
      claimsByPropId.set(claim.propositionId, claim.id);
    }
    allEdges.push(...buildEdges(payload.comparison, claimsByPropId));
  }

  const dedupedClaims = Array.from(new Map(allClaims.map((row) => [row.id, row])).values());
  const anchors = buildAnchors(thread.messages, dedupedClaims);
  addClaimCounterpoints(dedupedClaims, allEdges);
  const claimsById = new Map(dedupedClaims.map((row) => [row.id, row]));
  const families = buildFamilies(dedupedClaims, anchors);
  const badges = buildBadgeMap(thread.messages, anchors, claimsById);
  const defaultSelectedClaimIds = dedupedClaims.slice(0, 1).map((row) => row.id);

  return {
    ...base,
    unavailableReason: null,
    families,
    anchors,
    badges,
    claims: dedupedClaims,
    edges: allEdges,
    defaultSelectedClaimIds
  };
}
