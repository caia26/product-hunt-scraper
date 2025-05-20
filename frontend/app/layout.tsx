import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Product Hunt Database',
  description: 'View Product Hunt database scraped from Product Hunt API',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <header className="bg-white shadow-sm">
          <div className="max-w-6xl mx-auto py-4 px-6">
            <h1 className="text-xl font-bold text-orange-500">Product Hunt Database</h1>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
} 