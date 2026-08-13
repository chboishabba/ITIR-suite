import adapter from '@sveltejs/adapter-auto';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  compilerOptions: {
    // Disable Svelte runes until we upgrade the app to be runes-safe.
    runes: false
  },
  kit: {
    adapter: adapter()
  }
};

export default config;
