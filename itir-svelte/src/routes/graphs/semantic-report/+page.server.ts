import { listSemanticCorpora, loadSemanticComparison, loadSemanticReport } from '$lib/server/semanticReport';

export async function load({ url }: { url: URL }) {
  const source = (url.searchParams.get('source') || 'gwb').toLowerCase();
  const available = listSemanticCorpora();
  try {
    const [payload, comparison] = await Promise.all([loadSemanticReport(source), loadSemanticComparison()]);
    return { ...payload, comparison, graphGate: comparison.graphGate, semanticGraph: comparison.semanticGraph, available, error: null as string | null };
  } catch (e) {
    return {
      source,
      label: available.find((item) => item.key === source)?.label ?? source,
      report: null,
      comparison: null,
      graphGate: null,
      semanticGraph: null,
      available,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
