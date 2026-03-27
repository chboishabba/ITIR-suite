import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { loadBroaderDiagnosticsDetail } from '$lib/server/corpora';

export const load: PageServerLoad = async ({ params }) => {
  const detail = await loadBroaderDiagnosticsDetail(params.diagnosticKey);
  if (!detail) throw error(404, 'Unknown broader diagnostic.');
  return { detail };
};
