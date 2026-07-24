function normalizeInternalHref(value: string | null | undefined): string | null {
  const text = String(value ?? '').trim();
  if (!text || !text.startsWith('/')) return null;
  return text;
}

export function buildFactReviewHref(params: Record<string, string | null | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value);
  }
  return `/graphs/fact-review?${search.toString()}`;
}

export function buildRawSourceHref(sourceLabel: string, workflowKind: string): string {
  if (workflowKind === 'au_semantic') {
    return '/corpora/processed/personal';
  }
  if (sourceLabel.includes('transcript')) {
    return '/corpora/processed/personal';
  }
  if (sourceLabel.includes('messenger') || sourceLabel.includes('facebook') || sourceLabel.includes('fb')) {
    return '/corpora/messenger';
  }
  if (sourceLabel.includes('chat')) {
    return '/corpora/chat-archive';
  }
  return '/corpora';
}

export function deriveFeedbackDrillIn(
  row: {
    target_product?: string | null;
    target_surface?: string | null;
    workflow_label?: string | null;
    task_label?: string | null;
    provenance?: Record<string, unknown>;
  }
): { href: string | null; label: string | null } {
  const targetSurface = normalizeInternalHref(row.target_surface);
  if (targetSurface) {
    return { href: targetSurface, label: 'Open target surface' };
  }
  const provenance = row.provenance && typeof row.provenance === 'object' ? row.provenance : {};
  const provenanceSourceRef = String((provenance as Record<string, unknown>).source_ref ?? '').trim();
  const directSourceHref = normalizeInternalHref(provenanceSourceRef);
  if (directSourceHref) {
    return { href: directSourceHref, label: 'Open source-linked surface' };
  }
  if (/^[0-9a-f]{40}$/i.test(provenanceSourceRef)) {
    return { href: `/thread/${provenanceSourceRef}`, label: 'Open source thread' };
  }
  if (provenanceSourceRef.startsWith('thread:')) {
    const threadId = provenanceSourceRef.slice('thread:'.length).trim();
    if (/^[0-9a-f]{40}$/i.test(threadId)) {
      return { href: `/thread/${threadId}`, label: 'Open source thread' };
    }
  }
  const workflowKind = String((provenance as Record<string, unknown>).workflow_kind ?? '').trim();
  const workflowRunId = String((provenance as Record<string, unknown>).workflow_run_id ?? '').trim();
  const sourceLabel = String((provenance as Record<string, unknown>).source_label ?? '').trim();
  if (workflowKind || workflowRunId || sourceLabel) {
    return {
      href: buildFactReviewHref({
        workflow_kind: workflowKind || null,
        workflow_run_id: workflowRunId || null,
        source_label: sourceLabel || null
      }),
      label: 'Open linked fact review run'
    };
  }
  const targetProduct = String(row.target_product ?? '').trim().toLowerCase();
  const workflowLabel = String(row.workflow_label ?? '').trim().toLowerCase();
  const taskLabel = String(row.task_label ?? '').trim().toLowerCase();

  if (workflowLabel === 'personal_results_review' || targetProduct === 'itir-svelte') {
    return { href: '/corpora/processed/personal', label: 'Open personal results' };
  }
  if (workflowLabel.includes('fact_review') || taskLabel.includes('review')) {
    return { href: '/graphs/fact-review', label: 'Open fact review workbench' };
  }
  if (taskLabel.includes('browse_corpus')) {
    return { href: '/corpora', label: 'Open corpus browser' };
  }
  return { href: null, label: null };
}
