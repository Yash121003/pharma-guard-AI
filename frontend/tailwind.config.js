/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#12181F",
        "ink-soft": "#1C242E",
        paper: "#F6F7F9",
        line: "#E2E5EA",
        slate: {
          DEFAULT: "#5B6472",
          light: "#8B94A3",
        },
        signal: {
          DEFAULT: "#2A5DB0",
          dark: "#1F477F",
          light: "#EAF0FA",
        },
        severity: {
          low: "#3F8F63",
          medium: "#B8802E",
          high: "#D9622B",
          critical: "#C1432A",
        },
        duplicate: "#6B5FA8",
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        stamp: "0.08em",
      },
    },
  },
  plugins: [],
};
