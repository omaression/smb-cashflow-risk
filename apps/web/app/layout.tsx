import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Providers } from "./providers";
import { Navbar } from "@/components/navbar";

export const metadata: Metadata = {
  title: "SMB Cash Flow Risk",
  description: "Early warning dashboard for short-term liquidity pressure, receivables risk, and collections prioritization.",
  // Demo app with seeded data — must stay out of search indexes (Google had
  // indexed /invoices/INV-1002). Paired with the X-Robots-Tag header in
  // next.config.ts; robots.txt must keep ALLOWING crawls so bots can see these.
  robots: { index: false },
  openGraph: {
    title: "SMB Cash Flow Risk",
    description: "Early warning dashboard for SMB receivables risk and collections prioritization.",
    type: "website",
    siteName: "SMB Cash Flow Risk",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <Navbar />
          {children}
        </Providers>
        <footer className="site-footer">
          Built by <a href="https://omaression.com" target="_blank" rel="noreferrer">Omar</a> &middot; {new Date().getFullYear()}
        </footer>
      </body>
    </html>
  );
}