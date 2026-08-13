import { loadHcaCaseModel } from '$lib/server/viewers/hca-case';

export async function load({ url }: { url: URL }) {
  return await loadHcaCaseModel(url);
}
