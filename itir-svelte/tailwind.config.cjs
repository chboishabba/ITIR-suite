/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0b1020',
          900: '#101a33',
          800: '#162247'
        },
        paper: {
          50: '#fbfaf7',
          100: '#f3f1ea',
          200: '#e7e2d6'
        },
        accent: {
          600: '#c25b2a',
          700: '#9d4520'
        }
      },
      fontFamily: {
        display: ['Iowan Old Style', 'Palatino Linotype', 'Palatino', 'Georgia', 'serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'monospace']
      },
      boxShadow: {
        crisp: '0 1px 0 rgba(16,26,51,0.12), 0 10px 30px rgba(16,26,51,0.10)'
      }
    }
  },
  plugins: []
};
