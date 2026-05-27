import {
  BarChart3,
  LogOut,
  type LucideIcon,
  Settings as SettingsIcon,
  Sparkles,
  TerminalSquare,
  Ticket,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { logout } from "../api";

const LINKS: { to: string; label: string; icon: LucideIcon; end: boolean }[] = [
  { to: "/", label: "Tickets", icon: Ticket, end: true },
  { to: "/simulator", label: "Simulator", icon: TerminalSquare, end: false },
  { to: "/analytics", label: "Analytics", icon: BarChart3, end: false },
  { to: "/settings", label: "Settings", icon: SettingsIcon, end: false },
];

export default function Layout() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="grid min-h-screen grid-cols-[244px_1fr]">
      <aside className="sticky top-0 flex h-screen flex-col border-r border-line bg-surface px-4 py-6">
        <div className="flex items-center gap-3 px-2">
          <span className="brand-fill grid h-10 w-10 place-items-center rounded-2xl text-white shadow-[var(--shadow-lift)]">
            <Sparkles size={20} strokeWidth={2.4} />
          </span>
          <div className="leading-tight">
            <p className="font-display text-[15px] font-extrabold">Gatum</p>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted">Support AI</p>
          </div>
        </div>

        <nav className="mt-8 flex flex-col gap-1.5">
          {LINKS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                [
                  "group relative flex items-center gap-3 rounded-2xl px-3.5 py-2.5 text-sm font-semibold transition-colors",
                  isActive
                    ? "bg-surface-soft text-ink"
                    : "text-muted hover:bg-surface-soft hover:text-ink",
                ].join(" ")
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className={[
                      "absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-full transition-opacity",
                      isActive ? "brand-fill opacity-100" : "opacity-0",
                    ].join(" ")}
                  />
                  <Icon
                    size={18}
                    strokeWidth={2.2}
                    className={isActive ? "text-[#8a4fd0]" : "text-muted group-hover:text-ink"}
                  />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto rounded-2xl border border-line bg-surface-soft p-3">
          <div className="flex items-center gap-2.5">
            <span className="brand-fill grid h-9 w-9 place-items-center rounded-xl text-sm font-extrabold text-white">
              A
            </span>
            <div className="min-w-0 leading-tight">
              <p className="truncate text-[13px] font-bold">Admin</p>
              <p className="truncate text-[11px] text-muted">Support team</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="mt-2.5 flex w-full items-center justify-center gap-2 rounded-xl bg-surface px-3 py-2 text-[13px] font-semibold text-muted transition-colors hover:text-danger"
          >
            <LogOut size={15} strokeWidth={2.3} />
            Sign out
          </button>
        </div>
      </aside>

      <main className="mesh-bg min-h-screen overflow-auto px-8 py-8 scrollbar-slim">
        <Outlet />
      </main>
    </div>
  );
}
