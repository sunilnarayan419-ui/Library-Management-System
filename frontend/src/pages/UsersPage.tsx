import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError } from "../api/client";
import type { User } from "../types";
import StatusBadge from "../components/StatusBadge";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "MEMBER" });
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  function load() {
    api
      .get<User[]>("/users")
      .then(setUsers)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load users"));
  }

  useEffect(load, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setMessage(null);
    try {
      await api.post("/users", form);
      setMessage("User created.");
      setForm({ name: "", email: "", password: "", role: "MEMBER" });
      setShowForm(false);
      load();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to create user");
    }
  }

  async function toggleDisable(user: User) {
    try {
      if (user.status === "ACTIVE") {
        await api.post(`/users/${user.id}/disable`);
      } else {
        await api.patch(`/users/${user.id}`, { status: "ACTIVE" });
      }
      load();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to update user");
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Users</h1>
        <button onClick={() => setShowForm((s) => !s)}>{showForm ? "Cancel" : "+ Add User"}</button>
      </div>

      {showForm && (
        <form className="inline-form" onSubmit={handleCreate}>
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="MEMBER">Member</option>
            <option value="LIBRARIAN">Librarian</option>
            <option value="ADMIN">Admin</option>
          </select>
          <button type="submit">Save</button>
        </form>
      )}
      {message && <div className="alert-info">{message}</div>}
      {error && <div className="alert-error">{error}</div>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td>{u.role}</td>
              <td>
                <StatusBadge status={u.status} />
              </td>
              <td>
                <button className="btn-ghost" onClick={() => toggleDisable(u)}>
                  {u.status === "ACTIVE" ? "Disable" : "Enable"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
