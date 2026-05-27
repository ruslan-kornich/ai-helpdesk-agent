import { useEffect, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { fetchAnalytics } from "../api";
import StatCard from "../components/StatCard";
import type { AnalyticsReport } from "../types";

const COLORS = ["#5b8cff", "#2fbf71", "#f5a623", "#f25f5c", "#9b59b6", "#1abc9c", "#e67e22", "#7f8c8d"];

function toSeries(record: Record<string, number>) {
  return Object.entries(record).map(([name, value]) => ({ name, value }));
}

export default function Analytics() {
  const [report, setReport] = useState<AnalyticsReport | null>(null);

  useEffect(() => {
    fetchAnalytics().then(setReport);
  }, []);

  if (!report) return <div className="muted">Loading…</div>;

  const categoryData = toSeries(report.by_category);
  const sentimentData = toSeries(report.sentiment_distribution);
  const channelData = toSeries(report.by_channel);

  return (
    <div>
      <h2 className="page-title">Analytics</h2>
      <div className="grid cols-4" style={{ marginBottom: 16 }}>
        <StatCard label="Total tickets" value={report.total_tickets} />
        <StatCard label="AI resolution rate" value={`${Math.round(report.ai_resolution_rate * 100)}%`} />
        <StatCard label="Escalation rate" value={`${Math.round(report.escalation_rate * 100)}%`} />
        <StatCard label="After-hours volume" value={report.after_hours_volume} />
      </div>
      <div className="grid cols-2">
        <div className="card">
          <h3>By category</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3d" />
              <XAxis dataKey="name" stroke="#8b90a0" fontSize={11} />
              <YAxis stroke="#8b90a0" allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#5b8cff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Sentiment</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={sentimentData} dataKey="value" nameKey="name" outerRadius={90} label>
                {sentimentData.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
              </Pie>
              <Legend />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>By channel</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={channelData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3d" />
              <XAxis dataKey="name" stroke="#8b90a0" fontSize={11} />
              <YAxis stroke="#8b90a0" allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#2fbf71" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Tickets per day</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={report.by_day}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3d" />
              <XAxis dataKey="date" stroke="#8b90a0" fontSize={11} />
              <YAxis stroke="#8b90a0" allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#f5a623" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
