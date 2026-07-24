export function Spinner({ label }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-light border-t-signal" />
      {label && <span>{label}</span>}
    </div>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-sm border border-dashed border-line py-16 text-center">
      <p className="font-mono text-xs uppercase tracking-stamp text-slate">{title}</p>
      {hint && <p className="mt-2 max-w-sm text-sm text-slate-light">{hint}</p>}
    </div>
  );
}
