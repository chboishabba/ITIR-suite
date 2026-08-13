import type { ChatArchiveMessage } from '$lib/server/chatArchive';

export type ArgumentFamily = {
  id: string;
  label: string;
  color: string;
  messageIds: string[];
  claimIds: string[];
};

export type ArgumentAnchor = {
  id: string;
  claimId: string;
  familyId: string;
  messageId: string;
  charStart: number;
  charEnd: number;
  exact: boolean;
  preview: string;
};

export type ArgumentBadge = {
  messageId: string;
  claimCount: number;
  counterpointCount: number;
  refCount: number;
  abstentionCount: number;
  familyIds: string[];
};

export type ArgumentClaim = {
  id: string;
  sourceId: string;
  propositionId: string;
  familyId: string;
  predicateKey: string;
  propositionKind: string;
  normalizedText: string;
  surfaceText: string;
  arguments: Array<{ role: string; value: string }>;
  receipts: Array<{ kind: string; value: string }>;
  counterpointIds: string[];
  messageIds: string[];
  confidenceLabel: string;
};

export type ArgumentEdge = {
  id: string;
  fromClaimId: string;
  toClaimId: string;
  kind: string;
  label: string;
};

export type ThreadArgumentsWorkbench = {
  threadId: string;
  title: string | null;
  total: number;
  messages: ChatArchiveMessage[];
  unavailableReason: string | null;
  families: ArgumentFamily[];
  anchors: ArgumentAnchor[];
  badges: ArgumentBadge[];
  claims: ArgumentClaim[];
  edges: ArgumentEdge[];
  defaultSelectedClaimIds: string[];
  sourceThreadId: string | null;
};

export function buildClaimGraph(workbench: ThreadArgumentsWorkbench, claimIds: string[]): {
  layers: Array<{ id: string; title: string; nodes: Array<{ id: string; label: string; color?: string; fullLabel?: string }> }>;
  edges: Array<{ from: string; to: string; label?: string; kind?: 'role' | 'sequence' | 'evidence' | 'context' }>;
} {
  const selected = workbench.claims.filter((row) => claimIds.includes(row.id));
  const selectedIds = new Set(selected.map((row) => row.id));
  const relatedIds = new Set<string>();
  for (const edge of workbench.edges) {
    if (selectedIds.has(edge.fromClaimId)) relatedIds.add(edge.toClaimId);
    if (selectedIds.has(edge.toClaimId)) relatedIds.add(edge.fromClaimId);
  }
  const related = workbench.claims.filter((row) => relatedIds.has(row.id));
  const familyPeers = workbench.claims.filter(
    (row) => selected.some((sel) => sel.familyId === row.familyId) && !selectedIds.has(row.id) && !relatedIds.has(row.id)
  );
  const familyColor = (claim: ArgumentClaim) => workbench.families.find((row) => row.id === claim.familyId)?.color ?? '#6b7280';
  const nodeFor = (claim: ArgumentClaim) => ({
    id: claim.id,
    label: `${claim.predicateKey}: ${claim.normalizedText.slice(0, 42)}`,
    fullLabel: `${claim.predicateKey}: ${claim.normalizedText}`,
    color: familyColor(claim)
  });
  return {
    layers: [
      { id: 'family', title: 'Family', nodes: familyPeers.slice(0, 6).map(nodeFor) },
      { id: 'selected', title: 'Selected', nodes: selected.map(nodeFor) },
      { id: 'counterpoints', title: 'Counterpoints', nodes: related.slice(0, 10).map(nodeFor) }
    ],
    edges: workbench.edges
      .filter((row) => selectedIds.has(row.fromClaimId) || selectedIds.has(row.toClaimId))
      .map((row) => ({
        from: row.fromClaimId,
        to: row.toClaimId,
        label: row.label,
        kind: row.kind === 'undermines' ? 'context' : 'sequence'
      }))
  };
}
