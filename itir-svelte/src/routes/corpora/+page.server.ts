import type { PageServerLoad } from './$types';
import { loadCorpusHome } from '$lib/server/corpora';

export const load: PageServerLoad = async () => {
  return await loadCorpusHome();
};
