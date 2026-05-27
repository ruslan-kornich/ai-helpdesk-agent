import { useEffect, useState } from "react";
import { fetchSettings, saveSettings } from "../api";
import type { BotSettings } from "../types";

export default function Settings() {
  const [settings, setSettings] = useState<BotSettings | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetchSettings().then(setSettings);
  }, []);

  if (!settings) return <div className="muted">Loading…</div>;

  function update(patch: Partial<BotSettings>) {
    setSettings((current) => (current ? { ...current, ...patch } : current));
  }

  async function save() {
    if (!settings) return;
    const saved = await saveSettings(settings);
    setSettings(saved);
    setStatus("Saved");
    setTimeout(() => setStatus(""), 2000);
  }

  return (
    <div>
      <h2 className="page-title">Settings</h2>
      <div className="card" style={{ maxWidth: 640 }}>
        <dl className="kv">
          <dt>Working hours start</dt>
          <dd><input type="number" value={settings.working_hours_start}
            onChange={(event) => update({ working_hours_start: Number(event.target.value) })} /></dd>
          <dt>Working hours end</dt>
          <dd><input type="number" value={settings.working_hours_end}
            onChange={(event) => update({ working_hours_end: Number(event.target.value) })} /></dd>
          <dt>Timezone</dt>
          <dd><input value={settings.timezone}
            onChange={(event) => update({ timezone: event.target.value })} /></dd>
          <dt>Agent persona / tone</dt>
          <dd><textarea rows={6} style={{ width: "100%" }} value={settings.system_prompt}
            placeholder="e.g. Reply formally and concisely…"
            onChange={(event) => update({ system_prompt: event.target.value })} /></dd>
        </dl>
        <div className="row" style={{ marginTop: 12, alignItems: "center" }}>
          <button onClick={save}>Save</button>
          <span className="muted">{status}</span>
        </div>
      </div>
    </div>
  );
}
