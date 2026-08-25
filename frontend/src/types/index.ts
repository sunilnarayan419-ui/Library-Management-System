export type UserRole = "ADMIN" | "LIBRARIAN" | "MEMBER";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: "ACTIVE" | "DISABLED";
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Book {
  id: string;
  isbn: string | null;
  title: string;
  author: string;
  publisher: string | null;
  publication_year: number | null;
  category: string | null;
  description: string | null;
  language: string;
  total_copies: number;
  available_copies: number;
}

export interface Page<T> {
  items: T[];
  meta: { page: number; page_size: number; total: number; total_pages: number };
}

export interface Loan {
  id: string;
  book_id: string;
  copy_id: string;
  member_id: string;
  issued_at: string;
  due_at: string;
  returned_at: string | null;
  renewal_count: number;
  status: "ACTIVE" | "RETURNED" | "OVERDUE" | "LOST";
}

export interface DashboardSummary {
  total_books: number;
  total_copies: number;
  available_copies: number;
  issued_copies: number;
  overdue_loans: number;
  active_members: number;
  pending_reservations: number;
  outstanding_fines_amount: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  message: string;
  error_code?: string;
}
