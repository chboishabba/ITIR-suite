import { redirect } from '@sveltejs/kit';

function decodeGraphRef(rawValue: string | undefined): string {
  const joined = rawValue ?? '';
  try {
    return decodeURIComponent(joined);
  } catch {
    return joined;
  }
}

export async function load({ params }: { params: { graphRef?: string } }) {
  const graphRef = decodeGraphRef(params.graphRef);

  if (graphRef.startsWith('chat_archive://canonical_thread/')) {
    const threadId = graphRef.slice('chat_archive://canonical_thread/'.length).trim();
    if (threadId) {
      throw redirect(302, `/arguments/thread/${encodeURIComponent(threadId)}`);
    }
  }

  throw redirect(302, '/graphs/narrative-compare');
}
