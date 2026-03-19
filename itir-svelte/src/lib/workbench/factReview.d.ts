import type {
  FactReviewChronologyRow,
  FactReviewFact,
  FactReviewInspectorClassification,
  FactReviewRecentSource,
  FactReviewSource,
  FactReviewViewItem,
  FactReviewWorkbench,
} from '$lib/server/factReview';

export type FactReviewSourceRow = FactReviewSource | FactReviewRecentSource;

export function resolveFactReviewSourceRows(
  workbench: FactReviewWorkbench | null | undefined,
  sources: FactReviewSource[] | null | undefined
): FactReviewSourceRow[];

export function buildFactReviewHrefForSource(
  source: FactReviewSourceRow | null | undefined,
  params: {
    workflowKind?: string | null;
    wave?: string | null;
    view?: string | null;
  }
): string;

export function resolveFactReviewAvailableIssueFilters(
  workbench: FactReviewWorkbench | null | undefined,
  view: string | null | undefined
): string[];

export function resolveFactReviewFilteredItems(
  workbench: FactReviewWorkbench | null | undefined,
  view: string | null | undefined,
  selectedIssueFilter: string | null | undefined
): FactReviewViewItem[];

export function resolveSelectedFact(
  workbench: FactReviewWorkbench | null | undefined,
  selectedFactId: string | null | undefined
): FactReviewFact | null;

export function resolveInspectorClassification(
  workbench: FactReviewWorkbench | null | undefined,
  selectedFact: FactReviewFact | null | undefined
): FactReviewInspectorClassification | null;

export function resolveChronologyBuckets(
  workbench: FactReviewWorkbench | null | undefined
): {
  dated: FactReviewChronologyRow[];
  approximate: FactReviewChronologyRow[];
  undated: FactReviewChronologyRow[];
  contested: FactReviewChronologyRow[];
  undatedOrContested: FactReviewChronologyRow[];
};
