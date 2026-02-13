#!/usr/bin/env node
// Smoke-test Vite SSR module loading without binding a port.
// This helps pinpoint import cycles that trigger Vite SSR "module not yet fully initialized".
import { createServer } from 'vite';
import path from 'node:path';
import process from 'node:process';

const ROOT = process.cwd();

const CANDIDATES = [
  'src/routes/+layout.svelte',
  'src/routes/+page.svelte',
  'src/routes/graphs/wiki-timeline/+page.svelte',
  'src/routes/graphs/wiki-timeline-aoo/+page.svelte',
  'src/routes/graphs/wiki-timeline-aoo-all/+page.svelte',
  'src/routes/graphs/wiki-fact-timeline/+page.svelte'
];

function asFileUrl(p) {
  // Vite accepts filesystem paths for ssrLoadModule; keep it simple and absolute.
  return path.resolve(ROOT, p);
}

async function main() {
  const server = await createServer({
    root: ROOT,
    // NOTE: sandboxed runs can't bind ports; disable WS/HMR for this smoke test.
    server: { middlewareMode: true, hmr: false, ws: false },
    appType: 'custom',
    logLevel: 'warn'
  });

  let failed = false;
  for (const rel of CANDIDATES) {
    const id = asFileUrl(rel);
    try {
      await server.ssrLoadModule(id);
      // eslint-disable-next-line no-console
      console.log(`OK  ${rel}`);
    } catch (err) {
      failed = true;
      // eslint-disable-next-line no-console
      console.error(`FAIL ${rel}`);
      // eslint-disable-next-line no-console
      console.error(err?.stack || err);
      break;
    }
  }

  await server.close();
  process.exitCode = failed ? 1 : 0;
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err?.stack || err);
  process.exitCode = 1;
});
