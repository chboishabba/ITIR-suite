export type ReviewStateReason =
  | 'loading'
  | 'ready'
  | 'unsupported'
  | 'empty'
  | 'load_error'
  | 'producer_error'
  | 'graph_not_enabled'
  | 'missing_graph_payload'
  | 'no_graph';

export function threadReviewState(unavailableReason: string | null | undefined): ReviewStateReason {
  return unavailableReason ? 'unsupported' : 'ready';
}

export function narrativeCompareReviewState(error: string | null | undefined, rowCount: number): ReviewStateReason {
  if (error) return 'load_error';
  return rowCount > 0 ? 'ready' : 'empty';
}

export function wikiContestedReviewState(args: {
  hasLoadError: boolean;
  selectedArticleStatus: string;
  packGraphEnabled: boolean;
  selectedArticleExists: boolean;
  selectedArticleGraphAvailable: boolean;
  hasGraphPayload: boolean;
}): ReviewStateReason {
  if (args.hasLoadError) return 'load_error';
  if (args.selectedArticleStatus === 'error') return 'producer_error';
  if (args.selectedArticleExists && !args.packGraphEnabled) return 'graph_not_enabled';
  if (args.selectedArticleExists && args.selectedArticleGraphAvailable && !args.hasGraphPayload) return 'missing_graph_payload';
  if (args.selectedArticleExists && args.hasGraphPayload) return 'ready';
  return 'no_graph';
}

