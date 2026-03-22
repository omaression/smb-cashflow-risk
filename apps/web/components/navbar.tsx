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