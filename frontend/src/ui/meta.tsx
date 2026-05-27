import {
  AlertTriangle,
  Ban,
  BellRing,
  Building2,
  CircleHelp,
  Clock,
  CreditCard,
  Frown,
  Headset,
  HelpCircle,
  type LucideIcon,
  Meh,
  MessageCircle,
  MessagesSquare,
  Moon,
  PackageX,
  Send,
  ShieldAlert,
  Smile,
  Sparkles,
  Tag,
  TrendingUp,
  Users,
  Wallet,
} from "lucide-react";

export type Tone = "neutral" | "violet" | "sky" | "mint" | "pos" | "warn" | "danger";

export interface Meta {
  label: string;
  icon: LucideIcon;
  tone: Tone;
}

const FALLBACK: Meta = { label: "—", icon: CircleHelp, tone: "neutral" };

const humanize = (value: string) =>
  value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());

export const CHANNEL_META: Record<string, Meta> = {
  telegram: { label: "Telegram", icon: Send, tone: "sky" },
  zendesk: { label: "Zendesk", icon: Headset, tone: "mint" },
  whatsapp: { label: "WhatsApp", icon: MessageCircle, tone: "pos" },
  teams: { label: "Teams", icon: MessagesSquare, tone: "violet" },
};

export const CATEGORY_META: Record<string, Meta> = {
  how_to: { label: "How-to", icon: HelpCircle, tone: "mint" },
  billing: { label: "Billing", icon: Wallet, tone: "violet" },
  delivery_issue: { label: "Delivery", icon: PackageX, tone: "warn" },
  after_hours: { label: "After hours", icon: Moon, tone: "sky" },
  commercial: { label: "Commercial", icon: TrendingUp, tone: "violet" },
  outage: { label: "Outage", icon: AlertTriangle, tone: "danger" },
  unknown: { label: "Unknown", icon: CircleHelp, tone: "neutral" },
  other: { label: "Other", icon: Tag, tone: "neutral" },
};

export const PRIORITY_META: Record<string, Meta> = {
  urgent: { label: "Urgent", icon: ShieldAlert, tone: "danger" },
  high: { label: "High", icon: AlertTriangle, tone: "warn" },
  normal: { label: "Normal", icon: Tag, tone: "neutral" },
  low: { label: "Low", icon: Tag, tone: "neutral" },
};

export const SENTIMENT_META: Record<string, Meta> = {
  positive: { label: "Positive", icon: Smile, tone: "pos" },
  neutral: { label: "Neutral", icon: Meh, tone: "neutral" },
  negative: { label: "Negative", icon: Frown, tone: "danger" },
};

export const ESCALATION_META: Record<string, Meta> = {
  finance: { label: "Finance", icon: CreditCard, tone: "violet" },
  sales: { label: "Sales", icon: TrendingUp, tone: "mint" },
  l2_support: { label: "L2 support", icon: ShieldAlert, tone: "warn" },
  support_lead: { label: "Support lead", icon: BellRing, tone: "danger" },
  general_support: { label: "General queue", icon: Users, tone: "sky" },
};

const REGISTRIES = [
  CHANNEL_META,
  CATEGORY_META,
  PRIORITY_META,
  SENTIMENT_META,
  ESCALATION_META,
];

export function resolveMeta(value: string | null | boolean): Meta | null {
  if (value === null || value === undefined || value === "") return null;
  if (typeof value === "boolean") {
    return value
      ? { label: "AI resolved", icon: Sparkles, tone: "pos" }
      : { label: "Escalated", icon: Users, tone: "warn" };
  }
  for (const registry of REGISTRIES) {
    if (registry[value]) return registry[value];
  }
  return { ...FALLBACK, label: humanize(value) };
}

export const ICONS = {
  Ban,
  Clock,
  Building2,
  Sparkles,
};
