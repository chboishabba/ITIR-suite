import type { PageServerLoad } from './$types';
import { loadBroaderDiagnosticsSummaries } from '$lib/server/corpora';

export const load: PageServerLoad = async () => {
  return {
    diagnostics: await loadBroaderDiagnosticsSummaries()
  };
};
