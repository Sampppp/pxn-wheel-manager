/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'class',
  theme: { extend: { colors: { surface: '#0f0f1a', card: '#16162a', accent: '#2ecc71' } } },
  plugins: [],
}
