/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                'sic-dark': '#0a0a0f',
                'sic-card': '#12121a',
                'sic-border': '#1e1e2e',
                'sic-green': '#00ff9d',
                'sic-red': '#ff4757',
                'sic-blue': '#4da6ff',
                'sic-purple': '#a855f7',
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'monospace'],
            },
        },
    },
    plugins: [],
}
