"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

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
      <style jsx>{`
        .navbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 24px;
          background: var(--surface);
          border-bottom: 1px solid var(--border);
        }
        .navbar-brand a {
          font-weight: 700;
          font-size: 1.1rem;
          color: var(--text);
          text-decoration: none;
        }
        .navbar-links {
          display: flex;
          gap: 16px;
        }
        .nav-link {
          color: var(--muted);
          text-decoration: none;
          font-size: 0.9rem;
          padding: 6px 12px;
          border-radius: var(--radius-sm);
          transition: color 0.16s ease, background 0.16s ease;
        }
        .nav-link:hover {
          color: var(--text);
          background: rgba(255, 255, 255, 0.05);
        }
        .nav-link.active {
          color: var(--accent);
          background: var(--primary-fog);
        }
        @media (max-width: 768px) {
          .navbar {
            flex-direction: column;
            gap: 12px;
          }
          .navbar-links {
            flex-wrap: wrap;
            justify-content: center;
          }
        }
      `}</style>
    </nav>
  );
}