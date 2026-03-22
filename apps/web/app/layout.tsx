import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Providers } from "./providers";
import { Navbar } from "@/components/navbar";

export const metadata: Metadata = {
  title: "SMB Cash Flow Risk",
  description: "Early warning dashboard for short-term liquidity pressure, receivables risk, and collections prioritization.",
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