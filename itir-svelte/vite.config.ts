import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
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
