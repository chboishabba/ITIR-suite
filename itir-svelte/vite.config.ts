import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  // Work around intermittent Vite SSR resolution choosing browser-side Svelte
  // entrypoints, which can trigger a circular-import init error inside Svelte 5
  // (`index-client` <-> `store/utils` <-> `internal/client/...`).
  //
  // SSR should prefer non-browser exports (Svelte's `default`/server entries).
  // Also set non-SSR resolve conditions so dependency optimization doesn't pick
  // browser-first export maps and poison the SSR graph.
  resolve: {
    // Intentionally omit "browser" here.
    conditions: ['node', 'default', 'development']
  },
  ssr: {
    resolve: {
      // Intentionally omit "browser" here.
      conditions: ['node', 'default', 'development']
    },
    // Force Vite SSR to bundle Svelte rather than trying to externalize it under
    // a browser-biased condition set.
    noExternal: ['svelte']
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    watch: {
      ignored: [
        '**/StatiBaker/runs/**',
        '../StatiBaker/runs/**',
        '**/reverse-engineered-chatgpt/chat_exports/**',
        '../reverse-engineered-chatgpt/chat_exports/**',
        '**/chat-export-structurer/my_archive.sqlite*',
        '../chat-export-structurer/my_archive.sqlite*',
        '**/*.sqlite-shm',
        '**/*.sqlite-wal'
      ]
    }
  }
});
