import { useEffect, useState } from "react";
import { api, ApiError } from "../api/client";

interface Recommendation {
  book_id: string;
  title: string;
  author: string;
  category: string | null;
  reasons: string[];
}

export default function RecommendationsPage() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Recommendation[]>("/recommendations")
      .then(setRecs)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load recommendations"));
  }, []);

  return (
    <div>
      <h1>Recommended for You</h1>
      <p className="muted">
        Based on your borrowing history and what's popular in the library — no black-box ML, just
        explainable signals.
      </p>
      {error && <div className="alert-error">{error}</div>}
      <div className="card-grid">
        {recs.map((r) => (
          <div className="card" key={r.book_id}>
            <h3>{r.title}</h3>
            <p className="muted">
              {r.author} {r.category ? `· ${r.category}` : ""}
            </p>
            <ul className="reason-list">
              {r.reasons.map((reason, i) => (
                <li key={i}>{reason}</li>
              ))}
            </ul>
          </div>
        ))}
        {recs.length === 0 && !error && <p className="muted">No recommendations yet — borrow a few books first!</p>}
      </div>
    </div>
  );
}
