/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
    theme: {
        extend: {
            colors: {
                primary: '#007BFF', // Electric Blue
                secondary: '#00FFFF', // Cyan Neon (approx)
                dark: '#121212', // Dark Grey/Black
                darker: '#0a0a0a',
                surface: '#1e1e1e',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
