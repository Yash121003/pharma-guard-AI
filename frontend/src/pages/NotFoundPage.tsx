import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex h-screen flex-col items-center justify-center gap-3 bg-paper">
      <p className="font-mono text-[11px] uppercase tracking-stamp text-slate">Error 404</p>
      <h1 className="text-lg font-semibold text-ink">This record doesn't exist.</h1>
      <Link to="/complaints" className="text-sm text-signal underline underline-offset-2">
        Back to the complaint log
      </Link>
    </div>
  );
}
