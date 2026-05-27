import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["var(--font-display)", "Google Sans", "Inter", "system-ui", "sans-serif"],
        sans: ["var(--font-sans)", "Inter", "Roboto", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "Roboto Mono", "Consolas", "monospace"],
      },
      colors: {
        studio: {
          ink: "hsl(var(--studio-ink))",
          panel: "hsl(var(--studio-panel))",
          panel2: "hsl(var(--studio-panel-2))",
          panel3: "hsl(var(--studio-panel-3))",
          line: "hsl(var(--studio-line))",
          text: "hsl(var(--studio-text))",
          muted: "hsl(var(--studio-muted))",
          cyan: "hsl(var(--studio-cyan))",
          violet: "hsl(var(--studio-violet))",
          orange: "hsl(var(--studio-orange))",
          green: "hsl(var(--studio-green))",
          yellow: "hsl(var(--studio-yellow))",
          red: "hsl(var(--studio-red))",
          blue: "hsl(var(--studio-blue))",
        },
        gm: {
          "primary-container": "hsl(var(--gm-primary-container))",
          "on-primary": "hsl(var(--gm-on-primary))",
          "surface-variant": "hsl(var(--gm-surface-variant))",
        },
      },
      boxShadow: {
        "elevation-1": "0 1px 2px rgba(0,0,0,0.1)",
        "elevation-2": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08)",
        "elevation-3": "0 4px 8px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.08)",
        "elevation-4": "0 8px 16px rgba(0,0,0,0.14), 0 4px 8px rgba(0,0,0,0.1)",
        glass: "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08)",
        tactile: "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08)",
      },
      borderRadius: {
        xs: "4px",
        sm: "8px",
        md: "12px",
        lg: "16px",
        xl: "20px",
        expressive: "12px",
        pill: "999px",
      },
    },
  },
  plugins: [animate],
};

export default config;
