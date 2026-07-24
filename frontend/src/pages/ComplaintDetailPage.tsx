import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getComplaint } from "../api/complaints";
import { apiErrorMessage } from "../api/client";
import type { ComplaintPublic } from "../types";
import { Card } from "../components/ui/Card";
import { Stamp } from "../components/ui/Stamp";
import { Spinner } from "../components/ui/Spinner";
import { AIActionsPanel } from "../components/complaints/AIActionsPanel";
import { ChatPanel } from "../components/complaints/ChatPanel";
import { formatDate, formatDateTime, labelize } from "../lib/formatters";

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="field-label">{label}</p>
      <p className="text-sm text-ink">{value || "—"}</p>
    </div>
  );
}

export function ComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [complaint, setComplaint] = useState<ComplaintPublic | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getComplaint(Number(id))
      .then(setComplaint)
      .catch((err) => setError(apiErrorMessage(err, "Could not load this complaint.")));
  }, [id]);

  function applyPatch(patch: Partial<ComplaintPublic>) {
    setComplaint((prev) => (prev ? { ...prev, ...patch } : prev));
  }

  if (error) {
    return (
      <p className="rounded-sm border border-severity-critical/30 bg-severity-critical/5 px-3 py-2 text-sm text-severity-critical">
        {error}
      </p>
    );
  }

  if (!complaint) {
    return <Spinner label="Loading complaint record…" />;
  }

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-stamp text-slate">
            Case #{String(complaint.id).padStart(4, "0")}
          </p>
          <h1 className="text-xl font-semibold text-ink">{complaint.customer_name}</h1>
        </div>
        <div className="flex gap-2">
          <Stamp value={complaint.status} kind="status" />
          <Stamp value={complaint.priority} />
          <Stamp value={complaint.initial_severity} />
        </div>
      </div>

      <div className="grid grid-cols-[minmax(0,1fr)_360px] gap-6">
        <div className="space-y-6">
          <Card className="p-5">
            <p className="mb-4 font-mono text-[11px] uppercase tracking-stamp text-slate">
              1 · Origin &amp; Customer
            </p>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Complaint Source" value={labelize(complaint.complaint_source)} />
              <Field label="Customer Name" value={complaint.customer_name} />
            </div>
          </Card>

          <Card className="p-5">
            <p className="mb-4 font-mono text-[11px] uppercase tracking-stamp text-slate">
              2 · Product &amp; Batch
            </p>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Product" value={complaint.product_name_raw ?? ""} />
              <Field label="Strength" value={complaint.strength ?? ""} />
              <Field label="Batch Number" value={complaint.batch_number_raw ?? ""} />
              <Field label="Quantity Affected" value={complaint.quantity_affected ? `${complaint.quantity_affected} ${complaint.quantity_unit ?? ""}` : ""} />
              <Field label="Mfg. Date" value={formatDate(complaint.manufacturing_date)} />
              <Field label="Expiry Date" value={formatDate(complaint.expiry_date)} />
            </div>
          </Card>

          <Card className="p-5">
            <p className="mb-4 font-mono text-[11px] uppercase tracking-stamp text-slate">3 · Complaint Details</p>
            <div className="mb-4 grid grid-cols-2 gap-4">
              <Field label="Complaint Type" value={labelize(complaint.complaint_type)} />
              <Field label="Complaint Date" value={formatDate(complaint.complaint_date)} />
            </div>
            <Field label="Description" value={complaint.description} />
          </Card>

          <Card className="p-5">
            <p className="mb-2 font-mono text-[11px] uppercase tracking-stamp text-slate">Record Trail</p>
            <p className="text-xs text-slate-light">
              Logged {formatDateTime(complaint.created_at)} · Last updated {formatDateTime(complaint.updated_at)}
            </p>
          </Card>
        </div>

        <div className="space-y-6">
          <AIActionsPanel complaint={complaint} onUpdated={applyPatch} />
          <ChatPanel complaintId={complaint.id} />
        </div>
      </div>
    </div>
  );
}
