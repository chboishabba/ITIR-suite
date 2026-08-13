import type { PageServerLoad } from './$types';
import { loadChatArchiveOverview } from '$lib/server/corpora';

export const load: PageServerLoad = async () => {
  return await loadChatArchiveOverview();
};
