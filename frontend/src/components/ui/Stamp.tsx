import { labelize } from "../../lib/formatters";

type StampTone = "neutral" | "signal" | "low" | "medium" | "high" | "critical" | "duplicate";

const TONE_CLASSES: Record<StampTone, string> = {
  neutral: "border-slate-light text-slate bg-white",
  signal: "border-signal text-signal bg-signal-light",
  low: "border-severity-low text-severity-low bg-white",
  medium: "border-severity-medium text-severity-medium bg-white",
  high: "border-severity-high text-severity-high bg-white",
  critical: "border-severity-critical text-severity-critical bg-white",
  duplicate: "border-duplicate text-duplicate bg-white",
};

/** Maps a severity/priority/risk value to a stamp tone. Unrecognized values
 * (e.g. "urgent" for priority) fall back to the closest severity tone. */
function toneForLevel(value: string | null | undefined): StampTone {
  switch ((value ?? "").toLowerCase()) {
    case "low":
      return "low";
    case "medium":
      return "medium";
    case "high":
      return "high";
    case "critical":
    case "urgent":
      return "critical";
    default:
      return "neutral";
  }
}

function toneForStatus(status: string | null | undefined): StampTone {
  switch (status) {
    case "closed":
      return "low";
    case "capa_assigned":
      return "signal";
    case "under_investigation":
      return "medium";
    case "pending_triage":
    default:
      return "neutral";
  }
}

export function Stamp({
  value,
  tone,
  kind = "level",
}: {
  value: string | null | undefined;
  tone?: StampTone;
  kind?: "level" | "status" | "plain";
}) {
  const resolvedTone = tone ?? (kind === "status" ? toneForStatus(value) : kind === "level" ? toneForLevel(value) : "neutral");
  return (
    <span className={`stamp ${TONE_CLASSES[resolvedTone]}`}>
      {labelize(value)}
    </span>
  );
}
