import type { PageServerLoad } from './$types';
import { loadPersonalProcessedOverview } from '$lib/server/corpora';

export const load: PageServerLoad = async () => {
  return {
    overview: await loadPersonalProcessedOverview()
  };
};
