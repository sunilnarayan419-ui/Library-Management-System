import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "../api/client";
import type { Tokens, User } from "../types";

interface LoginResponseData {
  user: User;
  tokens: Tokens;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

// Mirrors app/core/dependencies.py's ROLE_PERMISSIONS on the backend.
// Kept in sync manually since the frontend has no server-rendered route
// guards; the backend is always the source of truth and re-checks every
// request regardless of what the UI shows.
const ROLE_PERMISSIONS: Record<string, string[]> = {
  ADMIN: [
    "books:create", "books:update", "books:delete", "books:view",
    "circulation:issue", "circulation:return", "circulation:renew",
    "users:create", "users:update", "users:disable",
    "analytics:view", "audit:view",
  ],
  LIBRARIAN: [
    "books:create", "books:update", "books:view",
    "circulation:issue", "circulation:return", "circulation:renew",
    "analytics:view", "audit:view",
  ],
  MEMBER: ["books:view"],
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("lms_access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get<User>("/auth/me")
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("lms_access_token");
        localStorage.removeItem("lms_refresh_token");
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const data = await api.post<LoginResponseData>("/auth/login", { email, password }, false);
    localStorage.setItem("lms_access_token", data.tokens.access_token);
    localStorage.setItem("lms_refresh_token", data.tokens.refresh_token);
    setUser(data.user);
  }

  function logout() {
    localStorage.removeItem("lms_access_token");
    localStorage.removeItem("lms_refresh_token");
    setUser(null);
  }

  function hasPermission(permission: string): boolean {
    if (!user) return false;
    return ROLE_PERMISSIONS[user.role]?.includes(permission) ?? false;
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
