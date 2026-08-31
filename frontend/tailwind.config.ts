import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: "#f0ead9",
          panel: "#e8dfc8",
        },
        ink: {
          DEFAULT: "#211d16",
          dim: "#6f6555",
          border: "#d6cbb0",
        },
        oxblood: {
          DEFAULT: "#7c2e28",
          bright: "#9c3d34",
          dim: "#f1ded7",
        },
        gold: {
          DEFAULT: "#8a6b28",
          dim: "#f1e7cf",
        },
      },
      fontFamily: {
        display: ["var(--font-display)", "serif"],
        body: ["var(--font-body)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
