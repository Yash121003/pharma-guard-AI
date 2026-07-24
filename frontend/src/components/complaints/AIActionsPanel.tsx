import { useState, type ReactNode } from "react";
import * as aiApi from "../../api/ai";
import { apiErrorMessage } from "../../api/client";
import type { ComplaintPublic } from "../../types";
import { Button } from "../ui/Button";
import { Stamp } from "../ui/Stamp";

type TaskKey = "summarize" | "root_cause" | "capa" | "risk" | "duplicate" | "completeness";

const TASKS: { key: TaskKey; label: string }[] = [
  { key: "summarize", label: "Summarize" },
  { key: "root_cause", label: "Root Cause" },
  { key: "capa", label: "Draft CAPA" },
  { key: "risk", label: "Risk Assessment" },
  { key: "duplicate", label: "Duplicate Check" },
  { key: "completeness", label: "Completeness Check" },
];

export function AIActionsPanel({
  complaint,
  onUpdated,
}: {
  complaint: ComplaintPublic;
  onUpdated: (patch: Partial<ComplaintPublic>) => void;
}) {
  const [running, setRunning] = useState<TaskKey | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [duplicateNote, setDuplicateNote] = useState<string | null>(null);
  const [completenessNote, setCompletenessNote] = useState<string | null>(null);
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [riskReasoning, setRiskReasoning] = useState<string | null>(null);

  async function run(task: TaskKey) {
    setError(null);
    setRunning(task);
    try {
      switch (task) {
        case "summarize": {
          const res = await aiApi.summarize(complaint.id);
          onUpdated({ ai_summary: res.summary });
          break;
        }
        case "root_cause": {
          const res = await aiApi.rootCause(complaint.id);
          onUpdated({ ai_root_cause: res.root_cause });
          break;
        }
        case "capa": {
          const res = await aiApi.capa(complaint.id);
          onUpdated({ ai_capa_recommendation: res.capa_recommendation });
          break;
        }
        case "risk": {
          const res = await aiApi.risk(complaint.id);
          onUpdated({ ai_risk_level: res.risk_level });
          setRiskReasoning(res.reasoning);
          break;
        }
        case "duplicate": {
          const res = await aiApi.duplicateCheck(complaint.id);
          onUpdated({ is_duplicate_of_id: res.duplicate_of_id });
          setDuplicateNote(res.reasoning);
          break;
        }
        case "completeness": {
          const res = await aiApi.completeness(complaint.id);
          onUpdated({ ai_completeness_score: res.completeness_score, ai_completeness_notes: res.completeness_notes });
          setCompletenessNote(res.completeness_notes);
          setMissingFields(res.missing_fields);
          break;
        }
      }
    } catch (err) {
      setError(apiErrorMessage(err, "This AI task failed. Please try again."));
    } finally {
      setRunning(null);
    }
  }

  return (
    <div className="card p-5">
      <p className="mb-3 font-mono text-[11px] uppercase tracking-stamp text-slate">AI Analysis</p>

      <div className="mb-4 grid grid-cols-2 gap-2">
        {TASKS.map((t) => (
          <Button
            key={t.key}
            variant="secondary"
            className="justify-center text-xs"
            isLoading={running === t.key}
            disabled={running !== null}
            onClick={() => void run(t.key)}
          >
            {t.label}
          </Button>
        ))}
      </div>

      {error && (
        <p className="mb-4 rounded-sm border border-severity-critical/30 bg-severity-critical/5 px-3 py-2 text-sm text-severity-critical">
          {error}
        </p>
      )}

      <div className="space-y-4 text-sm">
        {complaint.ai_summary && (
          <AIResultBlock title="Summary">{complaint.ai_summary}</AIResultBlock>
        )}
        {complaint.ai_root_cause && (
          <AIResultBlock title="Suggested Root Cause">{complaint.ai_root_cause}</AIResultBlock>
        )}
        {complaint.ai_capa_recommendation && (
          <AIResultBlock title="Draft CAPA">{complaint.ai_capa_recommendation}</AIResultBlock>
        )}
        {complaint.ai_risk_level && (
          <AIResultBlock title="AI Risk Level">
            <div className="mb-1">
              <Stamp value={complaint.ai_risk_level} />
            </div>
            {riskReasoning && <p>{riskReasoning}</p>}
          </AIResultBlock>
        )}
        {duplicateNote && (
          <AIResultBlock title="Duplicate Check">
            <div className="mb-1">
              {complaint.is_duplicate_of_id ? (
                <Stamp value={`Matches #${complaint.is_duplicate_of_id}`} tone="duplicate" />
              ) : (
                <Stamp value="No match found" tone="neutral" />
              )}
            </div>
            <p>{duplicateNote}</p>
          </AIResultBlock>
        )}
        {(completenessNote || complaint.ai_completeness_notes) && (
          <AIResultBlock title="Completeness">
            {complaint.ai_completeness_score !== null && (
              <p className="mb-1 font-mono text-xs text-slate">
                Score: {complaint.ai_completeness_score}%
              </p>
            )}
            <p>{completenessNote ?? complaint.ai_completeness_notes}</p>
            {missingFields.length > 0 && (
              <p className="mt-1 text-xs text-severity-medium">Missing: {missingFields.join(", ")}</p>
            )}
          </AIResultBlock>
        )}
      </div>
    </div>
  );
}

function AIResultBlock({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-sm border border-line bg-paper p-3">
      <p className="mb-1 font-mono text-[10px] uppercase tracking-stamp text-slate">{title}</p>
      <div className="text-ink">{children}</div>
    </div>
  );
}
