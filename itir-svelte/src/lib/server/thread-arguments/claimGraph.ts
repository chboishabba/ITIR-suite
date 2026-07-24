import type { NarrativeComparisonReport, NarrativeValidationReport } from '$lib/server/narrativeCompare';
import type { ChatArchiveMessage } from '$lib/server/chatArchive';
import type { ArgumentClaim, ArgumentEdge, ArgumentFamily, ArgumentAnchor, ArgumentBadge } from '$lib/arguments/workbench';
import { deriveFamilyId, familyMeta, THEME_ORDER } from './family';

export function buildEdges(report: NarrativeComparisonReport, claimsByPropId: Map<string, string>): ArgumentEdge[] {
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

export function collectClaims(report: NarrativeComparisonReport): { claims: ArgumentClaim[]; claimsByPropId: Map<string, string> } {
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

export function addClaimCounterpoints(claims: ArgumentClaim[], edges: ArgumentEdge[]): void {
  const claimsById = new Map(claims.map((row) => [row.id, row]));
  for (const edge of edges) {
    if (edge.kind !== 'undermines') continue;
    const from = claimsById.get(edge.fromClaimId);
    const to = claimsById.get(edge.toClaimId);
    if (from && !from.counterpointIds.includes(edge.toClaimId)) from.counterpointIds.push(edge.toClaimId);
    if (to && !to.counterpointIds.includes(edge.fromClaimId)) to.counterpointIds.push(edge.fromClaimId);
  }
}

export function buildFamilies(claims: ArgumentClaim[], anchors: ArgumentAnchor[]): ArgumentFamily[] {
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

export function buildBadgeMap(messages: ChatArchiveMessage[], anchors: ArgumentAnchor[], claimsById: Map<string, ArgumentClaim>): ArgumentBadge[] {
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
