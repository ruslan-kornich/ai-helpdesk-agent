export type Channel = "zendesk" | "telegram" | "teams" | "whatsapp";
export type Category =
  | "how_to" | "billing" | "delivery_issue" | "after_hours"
  | "commercial" | "outage" | "unknown" | "other";
export type Priority = "low" | "normal" | "high" | "urgent";
export type Sentiment = "positive" | "neutral" | "negative";
export type EscalationTarget =
  | "finance" | "sales" | "l2_support" | "support_lead" | "general_support" | null;
export type MessageRole = "client" | "agent" | "system";

export interface Ticket {
  ticket_id: string;
  created_at: string;
  channel: Channel;
  client_id: string;
  category: Category;
  priority: Priority;
  summary: string;
  conversation_snippet: string;
  escalation_target: EscalationTarget;
  resolved_by_ai: boolean;
  sentiment: Sentiment;
  ticket_metadata: Record<string, unknown>;
}

export interface Message {
  id: number;
  ticket_id: string;
  role: MessageRole;
  text: string;
  channel: Channel;
  created_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface DailyBucket {
  date: string;
  count: number;
}

export interface AnalyticsReport {
  total_tickets: number;
  by_channel: Record<string, number>;
  by_category: Record<string, number>;
  by_day: DailyBucket[];
  escalation_rate: number;
  ai_resolution_rate: number;
  sentiment_distribution: Record<string, number>;
  after_hours_volume: number;
}

export interface BotSettings {
  working_hours_start: number;
  working_hours_end: number;
  timezone: string;
  system_prompt: string;
}

export interface TicketFilters {
  channel?: Channel;
  category?: Category;
  priority?: Priority;
  sentiment?: Sentiment;
}

export interface SimulateResponse {
  reply: string;
  ticket: Ticket;
}
