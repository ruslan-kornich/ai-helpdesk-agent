type Tone = "neutral" | "green" | "amber" | "red" | "accent";

const TONE_BY_VALUE: Record<string, Tone> = {
  urgent: "red", high: "amber", normal: "neutral", low: "neutral",
  positive: "green", negative: "red",
  how_to: "green", outage: "red", after_hours: "accent",
};

export default function Badge({ value }: { value: string | null | boolean }) {
  if (value === null || value === undefined) return <span className="muted">—</span>;
  const text = String(value);
  const tone: Tone = TONE_BY_VALUE[text] ?? "neutral";
  return <span className={`badge badge-${tone}`}>{text}</span>;
}
