import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";

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
    <div style={{ display: "grid", placeItems: "center", minHeight: "100vh" }}>
      <form className="card" onSubmit={handleSubmit} style={{ width: 320, display: "grid", gap: 14 }}>
        <h1 style={{ margin: 0, fontSize: 18 }}>Gatum Support</h1>
        <label style={{ display: "grid", gap: 6 }}>
          <span className="muted" style={{ fontSize: 13 }}>Email</span>
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label style={{ display: "grid", gap: 6 }}>
          <span className="muted" style={{ fontSize: 13 }}>Password</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error && <span style={{ color: "var(--red)", fontSize: 13 }}>{error}</span>}
        <button type="submit" disabled={loading}>
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
    </div>
  );
}
