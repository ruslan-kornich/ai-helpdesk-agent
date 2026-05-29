import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

export default function PageHeader({
  icon: Icon,
  title,
  accent,
  subtitle,
  actions,
}: {
  icon: LucideIcon;
  title: string;
  accent?: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="mb-7 flex flex-wrap items-center justify-between gap-4">
      <div className="flex items-center gap-3.5">
        <span className="brand-fill grid h-11 w-11 place-items-center rounded-2xl text-white shadow-[var(--shadow-lift)]">
          <Icon size={21} strokeWidth={2.3} />
        </span>
        <div>
          <h1 className="font-display text-[1.7rem] font-extrabold leading-none">
            {title} {accent && <span className="brand-text">{accent}</span>}
          </h1>
          {subtitle && <p className="mt-1.5 text-sm text-muted">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="flex items-center gap-2.5">{actions}</div>}
    </header>
  );
}
