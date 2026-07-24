import type { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`card ${className}`}>{children}</div>;
}

/** A numbered section header, e.g. "1. Origin & Customer Details" -- the
 * numbering reflects the real fixed sequence of the intake form defined in
 * backend/app/models/complaint.py, so it encodes true structure rather than
 * decorating the page. */
export function SectionHeader({ number, title }: { number: number; title: string }) {
  return (
    <div className="mb-4 flex items-center gap-3 border-b border-line pb-3">
      <span className="section-number">{number}</span>
      <h2 className="text-sm font-semibold uppercase tracking-stamp text-ink">{title}</h2>
    </div>
  );
}
