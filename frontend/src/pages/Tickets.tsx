import { useEffect, useState } from "react";
import { connectWebSocket, fetchTickets } from "../api";
import TicketTable from "../components/TicketTable";
import type { Category, Channel, Ticket, TicketFilters } from "../types";

const PAGE_SIZE = 15;
const CHANNELS: Channel[] = ["telegram", "zendesk", "whatsapp", "teams"];
const CATEGORIES: Category[] = ["how_to", "billing", "delivery_issue", "after_hours", "commercial", "outage", "unknown", "other"];

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [filters, setFilters] = useState<TicketFilters>({});

  async function load() {
    const result = await fetchTickets(page, PAGE_SIZE, filters);
    setTickets(result.items);
    setPages(result.pages || 1);
  }

  useEffect(() => {
    load();
  }, [page, filters]);

  useEffect(() => {
    const socket = connectWebSocket((data) => {
      const message = data as { type?: string };
      if (message.type === "ticket") load();
    });
    return () => socket.close();
  }, [page, filters]);

  function updateFilter(key: keyof TicketFilters, value: string) {
    setPage(1);
    setFilters((current) => ({ ...current, [key]: value || undefined }));
  }

  return (
    <div>
      <h2 className="page-title">Tickets</h2>
      <div className="toolbar">
        <select onChange={(event) => updateFilter("channel", event.target.value)}>
          <option value="">All channels</option>
          {CHANNELS.map((channel) => <option key={channel} value={channel}>{channel}</option>)}
        </select>
        <select onChange={(event) => updateFilter("category", event.target.value)}>
          <option value="">All categories</option>
          {CATEGORIES.map((category) => <option key={category} value={category}>{category}</option>)}
        </select>
      </div>
      <div className="card">
        <TicketTable tickets={tickets} />
        <div className="pagination">
          <button className="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>
          <span className="muted">Page {page} / {pages}</span>
          <button className="secondary" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      </div>
    </div>
  );
}
