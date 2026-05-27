import type {
  AnalyticsReport, BotSettings, Message, Page, SimulateResponse,
  Ticket, TicketFilters,
} from "./types";

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`GET ${url} failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export async function fetchTickets(
  page: number, size: number, filters: TicketFilters,
): Promise<Page<Ticket>> {
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  return getJson<Page<Ticket>>(`/api/tickets?${params.toString()}`);
}

export function fetchTicket(ticketId: string): Promise<Ticket> {
  return getJson<Ticket>(`/api/tickets/${ticketId}`);
}

export function fetchMessages(
  ticketId: string, page: number, size: number,
): Promise<Page<Message>> {
  return getJson<Page<Message>>(`/api/tickets/${ticketId}/messages?page=${page}&size=${size}`);
}

export function fetchAnalytics(): Promise<AnalyticsReport> {
  return getJson<AnalyticsReport>("/api/analytics");
}

export function fetchSettings(): Promise<BotSettings> {
  return getJson<BotSettings>("/api/settings");
}

export async function saveSettings(settings: BotSettings): Promise<BotSettings> {
  const response = await fetch("/api/settings", {
    method: "PUT",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(settings),
  });
  if (!response.ok) throw new Error("PUT /api/settings failed");
  return response.json() as Promise<BotSettings>;
}

export async function simulate(
  channel: string, clientId: string, text: string,
): Promise<SimulateResponse> {
  const response = await fetch("/api/simulate", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ channel, client_id: clientId, text }),
  });
  if (!response.ok) throw new Error("POST /api/simulate failed");
  return response.json() as Promise<SimulateResponse>;
}

export function connectWebSocket(onMessage: (data: unknown) => void): WebSocket {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);
  socket.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      // ignore malformed frames
    }
  };
  return socket;
}
