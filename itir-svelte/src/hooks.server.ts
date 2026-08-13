import type { Handle } from '@sveltejs/kit';

function shouldTrace(pathname: string): boolean {
  if (pathname === '/') return true;
  if (pathname.startsWith('/thread/')) return true;
  if (pathname.startsWith('/api/chat-message')) return true;
  return false;
}

function mb(bytes: number): string {
  return (bytes / (1024 * 1024)).toFixed(1);
}

const TRACE_MEM = /^(1|true|yes)$/i.test(String(process.env.ITIR_TRACE_MEM ?? ''));

export const handle: Handle = async ({ event, resolve }) => {
  const t0 = Date.now();
  const res = await resolve(event);

  if (TRACE_MEM && shouldTrace(event.url.pathname)) {
    const m = process.memoryUsage();
    const elapsedMs = Date.now() - t0;
    console.error(
      `[mem] ${event.request.method} ${event.url.pathname}${event.url.search} -> ${res.status}` +
        ` rss=${mb(m.rss)}MB heap=${mb(m.heapUsed)}/${mb(m.heapTotal)}MB ext=${mb(m.external)}MB` +
        ` arr=${mb(m.arrayBuffers)}MB t=${elapsedMs}ms`
    );
  }

  return res;
};

