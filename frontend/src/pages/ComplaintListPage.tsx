import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { listComplaints } from "../api/complaints";
import { apiErrorMessage } from "../api/client";
import type { ComplaintListItem } from "../types";
import { Stamp } from "../components/ui/Stamp";
import { Spinner, EmptyState } from "../components/ui/Spinner";
import { Button } from "../components/ui/Button";
import { formatDate, labelize } from "../lib/formatters";

export function ComplaintListPage() {
  const navigate = useNavigate();
  const [complaints, setComplaints] = useState<ComplaintListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listComplaints({ limit: 100 })
      .then(setComplaints)
      .catch((err) => setError(apiErrorMessage(err, "Could not load the complaint log.")));
  }, []);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-stamp text-slate">Record 001</p>
          <h1 className="text-xl font-semibold text-ink">Complaint Log</h1>
        </div>
        <Link to="/complaints/new">
          <Button>+ New Intake</Button>
        </Link>
      </div>

      {error && (
        <p className="mb-4 rounded-sm border border-severity-critical/30 bg-severity-critical/5 px-3 py-2 text-sm text-severity-critical">
          {error}
        </p>
      )}

      {!complaints && !error && <Spinner label="Loading complaint log…" />}

      {complaints && complaints.length === 0 && (
        <EmptyState
          title="No complaints logged yet"
          hint="Start a new intake to upload a complaint document or paste its text for AI extraction."
        />
      )}

      {complaints && complaints.length > 0 && (
        <div className="overflow-hidden rounded-sm border border-line bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-line bg-paper">
              <tr className="font-mono text-[11px] uppercase tracking-stamp text-slate">
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Customer</th>
                <th className="px-4 py-3">Product</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Logged</th>
              </tr>
            </thead>
            <tbody>
              {complaints.map((c) => (
                <tr
                  key={c.id}
                  className="cursor-pointer border-b border-line last:border-0 hover:bg-paper"
                  onClick={() => navigate(`/complaints/${c.id}`)}
                >
                  <td className="px-4 py-3 font-mono text-xs text-slate">#{String(c.id).padStart(4, "0")}</td>
                  <td className="px-4 py-3 font-medium">{c.customer_name}</td>
                  <td className="px-4 py-3 text-slate">{c.product_name_raw ?? "—"}</td>
                  <td className="px-4 py-3 text-slate">{labelize(c.complaint_type)}</td>
                  <td className="px-4 py-3">
                    <Stamp value={c.priority} />
                  </td>
                  <td className="px-4 py-3">
                    <Stamp value={c.status} kind="status" />
                  </td>
                  <td className="px-4 py-3 text-slate">{formatDate(c.complaint_date)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
