/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        surface: { DEFAULT: '#0f1419', card: '#1a2332', hover: '#243044' },
        accent: { DEFAULT: '#00d4aa', dim: '#00a884', danger: '#ff4757', warn: '#ffa502' },
      },
    },
  },
  plugins: [],
}
