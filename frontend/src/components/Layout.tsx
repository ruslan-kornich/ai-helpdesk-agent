import { NavLink, Outlet } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Tickets", end: true },
  { to: "/simulator", label: "Simulator", end: false },
  { to: "/analytics", label: "Analytics", end: false },
  { to: "/settings", label: "Settings", end: false },
];

export default function Layout() {
  return (
    <div className="app">
      <aside className="sidebar">
        <h1>Gatum Support</h1>
        <nav>
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
