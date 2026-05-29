import type {
  AnalyticsReport, BotSettings, Message, Page, SimulateResponse,
  SupportMessage, Ticket, TicketFilters,
} from "./types";

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

function storeTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

function redirectToLogin(): void {
  clearTokens();
  if (window.location.pathname !== "/login") window.location.assign("/login");
}

async function tryRefresh(): Promise<boolean> {
  const refreshToken = localStorage.getItem(REFRESH_KEY);
  if (!refreshToken) return false;
  const response = await fetch("/api/auth/refresh", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) return false;
  const data = (await response.json()) as { access_token: string; refresh_token: string };
  storeTokens(data.access_token, data.refresh_token);
  return true;
}

interface RequestOptions extends RequestInit {
  auth?: boolean;
}

async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const { auth = true, headers: customHeaders, ...rest } = options;

  const doFetch = (): Promise<Response> => {
    const headers = new Headers(customHeaders);
    const token = getAccessToken();
    if (auth && token) headers.set("Authorization", `Bearer ${token}`);
    return fetch(url, { ...rest, headers });
  };

  let response = await doFetch();
  if (auth && response.status === 401) {
    if (await tryRefresh()) {
      response = await doFetch();
    } else {
      redirectToLogin();
      throw new Error("Unauthorized");
    }
    if (response.status === 401) {
      redirectToLogin();
      throw new Error("Unauthorized");
    }
  }
  if (!response.ok) throw new Error(`${rest.method ?? "GET"} ${url} failed: ${response.status}`);
  return response.json() as Promise<T>;
}

function jsonBody(method: string, body: unknown): RequestOptions {
  return { method, headers: { "content-type": "application/json" }, body: JSON.stringify(body) };
}

export async function login(email: string, password: string): Promise<void> {
  const response = await fetch("/api/auth/login", jsonBody("POST", { email, password }));
  if (!response.ok) throw new Error("Invalid email or password");
  const data = (await response.json()) as { access_token: string; refresh_token: string };
  storeTokens(data.access_token, data.refresh_token);
}

export function logout(): void {
  clearTokens();
}

export function fetchTickets(
  page: number, size: number, filters: TicketFilters,
): Promise<Page<Ticket>> {
  const params = new URLSearchParams({ page: String(page), size: String(size) });
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  return request<Page<Ticket>>(`/api/tickets?${params.toString()}`);
}

export function fetchTicket(ticketId: string): Promise<Ticket> {
  return request<Ticket>(`/api/tickets/${ticketId}`);
}

export function fetchMessages(
  ticketId: string, page: number, size: number,
): Promise<Page<Message>> {
  return request<Page<Message>>(`/api/tickets/${ticketId}/messages?page=${page}&size=${size}`);
}

export function fetchAnalytics(): Promise<AnalyticsReport> {
  return request<AnalyticsReport>("/api/analytics");
}

export function fetchSettings(): Promise<BotSettings> {
  return request<BotSettings>("/api/settings");
}

export function saveSettings(settings: BotSettings): Promise<BotSettings> {
  return request<BotSettings>("/api/settings", jsonBody("PUT", settings));
}

export function simulate(
  channel: string, clientId: string, text: string,
): Promise<SimulateResponse> {
  return request<SimulateResponse>(
    "/api/simulate",
    jsonBody("POST", { channel, client_id: clientId, text }),
  );
}

export function startSupportChat(
  name: string, email: string, text: string, zendeskTicketId?: string,
): Promise<{ zendesk_ticket_id: string }> {
  return request<{ zendesk_ticket_id: string }>("/api/support/chat", {
    ...jsonBody("POST", { name, email, text, zendesk_ticket_id: zendeskTicketId ?? null }),
    auth: false,
  });
}

export function fetchSupportReplies(
  zendeskTicketId: string, afterId: number,
): Promise<{ messages: SupportMessage[] }> {
  const params = new URLSearchParams({
    zendesk_ticket_id: zendeskTicketId, after_id: String(afterId),
  });
  return request<{ messages: SupportMessage[] }>(
    `/api/support/messages?${params.toString()}`, { auth: false },
  );
}

export function connectWebSocket(onMessage: (data: unknown) => void): WebSocket {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws`);
  socket.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      console.warn("Ignoring malformed WebSocket frame:", event.data);
    }
  };
  return socket;
}
