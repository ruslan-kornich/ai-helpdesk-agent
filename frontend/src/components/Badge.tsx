import { resolveMeta } from "../ui/meta";

export default function Badge({ value }: { value: string | null | boolean }) {
  const meta = resolveMeta(value);
  if (!meta) return <span className="text-muted">—</span>;
  const Icon = meta.icon;
  return (
    <span className={`badge badge-${meta.tone}`}>
      <Icon size={12} strokeWidth={2.4} />
      {meta.label}
    </span>
  );
}
