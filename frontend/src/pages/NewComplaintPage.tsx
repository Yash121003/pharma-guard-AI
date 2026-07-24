import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createComplaint } from "../api/complaints";
import { apiErrorMessage } from "../api/client";
import type { ComplaintCreate, ExtractResponse } from "../types";
import { IntakeSourcePanel } from "../components/complaints/IntakeSourcePanel";
import { ComplaintForm } from "../components/complaints/ComplaintForm";
import { Button } from "../components/ui/Button";
import { todayISODate } from "../lib/formatters";

const BLANK_COMPLAINT: ComplaintCreate = {
  complaint_source: "email",
  customer_name: "",
  product_name: "",
  strength: "",
  batch_number: "",
  manufacturing_date: null,
  expiry_date: null,
  quantity_affected: null,
  quantity_unit: "kg",
  complaint_type: "packaging_defect",
  complaint_date: todayISODate(),
  description: "",
  initial_severity: "medium",
  priority: "medium",
  source_document_path: null,
  source_document_type: null,
};

export function NewComplaintPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<ComplaintCreate>(BLANK_COMPLAINT);
  const [confidence, setConfidence] = useState<Record<string, number>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleExtracted(result: ExtractResponse) {
    const fields = result.fields as Partial<ComplaintCreate>;
    setForm((prev) => ({
      ...prev,
      ...fields,
      source_document_path: result.source_document_path ?? prev.source_document_path,
    }));
    setConfidence(result.confidence ?? {});
  }

  async function handleSave() {
    setError(null);
    setIsSaving(true);
    try {
      const created = await createComplaint(form);
      navigate(`/complaints/${created.id}`);
    } catch (err) {
      setError(apiErrorMessage(err, "Could not save this complaint."));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div>
      <div className="mb-6">
        <p className="font-mono text-[11px] uppercase tracking-stamp text-slate">New Intake</p>
        <h1 className="text-xl font-semibold text-ink">Log a Complaint</h1>
        <p className="mt-1 text-sm text-slate">
          Upload the source document or paste its text to auto-fill the form below, then review and save.
        </p>
      </div>

      <div className="grid grid-cols-[minmax(0,1fr)_360px] gap-6">
        <ComplaintForm value={form} onChange={setForm} confidence={confidence} />

        <div className="space-y-6">
          <IntakeSourcePanel onExtracted={handleExtracted} />

          {error && (
            <p className="rounded-sm border border-severity-critical/30 bg-severity-critical/5 px-3 py-2 text-sm text-severity-critical">
              {error}
            </p>
          )}

          <Button className="w-full" onClick={() => void handleSave()} isLoading={isSaving}>
            Save Complaint
          </Button>
        </div>
      </div>
    </div>
  );
}
