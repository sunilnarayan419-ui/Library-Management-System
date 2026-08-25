import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  const { user, logout, hasPermission } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">📚 LMS v5</div>
        <nav>
          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/books">Books</NavLink>
          {hasPermission("circulation:issue") && <NavLink to="/circulation">Circulation</NavLink>}
          <NavLink to="/recommendations">Recommendations</NavLink>
          <NavLink to="/ai">AI Librarian</NavLink>
          {hasPermission("analytics:view") && <NavLink to="/analytics">Analytics</NavLink>}
          {hasPermission("users:create") && <NavLink to="/users">Users</NavLink>}
        </nav>
        <div className="sidebar-footer">
          <div className="user-chip">
            <strong>{user?.name}</strong>
            <span>{user?.role}</span>
          </div>
          <button className="btn-ghost" onClick={logout}>
            Log out
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
