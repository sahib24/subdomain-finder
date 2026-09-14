import type { Metadata } from "next"; // Next.js metadata type
import type { ReactNode } from "react"; // React children-এর type
import { Geist, Geist_Mono } from "next/font/google"; // Google fonts
import "./globals.css"; // Global CSS

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Subdomain Finder", // Browser title
  description: "Subdomain Finder Tool", // Website description
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
