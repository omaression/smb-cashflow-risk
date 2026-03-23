"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import "./navbar.css";

export function Navbar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <a href="https://info.omaression.com" target="_blank" rel="noopener noreferrer" className="logo-link" aria-label="Omar Abdalla - Portfolio">
          <svg
            className="logo-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
          </svg>
        </a>
        <Link href="/">SMB Cashflow</Link>
      </div>
      <div className="navbar-links">
        <Link href="/" className={isActive("/") ? "nav-link active" : "nav-link"}>
          Dashboard
        </Link>
        <Link href="/ml" className={isActive("/ml") ? "nav-link active" : "nav-link"}>
          ML Evidence
        </Link>
        <Link href="/try" className={isActive("/try") ? "nav-link active" : "nav-link"}>
          Try BYOD
        </Link>
        <a
          href="https://api.cashflow.omaression.com/docs"
          className="nav-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          API Docs
        </a>
        <a
          href="https://api.cashflow.omaression.com/api/v1/dashboard/summary"
          className="nav-link"
          target="_blank"
          rel="noopener noreferrer"
        >
          Summary JSON
        </a>
      </div>
    </nav>
  );
}