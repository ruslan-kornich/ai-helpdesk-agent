import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { logout } from "../api";

const LINKS = [
  { to: "/", label: "Tickets", end: true },
  { to: "/simulator", label: "Simulator", end: false },
  { to: "/analytics", label: "Analytics", end: false },
  { to: "/settings", label: "Settings", end: false },
];

export default function Layout() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app">
      <aside className="sidebar" style={{ display: "flex", flexDirection: "column" }}>
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
        <button className="secondary" onClick={handleLogout} style={{ marginTop: "auto" }}>
          Logout
        </button>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
