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
          <svg className="logo-icon" viewBox="0 0 496 496" fill="currentColor" aria-hidden="true">
            <path d="M221.96 292.93c-18 20.48-40.35 30.6-67.24 30.36-44.26-.4-82.75-39.3-83.14-83.51-.31-35.3 15.05-61.74 45.59-78.61 45.2-25 99.46-1.96 117.9 41.15 13.92 32.54 8.94 62.74-13.11 90.61m-18.69-29.17c5-9.25 7.44-18.93 6.73-29.63-2.09-31.35-31.54-54.22-61.97-48.87-27.3 4.8-49.38 30.04-43.12 63.12 3.98 21.05 21.71 38.7 46.46 42.02 18.83 2.52 40.4-7.84 51.9-26.64z" />
            <path d="M359.95 240.11c11.65 26.48 23.15 52.6 34.75 78.96-3.55 1.88-6.58 1.16-9.47 1.22-6.33.11-12.66-.1-18.99.08-3.33.1-5.2-1.2-6.46-4.23-10.57-25.53-21.26-51.01-31.83-76.54-3.24-7.84-6.2-15.79-9.54-23.35-3.35 8.27-6.48 16.01-9.62 23.75-10.33 25.44-20.71 50.87-30.94 75.35-1.43 3.57-3.37 5.24-7.41 5.08-7.48-.29-14.99-.06-22.48-.11-1.6-.01-3.35.4-5.04-1.36 2.36-7.92 6.27-15.43 9.6-23.15 16.81-38.97 33.72-77.91 50.62-116.85 3.84-8.85 7.79-17.66 11.72-26.48.65-1.47 1.04-3.48 3.14-3.38 1.95.09 2.53 1.95 3.2 3.45 9.98 22.52 19.95 45.05 29.92 67.58 2.9 6.54 5.79 13.09 8.83 20z" />
            <g transform="translate(419 245.5) scale(1.2314) translate(-411 -259.5)">
              <path d="M429.02 279.94c-1.24 15.66-8.15 27.99-19.22 38.2-1.47 1.35-3.1 3.17-5.19 1.89-2.45-1.5-.58-3.53.1-5.27 2.43-6.21 4.48-12.52 5.06-19.22.19-2.16-.13-3.62-2.84-4.32-8.51-2.19-14.5-10.54-13.61-18.4.97-8.62 7.55-14.84 15.9-15.04 9.91-.24 17.38 5.51 19.05 14.79.41 2.28.51 4.62.75 7.37z" />
              <path d="M401.42 230.75c-7.72-5.71-10.34-15.58-6.39-23.08 3.9-7.4 13.5-10.97 21.42-7.98 9.67 3.65 14.08 14.19 9.89 23.64-4.33 9.76-14.67 12.96-24.92 7.42z" />
            </g>
            <path d="M176.15 237.07c-.95 9.13-5.1 15.51-13.66 18.32-10.26 3.37-21-2.35-24.24-12.68-3.09-9.82 2.59-20.58 12.39-23.5 10.64-3.16 21.62 2.66 24.56 13.05.4 1.44.63 2.93.95 4.81z" />
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