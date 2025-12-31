import type { Metadata } from 'next';
import { Toaster } from 'react-hot-toast';
import './globals.css';

export const metadata: Metadata = {
  title: 'KANZ | AI Investment Advisor',
  description: 'Uncover Hidden Opportunities in the Heart of the Desert',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#ffffff',
              color: '#1d1d1f',
              border: '1px solid #d2d2d7',
              borderRadius: '12px',
              boxShadow: '0 2px 16px rgba(0, 0, 0, 0.1)',
            },
          }}
        />
      </body>
    </html>
  );
}
