// T015: Create Next.js root layout with metadata
// T095: Add viewport meta tag for mobile rendering
// T089: Add responsive breakpoints using Tailwind CSS
// T102: Add frontend performance monitoring

import type { Metadata } from "next";
import { Inter, Poppins } from "next/font/google";
import "./globals.css";
import AnimatedRays from "@/components/AnimatedRays";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Todo App - Manage Your Tasks",
  description: "A full-stack todo application built with Next.js and FastAPI",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body
        className={`${inter.variable} ${poppins.variable} antialiased`}
        style={{ fontFamily: 'var(--font-inter)', position: 'relative', overflow: 'hidden' }}
      >
        <AnimatedRays />
        <div style={{ position: 'relative', zIndex: 1, minHeight: '100vh', overflow: 'auto' }}>
          {children}
        </div>
      </body>
    </html>
  );
}
