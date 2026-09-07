/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        darkBg: "#0f172a",
        cardBg: "#1e293b",
        borderSlate: "#334155",
        accentSky: "#38bdf8",
        accentAmber: "#f59e0b",
        alertRed: "#f43f5e",
        alertYellow: "#eab308",
        successGreen: "#10b981",
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
