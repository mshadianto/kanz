/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // MacOS-inspired color palette
        macos: {
          bg: '#f5f5f7',
          surface: '#ffffff',
          border: '#d2d2d7',
          text: {
            primary: '#1d1d1f',
            secondary: '#6e6e73',
            tertiary: '#86868b',
          },
          blue: {
            DEFAULT: '#007aff',
            light: '#5ac8fa',
            dark: '#0051d5',
          },
          gray: {
            50: '#f9fafb',
            100: '#f5f5f7',
            200: '#e8e8ed',
            300: '#d2d2d7',
            400: '#b0b0b5',
            500: '#8e8e93',
            600: '#6e6e73',
            700: '#515154',
            800: '#3a3a3c',
            900: '#1c1c1e',
          }
        },
        saudi: {
          green: '#006c35',
          gold: '#c09d5f',
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Text', 'Segoe UI', 'Roboto', 'sans-serif'],
        display: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      fontSize: {
        'display-lg': ['3.5rem', { lineHeight: '1.1', letterSpacing: '-0.02em' }],
        'display': ['3rem', { lineHeight: '1.15', letterSpacing: '-0.015em' }],
        'title-lg': ['2rem', { lineHeight: '1.2', letterSpacing: '-0.01em' }],
        'title': ['1.5rem', { lineHeight: '1.25', letterSpacing: '-0.01em' }],
        'body-lg': ['1.125rem', { lineHeight: '1.5' }],
        'body': ['1rem', { lineHeight: '1.5' }],
        'caption': ['0.875rem', { lineHeight: '1.4' }],
      },
      borderRadius: {
        'macos': '12px',
        'macos-lg': '16px',
      },
      boxShadow: {
        'macos': '0 2px 16px rgba(0, 0, 0, 0.1)',
        'macos-lg': '0 8px 32px rgba(0, 0, 0, 0.12)',
        'macos-inner': 'inset 0 1px 2px rgba(0, 0, 0, 0.06)',
      },
      backdropBlur: {
        'macos': '20px',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
