import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "NetTrace AI",
  description: "Network intelligence dashboard for packet metadata and alerts.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <aside className="sidebar" aria-label="Primary navigation">
            <Link className="brand" href="/dashboard">
              <span className="brand-mark">N</span>
              <span>
                <strong>NetTrace AI</strong>
                <small>Network Intelligence</small>
              </span>
            </Link>
            <nav className="nav-links">
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/scans">Scans</Link>
            </nav>
          </aside>
          <main className="main-content">{children}</main>
        </div>
      </body>
    </html>
  );
}
