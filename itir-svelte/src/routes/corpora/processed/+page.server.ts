import type { PageServerLoad } from './$types';
import { loadProcessedCorpusSummaries } from '$lib/server/corpora';

export const load: PageServerLoad = async () => {
  return {
    corpora: await loadProcessedCorpusSummaries()
  };
};
