import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api/client";

interface TopBook {
  book_id: string;
  title: string;
  borrow_count: number;
}
interface CategoryShare {
  category: string;
  count: number;
}
interface MonthlyCirculation {
  month: string;
  issued: number;
  returned: number;
}

export default function AnalyticsPage() {
  const [topBooks, setTopBooks] = useState<TopBook[]>([]);
  const [categories, setCategories] = useState<CategoryShare[]>([]);
  const [monthly, setMonthly] = useState<MonthlyCirculation[]>([]);

  useEffect(() => {
    api.get<TopBook[]>("/analytics/top-books").then(setTopBooks).catch(() => {});
    api.get<CategoryShare[]>("/analytics/categories").then(setCategories).catch(() => {});
    api.get<MonthlyCirculation[]>("/analytics/monthly-circulation").then(setMonthly).catch(() => {});
  }, []);

  return (
    <div>
      <h1>Analytics</h1>

      <div className="card">
        <h3>Monthly Circulation</h3>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={monthly}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="issued" stroke="#6366f1" />
            <Line type="monotone" dataKey="returned" stroke="#22c55e" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card-grid">
        <div className="card">
          <h3>Most Borrowed Books</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={topBooks}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="title" hide />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="borrow_count" fill="#6366f1" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3>Category Distribution</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={categories}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" hide />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
