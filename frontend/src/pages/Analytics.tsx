import { BarChart3, Moon, Sparkles, Ticket as TicketIcon, Users } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { fetchAnalytics } from "../api";
import StatCard from "../components/StatCard";
import PageHeader from "../ui/PageHeader";
import type { AnalyticsReport } from "../types";

const PALETTE = ["#ac7be5", "#6ec1e4", "#6ee5d1", "#f0a93b", "#ef5d68", "#8a4fd0", "#2980b5", "#138a76"];
const SENTIMENT_COLOR: Record<string, string> = {
  positive: "#14b87f",
  neutral: "#b9c0cc",
  negative: "#ef5d68",
};

const AXIS = { stroke: "#aeb4bf", fontSize: 11, tickLine: false, axisLine: false } as const;
const TOOLTIP_STYLE = {
  borderRadius: 14,
  border: "1px solid #ecedf3",
  boxShadow: "0 12px 28px -16px rgba(35,38,45,0.25)",
  fontSize: 12,
  fontFamily: "Montserrat, sans-serif",
};

function toSeries(record: Record<string, number>) {
  return Object.entries(record).map(([name, value]) => ({ name, value }));
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card p-5">
      <h3 className="mb-4 font-display text-[15px] font-bold">{title}</h3>
      {children}
    </div>
  );
}

function ResolutionGauge({ rate }: { rate: number }) {
  const percent = Math.round(rate * 100);
  return (
    <div className="card relative overflow-hidden p-5">
      <span className="blob -right-10 -top-10 h-40 w-40" style={{ background: "rgba(110,229,209,0.4)" }} />
      <h3 className="relative mb-4 font-display text-[15px] font-bold">AI resolution</h3>
      <div className="relative flex items-center gap-6">
        <div
          className="grid h-32 w-32 shrink-0 place-items-center rounded-full"
          style={{
            background: `conic-gradient(#ac7be5 0deg, #6ec1e4 ${percent * 1.8}deg, #6ee5d1 ${percent * 3.6}deg, #ecedf3 ${percent * 3.6}deg)`,
          }}
        >
          <div className="grid h-24 w-24 place-items-center rounded-full bg-surface">
            <span className="font-display text-2xl font-extrabold">{percent}%</span>
          </div>
        </div>
        <p className="text-[13px] leading-relaxed text-muted">
          Share of conversations the agent closed without escalating to a human specialist.
        </p>
      </div>
    </div>
  );
}

export default function Analytics() {
  const [report, setReport] = useState<AnalyticsReport | null>(null);

  useEffect(() => {
    fetchAnalytics().then(setReport);
  }, []);

  if (!report) return <div className="py-20 text-center text-sm text-muted">Loading…</div>;

  const categoryData = toSeries(report.by_category);
  const sentimentData = toSeries(report.sentiment_distribution);
  const channelData = toSeries(report.by_channel);

  return (
    <div className="mx-auto max-w-[1180px]">
      <PageHeader
        icon={BarChart3}
        title="Support"
        accent="analytics"
        subtitle="Aggregated from every ticket the agent has processed."
      />

      <div className="mb-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard icon={TicketIcon} tone="violet" label="Total tickets" value={report.total_tickets} />
        <StatCard icon={Sparkles} tone="pos" label="AI resolution rate" value={`${Math.round(report.ai_resolution_rate * 100)}%`} />
        <StatCard icon={Users} tone="warn" label="Escalation rate" value={`${Math.round(report.escalation_rate * 100)}%`} />
        <StatCard icon={Moon} tone="sky" label="After-hours volume" value={report.after_hours_volume} />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <ResolutionGauge rate={report.ai_resolution_rate} />

        <ChartCard title="Sentiment">
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={sentimentData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={3} stroke="none">
                {sentimentData.map((entry) => (
                  <Cell key={entry.name} fill={SENTIMENT_COLOR[entry.name] ?? "#b9c0cc"} />
                ))}
              </Pie>
              <Tooltip contentStyle={TOOLTIP_STYLE} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="By category">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={categoryData} margin={{ left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ecedf3" vertical={false} />
              <XAxis dataKey="name" {...AXIS} interval={0} angle={-18} textAnchor="end" height={50} />
              <YAxis {...AXIS} allowDecimals={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(172,123,229,0.08)" }} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {categoryData.map((_, index) => <Cell key={index} fill={PALETTE[index % PALETTE.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="By channel">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={channelData} margin={{ left: -16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ecedf3" vertical={false} />
              <XAxis dataKey="name" {...AXIS} />
              <YAxis {...AXIS} allowDecimals={false} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(110,193,228,0.1)" }} />
              <Bar dataKey="value" radius={[8, 8, 0, 0]} fill="#6ec1e4" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <div className="lg:col-span-2">
          <ChartCard title="Tickets per day">
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={report.by_day} margin={{ left: -16 }}>
                <defs>
                  <linearGradient id="dayFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ac7be5" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#6ee5d1" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#ecedf3" vertical={false} />
                <XAxis dataKey="date" {...AXIS} />
                <YAxis {...AXIS} allowDecimals={false} />
                <Tooltip contentStyle={TOOLTIP_STYLE} />
                <Area type="monotone" dataKey="count" stroke="#ac7be5" strokeWidth={2.5} fill="url(#dayFill)" />
              </AreaChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </div>
    </div>
  );
}
