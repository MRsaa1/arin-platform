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
        // SAA Alliance корпоративные цвета (точные из saa-alliance.com)
        'saa-dark': '#1a1a1a',      // Основной темный фон
        'saa-darker': '#0f0f0f',     // Еще темнее (для header)
        'saa-gold': '#CBA135',       // Золотой акцент (точный цвет с сайта)
        'saa-gold-dark': '#8B6F47',  // Темный золотой
        'saa-gold-light': '#E5D4A1',  // Светлый золотой
        'saa-white': '#FFFFFF',       // Белый текст
        'saa-gray': '#2a2a2a',       // Серый для карточек
        'saa-gray-light': '#3a3a3a', // Светло-серый
        'saa-border': '#404040',     // Цвет границ
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

