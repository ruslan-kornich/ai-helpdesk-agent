import { Check, Clock, Globe, MessageSquareQuote, Save, Settings as SettingsIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchSettings, saveSettings } from "../api";
import PageHeader from "../ui/PageHeader";
import type { BotSettings } from "../types";

export default function Settings() {
  const [settings, setSettings] = useState<BotSettings | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetchSettings().then(setSettings);
  }, []);

  useEffect(() => {
    if (!status) return;
    const timer = setTimeout(() => setStatus(""), 2000);
    return () => clearTimeout(timer);
  }, [status]);

  if (!settings) return <div className="py-20 text-center text-sm text-muted">Loading…</div>;

  function update(patch: Partial<BotSettings>) {
    setSettings((current) => (current ? { ...current, ...patch } : current));
  }

  async function save() {
    if (!settings) return;
    const saved = await saveSettings(settings);
    setSettings(saved);
    setStatus("Saved");
  }

  return (
    <div className="mx-auto max-w-[760px]">
      <PageHeader
        icon={SettingsIcon}
        title="Agent"
        accent="settings"
        subtitle="Tune working hours, timezone and the agent's persona."
      />

      <div className="space-y-5">
        <div className="card p-6">
          <div className="mb-5 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-muted">
            <Clock size={14} strokeWidth={2.3} /> Working hours
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1.5 block text-[13px] font-semibold text-ink-soft">Start hour</span>
              <input type="number" min={0} max={23} className="field" value={settings.working_hours_start}
                onChange={(event) => update({ working_hours_start: Number(event.target.value) })} />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-[13px] font-semibold text-ink-soft">End hour</span>
              <input type="number" min={0} max={23} className="field" value={settings.working_hours_end}
                onChange={(event) => update({ working_hours_end: Number(event.target.value) })} />
            </label>
            <label className="block sm:col-span-2">
              <span className="mb-1.5 flex items-center gap-1.5 text-[13px] font-semibold text-ink-soft">
                <Globe size={13} strokeWidth={2.3} /> Timezone
              </span>
              <input className="field" value={settings.timezone}
                onChange={(event) => update({ timezone: event.target.value })} />
            </label>
          </div>
        </div>

        <div className="card p-6">
          <div className="mb-5 flex items-center gap-2 text-[12px] font-bold uppercase tracking-wider text-muted">
            <MessageSquareQuote size={14} strokeWidth={2.3} /> Agent persona
          </div>
          <textarea rows={7} className="field resize-y font-mono text-[13px] leading-relaxed"
            value={settings.system_prompt}
            placeholder="e.g. Reply formally and concisely, always confirm receipt…"
            onChange={(event) => update({ system_prompt: event.target.value })} />
        </div>

        <div className="flex items-center gap-3">
          <button className="btn btn-dark" onClick={save}>
            <Save size={16} strokeWidth={2.3} /> Save changes
          </button>
          {status && (
            <span className="badge badge-pos gap-1.5 px-3 py-1.5">
              <Check size={13} strokeWidth={2.6} /> {status}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
