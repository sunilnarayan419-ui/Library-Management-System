import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { DashboardSummary } from "../types";

function KpiCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="kpi-card">
      <span className="kpi-value">{value}</span>
      <span className="kpi-label">{label}</span>
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<DashboardSummary>("/analytics/dashboard")
      .then(setSummary)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load dashboard"));
  }, []);

  if (error) return <div className="alert-error">{error}</div>;
  if (!summary) return <div className="centered">Loading dashboard…</div>;

  return (
    <div>
      <h1>Dashboard</h1>
      <div className="kpi-grid">
        <KpiCard label="Total Books" value={summary.total_books} />
        <KpiCard label="Total Copies" value={summary.total_copies} />
        <KpiCard label="Available Copies" value={summary.available_copies} />
        <KpiCard label="Issued Copies" value={summary.issued_copies} />
        <KpiCard label="Overdue Loans" value={summary.overdue_loans} />
        <KpiCard label="Active Members" value={summary.active_members} />
        <KpiCard label="Pending Reservations" value={summary.pending_reservations} />
        <KpiCard label="Outstanding Fines" value={`₹${summary.outstanding_fines_amount.toFixed(2)}`} />
      </div>
    </div>
  );
}
