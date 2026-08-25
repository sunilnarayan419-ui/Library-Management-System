import { useState, type FormEvent } from "react";
import { api, ApiError } from "../api/client";
import type { Loan } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function CirculationPage() {
  const [bookId, setBookId] = useState("");
  const [memberId, setMemberId] = useState("");
  const [loanId, setLoanId] = useState("");
  const [lastLoan, setLastLoan] = useState<Loan | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function issue(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const loan = await api.post<Loan>("/circulation/issue", { book_id: bookId, member_id: memberId });
      setLastLoan(loan);
      setMessage(`Issued. Loan ID: ${loan.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Issue failed");
    }
  }

  async function returnBook(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const loan = await api.post<Loan>("/circulation/return", { loan_id: loanId });
      setLastLoan(loan);
      setMessage("Book returned.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Return failed");
    }
  }

  async function renew(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const loan = await api.post<Loan>("/circulation/renew", { loan_id: loanId });
      setLastLoan(loan);
      setMessage("Loan renewed.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Renew failed");
    }
  }

  return (
    <div>
      <h1>Circulation</h1>
      <p className="muted">
        Use book/member/loan IDs from the Books and Users pages (or the API docs at <code>/swagger</code>).
      </p>

      {error && <div className="alert-error">{error}</div>}
      {message && <div className="alert-info">{message}</div>}

      <div className="card-grid">
        <form className="card" onSubmit={issue}>
          <h3>Issue a Book</h3>
          <input placeholder="Book ID" value={bookId} onChange={(e) => setBookId(e.target.value)} required />
          <input placeholder="Member ID" value={memberId} onChange={(e) => setMemberId(e.target.value)} required />
          <button type="submit">Issue</button>
        </form>

        <form className="card" onSubmit={returnBook}>
          <h3>Return / Renew a Loan</h3>
          <input placeholder="Loan ID" value={loanId} onChange={(e) => setLoanId(e.target.value)} required />
          <div className="button-row">
            <button type="submit">Return</button>
            <button type="button" onClick={renew}>
              Renew
            </button>
          </div>
        </form>
      </div>

      {lastLoan && (
        <div className="card">
          <h3>Last Loan</h3>
          <p>
            <strong>Status:</strong> <StatusBadge status={lastLoan.status} />
          </p>
          <p>
            <strong>Due:</strong> {new Date(lastLoan.due_at).toLocaleString()}
          </p>
          <p>
            <strong>Renewals used:</strong> {lastLoan.renewal_count}
          </p>
        </div>
      )}
    </div>
  );
}
