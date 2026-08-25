import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError } from "../api/client";
import type { Book, Page } from "../types";
import { useAuth } from "../context/AuthContext";

export default function BooksPage() {
  const { hasPermission } = useAuth();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState<Page<Book> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", author: "", category: "", initial_copies: 1 });
  const [message, setMessage] = useState<string | null>(null);

  function load(query: string) {
    const qs = query ? `?search=${encodeURIComponent(query)}` : "";
    api
      .get<Page<Book>>(`/books${qs}`)
      .then(setPage)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load books"));
  }

  useEffect(() => {
    load("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    load(search);
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    try {
      await api.post("/books", form);
      setMessage("Book created.");
      setForm({ title: "", author: "", category: "", initial_copies: 1 });
      setShowForm(false);
      load(search);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to create book");
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Books</h1>
        {hasPermission("books:create") && (
          <button onClick={() => setShowForm((s) => !s)}>{showForm ? "Cancel" : "+ Add Book"}</button>
        )}
      </div>

      {showForm && (
        <form className="inline-form" onSubmit={handleCreate}>
          <input
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            required
          />
          <input
            placeholder="Author"
            value={form.author}
            onChange={(e) => setForm({ ...form, author: e.target.value })}
            required
          />
          <input
            placeholder="Category"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
          />
          <input
            type="number"
            min={0}
            value={form.initial_copies}
            onChange={(e) => setForm({ ...form, initial_copies: Number(e.target.value) })}
          />
          <button type="submit">Save</button>
        </form>
      )}
      {message && <div className="alert-info">{message}</div>}

      <form className="search-bar" onSubmit={handleSearch}>
        <input placeholder="Search by title, author, ISBN…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <button type="submit">Search</button>
      </form>

      {error && <div className="alert-error">{error}</div>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Author</th>
            <th>Category</th>
            <th>Available / Total</th>
          </tr>
        </thead>
        <tbody>
          {page?.items.map((book) => (
            <tr key={book.id}>
              <td>{book.title}</td>
              <td>{book.author}</td>
              <td>{book.category ?? "—"}</td>
              <td>
                {book.available_copies} / {book.total_copies}
              </td>
            </tr>
          ))}
          {page && page.items.length === 0 && (
            <tr>
              <td colSpan={4} className="empty-state">
                No books found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
