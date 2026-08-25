import type { ApiResponse } from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1";

function getAccessToken(): string | null {
  return localStorage.getItem("lms_access_token");
}

export class ApiError extends Error {
  status: number;
  errorCode?: string;
  constructor(message: string, status: number, errorCode?: string) {
    super(message);
    this.status = status;
    this.errorCode = errorCode;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth: boolean = true
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };

  if (auth) {
    const token = getAccessToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  const body: ApiResponse<T> = await response.json().catch(() => ({
    success: false,
    data: null,
    message: "Invalid server response",
  }));

  if (!response.ok || !body.success) {
    throw new ApiError(body.message || "Request failed", response.status, body.error_code);
  }

  return body.data as T;
}

export const api = {
  get: <T,>(path: string) => request<T>(path, { method: "GET" }),
  post: <T,>(path: string, data?: unknown, auth = true) =>
    request<T>(path, { method: "POST", body: data ? JSON.stringify(data) : undefined }, auth),
  patch: <T,>(path: string, data?: unknown) =>
    request<T>(path, { method: "PATCH", body: data ? JSON.stringify(data) : undefined }),
  delete: <T,>(path: string) => request<T>(path, { method: "DELETE" }),
};

export { getAccessToken };
