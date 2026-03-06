import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  // SSR should prefer non-browser exports (Svelte's `default`/server entries).
  // Do NOT remove the "browser" condition globally, otherwise client-side
  // packages like `esm-env` resolve `BROWSER=false` and hydration never starts.
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
        '**/.chat_archive.sqlite*',
        '**/*.sqlite-shm',
        '**/*.sqlite-wal'
      ]
    }
  }
});
