import {
  ArrowRight,
  BarChart3,
  Bot,
  Lock,
  Mail,
  MessageSquareText,
  Sparkles,
  Zap,
} from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";

const HIGHLIGHTS = [
  { icon: Bot, title: "Autonomous triage", text: "GPT-4o classifies, routes and replies across every channel." },
  { icon: MessageSquareText, title: "One inbox", text: "Telegram, Zendesk, WhatsApp and Teams in a single pipeline." },
  { icon: BarChart3, title: "Live analytics", text: "Resolution rate, sentiment and after-hours volume in real time." },
];

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/", { replace: true });
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.05fr_1fr]">
      <aside className="brand-fill relative hidden overflow-hidden p-12 text-white lg:flex lg:flex-col">
        <span className="blob -left-16 -top-16 h-72 w-72" style={{ background: "rgba(255,255,255,0.45)" }} />
        <span className="blob bottom-10 right-0 h-80 w-80" style={{ background: "rgba(110,229,209,0.55)", animationDelay: "-6s" }} />
        <span className="blob left-1/3 top-1/2 h-64 w-64" style={{ background: "rgba(172,123,229,0.5)", animationDelay: "-10s" }} />

        <div className="relative flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-white/20 backdrop-blur-sm">
            <Sparkles size={22} strokeWidth={2.4} />
          </span>
          <span className="font-display text-xl font-extrabold tracking-tight">Gatum</span>
          <span className="rounded-full bg-white/15 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider">
            Support AI
          </span>
        </div>

        <div className="relative mt-auto max-w-md">
          <h1 className="font-display text-[2.6rem] font-extrabold leading-[1.05]">
            One AI agent.
            <br />
            Every channel.
          </h1>
          <p className="mt-4 text-[15px] leading-relaxed text-white/85">
            The multichannel AI support agent for Gatum's messaging platform — it answers,
            classifies and escalates every conversation, then turns it into a clean ticket.
          </p>

          <ul className="mt-9 space-y-4">
            {HIGHLIGHTS.map(({ icon: Icon, title, text }) => (
              <li key={title} className="flex items-start gap-3.5">
                <span className="mt-0.5 grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-white/18 backdrop-blur-sm">
                  <Icon size={19} strokeWidth={2.2} />
                </span>
                <div>
                  <p className="font-display text-sm font-bold">{title}</p>
                  <p className="text-[13px] leading-snug text-white/80">{text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <main className="mesh-bg flex items-center justify-center px-6 py-12">
        <div className="animate-rise w-full max-w-[400px]">
          <div className="mb-8 flex items-center gap-3 lg:hidden">
            <span className="brand-fill grid h-10 w-10 place-items-center rounded-2xl text-white">
              <Sparkles size={20} strokeWidth={2.4} />
            </span>
            <span className="font-display text-lg font-extrabold">Gatum Support</span>
          </div>

          <div className="mb-1 inline-flex items-center gap-2 rounded-full bg-violet-soft px-3 py-1 text-[12px] font-bold text-[#7c43c4]">
            <Zap size={13} strokeWidth={2.6} /> Admin console
          </div>
          <h2 className="font-display text-[1.9rem] font-extrabold leading-tight">
            Welcome <span className="brand-text">back</span>
          </h2>
          <p className="mt-1.5 text-sm text-muted">Sign in to the support agent dashboard.</p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            <label className="block">
              <span className="mb-1.5 block text-[13px] font-semibold text-ink-soft">Email</span>
              <div className="relative">
                <Mail size={17} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-muted" />
                <input
                  type="email"
                  className="field pl-11"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@gatum.io"
                  autoComplete="username"
                  required
                />
              </div>
            </label>

            <label className="block">
              <span className="mb-1.5 block text-[13px] font-semibold text-ink-soft">Password</span>
              <div className="relative">
                <Lock size={17} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-muted" />
                <input
                  type="password"
                  className="field pl-11"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="••••••••"
                  autoComplete="current-password"
                  required
                />
              </div>
            </label>

            {error && (
              <div className="badge badge-danger w-full justify-start rounded-xl px-3 py-2 text-[12px]">
                {error}
              </div>
            )}

            <button type="submit" className="btn btn-dark mt-2 w-full" disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
              {!loading && <ArrowRight size={17} strokeWidth={2.4} />}
            </button>
          </form>

          <p className="mt-8 text-center text-[12px] text-muted">
            Protected console · contact your admin for access
          </p>
        </div>
      </main>
    </div>
  );
}
