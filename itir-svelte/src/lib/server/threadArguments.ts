import { fetchThreadTail, fetchThreadTailBySourceThreadId } from '$lib/server/chatArchive';
import { loadNarrativeComparison } from '$lib/server/narrativeCompare';
import type { ChatArchiveMessage } from '$lib/server/chatArchive';
import type { ThreadArgumentsWorkbench, ArgumentClaim, ArgumentEdge } from '$lib/arguments/workbench';
import { addClaimCounterpoints, buildBadgeMap, buildEdges, buildFamilies, collectClaims } from '$lib/server/thread-arguments/claimGraph';
import { buildAnchors, claimCandidates as computeClaimCandidates, findFamilySentenceSpan as computeFindFamilySentenceSpan } from '$lib/server/thread-arguments/spans';

const COMPARISON_IDS = ['friendlyjordies_thread_extract', 'friendlyjordies_chat_arguments', 'friendlyjordies_authority_wrappers'] as const;

function looksLikeOnlineConversationId(v: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
}

async function loadThread(repoRoot: string, threadId: string) {
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
  const comparisons = await Promise.all(
    COMPARISON_IDS.map((comparisonId) => loadNarrativeComparison(comparisonId, { threadId: thread.sourceThreadId ?? thread.canonicalThreadId, threadTitle: thread.title }))
  );

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
  if (!dedupedClaims.length) {
    return {
      ...base,
      unavailableReason: 'No argument overlay could be derived from this archive thread.'
    };
  }

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

export function claimCandidates(claim: ArgumentClaim): string[] {
  return computeClaimCandidates(claim);
}

export function findFamilySentenceSpan(message: ChatArchiveMessage, claim: ArgumentClaim) {
  const span = computeFindFamilySentenceSpan(message, claim);
  if (!span) {
    return null;
  }
  return span;
}
