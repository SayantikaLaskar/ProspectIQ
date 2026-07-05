/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      keyframes: {
        float: { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-16px)' } },
        aurora: {
          '0%,100%': { transform: 'translate(0,0) scale(1)' },
          '33%': { transform: 'translate(5%,-7%) scale(1.15)' },
          '66%': { transform: 'translate(-6%,5%) scale(0.9)' },
        },
        shimmer: { '100%': { transform: 'translateX(100%)' } },
        glowpulse: { '0%,100%': { opacity: '0.55' }, '50%': { opacity: '1' } },
        pingslow: { '0%': { transform: 'scale(1)', opacity: '0.6' }, '80%,100%': { transform: 'scale(2.4)', opacity: '0' } },
        blink: { '0%,100%': { opacity: '1' }, '50%': { opacity: '0' } },
      },
      animation: {
        float: 'float 9s ease-in-out infinite',
        'float-slow': 'float 15s ease-in-out infinite',
        aurora: 'aurora 22s ease-in-out infinite',
        'aurora-slow': 'aurora 32s ease-in-out infinite',
        shimmer: 'shimmer 2.2s infinite',
        glowpulse: 'glowpulse 3s ease-in-out infinite',
        pingslow: 'pingslow 2.6s cubic-bezier(0,0,0.2,1) infinite',
        blink: 'blink 1s step-end infinite',
      },
    },
  },
  plugins: [],
}
