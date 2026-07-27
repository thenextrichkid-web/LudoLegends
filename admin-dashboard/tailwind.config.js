/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0A0A0F',
        surface: '#12121A',
        surfaceLight: '#1A1A25',
        primary: '#7B2FF2',
        primaryLight: '#9B5FF4',
        secondary: '#00D4AA',
        gold: '#FFD700',
        danger: '#FF4757',
        success: '#2ED573',
        border: '#2A2A3A',
      },
    },
  },
  plugins: [],
}
