export default function StatusBadge({ status }: { status: string }) {
  const tone: Record<string, string> = {
    ACTIVE: "badge-green",
    AVAILABLE: "badge-green",
    RETURNED: "badge-blue",
    OVERDUE: "badge-red",
    ISSUED: "badge-amber",
    DISABLED: "badge-red",
    PENDING: "badge-amber",
    FULFILLED: "badge-blue",
    CANCELLED: "badge-gray",
  };
  return <span className={`badge ${tone[status] ?? "badge-gray"}`}>{status}</span>;
}
