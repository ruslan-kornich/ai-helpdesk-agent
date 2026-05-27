import type { LucideIcon } from "lucide-react";
import type { Tone } from "../ui/meta";

const ICON_TONE: Record<Tone, string> = {
  neutral: "bg-surface-soft text-ink-soft",
  violet: "bg-violet-soft text-[#7c43c4]",
  sky: "bg-sky-soft text-[#2980b5]",
  mint: "bg-mint-soft text-[#138a76]",
  pos: "bg-mint-soft text-[#0f9268]",
  warn: "bg-[#fdf0db] text-[#b9791a]",
  danger: "bg-[#fde6e8] text-[#cf3d48]",
};

export default function StatCard({
  label,
  value,
  icon: Icon,
  tone = "violet",
  hint,
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: Tone;
  hint?: string;
}) {
  return (
    <div className="card p-5 transition-shadow hover:shadow-[var(--shadow-lift)]">
      <div className="flex items-start justify-between">
        <span className={`grid h-10 w-10 place-items-center rounded-2xl ${ICON_TONE[tone]}`}>
          <Icon size={19} strokeWidth={2.3} />
        </span>
        {hint && <span className="text-[11px] font-semibold text-muted">{hint}</span>}
      </div>
      <div className="mt-4 font-display text-[2rem] font-extrabold leading-none tracking-tight">
        {value}
      </div>
      <div className="mt-1.5 text-[13px] font-medium text-muted">{label}</div>
    </div>
  );
}
