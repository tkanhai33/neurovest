import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
} from "next/font/google";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_APP_URL ||
      "http://127.0.0.1:3001"
  ),
  title: {
    default:
      "NeuroVest — Controlled Market Intelligence",
    template: "%s | NeuroVest",
  },
  description:
    "A locally powered financial intelligence platform built to observe markets, evaluate strategies, enforce risk boundaries, and expose system activity.",
  applicationName: "NeuroVest",
  keywords: [
    "NeuroVest",
    "market intelligence",
    "financial technology",
    "risk governance",
    "local AI",
    "trading research",
  ],
  openGraph: {
    title:
      "NeuroVest — Controlled Market Intelligence",
    description:
      "Private, observable, and controlled market intelligence.",
    type: "website",
    siteName: "NeuroVest",
  },
  robots: {
    index: false,
    follow: false,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        {children}
      </body>
    </html>
  );
}
